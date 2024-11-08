# Usa la imagen base oficial de Python
FROM python:3.8-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install -r requirements.txt 

RUN apt-get update && apt-get install -y curl

# Copia el contenido de la aplicación al contenedor
COPY . .

# Expone el puerto 5000
EXPOSE 5000

CMD ["python", "app.py"]