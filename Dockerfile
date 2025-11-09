# Use Python 3.12 slim como base
FROM python:3.12.17-slim

# Diretório de trabalho
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe porta do Flask
EXPOSE 5000

# Comando padrão para iniciar a aplicação
CMD ["python", "run_server.py"]
