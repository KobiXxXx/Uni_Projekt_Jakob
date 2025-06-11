import matplotlib.pyplot as plt
import numpy as np
import json
import time

'''
Klasse zum Verarbeiten und Speichern von Testdaten.
'''

class data_processor:
    def __init__(self, test_type):
        self.test_type = test_type
        if test_type == 'Healthcheck':
            self.save_location = 'tests/health_check/'
        elif test_type == 'HTTP Request':
            self.save_location = 'tests/http_request/'
        elif test_type == 'Performance':
            self.save_location = 'tests/performance/'

    def process_data(self, data, titel):
        self.plot_data(data, titel)
        self.save_data_to_file(data, titel)

    def get_filename(self):
        return f'{self.test_type}_{time.strftime("%Y-%m-%d-%H-%M")}'

    def plot_data(self, data, titel):
        keys = list(data.keys())
        values = list(data.values())
        plt.title(titel)
        plt.figure(figsize=(12, 8))
        box = plt.boxplot(values, labels=keys)
        for i in range(len(values)):
            y = values[i]
            x = np.random.normal(1 + i, 0.04, size=len(y))
            plt.plot(x, y, 'r.', alpha=0.2)
        plt.text(1, max(max(values)), f'Number of Values: {len(values[0])}', horizontalalignment='right',
                 verticalalignment='top', transform=plt.gca().transAxes)
        plt.xlabel('Worker ID')
        plt.ylabel('Milliseconds')
        plt.title(f'{self.test_type} Test')
        plt.legend([box["boxes"][0]], ['RTT Values'], loc='upper right')
        plt.grid(True)
        plt.savefig(f'{self.save_location}{self.get_filename()}.png')

    def save_data_to_file(self, data, titel):
        filename = f'{self.save_location}{self.get_filename()}.txt'
        with open(filename, 'w') as file:
            file.write(f'{titel}\n')
            values = list(data.values())
            file.write(f'Number of Values: {len(values[0])}\n')
            for key, values in data.items():
                file.write(f'{key}: {values}\n')

    def json_to_dict(self, json_string):
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return None