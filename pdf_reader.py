import os
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import pandas as pd
import re
from datetime import datetime
import subprocess
import tempfile
import openpyxl
import warnings
warnings.filterwarnings('ignore')

def preprocess_text(text):
    # 줄바꿈을 공백으로 변환
    text = text.replace('\n', ' ')
    # 연속된 공백을 하나로 통일
    text = re.sub(r'\s+', ' ', text)
    # 특수문자 제거
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    return text.strip()

def extract_address(text):
    # 전처리된 텍스트에서 주소 추출
    text = preprocess_text(text)
    
    # 다양한 주소 패턴 정의
    patterns = [
        # 기본 패턴 (시/도 + 시/군/구 + 읍/면/동)
        r'([가-힣]+(?:시|도|특별시|광역시)\s+[가-힣]+(?:시|군|구)\s+[가-힣]+(?:읍|면|동)(?:\s+[가-힣]+리)?)',
        
        # 시/도 생략 패턴 (시/군/구 + 읍/면/동)
        r'([가-힣]+(?:시|군|구)\s+[가-힣]+(?:읍|면|동)(?:\s+[가-힣]+리)?)',
        
        # 읍/면/동 생략 패턴 (시/도 + 시/군/구)
        r'([가-힣]+(?:시|도|특별시|광역시)\s+[가-힣]+(?:시|군|구))',
        
        # 최소 패턴 (시/군/구)
        r'([가-힣]+(?:시|군|구))'
    ]
    
    # 각 패턴으로 주소 검색
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # 가장 긴 주소 반환 (더 상세한 주소 우선)
            return max(matches, key=len)
    
    return None

# 법정동코드 CSV 로드 함수
def load_address_db(csv_path):
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    return df

# 표 텍스트에서 '읍/면/동 + 리' 세트 추출 함수
def extract_eupmyeonri_pairs(text):
    # 예: '관산읍 외동리', '관산면 방촌리' 등
    pairs = re.findall(r'([가-힣]+(?:읍|면|동)\s+[가-힣]+리)', text)
    return pairs

# 세트로 추출한 후보를 주소 DB와 매칭하여 전체 주소 완성
def match_full_address_pairs(pairs, df_addr):
    results = []
    for pair in pairs:
        try:
            eupmyeon, ri = pair.split()
        except ValueError:
            continue
        match = df_addr[(df_addr['읍면동명'] == eupmyeon) & (df_addr['리명'] == ri)]
        for _, row in match.iterrows():
            full_addr = f"{row['시도명']} {row['시군구명']} {row['읍면동명']} {row['리명']}".strip()
            results.append(full_addr)
    return results

def process_pdf_file(file_path):
    addresses = []
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            pairs = extract_eupmyeonri_pairs(text)
            addresses.extend(match_full_address_pairs(pairs, df_addr))
    except Exception as e:
        print(f"PDF 파일 처리 중 오류 발생: {os.path.basename(file_path)}")
        print(f"오류 내용: {str(e)}")
    return addresses

def process_hwp_file(file_path):
    addresses = []
    try:
        # 임시 텍스트 파일 생성
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_path = temp_file.name

        # hwp5txt 명령어로 한글 파일을 텍스트로 변환
        try:
            subprocess.run(['hwp5txt', file_path, temp_path], check=True)
            
            # 변환된 텍스트 파일 읽기
            with open(temp_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 주소 추출
            pairs = extract_eupmyeonri_pairs(text)
            addresses.extend(match_full_address_pairs(pairs, df_addr))
            
        except subprocess.CalledProcessError:
            print(f"한글 파일 변환 중 오류 발생: {os.path.basename(file_path)}")
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        print(f"한글 파일 처리 중 오류 발생: {os.path.basename(file_path)}")
        print(f"오류 내용: {str(e)}")
    return addresses

def process_excel_file(file_path):
    addresses = []
    try:
        # 엑셀 파일 읽기
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        
        # 모든 셀의 텍스트를 하나의 문자열로 합치기
        text = ""
        for row in sheet.rows:
            for cell in row:
                if cell.value:
                    text += str(cell.value) + " "
        
        # 주소 추출 시도
        pairs = extract_eupmyeonri_pairs(text)
        addresses.extend(match_full_address_pairs(pairs, df_addr))
        
        # 열 구조가 있는 경우 (시도, 시군구, 읍면동, 리 순서로 되어있는 경우)
        for row in sheet.rows:
            row_values = [str(cell.value).strip() if cell.value else "" for cell in row]
            if len(row_values) >= 4:
                # 시도, 시군구, 읍면동, 리가 모두 있는 경우
                if all(row_values[1:4]):  # 2~4열에 값이 있는지 확인
                    try:
                        match = df_addr[
                            (df_addr['시도명'] == row_values[1]) &
                            (df_addr['시군구명'] == row_values[2]) &
                            (df_addr['읍면동명'] == row_values[3])
                        ]
                        if len(row_values) > 4 and row_values[4]:  # 리 정보가 있는 경우
                            match = match[match['리명'] == row_values[4]]
                        
                        for _, row in match.iterrows():
                            full_addr = f"{row['시도명']} {row['시군구명']} {row['읍면동명']} {row['리명']}".strip()
                            addresses.append(full_addr)
                    except Exception:
                        continue
    except Exception as e:
        print(f"엑셀 파일 처리 중 오류 발생: {os.path.basename(file_path)}")
        print(f"오류 내용: {str(e)}")
    return addresses

def process_files():
    # GUI로 폴더 선택
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="파일이 있는 폴더를 선택하세요")
    
    if not folder_path:
        print("폴더가 선택되지 않았습니다.")
        return
    
    # 법정동코드 CSV 경로
    addr_db_path = os.path.join(os.getcwd(), '법정동코드_전체.csv')
    if not os.path.exists(addr_db_path):
        print(f"법정동코드_전체.csv 파일이 {os.getcwd()}에 없습니다.")
        return
    
    global df_addr
    df_addr = load_address_db(addr_db_path)
    
    # 결과를 저장할 리스트
    results = []
    processed_files = 0
    extracted_addresses = 0
    files_with_no_addresses = 0
    
    # 지원하는 파일 확장자
    supported_extensions = {'.pdf', '.hwp', '.xlsx', '.xls'}
    
    # 선택된 폴더 내의 모든 파일 처리
    for filename in os.listdir(folder_path):
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext in supported_extensions:
            file_path = os.path.join(folder_path, filename)
            processed_files += 1
            
            # 파일 형식에 따라 적절한 처리 함수 호출
            if file_ext == '.pdf':
                addresses = process_pdf_file(file_path)
            elif file_ext == '.hwp':
                addresses = process_hwp_file(file_path)
            elif file_ext in {'.xlsx', '.xls'}:
                addresses = process_excel_file(file_path)
            
            if not addresses:
                files_with_no_addresses += 1
            else:
                for addr in addresses:
                    results.append({
                        'filename': filename,
                        'address': addr
                    })
                    extracted_addresses += 1
    
    # 결과를 DataFrame으로 변환
    df = pd.DataFrame(results)
    if not df.empty:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(folder_path, f'extracted_addresses_{current_time}.csv')
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n처리 결과:")
        print(f"처리된 파일 수: {processed_files}")
        print(f"주소 추출 성공: {extracted_addresses}")
        print(f"주소 추출 실패: {files_with_no_addresses}")
        print(f"결과가 {output_path}에 저장되었습니다.")
    else:
        print("추출된 주소가 없습니다.")

if __name__ == "__main__":
    process_files()
