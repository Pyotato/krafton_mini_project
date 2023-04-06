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
import random
# from localStoragePy import localStoragePy
import localstorage
load_dotenv()
my_secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
# production
# client = MongoClient('mongodb+srv://sparta:test@cluster0.6hzffoo.mongodb.net/?retryWrites=true&w=majority')#배포시 url

# dev
client = MongoClient('localhost', 27017)  
db = client.mini_project  
users_collection = db['pick_menu_user']
metro_category_coll = db.list_collection_names()
mylocation ={}
# scope_large =""
# scope_medium =""


app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config.update(DEBUG=True, JWT_SECRET_KEY=my_secret_key)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
data =[]
records =[]
total_data=[]
city = ""
# geopy
@app.route("/api/location/user", methods=['POST'])
def locate_user():
    x_y = request.json["curr_location"]
    mylocation = geocoding_reverse(x_y)
    print(mylocation["address_si"])
    return mylocation
# 위치 겁색어로 좌표 구하고 좌표를 통해 주소를 가져와서 db컬렉션에 해당 정보 찾아서 랜더링
@app.route("/api/location/user/find/me", methods=['POST'])
def locate_user_from_input():
    location = request.json["curr_location"]
    mylocation = geocoding(location)
    loc_str = mylocation["lat"]+","+mylocation["lng"]
    loc = geocoding_reverse(loc_str)
    # print(loc)
    return {"my_location":loc,"my_coord":loc_str}

##########################################################
# pages
@app.route('/')
def home():

    # return render_template('index.html',mylocation=city) # 아래 코드에 에러 남..
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, my_secret_key, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info,display_signup="true")
    except :
         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다.",display_signup="true"))
    # except jwt.ExpiredSignatureError:
    #     return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    # except jwt.exceptions.DecodeError:
    #     return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    

@app.route('/token', methods=["POST"])
def create_token():
    user_id = request.json.get("user_id", None)
    password = request.json.get("pwd", None)
    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    if  db.users.find_one({'user_id': user_id, 'password': pw_hash}) is None:
        return {"msg": "Wrong email or password"}, 401
    access_token = create_access_token(identity=user_id)
    response = {"result":"success","access_token":access_token}
    
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


@app.route('/restaurant/listcity/<string:location_city>')
def restaurant_list_page_city(location_city):
    item_filter =""
    city_data = []
    city_item = []
    print(location_city)
    for items in metro_category_coll: 
        if location_city in items or items in location_city :
            # print(items)
            city_data.append(items)
    
    print(city_data)
    if len(city_data)==0:
        item_filter="전체"
        return redirect(url_for("restaurant_list_page",city_filter=item_filter))
    else:
        for i in city_data:
            item_filter+=" , "+i
            city_item.extend(list(db[i].find()))
        print(city_item)
        return render_template('restaurantListPage.html',data=city_item,city_filter=item_filter)
    # else:
    #     return print(city_data)
        # else : return redirect(url_for("restaurant_list_page"))



@app.route('/restaurant/list')
def restaurant_list_page():
    if mylocation.get("address_si") is None:

        for items in metro_category_coll: 
            data.extend(list(db[items].find()))
        for i in data:
             if i.get("restaurant_name") is not None:
                 records.append(i)
    else:
        data.append(list(db[mylocation.get("address_si")].find()))
        for i in data:
            if i.get("restaurant_name") is not None:
                records.append(i)
    try:
        random.shuffle     
        return redirect(restaurant_detail_page("restaurant_detail_page",location_cat=data.get("location_category"),location_specific=data.get("location_specific"),restaurant_name=data.get("restaurant_name")))
    
    except:

        return render_template('restaurantListPage.html',data=records,city_filter="전체")



@app.route('/restaurant/detail/<string:location_cat>/<string:location_specific>/<string:restaurant_name>')
def restaurant_detail_page(location_cat,location_specific,restaurant_name):
    
    item = db[location_cat].find_one({"location_category":location_cat,"location_catagory_narrowed":location_specific,"restaurant_name":restaurant_name})
    
    return render_template('restaurantdetailPage.html',location_cat=location_cat,location_specific=location_specific,restaurant_name=restaurant_name,details=item)

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


# @app.route("/api/login", methods=['POST'])
# def login_user():

#     user_id = request.json["user_id"]
#     pwd = request.json["pwd"]
#     user = users_collection.find_one({'user_id': user_id})
#     if user is None:
#         return jsonify({'result': 'success', 'msg': 'user id does not exist'})
#     pw_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
#     result = db.users.find_one({'user_id': user_id, 'password': pw_hash})
   
#         # return jsonify(msg="login sucess", result="success", access_token=create_access_token(identity=user_id, expires_delta=jwt_access_token_expires))
#     if result is not None:
#         return jsonify(result="success", msg="login success", user_id=user["user_id"], access_token=create_access_token(identity=user_id, expires_delta=timedelta(hours=1)))
#         # return jsonify(result="success", access_token=create_access_token(identity=user_id, expires_delta=datetime.timedelta(hours=1)))
#     else:
#         return jsonify({'result': 'fail', 'msg': 'incorrect pwd'})


@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response






#################################################################################

# print("kakao_secret_key",kakao_secret_key)
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)