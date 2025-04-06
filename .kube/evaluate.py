#!/usr/bin/env python3
import os
import sys
import json
import math
from datetime import datetime

LOG_FILE = "/shared/metric-evaluate.log"
FILE_PATH = "/shared/current_replicas.txt"
FILE_DIR = os.path.dirname(FILE_PATH)

def ensure_dir_and_file():
    if not os.path.exists(FILE_DIR):
        os.makedirs(FILE_DIR)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write(f"[{datetime.now().isoformat()}] [INFO] Inizializzazione file di log\n")

def log_info(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] [INFO] {msg}\n")

def log_error(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] [ERROR] {msg}\n")

#Recupero current replicas da file condiviso
# def read_current_replicas():
#     try:
#         if not os.path.exists(FILE_DIR):
#             os.makedirs(FILE_DIR)
#             log_info(f"Creata la directory {FILE_DIR}")
#         with open(FILE_PATH, "r") as f:
#             value = f.read().strip()
#             log_info(f"Letto CURRENT_REPLICAS dal file: {value}")
#             return int(value)
#     except Exception as e:
#         log_info(f"Nessun file trovato o errore nella lettura, uso default 1: {e}")
#         return 1

def write_current_replicas(value):
    try:
        if not os.path.exists(FILE_DIR):
            os.makedirs(FILE_DIR)
            log_info(f"Creata la directory {FILE_DIR}")
        with open(FILE_PATH, "w") as f:
            f.write(str(value))
        log_info(f"Scritti CURRENT_REPLICAS nel file: {value}")
    except Exception as e:
        log_error(f"Errore nella scrittura del file: {e}")

def main():
    ensure_dir_and_file()
    
    try:
        # Legge l'input JSON dalla stdin
        spec = json.loads(sys.stdin.read())
        # log_info(f"Input JSON ricevuto: {json.dumps(spec)}")
    except Exception as e:
        log_error(f"Errore nel parsing dell'input JSON: {e}")
        sys.exit(1)
    
    evaluate(spec)

def evaluate(spec):
    try:
        metric_str = spec["metrics"][0]["value"]
        metric_data = json.loads(metric_str)
        current_cost = float(metric_data["cost"])
        log_info(f"Valore corrente cost: {current_cost}")
    except Exception as e:
        log_error(f"Errore nella lettura della metrica 'cost': {e}")
        sys.exit(1)
    
    try:
        current_latency = float(metric_data["latency"])
        log_info(f"Valore corrente average latency: {current_latency}")
    except Exception as e:
        log_error(f"Errore nella lettura della metrica 'latency': {e}")
        sys.exit(1)
    
    # # Legge il valore corrente delle repliche dal file
    # current_replicas = read_current_replicas()

    try:
        current_replicas = int(spec["resource"]["spec"]["replicas"])
        log_info(f"Repliche correnti (dal JSON): {current_replicas}")
    except Exception as e:
        log_error(f"Errore nel recupero delle repliche correnti dal JSON: {e}")
        sys.exit(1)
    
    try:
        target_cost = float(os.getenv("TARGET_COST", "0.5"))
    except Exception as e:
        log_error(f"Errore nel recupero di TARGET_COST, uso 0.5: {e}")
        target_cost = 0.5

    try:
        target_latency = float(os.getenv("TARGET_LATENCY", "70"))
    except Exception as e:
        log_error(f"Errore nel recupero di TARGET_LATENCY, uso 70: {e}")
        target_latency = 70 #target del cluster a 70ms

    log_info(f"CURRENT_REPLICAS: {current_replicas}, TARGET_COST: {target_cost}, TARGET_LATENCY: {target_latency}")
    
    # Logica di scaling:
    # - Se il costo è superiore al target e la latenza è sotto il target, riduciamo le repliche per abbassare i costi.
    # - Se la latenza supera il target e il costo è sotto il target, aumentiamo le repliche per migliorare lo SLO.
    # - Se entrambe le metriche sono fuori target, bilanciamo le due esigenze.
    desired_replicas = current_replicas  # valore iniziale
    
    if current_cost > target_cost and current_latency <= target_latency:
        # Riduzione: abbassiamo le repliche per diminuire i costi
        ratio_cost = target_cost / current_cost
        desired_replicas = math.floor(current_replicas * ratio_cost)
        log_info(f"Riduzione repliche: ratio_cost={ratio_cost}")
    elif current_latency > target_latency and current_cost <= target_cost:
        # Aumento: incrementiamo le repliche per migliorare la latenza
        ratio_latency = current_latency / target_latency
        desired_replicas = math.ceil(current_replicas * ratio_latency)
        log_info(f"Aumento repliche: ratio_latency={ratio_latency}")
    elif current_cost > target_cost and current_latency > target_latency:
        # Trade-off: entrambi i valori sono fuori target, bilanciamo la decisione
        ratio_latency = current_latency / target_latency
        ratio_cost = target_cost / current_cost
        #Diamo maggior peso al costo
        combined_ratio = (ratio_latency + ratio_cost) / 2
        desired_replicas = math.ceil(current_replicas * combined_ratio)
        log_info(f"Bilanciamento repliche: ratio_latency={ratio_latency}, ratio_cost={ratio_cost}, combined_ratio={combined_ratio}")
    else:
        log_info("Nessuna modifica necessaria.")
    
    # Garantiamo almeno 1 replica
    if desired_replicas < 1:
        desired_replicas = 1
    
    try:
        max_replicas = int(os.getenv("MAX_REPLICAS", "10"))
    except Exception as e:
        log_error(f"Errore nel recupero di MAX_REPLICAS, uso 10: {e}")
        max_replicas = 10

    if desired_replicas > max_replicas:
        log_info(f"desired_replicas ({desired_replicas}) > MAX_REPLICAS ({max_replicas}), impostazione a MAX_REPLICAS")
        desired_replicas = max_replicas

    log_info(f"Numero finale di repliche desiderate: {desired_replicas}")
    
    # Aggiorna il file con il nuovo valore delle repliche
    write_current_replicas(desired_replicas)
    
    # Costruisce l'output JSON (qui usiamo "targetReplicas", modifica se richiesto)
    evaluation = {"targetReplicas": desired_replicas}
    log_info("Output finale:")
    log_info(json.dumps(evaluation, indent=2))
    
    # Stampa l'output finale in stdout
    sys.stdout.write(json.dumps(evaluation))
    sys.stdout.flush()

if __name__ == '__main__':
    main()
