import jwt
from datetime import datetime, timedelta
from core.config import settings

PREFIX = "Bearer"

def create_custom_token(store_name: str, shopify_name: str = None):
    payload = {
        "dest": store_name,
        "shopify_name": shopify_name,
        "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRY)
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_custom_token(header: str):
    try:
        bearer, _, token = header.partition(" ")
        if bearer != PREFIX:
            raise ValueError("Invalid token prefix")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception as e:
        print("Token decode error:", e)
        return None
