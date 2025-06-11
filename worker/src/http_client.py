import socket
import time
import os
import threading
from models.http import HTTP_Request


class HttpClient:
    """
    Realisiert die Client-Verbindung zum REST-Service, um Daten in der Datenbank abzuspeichern.
    """
    def __init__(self, worker_id):
        self.host = os.getenv("DB_REST_SERVICE_IP")
        self.port = int(os.getenv("DB_REST_SERVICE_PORT"))
        self.client_socket = None
        self.worker_id = worker_id
        self.lock = threading.Lock()
        print(f"HTTP CLIENT: Initialized for Worker {self.worker_id}. {self.host}:{self.port}.")

    def connect(self):
        self.lock.acquire()
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(15)
            self.client_socket.connect((self.host, self.port))
        except Exception as e:
            print(f"HTTP CLIENT: Failed to connect to {self.host}:{self.port}: {e}")

    def send_post_request(self, data):
        try:
            http_request = HTTP_Request('POST', '/api/v1/matrices', len(data), data)
            request_bytes = http_request.to_bytes()
            self.client_socket.sendall(request_bytes)
            print(f"HTTP CLIENT: Sent POST request to {self.host}:{self.port}.")

            response = ""
            while True:
                try:
                    data = self.client_socket.recv(4096).decode()
                    if not data:
                        break
                    response += data
                except socket.timeout:
                    break

            response = response.split('\n')[0]
            print(f"HTTP CLIENT: {response}")
            return response

        except Exception as e:
            print(f"HTTP CLIENT: Failed to send POST request: {e}")
            return None

    def send_test_request(self):
        try:
            data = f"Test:{self.worker_id}"
            http_request = HTTP_Request('GET', f'/api/v1/test', len(data), data)
            request_bytes = http_request.to_bytes()
            rtt_start = time.time()
            self.client_socket.sendall(request_bytes)
            print(f"HTTP CLIENT: Sent Test request to {self.host}:{self.port}.")

            response = ""
            while True:
                try:
                    data = self.client_socket.recv(4096).decode()
                    if not data:
                        break
                    response += data
                except socket.timeout:
                    break

            return round((time.time() - rtt_start)*1000, 4)

        except Exception as e:
            print(f"HTTP CLIENT: Failed to send GET request: {e}")

    def close(self):
        try:
            if self.client_socket:
                self.client_socket.close()
        except Exception as e:
            print(f"HTTP CLIENT: Failed to close connection: {e}")
        finally:
            self.lock.release()
