FROM python:3.9-slim

# Installa locust
RUN pip install locust

# Copia il file locustfile.py nella cartella di lavoro
COPY locust_test.py /locust_test.py

# Espone la porta dell'interfaccia web (default 8089)
EXPOSE 8089

# Comando per avviare Locust in modalità web
CMD ["locust", "-f", "/locust_test.py"]
