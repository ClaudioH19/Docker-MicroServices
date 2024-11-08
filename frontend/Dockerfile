# Usa la imagen base oficial de Python
FROM python:3.8-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido de la aplicación al contenedor
COPY . .

# Define la variable de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Expone el puerto 80 para Flask
EXPOSE 80

# Comando por defecto para correr la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
