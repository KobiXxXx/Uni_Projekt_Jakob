import socket
import json
import threading
from data_processing import data_processor

'''
Testet die RTT der HTTP-Verbindung zwischen dem DB-Rest-Service und den Workern. 
'''
class http_tester:

    def __init__(self):
        self.sock = None
        self.controller_ip = "controller"
        self.controller_port = 8000
        self.worker = {}
        self.data_processor = data_processor("HTTP Request")

    def send_test(self, number):
        # Request worker list from the controller
        self.connect_to_controller()
        self.sock.sendall("RequestWorkers".encode())
        worker_list = self.receive_response()
        print(f"HTTP TESTER: Worker list: {worker_list}")
        self.worker = self.parse_worker_list(worker_list)
        self.sock.close()

        results = {}
        threads = []
        for worker_id in self.worker:
            worker_ip, worker_port = self.worker[worker_id]
            thread = threading.Thread(target=self.send_test_to_worker, args=(worker_id, worker_ip, number, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print(f"HTTP TESTER: Http results: {results}")
        self.data_processor.process_data(results, f'HTTP_Tests: {number}')
        return json.dumps(results)

    def connect_to_controller(self):
        try:
            if self.sock is None:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(300)
                self.sock.connect((self.controller_ip, self.controller_port))
            else:
                try:
                    if self.sock.getpeername() != (self.controller_ip, self.controller_port):
                        self.sock.close()
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.sock.settimeout(None)
                        self.sock.connect((self.controller_ip, self.controller_port))
                except OSError:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.settimeout(None)
                    self.sock.connect((self.controller_ip, self.controller_port))
        except socket.timeout:
            print("HTTP TESTER: Connection to controller timed out.")
        except Exception as e:
            print(f"HTTP TESTER: Exception occurred: {e}")

    def receive_response(self):
        response = ""
        while True:
            try:
                data = self.sock.recv(4096).decode()
                if not data:
                    break
                response += data
            except socket.timeout:
                break
        return response

    def parse_worker_list(self, worker_list):
        # Assuming worker_list is a comma-separated string of worker_id:worker_ip:worker_port
        workers = {}
        for worker in worker_list.split(','):
            worker_id, worker_ip, worker_port = worker.split(':')
            workers[worker_id] = (worker_ip, int(worker_port))
        return workers

    def send_test_to_worker(self, worker_id, worker_ip, number, results):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(300)
            sock.connect((worker_ip, 8000))
            data = f"Test:{number}"
            sock.sendall(data.encode())
            response = self.receive_worker_response(sock)
            sock.close()
            results[worker_id] = response
        except ConnectionRefusedError:
            print(f"HTTP TESTER: Connection to worker {worker_id} at {worker_ip}:5002 refused.")
            results[worker_id] = None

    def receive_worker_response(self, sock):
        response = ""
        while True:
            try:
                data = sock.recv(4096).decode()
                if not data:
                    break
                response += data
            except socket.timeout:
                break

        return json.loads(response)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
