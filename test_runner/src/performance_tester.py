import requests
import json
import random
import time
from data_processing import data_processor

'''
Testet die Performance der Matrixmultiplikation und misst die Dauer der Berechnung.
'''

class performance_tester:

    def __init__(self):
        self.data_processor = data_processor("Performance")
        self.start_time = None
        self.times = []

    def get_matrix_id(self):
        try:
            response = requests.get('http://db_rest_service/api/v1/highest_id')
            response.raise_for_status()
            data = response.json()
            if data[0] is None:
                return 10000
            id = data[0]
            if id < 10000:
                return 10000
            else:
                return id + 1
        except requests.RequestException as error:
            print('Error fetching highest matrix ID:', error)
            return 10000

    def send_http_request(self, matrixA, matrixB, matrixID):
        try:
            url = 'http://controller:5000/process_matrices'
            headers = {'Content-Type': 'application/json'}
            body = json.dumps({'matrixA': matrixA, 'matrixB': matrixB, 'matrixId': matrixID})

            response = requests.request('POST', url, headers=headers, data=body)
            if response.status_code == 200:
                self.start_time = time.time()
            else:
                print("PERFORMANCE TEST: Failed to send test")
        except Exception as e:
            print(f"PERFORMANCE TEST: Exception occurred: {e}")

    def get_matrix(self, matrixID, rows_a, cols_b):
        expected_data_count = rows_a * cols_b

        while True:
            try:
                response = requests.get(f'http://db_rest_service/api/v1/matrices?matrixID={matrixID}')
                response.raise_for_status()
                data = response.json()
                if len(data) == expected_data_count:
                    calculating_element = False
                    self.times.append(round(time.time() - self.start_time, 3))
                    break
                else:
                    time.sleep(1)
            except requests.RequestException as error:
                print('Error fetching data:', error)
                time.sleep(5)
    def generate_matrix(self, x, y):
        matrix = []
        for i in range(x):
            row = []
            for j in range(y):
                row.append(random.randint(0, 100))
            matrix.append(row)
        return matrix

    def send_test(self, number, x, y):
        self.times.clear()
        for i in range(number):
            matrixA = self.generate_matrix(x, y)
            matrixB = self.generate_matrix(x, y)
            matrixID = self.get_matrix_id()
            self.send_http_request(matrixA, matrixB, matrixID)
            self.get_matrix(matrixID, x, y)

        result = {'Duration': self.times}
        self.data_processor.process_data(result, f'Performance Test: {number} Tests with {x}x{y} Matrix')
        return self.times

    def close(self):
        pass
