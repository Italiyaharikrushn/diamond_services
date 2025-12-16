from fastapi.requests import Request
from fastapi import HTTPException
from typing import List


def get_current_user(request: Request):
    if not hasattr(request.state, "current_user"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.current_user


def get_current_user_permission(request: Request) -> List[str]:
    return request.state.permissions
