#!/bin/bash

echo "🚀 Deploying FraudShield to Railway..."
echo "======================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Initialize Railway project
echo "📦 Initializing Railway project..."
railway init

# Set environment variables
echo "⚙️ Setting environment variables..."
railway variables set CORS_ORIGINS="https://fraudshield-frontend.railway.app,https://fraudshield.railway.app"
railway variables set TRUSTED_HOSTS="fraudshield-backend.railway.app,fraudshield.railway.app"
railway variables set REACT_APP_API_URL="https://fraudshield-backend.railway.app"

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

# Get the deployment URL
echo "🔗 Getting deployment URL..."
DEPLOY_URL=$(railway status --json | jq -r '.url')

echo "✅ Deployment completed!"
echo "🌐 Your FraudShield application is now live at:"
echo "   Frontend: https://fraudshield-frontend.railway.app"
echo "   Backend: https://fraudshield-backend.railway.app"
echo "   API Docs: https://fraudshield-backend.railway.app/docs"
echo ""
echo "📋 Login Credentials:"
echo "   Central Bank: username=centralbank, password=admin123"
echo "   MANIT: username=manit, password=bhopal123"
echo ""
echo "🎉 Share these links with your team!" 