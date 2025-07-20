# 🚀 FraudShield Deployment Guide

## 📍 Repository Information
- **GitHub Username:** NehaSaha18
- **Repository:** https://github.com/Nehasaha18/FraudShieldrepo
- **Repository Name:** FraudShieldrepo

## 🌐 Deployment Options

### Option 1: Railway Deployment (Recommended - Free & Easy)

#### Prerequisites
1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

#### Quick Deploy
```bash
# Clone the repository
git clone https://github.com/Nehasaha18/FraudShieldrepo.git
cd FraudShieldrepo

# Run deployment script
# For Windows:
deploy-railway.bat

# For Linux/Mac:
chmod +x deploy-railway.sh
./deploy-railway.sh
```

#### Manual Railway Deployment
```bash
# Initialize Railway project
railway init

# Set environment variables
railway variables --set "CORS_ORIGINS=https://fraudshield-frontend.railway.app,https://fraudshield.railway.app"
railway variables --set "TRUSTED_HOSTS=fraudshield-backend.railway.app,fraudshield.railway.app"
railway variables --set "REACT_APP_API_URL=https://fraudshield-backend.railway.app"

# Deploy
railway up
```

### Option 2: Render Deployment

#### Prerequisites
1. Create account at [render.com](https://render.com)
2. Connect your GitHub repository

#### Setup Instructions
1. **Go to Render Dashboard**
2. **Click "New +" → "Web Service"**
3. **Connect GitHub Repository:** `Nehasaha18/FraudShieldrepo`
4. **Configure Backend Service:**
   - **Name:** `fraudshield-backend`
   - **Environment:** `Python 3.9`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:**
     ```
     CORS_ORIGINS=https://fraudshield-frontend.onrender.com
     TRUSTED_HOSTS=fraudshield-backend.onrender.com
     ```

5. **Configure Frontend Service:**
   - **Name:** `fraudshield-frontend`
   - **Environment:** `Node`
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Start Command:** `cd frontend && npm start`
   - **Environment Variables:**
     ```
     REACT_APP_API_URL=https://fraudshield-backend.onrender.com
     ```

## 🔐 Login Credentials

### Central Bank Dashboard
- **Username:** `centralbank`
- **Password:** `admin123`

### MANIT Dashboard
- **Username:** `manit`
- **Password:** `bhopal123`

## 📋 Features Available

### Central Bank Dashboard
- ✅ Upload transaction data (CSV)
- ✅ AI-powered fraud detection
- ✅ Block/verify suspicious transactions
- ✅ Generate detailed fraud reports
- ✅ Real-time transaction monitoring

### MANIT Dashboard
- ✅ Upload student loan data (CSV)
- ✅ Mark transactions as received
- ✅ Verify student registrations
- ✅ Generate loan verification reports
- ✅ Department-wise statistics

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |
| `TRUSTED_HOSTS` | Trusted backend hosts | `localhost,127.0.0.1` |
| `REACT_APP_API_URL` | Frontend API endpoint | `http://localhost:8000` |

## 📁 Repository Structure

```
FraudShieldrepo/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend container
│   └── security/          # Security modules
├── frontend/               # React frontend
│   ├── src/               # Source code
│   ├── package.json       # Node dependencies
│   └── Dockerfile         # Frontend container
├── docker-compose.yml     # Local development
├── docker-compose.prod.yml # Production deployment
├── railway.json           # Railway configuration
├── railway.toml           # Railway services
├── deploy-railway.bat     # Windows deployment script
├── deploy-railway.sh      # Linux/Mac deployment script
└── README.md              # Project documentation
```

## 🛠️ Local Development

### Prerequisites
- Docker Desktop
- Git

### Quick Start
```bash
# Clone repository
git clone https://github.com/Nehasaha18/FraudShieldrepo.git
cd FraudShieldrepo

# Start with Docker
docker-compose up -d

# Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Check `CORS_ORIGINS` environment variable
   - Ensure frontend URL is included

2. **Authentication Issues:**
   - Verify login credentials
   - Check JWT token storage

3. **File Upload Issues:**
   - Ensure CSV format is correct
   - Check file size limits

4. **Deployment Failures:**
   - Check build logs
   - Verify environment variables
   - Ensure all dependencies are listed

## 🔒 Security Features

- ✅ OAuth 2.0 Authentication
- ✅ Role-Based Access Control (RBAC)
- ✅ Rate Limiting
- ✅ Anomaly Detection
- ✅ CORS Protection
- ✅ Trusted Host Validation
- ✅ Security Headers
- ✅ JWT Token Management

## 🎉 Success!

Your FraudShield application is now deployed and accessible! Share the frontend URL with your team and start detecting fraud with AI-powered security.

### Quick Links
- **Repository:** https://github.com/Nehasaha18/FraudShieldrepo
- **Railway Dashboard:** https://railway.app/dashboard
- **Render Dashboard:** https://dashboard.render.com 