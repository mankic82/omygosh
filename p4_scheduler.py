from p4_vmbox import start_vm, stop_vm,  rollback_vm
from p4_event_uploader import connect_db, close_db, upload_to_db
import requests
import json
import psycopg2
from psycopg2 import OperationalError
from time import sleep
import os
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

timeout = int(os.environ.get('REQUEST_TIMEOUT', 30))

# 글로벌 변수 설정
HOST = 'http://172.30.1.84:8081'
MAX_RETRIES = 3  
MAX_DB_RETRIES = 3

def uploadfile_to_vm(vm_name: str, local_path: str, remote_path: str, retries=5):
    print("파일을 VM에 업로드 중...")
    while retries > 0:
        try:
            with open(local_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f'{HOST}/upload/{remote_path}', files=files, timeout=180, verify=False)
            print("파일 업로드 완료.")
            return
        except requests.exceptions.ConnectionError:
            print("Connection refused. Retrying...")
            sleep(5)
            retries -= 1
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return

def exec_remote_path(vm_name: str, remote_path: str, argument: str, timeout: int, retries=5):
    print("원격 경로 실행 중...")
    while retries > 0:
        try:
            data = {"command": remote_path, "arg": argument}
            headers = {'Content-type': 'application/json'}
            response = requests.post(f'{HOST}/command', data=json.dumps(data), headers=headers, timeout=timeout)
            if response.status_code == 200:
                print("원격 경로 실행 완료.")
                return
            else:
                print(f"Failed to execute remote path. Status code: {response.status_code}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        print("Retrying...")
        retries -= 1
        sleep(1)

# 이벤트 로그 처리
def exec_event_export(vm_name: str):
    print("이벤트 내보내기 실행 중...")
    data = {"command": "Your Sysmon export command here", "arg": ""}
    headers = {'Content-type': 'application/json'}
    response = requests.post(f'{HOST}/command', data=json.dumps(data), headers=headers)
    print("이벤트 내보내기 완료.")

def download_remote_file(vm_name: str, remote_path: str, local_path: str):
    print("원격 파일 다운로드 중...")
    response = requests.get(f'{HOST}/download/{remote_path}')
    with open(local_path, 'wb') as f:
        f.write(response.content)
    print("원격 파일 다운로드 완료.")

# 데이터베이스 연결
def connect_db(db_address: str):
    retries = 0
    while retries < MAX_DB_RETRIES:
        try:
            conn = psycopg2.connect(db_address, client_encoding='utf8')
            return conn, None
        except OperationalError as e:
            print(f"데이터베이스 연결 실패. 재시도 중... ({retries + 1})")
            retries += 1
            time.sleep(1)
    return None, "Max retries reached for DB connection"

# 데이터베이스 연결 종료
def close_db(db_handle):
    try:
        db_handle.close()
        print("데이터베이스 연결 종료")
    except Exception as e:
        print(f"An error occurred while closing the database: {e}")

# 분석 시작
def start_analyze(vm_name: str, file_path:str, argument:str, timeout:int):
    # 가상 머신 시작
    start_vm(vm_name)  

    # 1. 가상 머신에 분석 대상 파일을 업로드
    uploadfile_to_vm(vm_name, file_path, "C:\\Users\\gacci\\Documents\\target.exe")
        
    # 2. 업로드한 파일을 실행
    exec_remote_path(vm_name, "target.exe", argument, timeout)
        
    # 3. 이벤트 로그를 추출
    exec_event_export(vm_name)
        
    # 4. 이벤트 로그를 로컬에 다운로드
    download_remote_file(vm_name, "sysmon_output.csv", "local_sysmon_output.csv")
   
    # 5. 가상 머신 중지 및 원래 상태로 롤백
    stop_vm(vm_name)
    rollback_vm(vm_name, "<testsnap>")
    
def get_db_handler():
    db_address = os.environ.get('DB_ADDRESS', "postgresql://postgres:0984@localhost:5432/postgres")
    db_handler, error = connect_db(db_address)
    if db_handler:
        return db_handler, None
    else:
        return None, error
 
if __name__ == '__main__':
    db_handler, error = get_db_handler()
    if db_handler:
        print("Successfully connected to the database.")
    else:
        print(f"Failed to connect to the database. Error: {error}")
        exit(1)

    analyze_target_path = r'C:\Users\USER\Documents\Koino\Log\KASSvcMgr_AnySupportService.log'
    vm_name = 'Win11'
    argument = ''
    timeout = 180

    start_analyze(vm_name, analyze_target_path, argument, timeout)

    # 연결된 DB 핸들러를 사용하여 이벤트 로그를 업로드
    db_handler, error = get_db_handler()
    if db_handler:
        upload_to_db(db_handler, "local_sysmon_output.csv")
        close_db(db_handler)
    else:
        print(f"Failed to connect to DB: {error}")
