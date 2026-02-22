# Backend MediAgent — FastAPI
FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema (por si cryptography las necesita)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código y datos
COPY main.py config.py dependencies.py ./
COPY routers/ ./routers/
COPY schemas/ ./schemas/
COPY services/ ./services/
COPY bd/ ./bd/

# Puerto por defecto de la API
EXPOSE 8000

# Variables por defecto (sobrescribibles con -e o env_file)
ENV CORS_ORIGINS="http://localhost:8080" \
    SECRET_KEY="cambiar-en-produccion-clave-secreta-muy-larga" \
    ACCESS_TOKEN_EXPIRE_MINUTES=60

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
