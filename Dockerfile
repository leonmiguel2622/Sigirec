FROM python:3.11-slim

# Instalar dependencias para OpenCV y YOLO en Debian
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer el puerto
EXPOSE 5000

# Forzar a Flask a escuchar en todas las interfaces de red (0.0.0.0)
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
