# Python 3.12.17 slim
FROM python:3.12.17-slim

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1

# Dependências mínimas necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o projeto
COPY . .

# Expõe porta
EXPOSE 5000

# Usa Gunicorn no entrypoint
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "run_server:app"]
