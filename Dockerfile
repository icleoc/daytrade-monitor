# Python 3.12.17 slim (garante compatibilidade)
FROM python:3.12.17-slim

WORKDIR /app

# Evita compilação de dependências problemáticas
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema para pandas/numpy
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .

# Atualiza pip e instala pacotes
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe porta
EXPOSE 5000

# Comando para iniciar
CMD ["python", "run_server.py"]
