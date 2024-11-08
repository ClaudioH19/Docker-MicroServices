import signal
import sys
from flask import Flask, jsonify
import os
import requests
import psycopg2
import redis

app = Flask(__name__)

# Obtener el nombre del contenedor desde la variable de entorno
container_id = os.getenv('HOSTNAME')

# Configurar la conexión a Redis
try:
    r = redis.Redis(host='redis_cache', port=6379, db=0)
    r.ping()  # Verificar la conexión con Redis
    redis_available = True
except redis.exceptions.RedisError:
    print("Redis no está disponible, se procederá sin caché.")
    redis_available = False

def get_rocket_names():
    try:
        # Conectar a la base de datos PostgreSQL
        connection = psycopg2.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DB")
        )
        cursor = connection.cursor()

        # Consulta para obtener los nombres de los cohetes
        query = "SELECT rocket_name FROM spacex_rockets;"
        cursor.execute(query)

        # Obtener todos los resultados
        rocket_names = cursor.fetchall()

        # Convertir los resultados en una lista de diccionarios
        rockets = [{"rocket_name": name[0]} for name in rocket_names]
        return rockets

    except (Exception, psycopg2.Error) as error:
        print("Error al conectar a la base de datos", error)
        return []

    finally:
        if connection:
            cursor.close()
            connection.close()

def get_cached_rocket_names():
    # Intentar obtener los nombres de los cohetes desde Redis si está disponible
    if redis_available:
        try:
            cached_data = r.get('rocket_names')
            if cached_data:
                # Si existe en Redis, devolver los datos en caché
                return {"source": "cache", "data": eval(cached_data.decode('utf-8'))}
            else:
                # Si no existe en caché, obtener los datos desde PostgreSQL
                rocket_names = get_rocket_names()
                # Almacenar los datos en Redis con expiración de 1 hora
                r.set('rocket_names', str(rocket_names), ex=3600)
                return {"source": "database", "data": rocket_names}
        except redis.exceptions.RedisError as e:
            print("Error al conectar a Redis:", e)
            # Continuar sin caché si Redis falla
            rocket_names = get_rocket_names()
            return {"source": "database", "data": rocket_names}
    else:
        # Si Redis no está disponible desde el inicio, consultar directamente PostgreSQL
        rocket_names = get_rocket_names()
        return {"source": "database", "data": rocket_names}

@app.route('/')
def home():
    return f"Bienvenido al backend de microservicios, contenedor: {container_id}", 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "container": container_id}), 200

@app.route('/spacex', methods=['GET'])
def askAPI():
    try:
        # Petición a PostgreSQL
        rocket_names = get_cached_rocket_names()
        # Petición a la API de SpaceX
        response = requests.get("https://api.spacexdata.com/v4/launches/latest")
        response.raise_for_status()
        launch_data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "No se pudo conectar con la API de SpaceX", "details": str(e)}), 500

    # Extraer algunos datos interesantes del lanzamiento
    launch_info = {
        "id_contenedor": container_id,
        "name": launch_data.get("name"),
        "date_utc": launch_data.get("date_utc"),
        "rocket": launch_data.get("rocket"),
        "success": launch_data.get("success"),
        "details": launch_data.get("details"),
        "other_rockets": rocket_names
    }

    return jsonify(launch_info), 200

# Función para manejar señales y limpiar el caché de Redis
def handle_sigterm(*args):
    print("Recibiendo señal SIGTERM, limpiando caché de Redis...")
    if redis_available:
        r.flushdb()  # Limpia todos los datos de Redis
    sys.exit(0)

# Registrar la función manejadora para la señal SIGTERM
signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
