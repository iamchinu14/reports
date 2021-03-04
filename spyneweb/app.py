from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = "secret key"
app.config["MONGO_URI"] = "mongodb://15.206.92.130:27017/eventila"
mongo = PyMongo(app)