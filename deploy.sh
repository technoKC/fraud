#!/bin/bash

echo "🚀 FraudShield Docker Deployment Script"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Remove old images (optional)
read -p "Do you want to remove old images? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing old images..."
    docker-compose down --rmi all
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Check health status
echo "🏥 Checking health status..."
docker-compose exec backend curl -f http://localhost:8000/ || echo "❌ Backend health check failed"
docker-compose exec frontend wget --no-verbose --tries=1 --spider http://localhost:3000 || echo "❌ Frontend health check failed"

echo ""
echo "🎉 Deployment completed!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "🔐 Login Credentials:"
echo "   Central Bank: username='centralbank', password='admin123'"
echo "   MANIT: username='manit', password='bhopal123'"
echo "   Your Email: username='sahaneha1809@gmail.com', password='admin123'"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart" 