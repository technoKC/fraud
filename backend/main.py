from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
from dotenv import load_dotenv
import requests
import urllib.parse

# Load environment variables
load_dotenv()

# Initialize app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS Middleware
origins = [
    "http://localhost:3000",
    "https://fraud-front.onrender.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Google OAuth Constants
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = f"{os.getenv('BACKEND_URL')}/auth/google/callback"
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Step 1: Redirect to Google Auth
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
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(auth_url)

# Step 2: Google redirects back with code
@app.get("/auth/google/callback")
def google_auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Code not found")

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()

    if "access_token" not in token_json:
        return JSONResponse(status_code=400, content={"error": "Failed to retrieve access token"})

    access_token = token_json["access_token"]

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(userinfo_url, headers=headers)
    userinfo = userinfo_response.json()

    if "email" not in userinfo:
        return JSONResponse(status_code=400, content={"error": "User info not found"})

    # Optional: Create your own JWT or session here if needed

    # Auto redirect to frontend with user info
    redirect_to = f"{FRONTEND_URL}/?email={userinfo['email']}&name={userinfo['name']}"
    return RedirectResponse(redirect_to)
