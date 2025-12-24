from core.config import settings
from sqlalchemy.orm import Session
from api.dependencies import get_db
from datetime import timedelta, date
from schemas.auth import LoginSchema, RegisterSchema
from fastapi import APIRouter, Depends, status, HTTPException
from services.user_service import create_access_token, create_user, get_user_by_email
router = APIRouter()


@router.post('/login', status_code=(status.HTTP_201_CREATED))
def login(login_schema: LoginSchema, db: Session = Depends(get_db)):
    existing_users = get_user_by_email(db, login_schema.email)
    if len(existing_users) == 0:
        raise HTTPException(status_code=(status.HTTP_404_NOT_FOUND),
                            detail='User does not exist.')
    user = existing_users[0]
    print(date.today())
    claim = {'email': user.email,
             'id': user.id}
    token = create_access_token(claim, expires_delta=timedelta(
        minutes=(settings.ACCESS_TOKEN_EXPIRE_MINUTES)))
    return {'token': token}


@router.post('/register', response_model=RegisterSchema, response_model_exclude={'password'}, status_code=(status.HTTP_201_CREATED))
def register(register_schema: RegisterSchema, db: Session = Depends(get_db)):
    existing_users = get_user_by_email(db, register_schema.email)
    if len(existing_users) != 0:
        raise HTTPException(status_code=(status.HTTP_409_CONFLICT),
                            detail='Email already exist')
    user = create_user(db, register_schema)
    return user
