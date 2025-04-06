#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

# Elenco dei file di log da monitorare
LOG_FILES = [
    "/shared/metric-evaluate.log",
    "/shared/metric-gather.log"
]

def log_info(msg):
    print(f"[{datetime.now().isoformat()}] [INFO] {msg}")

def log_error(msg):
    print(f"[{datetime.now().isoformat()}] [ERROR] {msg}", file=sys.stderr)

def ensure_files_exist(files):
    for file_path in files:
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            log_info(f"Creata la directory: {directory}")
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("")
            log_info(f"Creato il file: {file_path}")

def read_and_clear_file(file_path):
    try:
        with open(file_path, "r+") as f:
            content = f.read().strip()
            # Tronca il file: imposta la dimensione a zero
            f.seek(0)
            f.truncate()
        return content
    except Exception as e:
        log_error(f"Errore nella lettura/clearing di {file_path}: {e}")
        return ""

def main():
    log_info("Starting log reader for files:")
    for file in LOG_FILES:
        log_info(file)
    
    ensure_files_exist(LOG_FILES)
    
    while True:
        for file_path in LOG_FILES:
            if os.path.exists(file_path):
                content = read_and_clear_file(file_path)
                if content:
                    log_info(f"Contenuto di {file_path}:")
                    log_info(content)
            else:
                log_error(f"File non trovato: {file_path}")
        time.sleep(1)

if __name__ == '__main__':
    main()
