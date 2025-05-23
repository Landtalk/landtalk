import requests
import json
from urllib.parse import quote
import os
from datetime import datetime

def search_address(address):
    """
    주소 검색 API를 호출하는 함수
    
    Args:
        address (str): 검색할 주소
        
    Returns:
        dict: API 응답 데이터
    """
    # API 엔드포인트 URL
    base_url = "https://search.disco.re/typeahead/"
    
    # 주소를 URL 인코딩
    encoded_address = quote(address)
    
    # API 요청 URL 생성
    url = f"{base_url}?phrase={encoded_address}"
    
    # API 요청 헤더 설정
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Origin': 'https://www.disco.re',
        'Referer': 'https://www.disco.re/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }
    
    try:
        # API 요청 보내기
        response = requests.get(url, headers=headers)
        
        # 응답 상태 코드 확인
        response.raise_for_status()
        
        # JSON 응답 데이터 반환
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {str(e)}")
        return None

def save_to_json(data, address):
    """
    API 응답 데이터를 JSON 파일로 저장하는 함수
    
    Args:
        data (dict): 저장할 데이터
        address (str): 검색한 주소 (파일명에 사용)
    """
    # 현재 날짜와 시간으로 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 주소에서 특수문자 제거하여 파일명 생성
    safe_address = "".join(c for c in address if c.isalnum() or c in (' ', '-', '_'))
    safe_address = safe_address.replace(' ', '_')
    
    # 저장할 디렉토리 생성
    output_dir = "address_search_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # 파일 경로 생성
    filename = f"{output_dir}/{timestamp}_{safe_address}.json"
    
    try:
        # JSON 파일로 저장
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"결과가 {filename}에 저장되었습니다.")
        return filename
        
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")
        return None

def filter_type_zero(json_file):
    """
    JSON 파일에서 type이 '0'(문자열)인 데이터만 필터링하여 새로운 파일로 저장
    """
    try:
        # JSON 파일 읽기
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # suggestions 키가 있고 리스트일 때만 필터링
        if isinstance(data, dict) and "suggestions" in data and isinstance(data["suggestions"], list):
            filtered_data = [item for item in data["suggestions"] if item.get('type') == "0"]
        elif isinstance(data, list):
            filtered_data = [item for item in data if item.get('type') == "0"]
        else:
            print("지원하지 않는 JSON 구조입니다.")
            return

        if filtered_data:
            filtered_filename = json_file.replace('.json', '_type0.json')
            with open(filtered_filename, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)
            print(f"\n필터링된 결과가 {filtered_filename}에 저장되었습니다.")
            print(f"type '0'인 결과 수: {len(filtered_data)}")
        else:
            print("\ntype '0'인 데이터가 없습니다.")

    except Exception as e:
        print(f"파일 필터링 중 오류 발생: {str(e)}")

def main():
    # 검색할 주소 입력 받기
    address = input("검색할 주소를 입력하세요: ")
    
    # 주소 검색 실행
    print(f"\n'{address}' 주소 검색 중...")
    result = search_address(address)
    
    if result:
        # 검색 결과 저장
        json_file = save_to_json(result, address)
        
        if json_file:
            # type 0인 데이터만 필터링
            filter_type_zero(json_file)
    else:
        print("검색 결과가 없습니다.")

if __name__ == "__main__":
    main() 