import socket
import time
import threading



class WorkerHealthCheck:
    """
    Implementiert die Healthcheck-Funktionalität für Worker.
    Registriert Worker beim Controller und antwortet auf Healthchecks.
    """
    def __init__(self, controller_ip, controller_port, worker_id, timeout=45):
        self.worker_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.worker_socket.bind(("0.0.0.0", 7000))
        self.worker_socket.settimeout(timeout)
        self.port = self.worker_socket.getsockname()[1]
        self.controller_ip = controller_ip
        self.controller_port = controller_port
        self.worker_id = worker_id
        self.timeout_count = 0


    def register(self):
        while True:
            try:
                self.worker_socket.sendto(f"READY:{self.port}:{self.worker_id}".encode(), (
                    self.controller_ip, self.controller_port))
                print(f"HEALTH CHECK: Registration message sent.")
                data, _ = self.worker_socket.recvfrom(1024)
                if data.decode() == "OK":
                    print(f"HEALTH CHECK: Registration acknowledged by controller.")
                    self.check()
            except socket.timeout:
                print("HEALTH CHECK: Timeout reached while waiting for registration acknowledgment.")
            except Exception as e:
                print(f"HEALTH CHECK: Exception occurred during registration: {e}")

    def check(self):
        while True:
            try:
                data, addr = self.worker_socket.recvfrom(1024)
                if data.decode() == "Healthcheck":
                    print(f"""HEALTH CHECK: Request received from {
                        addr[0]}:{addr[1]}.""")
                    self.worker_socket.sendto(f"Operational:{self.worker_id}".encode(), addr)
            except socket.timeout:
                self.timeout_count += 1
                print(f"HEALTH CHECK: {self.timeout_count}{'st.' if self.timeout_count == 1 else 'nd.'} Timeout reached. No Requests received.")
                if self.timeout_count > 1:  # worker reached more than one timeout while being operational
                    print(f"HEALTHCHECK: Not operational. Restart Registration.")
                    self.timeout_count = 0
                    break
            except Exception as e:
                print(f"HEALTH CHECK: Exception occurred during healthcheck: {e}")

    def __del__(self):
        self.worker_socket.close()
        print("HEALTH CHECK: Socket closed.")

    def start(self):
        self.register()
