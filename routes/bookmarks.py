from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from models import Bookmark
from models import Bookmark, User
from dependencies import get_current_user

router = APIRouter(prefix="/api/bookmarks")


# 🔹 Add bookmark
@router.post("")
def add_bookmark(
    data: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == user.id,
        Bookmark.course_url == data["course_url"]
    ).first()

    if existing:
        return existing

    bookmark = Bookmark(
        user_id=user.id,
        course_title=data["course_title"],
        course_url=data["course_url"],
        provider=data.get("provider")
    )

    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    db.close()

    return bookmark


# 🔹 Delete bookmark  ← YOUR QUESTION
@router.delete("")
def remove_bookmark(
    data: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db.query(Bookmark).filter(
        Bookmark.user_id == user.id,
        Bookmark.course_url == data["course_url"]
    ).delete()

    db.commit()

    db.close()

    return {"success": True}


# 🔹 Get bookmarks  ← YOUR QUESTION
@router.get("")
def get_bookmarks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    
    db.close()
    
    return db.query(Bookmark).filter(
        Bookmark.user_id == user.id
    ).all()