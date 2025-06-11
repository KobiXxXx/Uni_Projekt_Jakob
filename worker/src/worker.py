import os
import threading
import time
import docker
from health_check import WorkerHealthCheck
from matrix_processor import serve
from worker_tester import Tester
from http_client import HttpClient

def get_container_name():
    try:
        client = docker.from_env()
        container_id = os.path.basename(open('/proc/self/cgroup').read().splitlines()[0].split('/')[-1])
        container = client.containers.get(container_id)
        return container.name
    except Exception as e:
        print(f"Exception occurred while getting container name: {e}")
    return None


def extract_worker_id(container_name):
    num = ''
    for c in reversed(container_name):
        if c.isdigit():
            num += c
        else:
            break
    return num[::-1] if num else None


def main():
    """
    Startet die einzelnen Worker-Funktionalitäten.
    Initialisiert den Worker, erstellt und startet die Threads für den Matrix-Prozessor, den HTTP-Tester und die Healthcheck-Funktionalität.
    """
    container_name = get_container_name()
    worker_id = extract_worker_id(container_name) if container_name else "N/A"

    controller_ip = os.getenv("CONTROLLER_IP")
    controller_port = int(os.getenv("CONTROLLER_UDP_PORT"))

    http_client = HttpClient(worker_id)

    matrix_processor_thread = threading.Thread(target=serve, args=(worker_id, http_client,))
    matrix_processor_thread.daemon = True

    http_tester = Tester(http_client)
    http_tester_thread = threading.Thread(target=http_tester.run)
    http_tester_thread.daemon = True

    health_check = WorkerHealthCheck(controller_ip, controller_port, worker_id)
    health_check_thread = threading.Thread(target=health_check.start)
    health_check_thread.daemon = True

    matrix_processor_thread.start()
    health_check_thread.start()
    http_tester_thread.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
