from flask import Flask, request, jsonify
from flask_cors import CORS
import threading


class Server:
    """"
    Server-Klasse, die Matrizen vom Frontend empfängt und zur Weiterverarbeitung bereitstellt.
    """
    def __init__(self):
        self.app = Flask(__name__)
        self.matrix_a = None
        self.matrix_b = None
        self.matrixId = None
        self.new_matrix_event = threading.Event()
        self.setup_routes()
        CORS(self.app)

    def setup_routes(self):
        @self.app.route('/process_matrices', methods=['POST'])
        def process_matrices():
            data = request.get_json()
            self.matrix_a = data.get('matrixA')
            self.matrix_b = data.get('matrixB')
            self.matrixId = data.get('matrixId')    
            self.new_matrix_event.set()  # New matrix event is set
            return jsonify({"status": "success", "message": "Matrices received"}), 200

    def get_matrices(self):
        self.new_matrix_event.clear()  # New matrix event is cleared
        return self.matrix_a, self.matrix_b
    
    def get_matrix_id(self):
        return self.matrixId

    def run(self, host="0.0.0.0", port=5000):
        self.app.run(debug=True, host=host, port=port, use_reloader=False)
