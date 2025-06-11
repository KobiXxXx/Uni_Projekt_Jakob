FROM python:3.9-slim

WORKDIR /app

COPY test_runner/src/ /app
COPY test_runner/templates/ /app/templates

RUN pip install sockets Flask matplotlib requests

ENV PYTHONUNBUFFERED=1  PYTHONDONTWRITEBYTECODE=1

EXPOSE 8100

CMD ["python", "main.py"]