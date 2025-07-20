@echo off
echo 🚀 Deploying FraudShield to Railway...
echo ======================================

REM Check if Railway CLI is installed
railway --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Railway CLI not found. Installing...
    npm install -g @railway/cli
)

REM Login to Railway
echo 🔐 Logging into Railway...
railway login

REM Initialize Railway project
echo 📦 Initializing Railway project...
railway init

REM Set environment variables
echo ⚙️ Setting environment variables...
railway variables set CORS_ORIGINS="https://fraudshield-frontend.railway.app,https://fraudshield.railway.app"
railway variables set TRUSTED_HOSTS="fraudshield-backend.railway.app,fraudshield.railway.app"
railway variables set REACT_APP_API_URL="https://fraudshield-backend.railway.app"

REM Deploy the application
echo 🚀 Deploying to Railway...
railway up

echo ✅ Deployment completed!
echo 🌐 Your FraudShield application is now live at:
echo    Frontend: https://fraudshield-frontend.railway.app
echo    Backend: https://fraudshield-backend.railway.app
echo    API Docs: https://fraudshield-backend.railway.app/docs
echo.
echo 📋 Login Credentials:
echo    Central Bank: username=centralbank, password=admin123
echo    MANIT: username=manit, password=bhopal123
echo.
echo 🎉 Share these links with your team!
pause 