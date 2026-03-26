# Usa uma imagem oficial leve do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que o FastAPI vai rodar
EXPOSE 8000

# Comando para iniciar o servidor (o reload permite atualizar o código sem derrubar o container)
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["fastapi dev"]
