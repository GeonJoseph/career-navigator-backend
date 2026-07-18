from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_PASSWORD_LENGTH = 72  # bcrypt limit


def hash_password(password: str):
    if len(password.encode("utf-8")) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password too long (max 72 bytes).")
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)