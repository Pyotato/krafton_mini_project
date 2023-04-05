from flask import Flask
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import random
import string
app = Flask(__name__)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #웹스크래핑을 실행하는 브라우저
# driver.get("https://www.mangoplate.com/search/전국") #웹스크래핑할 사이트
# print("driver.title",driver.title)
# client = MongoClient('mongodb+srv://sparta:test@cluster0.6hzffoo.mongodb.net/?retryWrites=true&w=majority')#배포시 url
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.mini_project  # 'mini_project'라는 이름의 db를 만들거나 사용합니다.


# 지역의 대분류를 구하기 위해 xpath를 담을 배열
metro_category_xpath = []

# 지역의 대분류
metro_category = []
metro_category_coll = ['seoul_gangnam_col','seoul_gangbook_col','gyeonggi_col','incheon_col','daegu_col','busan_col','jeju_col','daejeon_col','gwangju_col','gangwon_col','gyeongsang_col','jeollanam_col','jeollabook_col','ullsan_col','choongcheongnam_col','choongcheongbook_col','sejong_col']

# 지역의 metro_category_coll
# 컬렉션 key - value ("지역명":"영문지역명_coll") 
db_collections = {}

areas_1 = range(1,6)
areas_2 = range(6,19)

for item in areas_1:
    metro_category_xpath.append("/html/body/main/article/div[2]/div/aside/div[1]/div/div[3]/p[1]/a["+str(item)+"]")
for item in areas_2:
    metro_category_xpath.append("/html/body/main/article/div[2]/div/aside/div[1]/div/div[3]/div[2]/a["+str(item)+"]")

#식당 카테고리
restaurant_category =[]
#식당 위치 대분류에 따른 식당 상세 페이지 url
restaurant_urls = []

infos = []

#음식점 지역
def get_restaurant_locations():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #웹스크래핑을 실행하는 브라우저
    driver.get("https://www.mangoplate.com/search/전국") #웹스크래핑할 사이트
    # 지역명 분류 ex서울,강남,경기도...
    for xpaths in metro_category_xpath:
        metro_cat = driver.find_element(By.XPATH,xpaths)
        metro_list = metro_cat.get_attribute("outerHTML")
        soup= BeautifulSoup(metro_list,'html.parser')
        m_cat = soup.select("a")
        for indx,items in enumerate(m_cat):
            metro_category.append(items.text)
            restaurant_urls.append({"location_cat":items.text,"urls":[]})
            db_collections.update({items.text:metro_category_coll[indx]})

            
            
    for metro_items in metro_category:
        # print("지역",items)
        # 20페이지 정도 max로 생각하고 있음..
        # page=range(1,21)
        page=range(1,2) # test용 1페이지
        for pg in page :
            link_arr = [] #상세 정보 링크들
            link_location_narrowed = [] #식당 위치 (구/동)
            food_category = [] #음식 카테고리
            driver.get("https://www.mangoplate.com/search/"+metro_items+"?keyword="+metro_items+"&page="+str(pg))
            if driver.find_element(By.CLASS_NAME,'list-restaurants') is not None:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
                data = requests.get("https://www.mangoplate.com/search/"+metro_items+"?keyword="+metro_items+"&page="+str(pg), headers=headers)
                soup = BeautifulSoup(data.text, 'html.parser')

                #식당 상세설명 링크
                restaurant_detail_link = soup.select('.restaurant-item > a.only-desktop_not')
                for links in restaurant_detail_link:
                    link_arr.append(links['href'])
                     
                #식당 위치 주소 (구/동)
                restaurant_n_location = soup.select('.restaurant-item >figcaption > .info > p.etc')        
                for restaurant_n_items in restaurant_n_location:
                    location_food_category_str =  restaurant_n_items.text
                    location_food_category_arr = str(location_food_category_str).split(' - ')
                    link_location_narrowed.append(location_food_category_arr[0])
                    food_category.append(location_food_category_arr[1])
       
            link_range = range(0,len(link_arr))
            
            print("driver successfully closed")

            for i in link_range:
                infos.append({"location_category":metro_items,"url":link_arr[i],"location_catagory_narrowed":link_location_narrowed[i],"food_category":food_category[i] })

    return infos    

detail_desc = []

def get_restaurant_details(restaurant_info):
    for items in restaurant_info:
            
        url =  items.get("url")
        location_category =  items.get("location_category")
        location_catagory_narrowed =  items.get("location_catagory_narrowed")
        food_category =  items.get("food_category")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get("https://www.mangoplate.com"+url, headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        restaurant_name = soup.select_one(".inner > .restaurant-detail > header > .restaurant_title_wrap > .title > .restaurant_name").text #식당이름
        restaurant_thumbnail_url = soup.find("meta",  {"property":"og:image"})#식당사진
        if restaurant_thumbnail_url is None:
            return;
        else: 
            restaurant_thumbnail_url=restaurant_thumbnail_url["content"]
        restaurant_ratings = soup.select_one("header > .restaurant_title_wrap > .title > strong.rate-point ") #식당 별점
        if restaurant_ratings is not None:
            restaurant_ratings = restaurant_ratings.text #식당 별점
        restaurant_address = soup.select_one("table > tbody>  tr.only-desktop > td > span.Restaurant__InfoAddress--Text ").text #식당 주소

        restaurant_data ={
            "restaurant_name":restaurant_name,
            "location_category":location_category,
            "location_catagory_narrowed":location_catagory_narrowed,
            "food_category":food_category,
            "restaurant_thumbnail_url":restaurant_thumbnail_url,
            "restaurant_ratings":restaurant_ratings,
            "restaurant_address":restaurant_address,
        }
        
        insert_db(restaurant_data)

        # 데이터량이 많으므로 random하게 생성하는 id에 중복이 생겨 들어가지 않을 수 있음 
        # id 중복 방지를 위해 지정해주기
        # item_id = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(24)) 
        # restaurant_data.update({"_id":item_id}) 
        # # location_category =  restaurant_data.get("location_category")
        # # check_duplicate(location_category,record)
        # current_collection = db[db_collections.get(location_category)]
        # current_collection.drop()
        # while current_collection.find_one({"_id": restaurant_data.get("item_id")}) is None:
        #     try:
        #         print(restaurant_data)
        #         current_collection.insert_one(restaurant_data)
        #         print('완료!-  등록 성공!!!!!')
        #         break
        #     except:
        #         item_id = ''.join(random.choice(
        #             string.ascii_letters + string.digits) for i in range(24))
        #         restaurant_data.update({"_id": item_id})


def insert_db(r_d):
    item_id = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(24)) 
    r_d.update({"_id":item_id})
    # r_d.get("location_category")
    current_collection = db.get_collection(name=r_d.get("location_category"))
    # current_collection.drop()
    # print(current_collection)
    current_collection.insert_one(r_d)
    # while current_collection.find_one({"_id": r_d.get("item_id")}) is None:
    #     try:
    #         print(r_d)
    #         current_collection.insert_one(r_d)
    #         print('완료!-  등록 성공!!!!!')
    #         break
    #     except:
    #         item_id = ''.join(random.choice(
    #             string.ascii_letters + string.digits) for i in range(24))
    #         r_d.update({"_id": item_id})
    

#식당 위치에 따른 식당 상세페이지 url 리스트 실행 함수

get_restaurant_locations()
print("스크래핑은 성공")
get_restaurant_details(infos)
print("디테일 성공")



