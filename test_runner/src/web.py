from flask import Flask, render_template, jsonify, request
from health_check_tester import health_check_tester
from http_tester import http_tester
from performance_tester import performance_tester


class WebApp:
    '''
    Webserver für die Testausführung.
    '''
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        self.health_check = health_check_tester()
        self.http_test = http_tester()
        self.performance_tester = performance_tester()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return render_template('index.html')

        @self.app.route('/health_check_test')
        def health_check():
            return render_template('health_check_test.html')

        @self.app.route('/http_test')
        def http_test():
            return render_template('http_test.html')

        @self.app.route('/performance_test')
        def performance_test():
            return render_template('performance_test.html')

        @self.app.route('/trigger_health_check', methods=['POST'])
        def trigger_health_check_test():
            size = int(request.json.get('size', 0))
            if size == 0:
                return jsonify({"message": "NULL"})
            response = self.health_check.send_test(size)
            return jsonify({"message": response})

        @self.app.route('/trigger_http', methods=['POST'])
        def trigger_http_test():
            size = int(request.json.get('size', 0))
            if size == 0:
                return jsonify({"message": "NULL"})
            response = self.http_test.send_test(size)
            return jsonify({"message": response})

        @self.app.route('/trigger_performance', methods=['POST'])
        def trigger_performance_test():
            size = int(request.json.get('size', 0))
            x = int(request.json.get('x', 0))
            y = int(request.json.get('y', 0))
            if size == 0:
                return jsonify({"message": "NULL"})
            response = self.performance_tester.send_test(size, x, y)
            return jsonify({"message": response})

    def run(self):
        self.app.run(debug=True, port=8100, host="0.0.0.0", use_reloader=True)
