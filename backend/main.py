# main.py

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import json
import os
import ssl
from dotenv import load_dotenv
from datetime import datetime
import requests
import urllib.parse
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# ========== Security + Modules ==========
from fraud_detection import FraudDetector
from graph_analyzer import GraphAnalyzer
from report_generator import ReportGenerator
from manit_processor import ManitProcessor
from models.ai_fraud_detector import AIFraudDetector
from security.security_config import SecurityManager
from security.oauth_handler import OAuth2Handler
from security.rbac_manager import RBACManager
from security.anomaly_detector import AnomalyDetector

# ========== App Initialization ==========
app = FastAPI(
    title="FraudShield API",
    version="2.0",
    description="Secure AI-Powered Anti-Fraud System"
)

# ========= Middleware ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1,fraud-front.onrender.com,fraud-shield-back.onrender.com,::1").split(",")
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    if hasattr(request.state, "user"):
        anomaly_detector.analyze_request_pattern(
            user=request.state.user.get("username", "anonymous"),
            endpoint=request.url.path,
            ip=client_ip,
            timestamp=datetime.now()
        )
    return await call_next(request)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== Global Components ==========
fraud_detector = FraudDetector()
ai_fraud_detector = AIFraudDetector()
graph_analyzer = GraphAnalyzer()
report_generator = ReportGenerator()
manit_processor = ManitProcessor()

security_manager = SecurityManager()
oauth_handler = OAuth2Handler()
rbac_manager = RBACManager(security_manager)
anomaly_detector = AnomalyDetector()

# ========== In-Memory Storage (Prototype Only) ==========
transaction_statuses = {}
manit_transaction_statuses = {}
registered_users = {
    "centralbank": {
        "password": security_manager.hash_password("admin123"),
        "full_name": "Central Admin",
        "role": "centralbank_admin",
        "organization": "Central Bank"
    },
    "manit": {
        "password": security_manager.hash_password("bhopal123"),
        "full_name": "MANIT Admin",
        "role": "manit_admin",
        "organization": "MANIT"
    }
}

# ========= Google OAuth ==========
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
REDIRECT_URI = f"{BACKEND_URL}/auth/google/callback"

@app.get("/auth/google/login")
def login_via_google():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    return RedirectResponse("https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params))

@app.get("/auth/google/callback")
def google_auth_callback(request: Request):
    try:
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Missing auth code")

        # Step 1: Exchange code for token
        token_response = requests.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        })
        tokens = token_response.json()

        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to retrieve access token")

        # Step 2: Get user info
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo = userinfo_response.json()

        if "email" not in userinfo:
            raise HTTPException(status_code=400, detail="User info not found")

        email = userinfo["email"]
        name = userinfo.get("name", "OAuth User")

        # Step 3: Register user (if not exists)
        if email not in registered_users:
            registered_users[email] = {
                "password": "oauth_user",
                "full_name": name,
                "organization": "OAuth",
                "role": "viewer",
                "dashboard_type": "basic"
            }

        # Step 4: Create JWT token using existing handler
        token_data = oauth_handler.create_oauth_response(
            {"username": email, **registered_users[email]},
            request.client.host
        )

        jwt_token = token_data.get("access_token")
        if not jwt_token:
            raise HTTPException(status_code=500, detail="Failed to generate JWT token")

        # Step 5: Redirect to frontend with token
        redirect_url = f"{FRONTEND_URL}/?token={jwt_token}&name={name}&email={email}"
        return RedirectResponse(redirect_url)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ========== Models ==========
class AdminLogin(BaseModel):
    username: str
    password: str
    dashboard_type: str = "centralbank"

class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str
    organization: str

class TransactionAction(BaseModel):
    transaction_id: str
    action: str

class ManitTransaction(BaseModel):
    transaction_id: str
    status: str

# ========== Routes ==========
@app.get("/")
def root():
    return {"message": "FraudShield API v2.0 - Secured", "docs": "/docs"}

@app.post("/admin/login/")
def login_admin(credentials: AdminLogin, request: Request):
    client_ip = request.client.host
    user_info = oauth_handler.authenticate_user(credentials.username, credentials.password, credentials.dashboard_type)

    if not user_info:
        anomaly_result = anomaly_detector.analyze_login_pattern(
            username=credentials.username, ip=client_ip, timestamp=datetime.now()
        )
        if anomaly_result.get('is_anomaly'):
            raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = oauth_handler.create_oauth_response(user_info, client_ip)
    return {"status": "success", "dashboard_type": credentials.dashboard_type, **token_data}

@app.post("/register/")
def register(user: UserRegistration):
    if user.email in registered_users:
        raise HTTPException(status_code=400, detail="User already exists")
    registered_users[user.email] = {
        "password": security_manager.hash_password(user.password),
        "full_name": user.full_name,
        "organization": user.organization,
        "role": "viewer"
    }
    return {"status": "success", "role": "viewer"}

@app.post("/detect-public/")
async def public_detect(file: UploadFile = File(...)):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    df = pd.read_csv(pd.io.common.BytesIO(contents))
    fraud_results = fraud_detector.detect_fraud(df)
    ai_results = ai_fraud_detector.detect_advanced_fraud(df)
    for i, item in enumerate(fraud_results["detailed_results"]):
        item["ai_analysis"] = ai_results["ai_insights"][i] if i < len(ai_results["ai_insights"]) else {}

    graph_data = graph_analyzer.create_graph(df)
    return {
        "total_transactions": len(df),
        "fraud_count": fraud_results["fraud_count"],
        "graph_data": graph_data,
        "results": fraud_results["detailed_results"],
        "ai_summary": ai_results["summary"]
    }

@app.post("/detect/")
async def secure_detect(
    file: UploadFile = File(...),
    current_user: dict = Depends(oauth_handler.get_current_user)
):
    df = pd.read_csv(pd.io.common.BytesIO(await file.read()))
    fraud_results = fraud_detector.detect_fraud(df)
    ai_results = ai_fraud_detector.detect_advanced_fraud(df)
    for i, item in enumerate(fraud_results["detailed_results"]):
        item["ai_analysis"] = ai_results["ai_insights"][i]
    graph_data = graph_analyzer.create_graph(df)
    return {
        "total": len(df),
        "fraud": fraud_results["fraud_count"],
        "graph_data": graph_data,
        "ai_summary": ai_results["summary"],
        "results": fraud_results["detailed_results"]
    }

@app.get("/manit/data/")
@rbac_manager.require_permission("view_loan_data")
async def load_manit_data(current_user: dict = Depends(oauth_handler.get_current_user)):
    path = os.path.join("data", "manit_loan_transactions.csv")
    if not os.path.exists(path): create_sample_manit_data()
    df = pd.read_csv(path)
    return manit_processor.process_loan_transactions(df, manit_transaction_statuses)

@app.post("/manit/upload/")
@rbac_manager.require_permission("view_loan_data")
async def upload_manit_data(file: UploadFile = File(...), current_user: dict = Depends(oauth_handler.get_current_user)):
    df = pd.read_csv(pd.io.common.BytesIO(await file.read()))
    return manit_processor.process_loan_transactions(df, manit_transaction_statuses)

@app.post("/manit/update-status/")
@rbac_manager.require_permission("verify_students")
async def update_manit_txn(transaction: ManitTransaction, current_user: dict = Depends(oauth_handler.get_current_user)):
    manit_transaction_statuses[transaction.transaction_id] = transaction.status
    return {"status": "success", "transaction": transaction.transaction_id, "updated_by": current_user["username"]}

@app.get("/admin/generate-report/")
@rbac_manager.require_permission("generate_reports")
async def generate_pdf(current_user: dict = Depends(oauth_handler.get_current_user)):
    df = pd.read_csv(os.path.join("data", "anonymized_sample_fraud_txn.csv"))
    fraud = fraud_detector.detect_fraud(df)["fraud_transactions"]
    pdf = report_generator.generate_centralbank_report(df, fraud, transaction_statuses)
    return FileResponse(pdf, media_type="application/pdf", filename="centralbank_report.pdf")

@app.get("/manit/generate-report/")
@rbac_manager.require_permission("generate_loan_reports")
async def generate_manit_pdf(current_user: dict = Depends(oauth_handler.get_current_user)):
    df = pd.read_csv(os.path.join("data", "manit_loan_transactions.csv"))
    loans = manit_processor.process_loan_transactions(df, manit_transaction_statuses)
    pdf = report_generator.generate_manit_report(df, loans, manit_transaction_statuses)
    return FileResponse(pdf, media_type="application/pdf", filename="manit_report.pdf")

@app.get("/security/dashboard/")
@rbac_manager.require_permission("manage_system")
async def security_dashboard(current_user: dict = Depends(oauth_handler.get_current_user)):
    return {
        "security": "Active",
        "tls": "1.3",
        "rbac": "Enabled",
        **anomaly_detector.get_security_dashboard_data()
    }

# ========== Sample Data Generator ==========
def create_sample_manit_data():
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame({
        "STUDENT_ID": ["MANIT001", "MANIT002"],
        "STUDENT_NAME": ["Alice", "Bob"],
        "TRANSACTION_ID": ["LTX001", "LTX002"],
        "LOAN_AMOUNT": [50000, 60000],
        "SEMESTER": ["VII", "V"],
        "DEPARTMENT": ["CSE", "ECE"],
        "TRANSACTION_DATE": ["2025-01-15", "2025-01-16"],
        "BANK_NAME": ["SBI", "HDFC"],
        "STATUS": ["Received", "Pending"]
    })
    df.to_csv(os.path.join("data", "manit_loan_transactions.csv"), index=False)

# ========== Entry Point ==========
if __name__ == "__main__":
    import uvicorn
    os.makedirs("static", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    port = int(os.environ.get("PORT", 8000))
    print("▶️  FraudShield v2.0 is running...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
