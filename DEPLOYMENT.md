# FraudShield Docker Deployment Guide

## Prerequisites

1. **Docker Desktop** installed and running
2. **Docker Compose** (usually comes with Docker Desktop)
3. **Git** (to clone the repository)

## Quick Deployment

### Option 1: Using PowerShell Script (Recommended for Windows)
```powershell
# Run the deployment script
.\deploy.ps1
```

### Option 2: Using Batch File
```cmd
# Double-click deploy.bat or run:
deploy.bat
```

### Option 3: Manual Deployment
```bash
# 1. Start Docker Desktop manually
# 2. Open PowerShell/Command Prompt in the project directory
# 3. Run the following commands:

# Stop any existing containers
docker-compose down

# Build and start services
docker-compose up --build -d

# Check status
docker-compose ps
```

## Manual Docker Desktop Startup

If Docker Desktop is not running:

1. **Windows**: 
   - Press `Win + R`, type `docker desktop`, press Enter
   - Or find "Docker Desktop" in Start Menu
   - Wait for the whale icon to appear in system tray

2. **macOS**:
   - Open Docker Desktop from Applications
   - Wait for the whale icon to appear in menu bar

3. **Linux**:
   - Run `sudo systemctl start docker`

## Accessing the Application

Once deployed successfully:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Login Credentials

### Central Bank Dashboard
- Username: `centralbank`
- Password: `admin123`

### MANIT Dashboard
- Username: `manit`
- Password: `bhopal123`

### Your Account
- Username: `sahaneha1809@gmail.com`
- Password: `admin123`

## Useful Commands

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Remove all containers and images
docker-compose down --rmi all

# Check service status
docker-compose ps

# Access backend container
docker-compose exec backend bash

# Access frontend container
docker-compose exec frontend sh
```

## Troubleshooting

### Docker Desktop Not Running
```
Error: error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/containers/json?all=1"
```
**Solution**: Start Docker Desktop manually and wait for it to fully load.

### Port Already in Use
```
Error: Ports are not available: listen tcp 0.0.0.0:8000: bind: address already in use
```
**Solution**: 
```bash
# Find process using the port
netstat -ano | findstr :8000
# Kill the process or change ports in docker-compose.yml
```

### Build Failures
```bash
# Clean build
docker-compose down --rmi all
docker-compose up --build -d
```

### Permission Issues (Linux/macOS)
```bash
# Add your user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

## Architecture Overview

The application consists of:

1. **Backend Service** (Port 8000)
   - FastAPI application with security features
   - Fraud detection engine with AI capabilities
   - OAuth2 authentication and RBAC
   - Report generation

2. **Frontend Service** (Port 3000)
   - React application
   - Central Bank and MANIT dashboards
   - Real-time fraud monitoring

3. **Network**: Custom bridge network for service communication

## Security Features

- **TLS 1.3** encryption
- **OAuth 2.0** authentication
- **Role-Based Access Control (RBAC)**
- **Anomaly Detection**
- **Rate Limiting**
- **Security Headers**
- **CORS Protection**

## Monitoring

- Health checks for both services
- Automatic restart on failure
- Volume mounts for data persistence
- Log aggregation

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Use `.env` files for sensitive data
2. **SSL/TLS**: Configure proper certificates
3. **Database**: Use external database instead of file storage
4. **Load Balancer**: Add reverse proxy (nginx)
5. **Monitoring**: Add Prometheus/Grafana
6. **Backup**: Configure data backup strategies

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify Docker Desktop is running
3. Ensure ports 3000 and 8000 are available
4. Check system resources (CPU, RAM, disk space) 