#!/bin/bash

# Script para iniciar el entorno de desarrollo
echo "🚀 Iniciando Sistema de Gestión ONG - Empuje Comunitario"
echo "=================================================="

# Verificar que Docker esté ejecutándose
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está ejecutándose"
    echo "Por favor, inicia Docker Desktop y vuelve a intentar"
    exit 1
fi

# Verificar que docker-compose esté disponible
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose no está instalado"
    echo "Por favor, instala docker-compose y vuelve a intentar"
    exit 1
fi

echo "✅ Docker está ejecutándose"
echo "📦 Construyendo e iniciando servicios..."

# Construir e iniciar todos los servicios
docker-compose up -d --build

echo ""
echo "🎉 Sistema iniciado exitosamente!"
echo ""
echo "📋 Servicios disponibles:"
echo "   • Frontend:     http://localhost:3001"
echo "   • API Gateway:  http://localhost:3000"
echo "   • PostgreSQL:   localhost:5432"
echo "   • Kafka:        localhost:9092"
echo ""
echo "📊 Para ver los logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para detener el sistema:"
echo "   docker-compose down"