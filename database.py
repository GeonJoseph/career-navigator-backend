import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
# --- Bulletproof Connection String Parser ---
if DATABASE_URL:
    try:
        # Standardize the scheme to postgresql:// if it isn't already
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
            
        # Parse the URL structure cleanly using Python's built-in tool
        parsed = urllib.parse.urlparse(DATABASE_URL)
        
        # Safely extract and decode the username/password elements
        username = parsed.username
        password = parsed.password
        
        if password:
            # Decode it first to ensure no double-encoding issues
            plain_password = urllib.parse.unquote(password)
            # Re-encode it perfectly for SQLAlchemy network transfer
            secure_password = urllib.parse.quote_plus(plain_password)
            
            # Rebuild the hostname section including the port
            netloc_host = parsed.hostname
            if parsed.port:
                netloc_host = f"{netloc_host}:{parsed.port}"
                
            # Reassemble the URL step-by-step
            DATABASE_URL = f"postgresql://{username}:{secure_password}@{netloc_host}{parsed.path}"
            
            # Append options required by connection poolers if missing
            if "?" in parsed.query:
                DATABASE_URL += f"?{parsed.query}"
    except Exception:
        pass
# ---------------------------------------------

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()