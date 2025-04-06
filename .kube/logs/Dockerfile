# # Utilizza l'immagine base fornita dal framework Custom Pod Autoscaler
# FROM custompodautoscaler/python:latest

# # Installa il modulo requests
# RUN pip install requests

# COPY config.yaml /config.yaml
# COPY evaluate.py /evaluate.py
# COPY metric.py /metric.py

# COPY run.sh /run.sh

# RUN chmod +x /metric.py /evaluate.py /run.sh

# CMD ["/run.sh"]

# Usa una immagine base leggera di Python
FROM python:3.9-slim

# Copia lo script all'interno del container
COPY read_logs.py /read_logs.py

# Imposta il comando di default per eseguire lo script in modalità non bufferizzata
CMD ["python", "-u", "/read_logs.py"]
