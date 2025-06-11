from health_check import ControllerHealthCheck
from server import Server
from matrices_distributor import MatricesDistributorServicer
from controller_tester import Tester
import threading
import queue
import time


def main():

    """
    Steuert Worker, sendet Healthchecks und koordiniert die Matrizenverteilung.
    """
    
    worker_queue = queue.Queue()
    health_check_queue = queue.Queue()
    health_check = ControllerHealthCheck(health_check_queue, worker_queue)
    health_check_thread = threading.Thread(target=health_check.start)
    health_check_thread.daemon = True

    health_check_tester = Tester(health_check_queue, worker_queue)
    health_check_tester_thread = threading.Thread(target=health_check_tester.run)
    health_check_tester_thread.daemon = True

    server = Server()
    server_thread = threading.Thread(target=server.run)
    server_thread.daemon = True

    matrices_distributor = MatricesDistributorServicer(server, health_check)
    matrices_distributor_thread = threading.Thread(
        target=matrices_distributor.distribute_matrices)
    matrices_distributor_thread.daemon = True

    health_check_thread.start()
    health_check_tester_thread.start()
    server_thread.start()
    matrices_distributor_thread.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
