import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from PIL import Image
import io
import base64

def get_coordinates(address):
    """주소를 좌표로 변환"""
    geolocator = Nominatim(user_agent="my_agent")
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        print(f"주소 변환 중 오류 발생: {e}")
        return None

def calculate_distance(home_address, farm_address):
    """두 주소 간의 직선 거리 계산 (km)"""
    home_coords = get_coordinates(home_address)
    farm_coords = get_coordinates(farm_address)
    
    if home_coords and farm_coords:
        distance = geodesic(home_coords, farm_coords).kilometers
        return round(distance, 1)
    return None

def create_map(home_address, farm_address, share_ratio):
    """네이버 지도에 농지 표시"""
    home_coords = get_coordinates(home_address)
    farm_coords = get_coordinates(farm_address)
    
    if not (home_coords and farm_coords):
        return None
    
    # 지도 생성
    m = folium.Map(location=farm_coords, zoom_start=15)
    
    # 집 위치 표시
    folium.Marker(
        home_coords,
        popup='집',
        icon=folium.Icon(color='red', icon='home')
    ).add_to(m)
    
    # 농지 위치 표시
    folium.Marker(
        farm_coords,
        popup=f'농지 (지분: {share_ratio}%)',
        icon=folium.Icon(color='green', icon='leaf')
    ).add_to(m)
    
    # 직선 거리 표시
    folium.PolyLine(
        [home_coords, farm_coords],
        color='blue',
        weight=2,
        opacity=0.8
    ).add_to(m)
    
    return m

def process_signature(signature_data):
    """서명 이미지 처리"""
    try:
        # Base64 데이터에서 이미지 추출
        image_data = signature_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # 이미지 처리
        image = Image.open(io.BytesIO(image_bytes))
        
        # 투명 배경 처리
        if image.mode == 'RGBA':
            # 이미 투명 배경이 있는 경우
            return image
        else:
            # RGB 이미지를 RGBA로 변환
            image = image.convert('RGBA')
            data = image.getdata()
            
            # 흰색 배경을 투명하게 처리
            new_data = []
            for item in data:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            
            image.putdata(new_data)
            return image
            
    except Exception as e:
        print(f"서명 처리 중 오류 발생: {e}")
        return None 