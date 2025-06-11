import socket
from concurrent.futures import ThreadPoolExecutor
from http_helper import HttpHelper

class HttpServer:
    """
    REST-Service, der Anfragen verarbeitet und Daten in die Datenbank speichert.
    """
    def __init__(self, host='0.0.0.0', port=80, max_workers=100):
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.server_socket = None

    def handle_client(self, client_socket):
        try:
            request = client_socket.recv(4096).decode()
            print(f"{request}")
            http_response = HttpHelper.handle_request(request)
            client_socket.sendall(http_response.to_bytes())
            client_socket.shutdown(socket.SHUT_WR)  # Ensure all data is sent
        except Exception as e:
            print(f"Exception in handle_client: {e}")
        finally:
            client_socket.close()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}.")

        thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"Received connection from: {addr[0]}:{addr[1]}.")
                thread_pool.submit(self.handle_client, client_socket)
        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            self.server_socket.close()

if __name__ == '__main__':
    server = HttpServer()
    server.start()