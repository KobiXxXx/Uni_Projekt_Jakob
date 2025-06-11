import socket
import time
import threading
import select
import numpy as np


class ControllerHealthCheck:
    """
    Implementiert die Healthcheck-Funktionalität für den Controller.
    Überwacht die Worker und misst die Round-Trip-Time (RTT) für Healthcheck-Anfragen.
    """
    def __init__(self, health_check_queue, worker_queue, port=7000):
        self.controller_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        self.controller_socket.bind(("0.0.0.0", port))
        self.workers = {}
        self.wait = time.time()
        self.send_timer = 30

        # Health check test
        self.health_check_queue = health_check_queue
        self.worker_queue = worker_queue
        self.rtt_start = {}
        self.rtt = {}
        self.do_test = False
        self.do_test_size = 0
        self.response = {}
        self.tested = []
        print(f"HEALTH CHECK: Ready on port {port} is ready.")

    def register_and_check(self):
        while True:
            try:
                ready_sockets, _, _ = select.select([self.controller_socket],
                                                    [], [], 5)
                if ready_sockets:
                    data, addr = self.controller_socket.recvfrom(1024)
                    message = data.decode()
                    if message.startswith("READY:"):
                        worker_port = int(message.split(":")[1])
                        worker_id = message.split(":")[2]
                        self.workers[worker_id] = (addr[0], worker_port)
                        self.controller_socket.sendto(b"OK", addr)
                        print(f"HEALTH CHECK: Worker-{worker_id} {addr[0]}:{worker_port} registered.")
                    elif message.startswith("Operational:"):
                        worker_id = message.split(":")[1]
                        rtt = round((time.time() - self.rtt_start[worker_id])*1000, 4)
                        print(f"HEALTH CHECK: Worker-{worker_id} {addr[0]}:{addr[1]} is operational. RTT: {rtt} ms.")
                        self.rtt[worker_id] = rtt
                else:
                    if time.time() - self.wait >= self.send_timer:  # send health check every 30 seconds
                        self.rtt.clear()
                        for worker_id, (worker_ip, worker_port) in self.workers.items():
                            self.controller_socket.sendto(b"Healthcheck", (
                                worker_ip, worker_port))
                            self.rtt_start[worker_id] = time.time()
                            print(f"HEALTH CHECK: Healthcheck sent to Worker-{worker_id} {worker_ip}:{worker_port}.")
                        self.wait = time.time()

                # Check for workers that did not respond to health check
                current_time = time.time()
                for worker_id, (worker_ip, worker_port) in list(self.workers.items()):
                    if worker_id in self.rtt_start and worker_id not in self.rtt:
                        if current_time - self.rtt_start[worker_id] > 5: # wait 5 seconds
                            print(f"HEALTH CHECK: Worker-{worker_id} {worker_ip}:{worker_port} did not respond to health check. Removing from list.")
                            del self.workers[worker_id]
                            del self.rtt_start[worker_id]

                if not self.health_check_queue.empty():
                    self.do_test_size = self.health_check_queue.get()
                    self.do_test = True
                    self.send_timer = 5
                    print(f"HEALTH CHECK: Received test request. Size: {self.do_test_size}")
                if self.do_test:
                    for worker_id, rtt in self.rtt.items():
                        if worker_id not in self.tested:
                            if worker_id not in self.response:
                                self.response[worker_id] = []
                            if rtt not in self.response[worker_id]:
                                self.response[worker_id].append(rtt)
                            if len(self.response[worker_id]) == self.do_test_size:
                                self.tested.append(worker_id)
                    if len(self.tested) == len(self.workers):
                        self.health_check_queue.put(self.response)
                        time.sleep(5)
                        self.tested.clear()
                        self.response.clear()
                        self.do_test_size = 0
                        self.do_test = False
                        self.send_timer = 30

                if not self.worker_queue.empty():
                    _ = self.worker_queue.get()
                    self.worker_queue.put(self.workers)

            except Exception as e:
                print(f"HEALTH CHECK: Exception occurred: {e}")

    def get_workers(self):
        return self.workers

    def __del__(self):
        self.controller_socket.close()
        print("HEALTH CHECK: Socket closed.")

    def start(self):
        register_and_check_thread = threading.Thread(target=self.
                                                     register_and_check)
        register_and_check_thread.daemon = True
        register_and_check_thread.start()
        while True:
            time.sleep(1)
