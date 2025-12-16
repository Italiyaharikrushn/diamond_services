from typing import Optional
from jose import jwt
from fastapi import HTTPException
from core.config import settings


def _strip_bearer(token_header: str) -> str:
    """Accept either raw token or "Bearer <token>" header value."""
    if not token_header:
        raise ValueError("Missing token header")
    if token_header.startswith("Bearer "):
        return token_header.split(" ", 1)[1]
    return token_header


def verify_external_jwt(token_header: str) -> dict:
    """Verify a JWT produced by the external (Node.js) generator.

    Expects the token to be HMAC-signed with the secret in
    `settings.EXTERNAL_JWT_SECRET` and contain a `dest` claim that matches
    `settings.EXTERNAL_JWT_DEST`.

    Raises HTTPException(401) on invalid/missing token or mismatched dest.
    Returns the decoded payload (dict) on success.
    """
    try:
        token = _strip_bearer(token_header)
    except ValueError:
        raise HTTPException(status_code=401, detail="Authentication header missing")

    if not settings.EXTERNAL_JWT_SECRET:
        raise HTTPException(status_code=500, detail="External JWT secret not configured")

    try:
        payload = jwt.decode(token, settings.EXTERNAL_JWT_SECRET, algorithms=[settings.ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid external token")

    expected = settings.EXTERNAL_JWT_DEST
    if expected:
        dest = payload.get("dest")
        if dest != expected:
            raise HTTPException(status_code=401, detail="Invalid token destination")

    return payload
