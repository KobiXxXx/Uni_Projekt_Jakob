import socket
import time
import json


class Tester:
    """
    Implementiert einen einfachen Server, der auf eingehende Verbindungen hört und Anfragen verarbeitet.
    Misst die Zeit bei Healthcheck-Anfragen.
    """
    
    def __init__(self, healthcheck_queue, worker_queue, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.healthcheck_queue = healthcheck_queue
        self.worker_queue = worker_queue
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.sock.settimeout(300)
        print(f"HEALTH CHECK TESTER: listening on {self.host}:{self.port}.")

    def run(self):
        while True:
            try:
                conn, addr = self.sock.accept()
                request = conn.recv(1024).decode()
                print(f"HEALTH CHECK TESTER: Received request.")
                if request.startswith("Test"):
                    split_data = request.split(":")
                    number = int(split_data[1])
                    self.healthcheck_queue.put(number)
                    time.sleep(5)
                    response = self.healthcheck_queue.get()
                    response = json.dumps(response)
                    conn.sendall(response.encode())
                elif request == "RequestWorkers":
                    self.worker_queue.put("RequestWorkers")
                    time.sleep(5)
                    response = self.worker_queue.get()
                    worker_string = ",".join([f"{worker_id}:{ip}:{port}" for worker_id, (ip, port) in response.items()])
                    conn.sendall(worker_string.encode())
                conn.close()
            except socket.timeout:
                pass
            except Exception as e:
                print(f"HEALTH CHECK TESTER: Tester Exception: {e}")
            time.sleep(1)

    def close(self):
        self.sock.close()
