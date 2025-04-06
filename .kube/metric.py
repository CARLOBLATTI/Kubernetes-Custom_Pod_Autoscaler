#!/usr/bin/env python3
import os
import requests
import json
import sys
from datetime import datetime

LOG_FILE = "/shared/metric-gather.log"

def ensure_dir_and_file():
    dir_path = os.path.dirname(LOG_FILE)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write(f"[{datetime.now().isoformat()}] [INFO] Inizializzazione log metric gather\n")

def log_info(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] [INFO] {msg}\n")

def log_error(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] [ERROR] {msg}\n")

def query_prometheus(prometheus_url, query):
    url = f"{prometheus_url}/api/v1/query"
    params = {'query': query}
    
    log_info(f"Invio richiesta a Prometheus: URL={url} con parametri {params}")
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except Exception as e:
        log_error(f"Errore durante la richiesta a Prometheus: {e}")
        sys.exit(1)
        
    try:
        data = response.json()
    except Exception as e:
        log_error(f"Errore nel parsing della risposta JSON: {e}")
        sys.exit(1)
    
    log_info("Dati ricevuti da Prometheus:")
    log_info(json.dumps(data, indent=2))
    
    if data.get('status') == 'success' and data.get('data', {}).get('result'):
        try:
            value = float(data['data']['result'][0]['value'][1])
            log_info(f"Valore estratto: {value}")
            return value
        except (IndexError, ValueError) as e:
            log_error(f"Errore nell'estrazione del valore: {e}")
            sys.exit(1)
    else:
        log_error("Nessun dato restituito dalla query Prometheus")
        sys.exit(1)

#Ottengo il costo orario del carico di lavoro del cluster in base agli ultimi 5 minuti
def get_cost_metric(prometheus_url):
    query = '''
sort_desc(
  sum by (instance) (
          sum_over_time(
            (
                    label_replace(
                      (
                          (
                              avg by (container, node, namespace, pod) (container_memory_allocation_bytes)
                            * on (node) group_left ()
                              avg by (node) (node_ram_hourly_cost)
                          )
                        /
                          (1024 * 1024 * 1024)
                      ),
                      "type",
                      "ram",
                      "",
                      ""
                    )
                  or
                    label_replace(
                      (
                          avg by (container, node, namespace, pod) (container_cpu_allocation)
                        * on (node) group_left ()
                          avg by (node) (node_cpu_hourly_cost)
                      ),
                      "type",
                      "cpu",
                      "",
                      ""
                    )
                or
                  label_replace(
                    (
                        avg by (container, node, namespace, pod) (container_gpu_allocation)
                      * on (node) group_left ()
                        avg by (node) (node_gpu_hourly_cost)
                    ),
                    "type",
                    "gpu",
                    "",
                    ""
                  )
              or
                label_replace(
                  (
                      (
                          avg by (persistentvolume, namespace, pod) (pod_pvc_allocation)
                        * on (persistentvolume) group_left ()
                          avg by (persistentvolume) (pv_hourly_cost)
                      )
                    /
                      (1024 * 1024 * 1024)
                  ),
                  "type",
                  "storage",
                  "",
                  ""
                )
            )[5m:5m]
          )
        /
          scalar(count_over_time(vector(1)[5m:5m]))
      * 12
  )
)
'''
    return query_prometheus(prometheus_url, query)

#Latenza media sul cluster degli ultimi 5 minuti
def get_latency_metric(prometheus_url):
    query = 'round(locust_requests_avg_response_time{name="Aggregated"})'
    return query_prometheus(prometheus_url, query)

def main():
    ensure_dir_and_file()
    log_info("Inizio recupero metriche da Prometheus...")
    prometheus_url = os.getenv('PROMETHEUS_URL', 'http://prometheus-server:80')
    log_info(f"Utilizzo Prometheus URL: {prometheus_url}")
    
    # Recupera entrambe le metriche
    cost = get_cost_metric(prometheus_url)
    latency = get_latency_metric(prometheus_url)
    
    log_info(f"Valore costo: {cost}")
    log_info(f"Valore latenza (95° percentile): {latency}")
    
    # Prepara il risultato in output come JSON
    result = {
        "cost": cost,
        "latency": latency
    }
    
    log_info("Output finale:")
    log_info(json.dumps(result, indent=2))
    
    # Stampa l'output finale in stdout
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()

if __name__ == '__main__':
    main()
