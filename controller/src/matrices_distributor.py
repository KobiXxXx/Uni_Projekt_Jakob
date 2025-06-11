import time
import grpc
import threading
import rpc.matrices_pb2 as matrices_pb2
import rpc.matrices_pb2_grpc as matrices_pb2_grpc
import random

class MatricesDistributorServicer:
    """
    Erstellt Aufgaben für die Verteilung der Matrizen, weist sie den Workern zu und startet RPC-Aufrufe,
    um die Berechnungen durchzuführen. Verarbeitet die Ergebnisse und leitet zum Speichern an.
    """
    def __init__(self, server, health_check):
        self.server = server
        self.health_check = health_check
        self.matrix_a = None
        self.matrix_b = None
        self.workers = {}
        self.matrix_id = None
        self.worker_locks = {}

    def distribute_matrices(self):
        while True:
            self.server.new_matrix_event.wait()  # Wait for new matrix event
            self.matrix_a, self.matrix_b = self.server.get_matrices()
            print(f"MATRIX DISTRIBUTOR: Matrix A: {len(self.matrix_a)}x{len(self.matrix_a[0])}")
            print(f"MATRIX DISTRIBUTOR: Matrix B: {len(self.matrix_b)}x{len(self.matrix_b[0])}")
            self.matrix_id = self.server.get_matrix_id()
            self.workers = self.health_check.workers
            if not self.workers:
                print("MATRIX DISTRIBUTOR: No workers available to distribute tasks.")
                continue
            if self.matrix_a and self.matrix_b and self.workers:
                self.assign_tasks()

    def assign_tasks(self):
        tasks = []
        for i in range(len(self.matrix_a)):
            for j in range(len(self.matrix_b[0])):
                row = self.matrix_a[i]
                col = [self.matrix_b[k][j] for k in range(len(self.matrix_b))]
                tasks.append((i, j, row, col))

        def process_task(worker_id, worker_ip, i, j, row, col):
            if worker_id not in self.worker_locks:
                self.worker_locks[worker_id] = threading.Lock()
            
            with self.worker_locks[worker_id]: # Wait until worker is available

                request = matrices_pb2.MatrixRequest(matrix_id=self.matrix_id, row=row, column=col, i=i, j=j)
                print(f"MATRIX DISTRIBUTOR: Assigning task (row: {row}, column {col}) to Worker-{worker_id} for Matrix-{self.matrix_id}.")
                channel = grpc.insecure_channel(f'{worker_ip}:50051')
                stub = matrices_pb2_grpc.MatrixServiceStub(channel)
                try:
                    response = stub.DistributeMatrix(request, timeout=60)
                    print(f"{response.message}")
                    self.save_result(self.matrix_id, response.result, i, j, worker_id, worker_ip)
                except grpc.RpcError as e:
                    print(f"MATRIX DISTRIBUTOR: Worker-{worker_id} failed or timed out. Reassigning task (row: {row}, column: {col}).")
                    reassign_task_calculate_result(i=i, j=j, row=row, col=col) # Reassign task

        def reassign_task_calculate_result(i, j, row, col):
            available_workers = list(self.workers.items())
            if not available_workers:
                print("MATRIX DISTRIBUTOR: No available workers to reassign the task.")
                return

            new_worker_id, (new_worker_ip, new_worker_port) = random.choice(available_workers)
            thread = threading.Thread(target=process_task, args=(new_worker_id, new_worker_ip, i, j, row, col))
            thread.start()
            thread.join()

        while tasks:
            worker_list = list(self.workers.items())
            threads = []
            worker_id, (worker_ip, worker_port) = random.choice(worker_list)
            if not tasks:
                break
            i, j, row, col = tasks.pop(0)
            thread = threading.Thread(target=process_task, args=(worker_id, worker_ip, i, j, row, col))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def save_result(self, matrix_id, result, i, j, worker_id, worker_ip):
        def attempt_save():
            while True:
                try:
                    request = matrices_pb2.ResultRequest(matrix_id=matrix_id, result=result, i=i, j=j)
                    print(f"MATRIX DISTRIBUTOR: Instructing Worker-{worker_id} to save the result for Matrix-{matrix_id}.")
                    channel = grpc.insecure_channel(f'{worker_ip}:50051')
                    stub = matrices_pb2_grpc.MatrixServiceStub(channel)
                    response = stub.SaveResult(request, timeout=60)
                    print(f"{response.message}")
                    if f"RPC: Worker-{worker_id} available but failed to save result" in response.message:
                        time.sleep(5) # Wait 5 seconds before retrying
                        continue
                    break
                except (grpc.RpcError, Exception) as e:
                    print(f"MATRIX DISTRIBUTOR: Worker-{worker_id} failed or timed out. Reassigning task (result: [{result}]).")
                    reassign_task_save_result(matrix_id=matrix_id, result=result, i=i, j=j) # Reassign task
                    break
        
        def reassign_task_save_result(matrix_id, result, i, j):
            available_workers = list(self.workers.items())
            if not available_workers:
                print("MATRIX DISTRIBUTOR: No available workers to reassign the task.")
                return

            new_worker_id, (new_worker_ip, new_worker_port) = random.choice(available_workers)
            self.save_result(matrix_id, result, i, j, new_worker_id, new_worker_ip)

        save_thread = threading.Thread(target=attempt_save)
        save_thread.start()
        save_thread.join()
    
