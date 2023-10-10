import requests
import json

def main():
    HOST = 'http://172.30.1.84:8081'
    
    
    try:
        # GET 요청을 수행합니다.
        print("Sending GET request...")
        response = requests.get(f'{HOST}/', timeout=180)  # 60초 타임아웃 설정
        print("GET Response received.")
        print(response.text)
        
        # POST 요청을 수행합니다.
        print("Sending POST request...")
        data = {"command": "ipconfig", "arg": "/all"}
        headers = {'Content-type': 'application/json'}
        response = requests.post(f'{HOST}/command', data=json.dumps(data), headers=headers)
        print("POST Response received.")  
        print(response.text)

        # 파일 다운로드 테스트
        response = requests.get(f'{HOST}/download/sysmon_output.csv')
        with open('sysmon_output.csv', 'wb') as f:
            f.write(response.content)
        print("\nDownload complete.")

        # 파일 업로드 테스트
        with open('', 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{HOST}/upload/', files=files)
        print("\nUpload Response:")
        print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
