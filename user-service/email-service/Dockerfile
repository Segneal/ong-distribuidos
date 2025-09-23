FROM node:18-alpine

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Crear directorio para testing
RUN mkdir -p ../testing/usuarios

# Exponer puerto
EXPOSE 3001

# Comando para iniciar el servicio
CMD ["npm", "start"]