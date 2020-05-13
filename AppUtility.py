import pyodbc as odbc
import pandas as pd
#定義資料dict 
person1={"id":1,"name":"張三丰","address":"高雄市鼓山區","phone":"07-343434"}
person2={"id":2,"name":"張泰山","address":"高雄市鼓山區","phone":"07-343434"}
person3={"id":3,"name":"張無際","address":"高雄市鼓山區","phone":"07-343434"}
#回應集合list
def data():
	return [person1,person2,person3]  #建構list物件封裝dict物件資料


