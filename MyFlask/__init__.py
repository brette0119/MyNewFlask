"""
The flask application package.
"""
#引用Flask
from flask import Flask
#網站應用系統物件(配置路由Route) http://xxxxx/route/....
app = Flask(__name__)

import MyFlask.views
