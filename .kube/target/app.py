from flask import Flask, jsonify, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import math

app = Flask(__name__)

REQUEST_COUNT = Counter('api_request_count', 'Numero totale di richieste all\'API')
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'Latenza delle richieste API in secondi')

def cpu_burn(duration_seconds=0.05):
    start = time.process_time()
    while (time.process_time() - start) < duration_seconds:
        math.sqrt(12345.6789)

@app.route('/')
def index():
    start_time = time.time()
    REQUEST_COUNT.inc()

    # CPU burn per circa 1% del tempo di 1 core per 1 secondo
    cpu_burn(0.05)

    latency = time.time() - start_time
    REQUEST_LATENCY.observe(latency)
    return jsonify({
        'message': 'Hello, questo è un endpoint API di test!',
        'latency': latency
    })

@app.route('/metrics')
def metrics():
    data = generate_latest()
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
