from flask import Flask, render_template, jsonify, request, session,redirect,url_for
from pymongo import MongoClient  
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from flask_jwt_extended import *
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import json
import hashlib
from jwt import ExpiredSignatureError,DecodeError
from find_my_location import geocoding_reverse,geocoding

load_dotenv()
my_secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
# production
# client = MongoClient('mongodb+srv://sparta:test@cluster0.6hzffoo.mongodb.net/?retryWrites=true&w=majority')#배포시 url

# dev
client = MongoClient('localhost', 27017)  
db = client.mini_project  
users_collection = db['pick_menu_user']


app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config.update(DEBUG=True, JWT_SECRET_KEY=my_secret_key)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

##########################################################
# pages
@app.route('/')
def home():
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, my_secret_key, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    # except :
    #      return redirect(url_for("login"))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    

@app.route('/token', methods=["POST"])
def create_token():
    user_id = request.json.get("user_id", None)
    password = request.json.get("password", None)
    if user_id != "test" or password != "test":       # 여기를 어떻게 해야할지?
        return {"msg": "Wrong email or password"}, 401
    access_token = create_access_token(identity=user_id)
    response = {"access_token":access_token}
    return response

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.errorhandler(404)
def error_page(error):
    return render_template('errorPage.html')


@app.route('/restaurant/list')
def restaurant_list_page():
    return render_template('restaurantListPage.html')

@app.route('/restaurant/detail')
def restaurant_detail_page():
    return render_template('restaurantdetailPage.html')

##########################################################
# apis
@app.route("/api/check/duplicate/id", methods=['POST'])
def check_duplicate_user_id():
    user_id = request.json["user_id"]
    user_userid_exists = users_collection.find_one({'user_id': user_id})
    if user_userid_exists:
        # return True
        return jsonify({'result': 'success', 'msg': "unavailable"})
    elif user_userid_exists is None:
        # return False
        return jsonify({'result': 'success', 'msg': "available"})
    else:
        jsonify({'result': 'fail', 'msg': "internal error"})



@app.route("/api/register", methods=['POST'])
def register_user():
    user_id = request.json["user_id"]
    pwd = request.json["pwd"]

    user_id_exists = users_collection.find_one({'user_id': user_id})
    if user_id_exists:
        return jsonify({'result': 'fail', 'msg': "duplicate"})
    hashed_pwd = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
    new_user = {'user_id': user_id,'password': hashed_pwd}
    users_collection.insert_one(new_user)
    return jsonify({'result': 'success',  "user_id": user_id})


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now+timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route("/api/login", methods=['POST'])
def login_user():

    user_id = request.json["user_id"]
    pwd = request.json["pwd"]
    user = users_collection.find_one({'user_id': user_id})
    if user is None:
        return jsonify({'result': 'success', 'msg': 'user id does not exist'})
    pw_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
    result = db.users.find_one({'user_id': user_id, 'password': pw_hash})
        # return jsonify(msg="login sucess", result="success", access_token=create_access_token(identity=user_id, expires_delta=jwt_access_token_expires))
    if result is not None:
        return jsonify(result="success", msg="login success", user_id=user["user_id"],  access_token=create_access_token(identity=user_id))
        # return jsonify(result="success", access_token=create_access_token(identity=user_id, expires_delta=datetime.timedelta(hours=1)))
    else:
        return jsonify({'result': 'fail', 'msg': 'incorrect pwd'})


@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

#################################################################################
# geopy
@app.route("/api/location/user", methods=['POST'])
def locate_user():
    x_y = request.json["curr_location"]
    mylocation = geocoding_reverse(x_y)
    print(mylocation)
    return mylocation

# print("kakao_secret_key",kakao_secret_key)
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)