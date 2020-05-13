"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from MyFlask import app
import requests #類似http client
from AppUtility import data #自訂模組引用
from flask import jsonify,request,make_response  #類似HttpRequest(封裝前端送進來所有資訊)
import SofaPrice as sofa
import pyodbc as odbc
import pandas as pd
#測試連接環境設定
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table,Column
#引用資料風格(不同資料庫風格不一樣)
from sqlalchemy.dialects.mssql import (NCHAR,NVARCHAR,MONEY)
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json as json
#定義一個Entity Class Mapping Table用的
class Customers(object):
    #自訂建構子
	def __init__(self,CustomerID,CompanyName,Address,Country):
		#設定Attribute指派相對參數內容
		self.CustomerID=CustomerID
		self.CompanyName=CompanyName
		self.Address=Address
		self.Country=Country

#首頁
@app.route('/')
@app.route('/default')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )


def homePage():
    #使用requests Module取出遠端的HTTP內容
    urlString='https://www.google.com'
    #採用GET傳送方式 提出遠端請求 產生一個回應Response物件
    response=requests.get(urlString)
    print(type(response))
    return str(response.text)  #透過Response取出爬取回的網頁字串
    
    
@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

#客製化一個端點End Point 請求
@app.route('/cdc/covid19')
def covid19():
    #服務網址
    urlString='https://od.cdc.gov.tw/eic/covid19/covid19_tw_specimen1.csv'
    #假設需要在Header 傳遞apikey value
    #建構辭典物件dict
    myHeader={"apikey":"1234567890","user-agent":"mypython"}

    #透過request進行請求(採用具名參數架構 paramName=value)
    response=requests.get(urlString,headers=myHeader)
    #進行判斷是否OK 200狀態碼
    if response.status_code==200:
        return response.text
    else:
        msg=str.format("<font size='7' color='red'>錯誤訊息:{}</font>".format(response.status_code))
        return  msg

#設定Route Decorator 設定request method -GET/POST/PUT/DELETE
@app.route('/data/persons',methods=['GET','POST'])
def personData():
    #呼叫模組取出list類別資料
    personList=data()
    #將dict物件序列化成JSON String(非ascii轉換成\u0000 \uffff unicode表示方式
    return jsonify(personList) #資訊服務 預設Content-Type:application/json
   

#定義一個可以配合編號找出個人資料
@app.route('/personal/search')
def personSearch():
    #參考出前端request所傳送進來參數
    argument=request.args #配合QueryString ?xxx=value1&xxx=value2
    key=request.headers.get('apikey')
    #body=request.body 沒有這一個attribute
    return str(key)

#定義一個提供動態爬IKEA沙發價格
@app.route('/ikea/sofa')
def sofaPrice():
    #接受到一個dict 
    data=sofa.SofaPriceList()
    jsonString=jsonify(data) #序列化物件為json String
    return jsonString  #只能回應字串

#定義一個app route進行客戶資料查詢
@app.route('/customers/qry')
def customersQry():
    #截去前端傳遞進來參數(QueryString ...?參數=值&參數=value,....
    params=request.args #結果是一個dict 透過名稱取值
    #設定連接資料庫組態
    server='localhost'
    username='sa'
    password='1111'
    database='NORTHWND'
    driver='{ODBC Driver 17 for SQL Server}'
    #連接上SQL(開啟一條連接)
    connString='DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format(driver,server,database,username,password)
    connection=odbc.connect(connString)
    #進行資料查詢 借助cursor物件
    cursor=connection.cursor()
    #進行資料查詢執行
    sql="Select CustomerID,CompanyName,Address,Phone,Country From Customers Where Country=N'{}'".format(params['country'])
    cursor.execute(sql)
    #進行Fetching
    res=cursor.fetchone()
    #建構一個list物件
    customers=[]
    #進行回圈
    while res!=None:
        #整理物件相關欄位為list
        row={} #建構一個空的dict物件
        #動態新增Map(key->value)
        row.update(CustomerID=res[0])
        row.update(CompanyName=res[1])
        row.update(Address=res[2])
        row.update(Phone=res[3])
        row.update(Country=res[4])
        #將這一筆dict讓list參考
        customers.append(row)
        #再往下擷取
        res=cursor.fetchone()
    #先關閉cursor
    cursor.close()
    #關閉連接
    connection.close()

    #序列化物件(list->dict)
    jsonString=jsonify(customers)
    #return jsonString
    #resp=make_response(jsonString)
    #resp.headers['apikey']='123456789'
    #resp.minetype='application/json'
    return jsonString


@app.route('/customers/qrytodfsave')
def customersQryDF():
    #截去前端傳遞進來參數(QueryString ...?參數=值&參數=value,....
    params=request.args #結果是一個dict 透過名稱取值
    #設定連接資料庫組態
    server='localhost'
    username='sa'
    password='1111'
    database='NORTHWND'
    driver='{ODBC Driver 17 for SQL Server}'
    #連接上SQL(開啟一條連接)
    connString='DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format(driver,server,database,username,password)
    connection=odbc.connect(connString)
    #進行資料查詢 借助cursor物件
    cursor=connection.cursor()
    #進行資料查詢執行
    sql="Select CustomerID,CompanyName,Address,Phone,Country From Customers Where Country=N'{}'".format(params['country'])
    cursor.execute(sql)
    #進行Fetching
    res=cursor.fetchone()
    #建構一個list物件
    customers=[]
    #欄位清單list
    customerid=[]
    company=[]
    address=[]
    #進行回圈
    while res!=None:
        #整理物件相關欄位為list
        row={} #建構一個空的dict物件
        #動態新增Map(key->value)
        row.update(CustomerID=res[0])
        row.update(CompanyName=res[1])
        row.update(Address=res[2])
        row.update(Phone=res[3])
        row.update(Country=res[4])
        #將這一筆dict讓list參考
        customers.append(row)
        #收集欄位清單
        customerid.append(res[0])
        company.append(res[1])
        address.append(res[2])
        #再往下擷取
        res=cursor.fetchone()
    #先關閉cursor
    cursor.close()
    #關閉連接
    connection.close()
    #建構DataFrame
    df=pd.DataFrame({'CustomerID':customerid,'CompanyName':company,'Address':address})
    #儲存成json file
    df.to_json('c:/tools/customerdata.json')
    #序列化物件(list->dict)
    jsonString=jsonify(customers)
    #return jsonString
    #resp=make_response(jsonString)
    #resp.headers['apikey']='123456789'
    #resp.minetype='application/json'
    return jsonString


#採用SQLAlchemy ORM進行資料庫客戶資料查詢 by Coountry
@app.route('/customers/country/<country>/rawdata',methods=['GET'])
def CustomersQryORM(country):
    #建立一個連接資料庫引擎物件(連接工廠 不會建立一條連接出來)
    dbEngine=create_engine('mssql+pyodbc://sa:1111@DESKTOP-FTVU75K/NORTHWND?driver=SQL Server Native Client 11.0')
    
    #要一條連接(具有Open)
    connection=dbEngine.connect()
    
    #建立MetaData 應對資料庫資料表Table Schema
    customersMetaData=MetaData() #可以設定到兩個Table結構以上

    #ORM(R-Rlational Table結構描述)
    #設定MetaData應對資料結構物件(Table)(table name->field Name attribute)
    customersTB=Table('Customers',customersMetaData,
				      Column('CustomerID',NCHAR(5),nullable=False,primary_key=True),
				      Column('CompanyName',NVARCHAR(40),nullable=False),
				      Column('Address',NVARCHAR(60)),
				      Column('Country',NVARCHAR(15))
			     )
    #Mapping(ORM-M)
    mapper(Customers,customersTB) #Entity->Table Mapping
    #連接資料庫綁定結構(採用一個Global綁定後端資料庫架構)
    base=declarative_base()
    base.metadata.create_all(dbEngine)
    #建構一個SessionMaker物件
    Session=sessionmaker()
    #將這一個SessionMaker綁定在應對資料庫的引擎上
    Session.configure(bind=dbEngine)
    #產生一條Session Criteria(查詢)
    session=Session()
    #撰寫查詢敘述(針對Entity Class)
    resultList=session.query(Customers).filter(Customers.Country==country).all()

    #序列化成JSON字串
    return json.dumps(resultList[0])