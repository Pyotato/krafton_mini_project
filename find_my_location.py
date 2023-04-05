from geopy.geocoders import Nominatim
# 사용자의 주소 -> 서버데이터의 좌표에 맞도록
# ssr 쪽에 가까운 느낌 : 사용자의 좌표를 입력하면 '서버에서 계산'을해서 db에 있는 해당 데이터를 가져옴
# 좌표 -> 주소
def geocoding_reverse(lat_lng_str): 
    geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
    address = geolocoder.reverse(lat_lng_str)
    address_arr = str(address).split(', ')
    address_info = {}
    last_index = len(address_arr)-1
    if address_arr[last_index]=="대한민국":
        for items in address_arr:  
            last_index = len(items)-1
            if items[last_index]=='동':
                address_info.update({"address_dong":items})
            if items[last_index]=='구':
                address_info.update({"address_gu":items})
            if items[last_index]!='구' and items[last_index]!='동'and items[last_index]!='길' and items!='대한민국': 
                try: # 우편 주소 (숫자)가 아닌
                    int(items[0])
                except: # 시 (위치 대분류 뽑아오기)
                    items
                    address_info.update({"address_si":items})
    
        return address_info
    else:
       return {"msg":"foreign user_agent", "address_arr":address_arr}


# address = geocoding_reverse('37.5132615,127.03155987091925') # client에서 현재 주소 가져오기
# print(address) # 116, 정왕신길로49번길, 정왕4동, 정왕동, 시흥시, 15028, 대한민국

# 서버데이터의 주소 -> 사용자의 좌표에 맞도록
# csr 쪽에 가까운 느낌 : 절대값(데이터의 x좌표- 사용자의 x 좌표)  + 절대값(데이터의 y좌표- 사용자의 y 좌표) 거리가 단거리가 되도록 데이터베이스의 정보를 클라이언트 쪽에서 계산해서 랜더링하게 될듯
# 주소 -> 좌표
def geocoding(address):
    geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
    geo = geolocoder.geocode(address)
    crd = {"lat": str(geo.latitude), "lng": str(geo.longitude)}

    return crd

# crd = geocoding("서울시 강남구 논현동 106-17")
# print(crd['lat'])
# print(crd['lng'])