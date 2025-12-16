
from db.database import SessionLocal
from fastapi import Request, HTTPException, status

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request):
    return request.state.current_user

def get_current_store(request: Request):
    store_name = getattr(request.state, "store_name", None)
    if store_name is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )
    return store_name
