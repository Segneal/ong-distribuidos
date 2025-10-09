FROM node:18-alpine

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install --only=production

# Instalar herramientas de protobuf globalmente
RUN npm install -g @grpc/proto-loader

# Copiar código fuente
COPY src/ ./src/
COPY proto/ ./proto/

# Exponer puerto
EXPOSE 3000

# Comando para ejecutar la aplicación
CMD ["npm", "start"]