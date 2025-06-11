FROM python:3.9-slim

WORKDIR /app

COPY worker/src/ /app
COPY models/ /app/models
COPY rpc/ /app/rpc
COPY lamport/ /app/lamport

RUN pip install sockets docker numpy grpcio grpcio-tools protobuf paho-mqtt

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000/udp

CMD ["python", "worker.py"]
