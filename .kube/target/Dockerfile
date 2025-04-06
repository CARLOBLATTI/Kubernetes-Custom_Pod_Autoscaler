FROM python:3.9-slim

RUN pip install flask prometheus_client

EXPOSE 8090

COPY app.py /app.py

CMD ["python", "-u", "/app.py"]
