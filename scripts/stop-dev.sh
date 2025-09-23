#!/bin/bash

# Script para detener el entorno de desarrollo
echo "🛑 Deteniendo Sistema de Gestión ONG - Empuje Comunitario"
echo "======================================================="

# Detener todos los servicios
docker-compose down

echo "✅ Sistema detenido exitosamente"
echo ""
echo "💡 Para eliminar también los volúmenes de datos:"
echo "   docker-compose down -v"