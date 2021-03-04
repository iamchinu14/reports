from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = "secret key"
app.config["MONGO_URI"] = "mongodb://172.31.18.236:27017/eventila"
mongo = PyMongo(app)

app1 = Flask(__name__)
app1.secret_key = "secret key"
app1.config["MONGO_URI"] = "mongodb://172.31.18.236:27017/cliq"
mongo1 = PyMongo(app1)
