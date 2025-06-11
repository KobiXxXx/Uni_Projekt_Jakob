from concurrent import futures
from lamport.lamport_clock import LamportClock
from lamport.distributed_mutex import DistributedMutex
import time
import grpc
import rpc.matrices_pb2 as matrices_pb2
import rpc.matrices_pb2_grpc as matrices_pb2_grpc


class MatrixProcessorServicer(matrices_pb2_grpc.MatrixServiceServicer):
    """
    Implementiert die Methoden für die RPC-Aufrufe zur Verteilung und Speicherung von Matrizenberechnungen.
    """
    def __init__(self, worker_id, http_client):
        self.worker_id = worker_id
        self.http_client = http_client
        self.lamport_clock = LamportClock()
        self.distributed_mutex = DistributedMutex(worker_id, self.lamport_clock)

    def DistributeMatrix(self, request, context):
        try:
            print(f"MATRIX PROCESSOR: Received job for Matrix-{request.matrix_id} at index [{request.i}, {request.j}] with row: {request.row} and column: {request.column}.")
            result = sum(r * c for r, c in zip(request.row, request.column))
            return matrices_pb2.MatrixResponse(message=f"RPC: Worker-{self.worker_id} calculated [{result}] for Matrix-{request.matrix_id}.", result=result)
        except Exception as e:
            print(f"MATRIX PROCESSOR: Error: {e}")
            return matrices_pb2.MatrixResponse(message=f"RPC: Error calculating result for Matrix-{request.matrix_id} at index [{request.i}, {request.j}].", result=None) 

    def SaveResult(self, request, context):
        try:
            self.distributed_mutex.request_cs()
            while not self.distributed_mutex.can_enter_cs():
                time.sleep(0.1)

            data = f"matrixId={request.matrix_id} i={request.i} j={request.j} result={request.result}"
            self.http_client.connect()
            response = self.http_client.send_post_request(data)
            self.http_client.close()

            self.distributed_mutex.release_cs()

            if "500 Internal Server Error" in response:
                print(f"MATRIX PROCESSOR: Failing to save result [{request.result}] for Matrix-{request.matrix_id}.")
                return matrices_pb2.ResultResponse(message=f"RPC: Worker-{self.worker_id} available but failed to save result. [LC:{self.lamport_clock.time}]" )
            
            print(f"MATRIX PROCESSOR: Stored result [{request.result}] for Matrix-{request.matrix_id}.")
            return matrices_pb2.ResultResponse(message=f"RPC: Worker-{self.worker_id} stored the result [{request.result}] for Matrix-{request.matrix_id}. [LC:{self.lamport_clock.time}]")
        except Exception as e:
            self.distributed_mutex.release_cs()
            print(f"MATRIX PROCESSOR: Error: {e}")
            return matrices_pb2.ResultResponse(message=f"RPC: Worker-{self.worker_id} failed to save result [{request.result}] for Matrix-{request.matrix_id}. [LC:{self.lamport_clock.time}]")


def serve(worker_id, http_client):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    matrices_pb2_grpc.add_MatrixServiceServicer_to_server(MatrixProcessorServicer(worker_id, http_client), server)
    server.add_insecure_port(f'0.0.0.0:50051')

    def stop_server():
        print("MATRIX PROCESSOR: Stopping gRPC server...")
        server.stop(0)

    server.start()
    print(f"MATRIX PROCESSOR: gRPC server started on port 50051.")
    server.wait_for_termination()