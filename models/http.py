class HTTP_Status:
    """
    Stellt HTTP-Statuscodes bereit.
    """
    OK = '200 OK'
    CREATED = '201 CREATED'
    NOT_FOUND = '404 Not Found'
    INTERNAL_SERVER_ERROR = '500 Internal Server Error'

class HTTP_Content_type:
    """
    Stellt HTTP-Content-Typen bereit.
    """
    HTML = 'Content-Type: text/html'
    PLAIN = "Content-Type: text/plain"
    JSON = 'Content-Type: application/json'

class HTTP_Request:
    """
    Modelliert eine HTTP-Anfrage.
    """
    def __init__(self, method, path, content_length, body):
        self.method = method
        self.path = path
        self.content_length = content_length
        self.body = body

    def to_bytes(self):
        request = f'{self.method} {self.path} HTTP/1.1\r\nContent-Length: {self.content_length}\r\n\r\n{self.body}'
        return request.encode()

class HTTP_Response:
    """
    Modelliert eine HTTP-Antwort.
    """
    def __init__(self, status, content_type, body, headers=None):
        self.status = status
        self.content_type = content_type
        self.body = body
        self.headers = headers if headers else {}

    def to_bytes(self):
        headers = '\r\n'.join([f'{key}: {value}' for key, value in self.headers.items()])
        response = f'HTTP/1.1 {self.status}\r\n{self.content_type}\r\n{headers}\r\n\r\n{self.body}'
        return response.encode()
