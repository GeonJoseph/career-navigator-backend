from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Security, Query, Request, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
import httpx
import os
import io
import PyPDF2
import re
import secrets
import smtplib
from email.message import EmailMessage
from datetime import timedelta, datetime, timezone
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# AI & LangChain Integrations
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Local Modules
from security import hash_password, verify_password
from database import engine, SessionLocal
from models import Base, User, Bookmark, ResumeAnalysis  # 👈 Explicitly imported models
from jose import jwt, JWTError
from auth import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM
from services.jsearch_service import search_jobs, search_internships
from services.course_service import search_courses

# Chatbot Services
from services.chatbot.controller import process_input
from services.chatbot.state import create_initial_state
from services.chatbot.model import load_model
from dependencies import get_current_user, get_db
from services.chatbot.data_loader import load_nodes

from routes import bookmarks

# Initialize FastAPI App Instance
app = FastAPI()

# Include Routers
app.include_router(bookmarks.router)

# Simple in-memory state for conversational system
user_states = {}

# Force Database Table Synchronization
Base.metadata.create_all(bind=engine)

# Rate Limiter Configurations
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Cross-Origin Resource Sharing Rules
FRONTEND_URL = os.getenv("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
         FRONTEND_URL,
        

    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load heavy core assets into memory globally once on startup
nodes = load_nodes()
model = load_model()


def is_profile_complete(user: User):
    return all([
        user.first_name,
        user.last_name,
        user.user_type,
        user.skills
    ])

# ────────────────────────────────────────────────────────────────
# PYDANTIC VALIDATION AND ROUTE SCHEMAS
# ────────────────────────────────────────────────────────────────

class MetricScore(BaseModel):
    score: int
    feedback: str

class ResumeAnalysisResponse(BaseModel):
    overall_score: int
    impact_metrics: MetricScore
    formatting_structure: MetricScore
    skills_density: MetricScore
    strengths: List[str]
    improvements: List[str]

class ChatRequest(BaseModel):
    user_id: str
    message: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email_tld(cls, v):
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError('Invalid email format. Must be a valid TLD-based email address.')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError('Password must contain at least one special character')
        return v

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError('Password must contain at least one special character')
        return v

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str
    remember_me: bool = False

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class UpdateRoleRequest(BaseModel):
    role: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError('Password must contain at least one special character')
        return v

class ProfileResponse(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    profile_photo: Optional[str]
    name: str
    user_type: Optional[str]
    document_filename: Optional[str]
    skills: Optional[str]
    dob: Optional[str]
    location: Optional[str]
    interests: Optional[str]
    marks: Optional[list]
    is_profile_complete: bool

# ────────────────────────────────────────────────────────────────
# BASE AND AUTH ROUTING CONTROLLERS
# ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Backend running"}

@app.post("/chat")
def chat(req: ChatRequest):
    if req.user_id not in user_states:
        user_states[req.user_id] = create_initial_state()
    state = user_states[req.user_id]
    response = process_input(req.message, state, nodes, model)
    return {"response": response}

def send_verification_email(receiver_email: str, otp: str):
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    
    if not sender_email or not sender_password:
        print(f"\n[EMAIL SIMULATION] Sent to: {receiver_email}")
        print(f"Subject: Verify your Career Navigator account")
        print(f"OTP: {otp}\n")
        return
        
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Verify your Career Navigator account'
        msg['From'] = f"Career Navigator <{sender_email}>"
        msg['To'] = receiver_email
        msg.set_content(f"Welcome to Career Navigator!\n\nYour 6-digit verification code is: {otp}\n\nBest regards,\nThe Career Navigator Team")
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Successfully sent verification email to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {e}")

def send_welcome_email(receiver_email: str):
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    
    if not sender_email or not sender_password:
        print(f"\n[EMAIL SIMULATION] Sent to: {receiver_email}")
        print(f"Subject: Registration Successful")
        print(f"Body: Welcome to Career Navigator! Your registration is complete.\n")
        return
        
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Welcome to Career Navigator!'
        msg['From'] = f"Career Navigator <{sender_email}>"
        msg['To'] = receiver_email
        msg.set_content(f"Dear User,\n\nYour registration is successfully completed. Welcome to Career Navigator!\n\nBest regards,\nThe Career Navigator Team")
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Successfully sent welcome email to {receiver_email}")
    except Exception as e:
        print(f"Failed to send welcome email to {receiver_email}: {e}")

@app.post("/register")
def register(request: RegisterRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(request.password)
    otp = '%06d' % secrets.randbelow(1000000)

    new_user = User(
        name=request.name,
        email=request.email,
        hashed_password=hashed_pw,
        is_verified=False,
        verification_code=otp
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    background_tasks.add_task(send_verification_email, new_user.email, otp)
    return {"message": "Verification required", "email": new_user.email}

@app.post("/verify-email")
def verify_email(request: VerifyEmailRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.verification_code or user.verification_code != request.otp:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user.is_verified = True
    user.verification_code = None
    background_tasks.add_task(send_welcome_email, user.email)

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    expires_delta = timedelta(days=30) if request.remember_me else timedelta(days=1)
    refresh_token = create_refresh_token({"sub": str(user.id)}, expires_delta=expires_delta)

    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "profile_completed": is_profile_complete(user)
    }

@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, login_req: LoginRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_req.email).first()

    if not user or not verify_password(login_req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not user.is_verified:
        otp = '%06d' % secrets.randbelow(1000000)
        user.verification_code = otp
        db.commit()
        background_tasks.add_task(send_verification_email, user.email, otp)
        return {"message": "Verification Required", "email": user.email}

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    expires_delta = timedelta(days=30) if login_req.remember_me else timedelta(days=1)
    refresh_token = create_refresh_token({"sub": str(user.id)}, expires_delta=expires_delta)
    
    user.refresh_token = refresh_token
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "profile_completed": is_profile_complete(user)
    }

@app.post("/refresh")
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or user.refresh_token != request.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "profile_completed": is_profile_complete(user)
    }

@app.post("/logout")
def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or user.refresh_token != request.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user.refresh_token = None
    db.commit()
    return {"message": "Logged out successfully"}

def send_reset_password_email(receiver_email: str, token: str):
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    
    if not sender_email or not sender_password:
        print(f"\n[EMAIL SIMULATION] Sent to: {receiver_email}")
        print(f"Subject: Reset your password")
        print(f"Token: {token}\n")
        return
        
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Reset your Career Navigator password'
        msg['From'] = f"Career Navigator <{sender_email}>"
        msg['To'] = receiver_email
        FRONTEND_URL = os.getenv("FRONTEND_URL")

        reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
        msg.set_content(f"Hello,\n\nYou requested to reset your password. Click the link below to set a new password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email.")
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Successfully sent password reset email to {receiver_email}")
    except Exception as e:
        print(f"Failed to send reset email to {receiver_email}: {e}")

@app.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, forgot_req: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == forgot_req.email).first()
    if user:
        reset_token = secrets.token_urlsafe(32)
        user.reset_password_token = reset_token
        user.reset_password_expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        db.commit()
        background_tasks.add_task(send_reset_password_email, user.email, reset_token)
    return {"message": "If that email exists, a reset link has been sent."}

@app.post("/reset-password")
@limiter.limit("3/minute")
def reset_password(request: Request, reset_req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_password_token == reset_req.token).first()
    if not user or not user.reset_password_expire:
        raise HTTPException(status_code=400, detail="Invalid token")
        
    now = datetime.now(timezone.utc)
    if user.reset_password_expire.tzinfo is None:
        now = datetime.utcnow()
        
    if now > user.reset_password_expire:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user.hashed_password = hash_password(reset_req.new_password)
    user.reset_password_token = None
    user.reset_password_expire = None
    user.refresh_token = None
    db.commit()
    return {"message": "Password successfully reset."}

@app.get("/me")
def read_current_user(current_user: User = Security(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }

@app.get("/admin/users")
def get_all_users(current_user: User = Security(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "status": "Active" if u.refresh_token else "Inactive",
            "joined": u.created_at.strftime("%Y-%m-%d")
        } for u in users
    ]

@app.patch("/admin/users/{user_id}")
def update_user_role(user_id: int, request: UpdateRoleRequest, current_user: User = Security(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if request.role not in ["User", "Admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user.role = request.role
    db.commit()
    return {"message": "Role updated successfully"}

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, current_user: User = Security(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

import urllib.parse

# ────────────────────────────────────────────────────────────────
# THIRD-PARTY SOCIAL OAUTH2 INTEGRATIONS
# ────────────────────────────────────────────────────────────────

@app.get("/auth/google/login")
def google_login():
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    if not GOOGLE_CLIENT_ID:
        FRONTEND_URL = os.getenv("FRONTEND_URL")
        return RedirectResponse(
                url=f"{FRONTEND_URL}/auth/callback?error=missing_google_credentials"
        )




        
    BACKEND_URL = os.getenv("BACKEND_URL")
    redirect_uri = f"{BACKEND_URL}/auth/google/callback"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return RedirectResponse(url=url)

@app.get("/auth/google/callback")
async def google_callback(code: str = None, error: str = None, db: Session = Depends(get_db)):
    if error or not code:
        FRONTEND_URL = os.getenv("FRONTEND_URL")
        return RedirectResponse(
                url=f"{FRONTEND_URL}/auth/callback?error=auth_failed"
        )





    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    BACKEND_URL = os.getenv("BACKEND_URL")
    redirect_uri = f"{BACKEND_URL}/auth/google/callback"

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
        )
        token_data = token_res.json()
        google_access_token = token_data.get("access_token")

        if not google_access_token:
            FRONTEND_URL = os.getenv("FRONTEND_URL")
            return RedirectResponse(
                        url=f"{FRONTEND_URL}/auth/callback?error=token_failed"

            )
        user_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {google_access_token}"}
        )
        user_data = user_res.json()

    email = user_data.get("email")
    name = user_data.get("name")

    if not email:
        FRONTEND_URL = os.getenv("FRONTEND_URL")
        return RedirectResponse(
                url=f"{FRONTEND_URL}/auth/callback?error=no_email"

        )




    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            name=name or "Google User",
            email=email,
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)}, expires_delta=timedelta(days=30))

    user.refresh_token = refresh_token
    db.commit()

    profile_completed = "true" if is_profile_complete(user) else "false"
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    return RedirectResponse(
        url=f"{FRONTEND_URL}/auth/callback?access_token={jwt_token}&refresh_token={refresh_token}&profile_completed={profile_completed}"
    )

    

@app.get("/auth/github/login")
def github_login():
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    FRONTEND_URL = os.getenv("FRONTEND_URL")

    if not GITHUB_CLIENT_ID:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error=missing_github_credentials"
        )

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "scope": "user:email"
    }

    github_url = (
        "https://github.com/login/oauth/authorize?"
        + urllib.parse.urlencode(params)
    )

    return RedirectResponse(url=github_url)

@app.get("/auth/github/callback")
async def github_callback(
    code: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    FRONTEND_URL = os.getenv("FRONTEND_URL")

    if error or not code:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?error=auth_failed"
        )

    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={"client_id": GITHUB_CLIENT_ID, "client_secret": GITHUB_CLIENT_SECRET, "code": code}
        )
        github_access_token = token_res.json().get("access_token")

        if not github_access_token:
                return RedirectResponse(
                            url=f"{FRONTEND_URL}/auth/callback?error=token_failed"

                )



        user_res = await client.get("https://api.github.com/user", headers={"Authorization": f"Bearer {github_access_token}"})
        user_data = user_res.json()
        email = user_data.get("email")

        if not email:
            email_res = await client.get("https://api.github.com/user/emails", headers={"Authorization": f"Bearer {github_access_token}"})
            emails = email_res.json()
            primary_email = next((e["email"] for e in emails if e.get("primary")), None)
            email = primary_email or (emails[0]["email"] if emails else None)

    if not email:
            return RedirectResponse(
                        url=f"{FRONTEND_URL}/auth/callback?error=no_email"
        )




    name = user_data.get("name") or user_data.get("login") or "GitHub User"
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(secrets.token_hex(16)),
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)}, expires_delta=timedelta(days=30))

    user.refresh_token = refresh_token
    db.commit()

    profile_completed = "true" if is_profile_complete(user) else "false"
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?access_token={jwt_token}&refresh_token={refresh_token}&profile_completed={profile_completed}"
    )


# ────────────────────────────────────────────────────────────────
# DATA EXTRACTION AGGREGATION ROUTES
# ────────────────────────────────────────────────────────────────

@app.get("/api/jobs")
def get_jobs(query: str = Query("", description="Job search query"), location: str = Query("", description="Location filter"), page: int = Query(1, ge=1), current_user: User = Depends(get_current_user)):
    return search_jobs(query=query, location=location, page=page)

@app.get("/api/internships")
def get_internships(query: str = Query("", description="Internship search query"), location: str = Query("", description="Location filter"), page: int = Query(1, ge=1), current_user: User = Depends(get_current_user)):
    return search_internships(query=query, location=location, page=page)

@app.get("/api/courses")
def get_courses(query: str = Query("", description="Course search query"), current_user: User = Depends(get_current_user)):
    results = search_courses(query=query)
    return {"results": results}

@app.get("/api/bookmarks")
def get_bookmarks(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization")
    token = auth.split(" ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")

    user = db.query(User).filter(User.email == email).first()
    return db.query(Bookmark).filter(Bookmark.user_id == user.id).all()

@app.post("/api/bookmarks")
async def add_bookmark(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization")
    token = auth.split(" ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")

    user = db.query(User).filter(User.email == email).first()
    data = await request.json()

    bookmark = Bookmark(
        user_id=user.id,
        course_title=data["title"],
        course_url=data["url"],
        provider=data.get("provider", "")
    )
    db.add(bookmark)
    db.commit()
    return {"message": "Bookmarked"}

@app.delete("/api/bookmarks/{bookmark_id}")
def delete_bookmark(bookmark_id: int, request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization")
    token = auth.split(" ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")

    user = db.query(User).filter(User.email == email).first()
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == user.id).first()

    if bookmark:
        db.delete(bookmark)
        db.commit()
    return {"message": "Deleted"}

# ────────────────────────────────────────────────────────────────
# PROFILE & FILE REPOSITORY ENGINE
# ────────────────────────────────────────────────────────────────

@app.get("/api/user/profile", response_model=ProfileResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "first_name": getattr(current_user, "first_name", ""),
        "last_name": getattr(current_user, "last_name", ""),
        "email": getattr(current_user, "email", ""),
        "profile_photo": getattr(current_user, "profile_photo", ""),
        "name": getattr(current_user, "name", ""),
        "user_type": getattr(current_user, "user_type", "student"),
        "document_filename": getattr(current_user, "document_filename", ""),
        "skills": getattr(current_user, "skills", ""),
        "dob": getattr(current_user, "dob", ""),
        "location": getattr(current_user, "location", ""),
        "interests": getattr(current_user, "interests", ""),
        "marks": getattr(current_user, "marks", []) or [],
        "is_profile_complete": is_profile_complete(current_user)
    }

@app.put("/api/user/profile")
async def update_user_profile(
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    user_type: Optional[str] = Form(None),
    profile_photo: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    interests: Optional[str] = Form(None),
    marks: Optional[str] = Form(None),  # JSON string
    document: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if first_name is not None: current_user.first_name = first_name
    if last_name is not None: current_user.last_name = last_name
    if user_type is not None: current_user.user_type = user_type
    if profile_photo is not None: current_user.profile_photo = profile_photo
    if skills is not None: current_user.skills = skills
    if dob is not None: current_user.dob = dob
    if location is not None: current_user.location = location
    if interests is not None: current_user.interests = interests
    if marks is not None:
        import json as _json
        try:
            current_user.marks = _json.loads(marks)
        except Exception:
            current_user.marks = []

    if document and hasattr(document, "filename") and document.filename:
        current_user.document_filename = document.filename
        try:
            content = await document.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            extracted_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text: extracted_text += text + "\n"
            current_user.document_text = extracted_text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail="Failed to parse document. Please upload a valid PDF.")

    fname = current_user.first_name or ""
    lname = current_user.last_name or ""
    current_user.name = f"{fname} {lname}".strip()

    db.commit()
    return {"message": "Profile updated successfully"}

@app.post("/api/user/change-password")
def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.hashed_password = hash_password(request.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

# ────────────────────────────────────────────────────────────────
# RESUME AI ANALYZER ENDPOINTS
# ────────────────────────────────────────────────────────────────

@app.post("/api/resume/analyze", response_model=ResumeAnalysisResponse)
async def analyze_uploaded_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),  # 👈 Added DB Session dependency injection
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        
        raw_text = extracted_text.strip()
        if not raw_text:
            raise HTTPException(status_code=400, detail="The PDF appears to be empty or unreadable.")
            
    except Exception as e:
        print("Resume Analysis PDF Parse Error:", e)
        raise HTTPException(status_code=400, detail="Failed to process file. Ensure it is a valid PDF.")

    try:
        # Check if GOOGLE_API_KEY is configured
        api_key = os.getenv("GOOGLE_API_KEY")
        is_mock = False
        if not api_key or api_key.strip() == "" or api_key.strip() == "your_api_key_here":
            is_mock = True
            print("[WARNING] GOOGLE_API_KEY is missing or placeholder! Using mock analysis for testing.")

        if is_mock:
            # Generate a realistic mockup analysis
            # We vary the score slightly based on the length of resume text
            score = min(max(40 + len(raw_text) % 45, 65), 94)
            
            # Simple keyword matching to make the mock dynamic
            has_react = "react" in raw_text.lower()
            has_python = "python" in raw_text.lower()
            has_experience = "experience" in raw_text.lower() or "work" in raw_text.lower()
            
            strengths = ["Clear contact details and professional summary section."]
            if has_react: strengths.append("Strong demonstration of modern React and frontend architecture skills.")
            if has_python: strengths.append("Good backend foundation with Python language proficiency.")
            if has_experience: strengths.append("Solid career history showing clear progression and responsibilities.")
            else: strengths.append("Structured educational highlights showing clear academic foundations.")
            
            improvements = []
            if not has_experience:
                improvements.append("Add quantifiable metrics or bullet points highlighting project achievements.")
            else:
                improvements.append("Incorporate more metric-driven bullet points (e.g., 'Improved database query speeds by 20%').")
            if len(raw_text) < 500:
                improvements.append("Expand sections to ensure adequate detail for applicant tracking systems (ATS).")
            if "education" not in raw_text.lower():
                improvements.append("Ensure an 'Education' section is explicitly listed with graduation dates.")
            if len(improvements) == 0:
                improvements.append("Consider highlighting community open source contributions or leadership roles.")
            
            analysis_result = ResumeAnalysisResponse(
                overall_score=score,
                impact_metrics=MetricScore(
                    score=score - 5,
                    feedback="The resume has good clarity. Add more numeric data, percentages, and accomplishments to increase impact score."
                ),
                formatting_structure=MetricScore(
                    score=score + 3,
                    feedback="Structure is clean and readable by ATS parsers. Section headers are standard and chronologically arranged."
                ),
                skills_density=MetricScore(
                    score=score - 2,
                    feedback="Good presence of industry keywords. Consider grouping skills by categories (e.g., Languages, Libraries, Tools)."
                ),
                strengths=strengths,
                improvements=improvements
            )
        else:
            # Pass the extracted text to Gemini using LangChain structural JSON mapping
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
            structured_llm = llm.with_structured_output(ResumeAnalysisResponse)

            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "You are an expert executive recruiter and advanced Applicant Tracking System (ATS) optimization engine. "
                    "Critically audit the provided resume text. Be completely objective, demanding, and thorough. "
                    "You must strictly return data matching the JSON schema requested."
                ),
                ("user", "Analyze this resume text content:\n\n{resume_content}")
            ])

            analysis_chain = prompt | structured_llm
            analysis_result = analysis_chain.invoke({"resume_content": raw_text})
        
        # Commit report directly into Supabase via SQLAlchemy
        db_report = ResumeAnalysis(
            user_id=current_user.id,
            overall_score=analysis_result.overall_score,
            impact_metrics=analysis_result.impact_metrics.model_dump(),
            formatting_structure=analysis_result.formatting_structure.model_dump(),
            skills_density=analysis_result.skills_density.model_dump(),
            strengths=analysis_result.strengths,
            improvements=analysis_result.improvements
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        return analysis_result

    except Exception as ai_err:
        print("AI Analysis Engine Execution Error:", ai_err)
        raise HTTPException(status_code=500, detail="The AI engine failed to analyze the document. Please try again.")

@app.get("/api/resume/history")
def get_resume_analysis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 👈 Added: Fetch historical reports linked to this specific user account
    history = db.query(ResumeAnalysis)\
                .filter(ResumeAnalysis.user_id == current_user.id)\
                .order_by(ResumeAnalysis.created_at.desc())\
                .all()
                
    return [
        {
            "id": report.id,
            "overall_score": report.overall_score,
            "impact_metrics": report.impact_metrics,
            "formatting_structure": report.formatting_structure,
            "skills_density": report.skills_density,
            "strengths": report.strengths,
            "improvements": report.improvements,
            "date": report.created_at.strftime("%b %d, %Y")
        } for report in history
    ]