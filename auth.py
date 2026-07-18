from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"

# Load .env FIRST
load_dotenv(dotenv_path=env_path)



SECRET_KEY = os.getenv("SECRET_KEY")



ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict):
    to_encode = data.copy()

    if "sub" not in to_encode:
        raise ValueError("Token must include 'sub'")

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def send_verification_email(receiver_email: str, otp: str):
    
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    

    try:
        msg = EmailMessage()
        msg["Subject"] = "Verify your Career Navigator account"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.set_content(f"Your OTP is: {otp}")


        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)

            server.send_message(msg)
            print("EMAIL SENT SUCCESSFULLY")

    except Exception as e:
        print("EMAIL ERROR:", str(e))