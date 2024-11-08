from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# URL del balanceador de carga
BACKEND_URL = "http://nginx-load-balancer:5001"

@app.route('/')
def index():
    # Realiza una solicitud al balanceador de carga (que a su vez distribuye a los backends)
    try:
        response = requests.get(f"{BACKEND_URL}/")
        container_info = response.json()  # Aquí se recibirá la respuesta de uno de los backends
    except requests.exceptions.RequestException as e:
        container_info = "Error: No se pudo conectar con el frontend."
    print(container_info)

    return render_template('index.html', container_info=container_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)  # El frontend se sirve en el puerto 80