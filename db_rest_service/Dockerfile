FROM python:3.9-slim

WORKDIR /app

COPY db_rest_service/src/ /app
COPY models/ /app/models

RUN pip install sockets pymysql 

ENV PYTHONUNBUFFERED=1  PYTHONDONTWRITEBYTECODE=1

EXPOSE 80

CMD ["python", "http_server.py"]
