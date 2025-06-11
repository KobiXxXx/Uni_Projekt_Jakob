import socket
import time
import json


class Tester:
    """
    Implementiert einen Tester, der HTTP-Anfragen sendet und die Round-Trip-Time (RTT) misst.
    """
    def __init__(self, http_client):
        self.http_client = http_client
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0", 8000))
        self.sock.listen(1)
        self.sock.settimeout(300)
        print(f"HTTP TESTER: Socket listening.")

    def run(self):
        while True:
            try:
                conn, addr = self.sock.accept()
                request = conn.recv(1024).decode()
                if request.startswith("Test"):
                    print("HTTP TESTER: Received request.")
                    split_data = request.split(":")
                    number = int(split_data[1])
                    response = []
                    for _ in range(number):
                        self.http_client.connect()
                        rtt = self.http_client.send_test_request()
                        self.http_client.close()
                        response.append(rtt)
                        time.sleep(1)
                    print(f"HTTP TESTER: Sending response: {response}")
                    response = json.dumps(response)
                    conn.sendall(response.encode())
                conn.close()
            except socket.timeout:
                pass
            except Exception as e:
                print(f"HTTP TESTER: Exception: {e}")

    def close(self):
        self.sock.close()
