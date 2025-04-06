# Utilizza l'immagine base fornita dal framework Custom Pod Autoscaler
FROM custompodautoscaler/python:latest

# Installa il modulo requests
RUN pip install requests

ADD config.yaml evaluate.py metric.py /

# COPY config.yaml /config.yaml
# COPY evaluate.py /evaluate.py
# COPY metric.py /metric.py

# COPY run.sh /run.sh

# RUN chmod +x /metric.py /evaluate.py /run.sh

# CMD ["/run.sh"]
