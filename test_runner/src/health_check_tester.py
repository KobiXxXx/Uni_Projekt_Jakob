import socket
from data_processing import data_processor

'''
Testet die RTT der Health Checks zwischen dem Controller und den Workern.
'''
class health_check_tester:

    def __init__(self):
        self.sock = None
        self.host = "controller"
        self.port = 8000
        self.data_processor = data_processor("Healthcheck")

    def send_test(self, number):
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(None)
            self.sock.connect((self.host, self.port))
        elif self.sock.getpeername() != (self.host, self.port):
            self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(None)
            self.sock.connect((self.host, self.port))

        data = f"Test:{number}"
        self.sock.sendall(data.encode())
        print(f"HEALTH CHECK TESTER: Sent request to {self.host}:{self.port}. With size: {number}")

        response = ""
        while True:
            try:
                data = self.sock.recv(4096).decode()
                if not data:
                    break
                response = data
            except socket.timeout:
                response = "Timeout occurred."
                break
            print(f"HEALTH CHECK TESTER: Response {response}")
            self.data_processor.process_data(self.data_processor.json_to_dict(response), f'Health_Check_Tests: {number}')
            return response

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
