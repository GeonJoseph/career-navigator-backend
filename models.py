from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    reset_password_token = Column(String, nullable=True)
    reset_password_expire = Column(DateTime(timezone=True), nullable=True)
    
    # Email Verification
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)
    
    # Basic Profile
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    profile_photo = Column(String, nullable=True)
    
    # Professional Profile
    skills = Column(Text, nullable=True)  # JSON or comma-separated
    interests = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    dob = Column(String, nullable=True)

    # Document-Aware Profile addition
    user_type = Column(String, default="student") # "professional" or "student"
    document_text = Column(Text, nullable=True)
    document_filename = Column(String, nullable=True)
    marks = Column(JSON, nullable=True, default=list)  # list of {subject, score, total}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(String, default="User")

    # Relationship to track all resume reports linked to this user instance
    resume_analyses = relationship("ResumeAnalysis", back_populates="user", cascade="all, delete-orphan")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    course_title = Column(String, nullable=False)
    course_url = Column(String, nullable=False)
    provider = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ────────────────────────────────────────────────────────────────
# NEW ADDITION: RESUME ANALYSIS REPORT MODEL
# ────────────────────────────────────────────────────────────────

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    overall_score = Column(Integer, nullable=False)
    
    # Using JSON type columns allows us to map nested Pydantic MetricScore dicts
    # directly into PostgreSQL/Supabase safely without parsing strings manually.
    impact_metrics = Column(JSON, nullable=False)
    formatting_structure = Column(JSON, nullable=False)
    skills_density = Column(JSON, nullable=False)
    
    # Lists of strings map perfectly to JSON block columns
    strengths = Column(JSON, nullable=False)
    improvements = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Establish bidirectional link back to the parent User object
    user = relationship("User", back_populates="resume_analyses")