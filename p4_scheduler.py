from p4_vmbox import start_vm, stop_vm,  rollback_vm
from p4_event_uploader import connect_db, close_db, upload_to_db
import requests
import json
import psycopg2
from psycopg2 import OperationalError
from time import sleep

HOST = 'http://172.30.1.5:8081'

def uploadfile_to_vm(vm_name: str, local_path: str, remote_path: str):
    print("파일을 VM에 업로드 중...")
    try:
        with open(local_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{HOST}/upload/{remote_path}', files=files, timeout=60, verify=False)
        print("파일 업로드 완료.")
    except requests.exceptions.ConnectionError:
        print("Connection refused. Retrying...")
        sleep(5)  # 5초 동안 대기합니다.
        uploadfile_to_vm(vm_name, local_path, remote_path)  
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def exec_remote_path(vm_name: str, remote_path: str, argument: str, timeout: int):
    print("원격 경로 실행 중...")
    data = {"command": remote_path, "arg": argument}
    headers = {'Content-type': 'application/json'}
    response = requests.post(f'{HOST}/command', data=json.dumps(data), headers=headers, timeout=timeout)
    print("원격 경로 실행 완료.")

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
    try:
        conn = psycopg2.connect(db_address)
        return conn, None
    except OperationalError as e:
        return None, str(e)

def close_db(db_handle):
    db_handle.close()
    print("데이터베이스 연결 종료")

def start_analyze(vm_name: str, file_path:str, argument:str, timeout:int):
    # 가상 머신 시작
    start_vm(vm_name)  

    # 1. 가상 머신에 분석 대상 파일을 업로드
    uploadfile_to_vm(vm_name, file_path, "target.exe")
        
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
    db_address = "postgresql://postgres:0984@localhost:5432/event_logs"
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
    vm_name = 'Win-11'
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
