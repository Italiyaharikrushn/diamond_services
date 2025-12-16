from datetime import datetime, timedelta
from jose import jwt
import time
from fastapi.requests import Request
from typing import Optional
from pydantic import BaseModel
from core.config import settings

SECRET_KEY = "qwertyuiopasdfghjklzxcvbnmmnbvcxzlkjhgfdsapoiuytrewq"
ALGORITHM = "HS256"
PREFIX = "Bearer"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    jwt_token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return jwt_token


def decode_access_token(token: str):
    payload = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        print("Token Decode Error:", str(e))
        return None

def is_unauthorized_url(request: Request):
    allow_urls = [
        "/docs",
        "/openapi.json",
        "/auth/login",
        "/auth/register",
        "/token/generate-token"
    ]

    path = request.url.path

    if path.startswith("/static"):
        return True

    if path in allow_urls:
        return True
    return False

def get_token(header: str):
    bearer, _, token = header.partition(" ")
    if bearer != PREFIX:
        raise ValueError("Invalid token")

    return token