# FraudShield Docker Deployment Script for Windows
Write-Host "🚀 FraudShield Docker Deployment Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check if Docker Desktop is running
Write-Host "🔍 Checking Docker Desktop status..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker Desktop is not running" -ForegroundColor Red
        Write-Host "Please start Docker Desktop manually:" -ForegroundColor Yellow
        Write-Host "1. Open Docker Desktop from Start Menu" -ForegroundColor White
        Write-Host "2. Wait for it to fully start (you'll see the whale icon in system tray)" -ForegroundColor White
        Write-Host "3. Run this script again" -ForegroundColor White
        exit 1
    }
} catch {
    Write-Host "❌ Docker Desktop is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop manually and try again" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is available
Write-Host "🔍 Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose is available: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available" -ForegroundColor Red
    exit 1
}

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Ask about removing old images
$removeImages = Read-Host "Do you want to remove old images? (y/n)"
if ($removeImages -eq 'y' -or $removeImages -eq 'Y') {
    Write-Host "🗑️ Removing old images..." -ForegroundColor Yellow
    docker-compose down --rmi all
}

# Build and start services
Write-Host "🔨 Building and starting services..." -ForegroundColor Yellow
docker-compose up --build -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check service status
Write-Host "📊 Checking service status..." -ForegroundColor Yellow
docker-compose ps

# Check if services are healthy
Write-Host "🏥 Checking health status..." -ForegroundColor Yellow
try {
    $backendHealth = docker-compose exec -T backend curl -f http://localhost:8000/ 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend health check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Backend health check failed" -ForegroundColor Red
}

try {
    $frontendHealth = docker-compose exec -T frontend wget --no-verbose --tries=1 --spider http://localhost:3000 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend health check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend health check failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Login Credentials:" -ForegroundColor Yellow
Write-Host "   Central Bank: username='centralbank', password='admin123'" -ForegroundColor White
Write-Host "   MANIT: username='manit', password='bhopal123'" -ForegroundColor White
Write-Host "   Your Email: username='sahaneha1809@gmail.com', password='admin123'" -ForegroundColor White
Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Yellow
Write-Host "   View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop services: docker-compose down" -ForegroundColor White
Write-Host "   Restart services: docker-compose restart" -ForegroundColor White 