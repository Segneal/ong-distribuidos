FROM node:18-alpine

WORKDIR /app

# Instalar dependencias
COPY package*.json ./
RUN npm ci --only=production

# Copiar código fuente
COPY src/ ./src/

# Configurar variables de entorno
ENV NODE_ENV=production
ENV PORT=3002

# Exponer puerto
EXPOSE 3002

# Comando para iniciar el servicio
CMD ["npm", "start"]