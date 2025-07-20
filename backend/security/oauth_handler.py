import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import jwt
from passlib.context import CryptContext
import ssl
import logging
from functools import wraps
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security Configuration
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security_scheme = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create security logs directory if not exists
os.makedirs('security_logs', exist_ok=True)

# Logging configuration for anomaly detection
logging.basicConfig(
    filename='security_logs/anomaly_detection.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
security_logger = logging.getLogger('security')

class SecurityManager:
    """AI-powered Security Manager implementing TLS 1.3, OAuth 2.0, RBAC, and Anomaly Detection"""
    
    def __init__(self):
        self.failed_login_attempts = {}
        self.anomaly_threshold = 5
        self.session_tokens = {}
        self.roles_permissions = {
            'centralbank_admin': [
                'view_fraud_data',
                'block_transactions',
                'verify_transactions',
                'generate_reports',
                'view_ai_insights',
                'manage_system'
            ],
            'manit_admin': [
                'view_loan_data',
                'verify_students',
                'generate_loan_reports',
                'manage_departments'
            ],
            'viewer': [
                'view_data',
                'download_reports'
            ]
        }
    
    # Hashing Functions
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    # OAuth 2.0 Implementation
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # Store token for session management
        user = data.get('sub')
        self.session_tokens[user] = {
            'token': encoded_jwt,
            'expires': expire,
            'ip': data.get('ip_address')
        }
        
        # Log token creation
        security_logger.info(f"Access token created for user: {user} from IP: {data.get('ip_address')}")
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            
            # Check if token is still in active sessions
            if username in self.session_tokens:
                stored_token = self.session_tokens[username]['token']
                if stored_token == token:
                    return payload
            
            return None
        except jwt.ExpiredSignatureError:
            security_logger.warning("Expired token verification attempt")
            return None
        except jwt.PyJWTError:
            security_logger.warning("Invalid token verification attempt")
            return None
    
    # RBAC (Role-Based Access Control)
    def check_permission(self, user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission"""
        permissions = self.roles_permissions.get(user_role, [])
        has_permission = required_permission in permissions
        
        if not has_permission:
            security_logger.warning(f"Permission denied: {user_role} attempted to access {required_permission}")
        
        return has_permission
    
    def get_user_permissions(self, user_role: str) -> list:
        """Get all permissions for a user role"""
        return self.roles_permissions.get(user_role, [])
    
    # Anomaly Detection
    def log_login_attempt(self, username: str, ip_address: str, success: bool):
        """Log login attempt for anomaly detection"""
        timestamp = datetime.utcnow()
        
        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = []
        
        if not success:
            self.failed_login_attempts[username].append({
                'timestamp': timestamp,
                'ip': ip_address
            })
            
            # Check for anomalies
            recent_failures = [
                attempt for attempt in self.failed_login_attempts[username]
                if (timestamp - attempt['timestamp']).seconds < 300  # 5 minutes
            ]
            
            if len(recent_failures) >= self.anomaly_threshold:
                security_logger.critical(
                    f"ANOMALY DETECTED: Multiple failed login attempts for {username} from {ip_address}"
                )
                return False  # Block further attempts
        else:
            # Clear failed attempts on successful login
            self.failed_login_attempts[username] = []
            security_logger.info(f"Successful login: {username} from {ip_address}")
        
        return True
    
    def check_request_anomaly(self, user: str, endpoint: str, ip_address: str) -> bool:
        """Check for anomalous request patterns"""
        # Implement AI-based anomaly detection logic
        # For now, basic rate limiting and pattern detection
        
        current_time = datetime.utcnow()
        
        # Log the request
        security_logger.info(f"Request: {user} -> {endpoint} from {ip_address}")
        
        # Check for suspicious patterns
        if endpoint in ['/admin/delete-all', '/admin/export-all-data']:
            security_logger.warning(f"Sensitive endpoint accessed: {endpoint} by {user}")
            return False
        
        return True
    
    # TLS 1.3 Configuration
    def get_tls_context(self):
        """Get TLS 1.3 context for secure connections"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # Load certificates if available
        cert_file = os.getenv('TLS_CERT_FILE')
        key_file = os.getenv('TLS_KEY_FILE')
        
        if cert_file and key_file and os.path.exists(cert_file) and os.path.exists(key_file):
            context.load_cert_chain(cert_file, key_file)
        
        return context
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        return hashlib.sha256(f"{session_id}{SECRET_KEY}".encode()).hexdigest()
    
    def verify_csrf_token(self, session_id: str, token: str) -> bool:
        """Verify CSRF token"""
        expected_token = self.generate_csrf_token(session_id)
        return secrets.compare_digest(expected_token, token)

class OAuth2Handler:
    """OAuth 2.0 Handler - wrapper around SecurityManager for OAuth operations"""
    
    def __init__(self):
        self.security_manager = SecurityManager()
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create OAuth 2.0 access token"""
        return self.security_manager.create_access_token(data, expires_delta)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify OAuth 2.0 token"""
        return self.security_manager.verify_token(token)
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return self.security_manager.hash_password(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return self.security_manager.verify_password(plain_password, hashed_password)
    
    def check_permission(self, user_role: str, required_permission: str) -> bool:
        """Check user permissions"""
        return self.security_manager.check_permission(user_role, required_permission)
    
    def log_login_attempt(self, username: str, ip_address: str, success: bool):
        """Log login attempt"""
        return self.security_manager.log_login_attempt(username, ip_address, success)
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
        """Get current user from JWT token"""
        token = credentials.credentials
        payload = self.verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    
    def authenticate_user(self, username: str, password: str, dashboard_type: str):
        """Authenticate user credentials"""
        # Default credentials for demo
        valid_credentials = {
            'centralbank': {'username': 'centralbank', 'password': 'admin123', 'role': 'centralbank_admin'},
            'manit': {'username': 'manit', 'password': 'bhopal123', 'role': 'manit_admin'},
            'sahaneha1809@gmail.com': {'username': 'sahaneha1809@gmail.com', 'password': 'admin123', 'role': 'centralbank_admin'}
        }
        
        if username in valid_credentials:
            creds = valid_credentials[username]
            if password == creds['password']:
                return {
                    'username': username,
                    'role': creds['role'],
                    'dashboard_type': dashboard_type
                }
        
        return None
    
    def create_oauth_response(self, user_data: dict, client_ip: str):
        """Create OAuth response with token"""
        token_data = {
            'sub': user_data['username'],
            'role': user_data['role'],
            'dashboard_type': user_data['dashboard_type'],
            'ip_address': client_ip
        }
        
        access_token = self.create_access_token(token_data)
        
        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'user': user_data
        }