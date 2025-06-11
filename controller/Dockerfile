FROM python:3.9-slim

WORKDIR /app

COPY controller/src/ /app
COPY rpc/ /app/rpc

RUN pip install sockets Flask Flask-CORS numpy grpcio grpcio-tools protobuf

ENV PYTHONUNBUFFERED=1  PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000 5001/udp

CMD ["python", "controller.py"]