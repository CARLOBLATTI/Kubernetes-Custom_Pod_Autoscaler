#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime
from locust import HttpUser, task, between

def log_info(msg):
    print(f"[{datetime.now().isoformat()}] [INFO] {msg}")

def log_error(msg):
    print(f"[{datetime.now().isoformat()}] [ERROR] {msg}", file=sys.stderr)

class APITestUser(HttpUser):
    host = "http://app-service:90"
    # Tempo di attesa fra un task e l'altro
    wait_time = between(1, 3)

    @task(1)
    def index_endpoint(self):
        log_info(f"Index Endpoint: invio richiesta")
        with self.client.get("/", name="Index Endpoint", catch_response=True) as response:
            if response.status_code != 200:
                log_error(f"Index Endpoint: richiesta fallita con status {response.status_code}")
                response.failure(f"Status code errato: {response.status_code}")
            else:
                log_info(f"Index Endpoint: richiesta completata in {response.elapsed.total_seconds()} s")
        # Numero di richieste consecutive per "stressare" l'endpoint
        # num_requests = 50
        # for i in range(num_requests):
        #     log_info(f"Index Endpoint: invio richiesta {i+1} di {num_requests}")
        #     with self.client.get("/", name="Index Endpoint", catch_response=True) as response:
        #         if response.status_code != 200:
        #             log_error(f"Index Endpoint: richiesta {i+1} fallita con status {response.status_code}")
        #             response.failure(f"Status code errato: {response.status_code}")
        #         else:
        #             log_info(f"Index Endpoint: richiesta {i+1} completata in {response.elapsed.total_seconds()} s")
    
    # @task(1)
    # def metrics_endpoint(self):
    #     log_info("Metrics Endpoint: invio richiesta per recuperare le metriche")
    #     with self.client.get("/metrics", name="Metrics Endpoint", catch_response=True) as response:
    #         if response.status_code != 200:
    #             log_error(f"Metrics Endpoint: richiesta fallita con status {response.status_code}")
    #             response.failure(f"Status code errato: {response.status_code}")
    #         else:
    #             log_info("Metrics Endpoint: richiesta completata con successo")
