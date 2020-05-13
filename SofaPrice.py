#沙發價格
import requests as req
from bs4 import BeautifulSoup
import pandas 

def SofaPriceList():
	#定義網址
	urlString='https://www.ikea.com.tw/zh/products/sofas/fabric-sofas/'
	#使用requests 進行請求讀取內容回來 採用Http Request Method-GET
	response=req.get(urlString) #回應一個response物件(封裝訊息送往前端)
	#是否OK(Http Status Code-200 OK/404-not found...)
	#print(type(response))
	if response.status_code==req.codes.ok:
		print('網頁讀取成功')
		#定義收集產品名稱與價格兩個list物件 動態加入
		productList=[]
		priceList=[]
		#透過Response讀取網頁所有內容
		content=response.text
		#print(content)
		#進行爬文處理-整理內容與剖析
		#1建構BeautifulSoup 物件
		soup=BeautifulSoup(content,'html.parser')
		#print(soup)
		#透過find_all() 找出整個網頁符合 找出特定標籤<div> 回應ResultSet
		result=soup.find_all('div',class_='itemInfo') #產品清單的card-body區段
		#print(result) ResultSet as list(類似)
		for item in result: #使用foreach 語法問出每一個項目Tag物件
			#print(type(item)) #bs4.element.Tag
			#找出hyper lnk<a..
			#anchor=item.find('a');
			#透過Tag標籤物件找出Attribute
			#href=anchor.get('href')
			details=item.find_all('div',class_='itemDetails')
			#走訪itemDetails裡面的標籤物件
			#產品名稱
			for detailsTag in details:
				print('產品名稱:'+detailsTag.text) #<xxx>hello</xxx> hello innerText Tag.text
				#使用list進行動態加入
				productList.append(detailsTag.text.replace('\n',''))
			#價格
			prices=item.find_all('div',class_='itemPrice-wrapper')
			#走訪ResultSet裡面的Tag
			for priceTag in prices:
				classNameList=priceTag.find('p').get('class') #itemNormalPrice display-6 切換成list 兩個項目
				if classNameList[0]=='itemNormalPrice':
					#print("一般價格:"+priceTag.text) #Normal or Lower
					#讓集合物件進行動態參考
					priceList.append(priceTag.text.replace('\n\n',''))
				if classNameList[0]=='itemLowerPrice':
					#print("調降後最低價格:"+priceTag.text) #Normal or Lower
					priceList.append('**'+priceTag.text.replace('\n\n',''))
		#print(productList)
		#print(priceList)
		#收集成一個dict 欄位:list,...
		data={'產品名稱':productList,'價格/**特價':priceList}
		#透過pandas DataFrame
		df=pandas.DataFrame(data) #將dict封裝成DataFrame物件
		#print(df)
		#寫出去變成一個excel檔案(前置作業 產生一個Writer物件)
		#writer=pandas.ExcelWriter('c:/東門/sofaprice.xlsx',engine='xlsxwriter')
		#正式透過writer物件寫出去
		#df.to_excel(writer,sheet_name='沙發產品價格')
		#writer.save() #正式儲存commit 清除緩存取(關閉檔案)
		return df #回應dict
	



