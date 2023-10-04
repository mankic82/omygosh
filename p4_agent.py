from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os 

def exec_command(command):
    cmd = command['command'] + ' ' + command['arg']
    result = subprocess.getoutput(cmd)
    return result

def save_file(data, save_path) -> bool:
    try:
        with open(save_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f'Error while saving the file: {str(e)}')
        return False

def load_file(file_path) -> bytes:
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        return data
    except Exception as e:
        print(f"Error while loading the file: {e}")
        return None

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b'Hello, this is a GET request!')

        elif self.path.startswith('/download/'):
            # Handle file download
            file_path = self.path[len('/download/'):]
            data = load_file(file_path)
            if data:
                self.send_response(200)
                
                if file_path.endswith('.csv'):
                    self.send_header('Content-type', 'text/csv')
                elif file_path.endswith('.json'):
                    self.send_header('Content-type', 'application/json')
                elif file_path.endswith('.txt'):
                    self.send_header('Content-type', 'text/plain')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b'404 Not Found')

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        if self.path == '/command':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                result = exec_command(data)
                #response_data = {'message': 'Data received successfully', 'data': result}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                #self.wfile.write(json.dumps(response_data).encode('utf-8'))
                self.wfile.write(result.encode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", 'text/html')
                self.end_headers()
                self.wfile.write(b'Bad Request: Invalid JSON data')

        elif self.path.startswith('/upload/'):
            # Handle file upload
            file_name = self.path[len('/upload/'):]
            content_length = int(self.headers['Content-Length'])
            file_data = self.rfile.read(content_length)
            file_path = os.getcwd()
            file_path = os.path.join(file_path, file_name)
            success = save_file(file_data, file_path)
            if success:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b'File uploaded successfully')
            else:
                self.send_response(500)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b'Internal Server Error')

        else:
            self.send_response(404)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

def run_server():
    address = ('0.0.0.0', 8081)
    with HTTPServer(address, MyRequestHandler) as server:
        print("Starting server...")
        server.serve_forever()

if __name__ == '__main__':
    run_server()