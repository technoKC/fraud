# 🚀 FraudShield Render Deployment Guide

## ✅ Fixed Issues
- ✅ npm vulnerabilities resolved
- ✅ Permission denied errors fixed
- ✅ Build configuration optimized
- ✅ Environment variables configured

## 🚀 Quick Deploy to Render

### Step 1: Backend Deployment

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect GitHub Repository:** `Nehasaha18/FraudShieldrepo`
4. **Configure Backend Service:**

   **Basic Settings:**
   - **Name:** `fraudshield-backend`
   - **Environment:** `Python 3`
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** `backend`

   **Build & Deploy:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

   **Environment Variables:**
   ```
   CORS_ORIGINS=https://fraudshield-frontend.onrender.com
   TRUSTED_HOSTS=fraudshield-backend.onrender.com
   ```

5. **Click "Create Web Service"**

### Step 2: Frontend Deployment

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect GitHub Repository:** `Nehasaha18/FraudShieldrepo`
4. **Configure Frontend Service:**

   **Basic Settings:**
   - **Name:** `fraudshield-frontend`
   - **Environment:** `Node`
   - **Region:** Same as backend
   - **Branch:** `main`
   - **Root Directory:** `frontend`

   **Build & Deploy:**
   - **Build Command:** `npm install --legacy-peer-deps && npm run build`
   - **Start Command:** `npx serve -s build -l $PORT`

   **Environment Variables:**
   ```
   REACT_APP_API_URL=https://fraudshield-backend.onrender.com
   CI=false
   NODE_ENV=production
   ```

5. **Click "Create Web Service"**

## 🔐 Login Credentials

### Central Bank Dashboard
- **Username:** `centralbank`
- **Password:** `admin123`

### MANIT Dashboard
- **Username:** `manit`
- **Password:** `bhopal123`

## 🌐 Access Your Application

After deployment, your application will be available at:

- **Frontend:** https://fraudshield-frontend.onrender.com
- **Backend:** https://fraudshield-backend.onrender.com
- **API Docs:** https://fraudshield-backend.onrender.com/docs

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

## 🔧 Troubleshooting

### Common Issues & Solutions

1. **Build Failures:**
   - ✅ Fixed: npm vulnerabilities resolved
   - ✅ Fixed: Permission issues resolved
   - ✅ Fixed: CI=false flag added

2. **CORS Errors:**
   - Ensure `CORS_ORIGINS` includes your frontend URL
   - Check `TRUSTED_HOSTS` includes your backend URL

3. **Authentication Issues:**
   - Verify login credentials
   - Check if tokens are being stored properly

4. **File Upload Issues:**
   - Ensure CSV files are properly formatted
   - Check file size limits (max 10MB)

## 📊 Monitoring

- **Render Dashboard:** https://dashboard.render.com
- **Service Logs:** Available in Render Dashboard
- **Health Checks:** Automatic monitoring

## 🔄 Updates

To update your deployed application:

1. **Push changes to GitHub:**
   ```bash
   git add .
   git commit -m "Update message"
   git push origin main
   ```

2. **Render will automatically redeploy**

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

Your FraudShield application is now live on Render! Share the frontend URL with your team and start detecting fraud with AI-powered security.

### Quick Links
- **Repository:** https://github.com/Nehasaha18/FraudShieldrepo
- **Render Dashboard:** https://dashboard.render.com
- **Frontend:** https://fraudshield-frontend.onrender.com
- **Backend:** https://fraudshield-backend.onrender.com 