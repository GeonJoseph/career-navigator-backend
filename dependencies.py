from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from auth import SECRET_KEY, ALGORITHM


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No auth header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid header format")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user