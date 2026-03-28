# Usa uma imagem oficial leve do Node.js
FROM node:20-alpine

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependência e instala
# O asterisco garante que copie o package-lock.json se ele existir
COPY package.json package-lock.json* ./
RUN npm install

# Copia o restante do código do frontend
COPY . .

# Expõe a porta padrão do Vite
EXPOSE 5173

# Comando para rodar o Vite (o --host expõe para fora do container)
CMD ["npm", "run", "dev", "--", "--host"]
