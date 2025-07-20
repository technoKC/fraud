# 🚀 FraudShield Railway Deployment Guide

## Quick Deploy to Railway

### Option 1: Automatic Deployment (Recommended)

**For Windows:**
```bash
deploy-railway.bat
```

**For Linux/Mac:**
```bash
chmod +x deploy-railway.sh
./deploy-railway.sh
```

### Option 2: Manual Deployment

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize Project:**
   ```bash
   railway init
   ```

4. **Set Environment Variables:**
   ```bash
   railway variables set CORS_ORIGINS="https://fraudshield-frontend.railway.app,https://fraudshield.railway.app"
   railway variables set TRUSTED_HOSTS="fraudshield-backend.railway.app,fraudshield.railway.app"
   railway variables set REACT_APP_API_URL="https://fraudshield-backend.railway.app"
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

## 🌐 Access Your Application

After deployment, your application will be available at:

- **Frontend Dashboard:** https://fraudshield-frontend.railway.app
- **Backend API:** https://fraudshield-backend.railway.app
- **API Documentation:** https://fraudshield-backend.railway.app/docs

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

The application uses these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |
| `TRUSTED_HOSTS` | Trusted backend hosts | `localhost,127.0.0.1` |
| `REACT_APP_API_URL` | Frontend API endpoint | `http://localhost:8000` |

## 📊 Monitoring

- **Health Check:** https://fraudshield-backend.railway.app/
- **API Status:** https://fraudshield-backend.railway.app/docs
- **Railway Dashboard:** https://railway.app/dashboard

## 🛠️ Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Check if `CORS_ORIGINS` includes your frontend URL
   - Ensure `TRUSTED_HOSTS` includes your backend URL

2. **Authentication Issues:**
   - Verify login credentials
   - Check if tokens are being stored properly

3. **File Upload Issues:**
   - Ensure CSV files are properly formatted
   - Check file size limits (max 10MB)

4. **Report Generation:**
   - Verify static files are accessible
   - Check if reports directory exists

### Support

If you encounter issues:
1. Check Railway logs: `railway logs`
2. Verify environment variables: `railway variables`
3. Restart services: `railway restart`

## 🔄 Updates

To update your deployed application:

```bash
git pull origin main
railway up
```

## 📈 Scaling

Railway automatically scales your application based on traffic. For custom scaling:

```bash
railway scale web=2
```

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

Your FraudShield application is now live and accessible to everyone! Share the frontend URL with your team and start detecting fraud with AI-powered security. 