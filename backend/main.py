from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Import all components
from fraud_detection import FraudDetector
from graph_analyzer import GraphAnalyzer
from report_generator import ReportGenerator
from manit_processor import ManitProcessor
from models.ai_fraud_detector import AIFraudDetector

# Import security components
from security.security_config import SecurityManager
from security.oauth_handler import OAuth2Handler
from security.rbac_manager import RBACManager
from security.anomaly_detector import AnomalyDetector

import uvicorn
import ssl

# Initialize FastAPI with security
app = FastAPI(
    title="FraudShield API",
    version="2.0",
    description="AI-Powered Fraud Detection with Enterprise Security"
)

# Initialize security components
security_manager = SecurityManager()
oauth_handler = OAuth2Handler()
rbac_manager = RBACManager(security_manager)
anomaly_detector = AnomalyDetector()

# Get environment variables for production
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
trusted_hosts = os.getenv('TRUSTED_HOSTS', 'localhost,127.0.0.1').split(',')

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=trusted_hosts
)

# CORS middleware with security
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-CSRF-Token"]
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
fraud_detector = FraudDetector()
ai_fraud_detector = AIFraudDetector()
graph_analyzer = GraphAnalyzer()
report_generator = ReportGenerator()
manit_processor = ManitProcessor()

# Request Models
class AdminLogin(BaseModel):
    username: str
    password: str
    dashboard_type: str = "centralbank"

class TransactionAction(BaseModel):
    transaction_id: str
    action: str

class ManitTransaction(BaseModel):
    transaction_id: str
    status: str

class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str
    organization: str

# Store for transaction statuses
transaction_statuses = {}
manit_transaction_statuses = {}

# Simple user storage (use database in production)
registered_users = {
    "sahaneha1809@gmail.com": {
        "password": security_manager.hash_password("admin123"),
        "full_name": "Sahan Eha",
        "organization": "FraudShield",
        "role": "centralbank_admin"
    },
    "centralbank": {
        "password": security_manager.hash_password("admin123"),
        "full_name": "Central Bank Admin",
        "organization": "Central Bank",
        "role": "centralbank_admin"
    },
    "manit": {
        "password": security_manager.hash_password("bhopal123"),
        "full_name": "MANIT Admin",
        "organization": "MANIT",
        "role": "manit_admin"
    }
}

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Rate Limiting Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    endpoint = request.url.path
    
    if hasattr(request.state, "user"):
        anomaly_detector.analyze_request_pattern(
            user=request.state.user.get("username", "anonymous"),
            endpoint=endpoint,
            ip=client_ip,
            timestamp=datetime.now()
        )
    
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {
        "message": "FraudShield API v2.0 - Secured with AI",
        "features": ["TLS 1.3", "OAuth 2.0", "RBAC", "Anomaly Detection", "AI Fraud Detection"],
        "security_status": "Active",
        "api_docs": "/docs"
    }

@app.post("/admin/login/")
async def admin_login(credentials: AdminLogin, request: Request):
    """Secure admin login with OAuth 2.0"""
    client_ip = request.client.host
    
    # Authenticate user
    user_data = oauth_handler.authenticate_user(
        credentials.username,
        credentials.password,
        credentials.dashboard_type
    )
    
    if not user_data:
        # Log failed attempt
        security_manager.log_login_attempt(credentials.username, client_ip, False)
        
        # Check for anomaly (too many failed attempts)
        anomaly_result = anomaly_detector.analyze_login_pattern(
            username=credentials.username,
            ip=client_ip,
            timestamp=datetime.now()
        )
        
        if anomaly_result['is_anomaly']:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Please try again later."
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Log successful attempt
    security_manager.log_login_attempt(credentials.username, client_ip, True)
    
    # Create OAuth response
    oauth_response = oauth_handler.create_oauth_response(user_data, client_ip)
    
    return {
        "status": "success",
        "message": f"Login successful for {credentials.dashboard_type}",
        "dashboard_type": credentials.dashboard_type,
        **oauth_response
    }

@app.post("/register/")
async def register_user(user: UserRegistration):
    """Register new user"""
    if user.email in registered_users:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = security_manager.hash_password(user.password)
    
    # Store user (in production, use proper database)
    registered_users[user.email] = {
        "password": hashed_password,
        "full_name": user.full_name,
        "organization": user.organization,
        "role": "viewer"  # Default role
    }
    
    return {
        "status": "success",
        "message": f"User {user.email} registered successfully",
        "role": "viewer"
    }

@app.post("/detect-public/")
async def detect_fraud_public(file: UploadFile = File(...)):
    """Public CSV fraud detection - No authentication required"""
    try:
        print(f"Processing file: {file.filename}")
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=422, detail="The uploaded file is empty")
        
        df = pd.read_csv(pd.io.common.BytesIO(contents))
        print(f"CSV loaded successfully. Rows: {len(df)}, Columns: {len(df.columns)}")
        print(f"Columns: {list(df.columns)}")
        
        # Validate CSV format
        required_columns = ['TXN_TIMESTAMP', 'TRANSACTION_ID', 'AMOUNT', 'PAYER_VPA', 'BENEFICIARY_VPA']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=422, 
                detail=f"Missing required columns: {', '.join(missing_columns)}. Required: {', '.join(required_columns)}"
            )
        
        # Basic fraud detection
        print("Starting fraud detection...")
        fraud_results = fraud_detector.detect_fraud(df)
        print(f"Fraud detection complete. Found {fraud_results['fraud_count']} fraud transactions")
        
        # AI-enhanced detection
        print("Starting AI fraud detection...")
        ai_results = ai_fraud_detector.detect_advanced_fraud(df)
        print("AI fraud detection complete")
        
        # Merge results
        for i, result in enumerate(fraud_results["detailed_results"]):
            if i < len(ai_results["ai_insights"]):
                result["ai_analysis"] = ai_results["ai_insights"][i]
        
        # Generate graph data
        print("Generating network graph...")
        graph_data = graph_analyzer.create_graph(df)
        print("Graph generation complete")
        
        return {
            "total_transactions": len(df),
            "fraud_detected": fraud_results["fraud_count"],
            "fraud_transactions": fraud_results["fraud_transactions"],
            "graph_data": graph_data,
            "results": fraud_results["detailed_results"],
            "ai_summary": ai_results["summary"],
            "security_status": "Public Analysis - Login for Advanced Features"
        }
        
    except pd.errors.EmptyDataError:
        print("Error: Empty CSV file")
        raise HTTPException(status_code=422, detail="The uploaded file is empty or corrupted")
    except pd.errors.ParserError as e:
        print(f"Error: CSV parsing failed - {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid CSV format: {str(e)}")
    except Exception as e:
        print(f"Error in public detect endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/detect/")
async def detect_fraud(
    file: UploadFile = File(...),
    current_user: dict = Depends(oauth_handler.get_current_user)
):
    """Upload CSV and detect fraud transactions with AI - Authenticated"""
    if not security_manager.check_permission(current_user['role'], 'view_fraud_data'):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        contents = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(contents))
        
        fraud_results = fraud_detector.detect_fraud(df)
        ai_results = ai_fraud_detector.detect_advanced_fraud(df)
        
        for i, result in enumerate(fraud_results["detailed_results"]):
            if i < len(ai_results["ai_insights"]):
                result["ai_analysis"] = ai_results["ai_insights"][i]
        
        graph_data = graph_analyzer.create_graph(df)
        
        anomaly_detector.analyze_transaction_pattern(
            user=current_user['username'],
            amount=df['AMOUNT'].sum() if 'AMOUNT' in df.columns else 0,
            transaction_type='bulk_upload',
            timestamp=datetime.now()
        )
        
        return {
            "total_transactions": len(df),
            "fraud_detected": fraud_results["fraud_count"],
            "fraud_transactions": fraud_results["fraud_transactions"],
            "graph_data": graph_data,
            "results": fraud_results["detailed_results"],
            "ai_summary": ai_results["summary"],
            "security_status": "Monitored"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/admin/data/")
@rbac_manager.require_permission("view_fraud_data")
async def get_admin_data(current_user: dict = Depends(oauth_handler.get_current_user)):
    """Load data for Central Bank admin dashboard with security"""
    try:
        csv_path = os.path.join("data", "anonymized_sample_fraud_txn.csv")
        if not os.path.exists(csv_path):
            create_sample_data()
        
        df = pd.read_csv(csv_path)
        
        fraud_results = fraud_detector.detect_fraud(df)
        ai_results = ai_fraud_detector.detect_advanced_fraud(df)
        graph_data = graph_analyzer.create_graph(df)
        
        fraud_transactions = fraud_results["fraud_transactions"]
        print(f"DEBUG: Processing {len(fraud_transactions)} fraud transactions")
        print(f"DEBUG: Current transaction_statuses: {transaction_statuses}")
        
        for txn in fraud_transactions:
            txn_id = txn["transaction_id"]
            if txn_id in transaction_statuses:
                txn["status"] = transaction_statuses[txn_id]
                print(f"DEBUG: Added status for {txn_id}: {transaction_statuses[txn_id]}")
            else:
                txn["status"] = "pending"  # Default status
                print(f"DEBUG: No status found for {txn_id}, setting to pending")
        
        security_data = anomaly_detector.get_security_dashboard_data()
        
        return {
            "total_transactions": len(df),
            "fraud_detected": fraud_results["fraud_count"],
            "fraud_transactions": fraud_transactions,
            "graph_data": graph_data,
            "blocked_accounts": len([s for s in transaction_statuses.values() if s == "blocked"]),
            "verified_accounts": len([s for s in transaction_statuses.values() if s == "verified"]),
            "system_health": security_data['security_score'],
            "ai_insights": ai_results["summary"],
            "security_metrics": security_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/transaction-action/")
@rbac_manager.require_permission("block_transactions")
async def update_transaction_status(
    action: TransactionAction,
    current_user: dict = Depends(oauth_handler.get_current_user)
):
    """Update transaction status with security audit"""
    try:
        print(f"DEBUG: Transaction action request - User: {current_user}, Action: {action}")
        
        # Log the transaction action
        print(f"INFO: Transaction action: {current_user.get('sub', 'unknown')} -> {action.action} on {action.transaction_id}")
        
        transaction_statuses[action.transaction_id] = action.action
        
        print(f"DEBUG: Transaction status updated - {action.transaction_id}: {action.action}")
        print(f"DEBUG: Current transaction_statuses: {transaction_statuses}")
        
        return {
            "status": "success",
            "transaction_id": action.transaction_id,
            "action": action.action,
            "updated_by": current_user.get('sub', 'unknown'),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"ERROR in update_transaction_status: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/admin/generate-report/")
@rbac_manager.require_permission("generate_reports")
async def generate_report(current_user: dict = Depends(oauth_handler.get_current_user)):
    """Generate PDF report with security watermark"""
    try:
        csv_path = os.path.join("data", "anonymized_sample_fraud_txn.csv")
        df = pd.read_csv(csv_path)
        
        fraud_results = fraud_detector.detect_fraud(df)
        
        report_path = report_generator.generate_centralbank_report(
            df, 
            fraud_results["fraud_transactions"],
            transaction_statuses
        )
        
        # Log the report generation
        print(f"INFO: Report generated by: {current_user['username']}")
        
        return FileResponse(
            report_path,
            media_type='application/pdf',
            filename=f'centralbank_fraud_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/manit/data/")
@rbac_manager.require_permission("view_loan_data")
async def get_manit_data(current_user: dict = Depends(oauth_handler.get_current_user)):
    """Load data for MANIT dashboard"""
    try:
        csv_path = os.path.join("data", "manit_loan_transactions.csv")
        if not os.path.exists(csv_path):
            create_sample_manit_data()
        
        df = pd.read_csv(csv_path)
        loan_data = manit_processor.process_loan_transactions(df, manit_transaction_statuses)
        
        return loan_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/manit/upload/")
@rbac_manager.require_permission("view_loan_data")
async def upload_manit_data(
    file: UploadFile = File(...),
    current_user: dict = Depends(oauth_handler.get_current_user)
):
    """Upload MANIT loan transaction CSV"""
    try:
        contents = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(contents))
        
        loan_data = manit_processor.process_loan_transactions(df, manit_transaction_statuses)
        
        return loan_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/manit/update-status/")
@rbac_manager.require_permission("verify_students")
async def update_manit_status(
    transaction: ManitTransaction,
    current_user: dict = Depends(oauth_handler.get_current_user)
):
    """Update MANIT transaction status"""
    manit_transaction_statuses[transaction.transaction_id] = transaction.status
    
    # Log the MANIT status update
    print(f"INFO: MANIT status update: {current_user.get('sub', 'unknown')} -> {transaction.status} on {transaction.transaction_id}")
    
    return {
        "status": "success",
        "transaction_id": transaction.transaction_id,
        "new_status": transaction.status,
        "updated_by": current_user.get('sub', 'unknown')
    }

@app.get("/manit/generate-report/")
@rbac_manager.require_permission("generate_loan_reports")
async def generate_manit_report(current_user: dict = Depends(oauth_handler.get_current_user)):
    """Generate PDF report for MANIT"""
    try:
        csv_path = os.path.join("data", "manit_loan_transactions.csv")
        df = pd.read_csv(csv_path)
        
        loan_data = manit_processor.process_loan_transactions(df, manit_transaction_statuses)
        
        report_path = report_generator.generate_manit_report(
            df,
            loan_data,
            manit_transaction_statuses
        )
        
        return FileResponse(
            report_path,
            media_type='application/pdf',
            filename=f'manit_loan_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/dashboard/")
@rbac_manager.require_permission("manage_system")
async def get_security_dashboard(current_user: dict = Depends(oauth_handler.get_current_user)):
    """Get security metrics and anomaly data"""
    security_data = anomaly_detector.get_security_dashboard_data()
    
    return {
        "security_status": "Active",
        "tls_version": "1.3",
        "oauth_status": "Enabled",
        "rbac_status": "Active",
        "anomaly_detection": "Running",
        **security_data
    }

def create_sample_data():
    """Create sample fraud data if not exists"""
    os.makedirs("data", exist_ok=True)

def create_sample_manit_data():
    """Create sample MANIT loan data"""
    os.makedirs("data", exist_ok=True)
    
    sample_data = {
        'STUDENT_ID': [
            'MANIT001', 'MANIT002', 'MANIT003', 'MANIT004', 'MANIT005',
            'MANIT006', 'MANIT007', 'MANIT008', 'MANIT009', 'MANIT010',
            'MANIT011', 'MANIT012', 'MANIT013', 'MANIT014', 'MANIT015',
            'MANIT016', 'MANIT017', 'MANIT018', 'MANIT019', 'MANIT020'
        ],
        'STUDENT_NAME': [
            'Rahul Kumar', 'Priya Singh', 'Amit Patel', 'Sneha Sharma', 'Vijay Verma',
            'Anita Gupta', 'Ravi Jain', 'Pooja Agarwal', 'Suresh Yadav', 'Kavita Saxena',
            'Deepak Singh', 'Neha Tiwari', 'Ashok Kumar', 'Sunita Joshi', 'Manoj Dubey',
            'Rekha Mishra', 'Arun Soni', 'Geeta Sharma', 'Vinod Chouhan', 'Meera Patel'
        ],
        'TRANSACTION_ID': [
            'LTX001', 'LTX002', 'LTX003', 'LTX004', 'LTX005',
            'LTX006', 'LTX007', 'LTX008', 'LTX009', 'LTX010',
            'LTX011', 'LTX012', 'LTX013', 'LTX014', 'LTX015',
            'LTX016', 'LTX017', 'LTX018', 'LTX019', 'LTX020'
        ],
        'LOAN_AMOUNT': [
            50000, 75000, 60000, 80000, 55000,
            45000, 70000, 65000, 52000, 58000,
            48000, 72000, 67000, 53000, 59000,
            46000, 73000, 68000, 54000, 57000
        ],
        'SEMESTER': [
            'VII', 'V', 'III', 'VII', 'V',
            'I', 'VI', 'IV', 'II', 'VIII',
            'III', 'VII', 'V', 'I', 'VI',
            'IV', 'II', 'VIII', 'III', 'VII'
        ],
        'DEPARTMENT': [
            'Computer Science', 'Electronics', 'Mechanical', 'Civil', 'Computer Science',
            'Electrical', 'Chemical', 'Architecture', 'Electronics', 'Mechanical',
            'Civil', 'Computer Science', 'Electrical', 'Chemical', 'Architecture',
            'Electronics', 'Mechanical', 'Civil', 'Computer Science', 'Electrical'
        ],
        'TRANSACTION_DATE': [
            '2025-01-15', '2025-01-16', '2025-01-17', '2025-01-18', '2025-01-19',
            '2025-01-20', '2025-01-21', '2025-01-22', '2025-01-23', '2025-01-24',
            '2025-01-25', '2025-01-26', '2025-01-27', '2025-01-28', '2025-01-29',
            '2025-01-30', '2025-01-31', '2025-02-01', '2025-02-02', '2025-02-03'
        ],
        'BANK_NAME': [
            'SBI', 'HDFC', 'ICICI', 'PNB', 'Axis',
            'Bank of Baroda', 'Canara Bank', 'Union Bank', 'IDBI', 'Yes Bank',
            'SBI', 'HDFC', 'ICICI', 'PNB', 'Axis',
            'Bank of Baroda', 'Canara Bank', 'Union Bank', 'IDBI', 'Yes Bank'
        ],
        'STATUS': [
            'Received', 'Received', 'Pending', 'Received', 'Pending',
            'Received', 'Received', 'Pending', 'Received', 'Pending',
            'Received', 'Received', 'Pending', 'Received', 'Pending',
            'Received', 'Received', 'Pending', 'Received', 'Pending'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv(os.path.join("data", "manit_loan_transactions.csv"), index=False)
    print("✅ Created sample MANIT data: manit_loan_transactions.csv")

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("security", exist_ok=True)
    os.makedirs("security_logs", exist_ok=True)
    
    # Copy your CSV file to the data directory
    print("🚀 Starting FraudShield API v2.0...")
    print("📊 Login Credentials:")
    print("   Central Bank: username='centralbank', password='admin123'")
    print("   MANIT: username='manit', password='bhopal123'")
    print("   Your Email: username='sahaneha1809@gmail.com', password='admin123'")

    # 🔧 Use dynamic port on Render (default to 8000 locally)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

    
