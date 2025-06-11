import pymysql
import json
from models.http import HTTP_Request, HTTP_Response, HTTP_Status, HTTP_Content_type

class HttpHelper:
    """
    Helfer-Klasse, die die HTTP-Request-Verarbeitung durchführt.
    """
    @staticmethod
    def parse_request(request):
        headers = request.split('\r\n')
        method, path, _ = headers[0].split()
        content_length = 0
        for header in headers:
            if header.startswith('Content-Length'):
                content_length = int(header.split(': ')[1])
                break
        body = request.split('\r\n\r\n')[1] if '\r\n\r\n' in request else ''
        return HTTP_Request(method, path, content_length, body)

    @staticmethod
    def connect_database():
        try:
            connection = pymysql.connect(
                host='vs_mariadb',
                user='vs',
                password='vs',
                database='vsdb'
            )
            return connection, True
        except Exception as e:
            print(f'Failed to connect to database: {e}')
            return None, False

    @staticmethod
    def execute_sql(sql, params=None):
        connection, connected = HttpHelper.connect_database()
        if not connected:
            return None, False
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                if sql.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                    return result, True
                else:
                    connection.commit()
                    rowcount = cursor.rowcount
                    return rowcount, True
        except Exception as e:
            print(f'Failed to execute SQL: {e}')
            return None, False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def generate_cors_headers():
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

    @staticmethod
    def handle_request(request):
        try:
            http_request = HttpHelper.parse_request(request)
            cors_headers = HttpHelper.generate_cors_headers()

            if http_request.method == 'POST' and http_request.path == '/api/v1/matrices':
                data = http_request.body.split()
                matrix_id = int(data[0].split('=')[1])
                i = int(data[1].split('=')[1])
                j = int(data[2].split('=')[1])
                result = int(data[3].split('=')[1])
                sql = "INSERT INTO matrix (matrix_id, i, j, result) VALUES (%s, %s, %s, %s)"
                _, success = HttpHelper.execute_sql(sql, (matrix_id, i, j, result))
                if success:
                    response = HTTP_Response(
                        HTTP_Status.CREATED,
                        HTTP_Content_type.HTML,
                        headers=cors_headers,
                        body='<html><body><h1>201 Created</h1></body></html>'
                    )
                else:
                    response = HTTP_Response(
                        HTTP_Status.INTERNAL_SERVER_ERROR,
                        HTTP_Content_type.HTML,
                        headers=cors_headers,
                        body='<html><body><h1>500 Internal Server Error</h1></body></html>'
                    )
            elif http_request.method == 'GET' and http_request.path.startswith('/api/v1/matrices'):
                matrix_id = int(http_request.path.split('=')[1])
                sql = 'SELECT * FROM matrix WHERE matrix_id = %s'
                data, success = HttpHelper.execute_sql(sql, (matrix_id,))
                if success:
                    response = HTTP_Response(
                        HTTP_Status.OK,
                        HTTP_Content_type.JSON,
                        headers=cors_headers,
                        body=json.dumps(data)
                    )
                else:
                    response = HTTP_Response(
                        HTTP_Status.INTERNAL_SERVER_ERROR,
                        HTTP_Content_type.HTML,
                        headers=cors_headers,
                        body='<html><body><h1>500 Internal Server Error</h1></body></html>'
                    )
            elif http_request.method == 'GET' and http_request.path == '/api/v1/highest_id':
                sql = 'SELECT MAX(matrix_id) AS highest_id FROM matrix'
                data, success = HttpHelper.execute_sql(sql)
                if success:
                    response = HTTP_Response(
                        HTTP_Status.OK,
                        HTTP_Content_type.JSON,
                        headers=cors_headers,
                        body=json.dumps(data[0])
                    )
                else:
                    response = HTTP_Response(
                        HTTP_Status.INTERNAL_SERVER_ERROR,
                        HTTP_Content_type.HTML,
                        headers=cors_headers,
                        body='<html><body><h1>500 Internal Server Error</h1></body></html>'
                    )
            elif http_request.method == 'GET' and http_request.path.startswith('/api/v1/test'):
                response = HTTP_Response(
                    HTTP_Status.OK,
                    HTTP_Content_type.PLAIN,
                    headers=cors_headers,
                    body='OK'
                )
            else:
                response = HTTP_Response(
                    HTTP_Status.NOT_FOUND,
                    HTTP_Content_type.HTML,
                    headers=cors_headers,
                    body='<html><body><h1>404 Not Found</h1></body></html>'
                )
            return response
        except Exception as e:
            print(f'Failed to handle request: {e}')
            response = HTTP_Response(
                HTTP_Status.INTERNAL_SERVER_ERROR,
                HTTP_Content_type.HTML,
                headers=cors_headers,
                body='<html><body><h1>500 Internal Server Error</h1></body></html>'
            )
        return response