import hashlib
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from backend.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("pbkdf2_sha256$"):
        algorithm, salt, expected = hashed_password.split("$", 2)
        digest = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 200000)
        return digest.hex() == expected
    return False


def get_password_hash(password: str) -> str:
    salt = hashlib.sha256(password.encode("utf-8")).hexdigest()[:16]
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
