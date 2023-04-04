from flask import Flask, render_template, jsonify, request, session
from pymongo import MongoClient  
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from flask_jwt_extended import *
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import json

load_dotenv()
app = Flask(__name__)
# production
# client = MongoClient('mongodb://test:test@localhost',27017)
# dev
client = MongoClient('localhost', 27017)  
db = client.dbjungle  

@app.route('/')
def home():
    return render_template('index.html')
    

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)