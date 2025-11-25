# Usa a imagem base oficial do Python para a versão 3.13
FROM python:3.13-slim

# Variáveis de ambiente padrão
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho dentro do container.
# O nome é irrelevante, mas /app é a convenção padrão.
WORKDIR /app

# 1. Copia o arquivo de dependências
COPY requirements.txt /app/

# 2. Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn uvicorn[standard]
# 3. Copia todo o código da aplicação e arquivos de configuração (incluindo src/, alembic/, main.py, etc.)
# O '.' representa o diretório atual (a raiz do seu projeto)
COPY . /app/

# 4. Comando para iniciar a aplicação (produção)
# O comando de execução: aplica migrações e inicia o servidor.
CMD ["/bin/sh", "-c", "alembic upgrade head && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80"]