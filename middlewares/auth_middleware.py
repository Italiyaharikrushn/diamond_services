import logging
from fastapi import status
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from util.token import decode_custom_token
import crud
from db.database import SessionLocal
from services.user_service import decode_access_token
from core.security import is_unauthorized_url

logging.basicConfig(level=logging.INFO)

class AuthMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        if is_unauthorized_url(request):
            return await call_next(request)

        token = request.headers.get("Authorization", None)
        if not token:
            return JSONResponse(
                content={"detail": "Authentication header missing"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        store_payload = decode_custom_token(token)
        if store_payload:
            store = store_payload.get("dest", "").replace("https://", "")
            request.state.store_name = store
            request.state.shopify_name = store_payload.get("shopify_name", None)
            request.state.current_user = None
            return await call_next(request)

        claim = decode_access_token(token)
        if not claim:
            return JSONResponse(
                content={"detail": "Invalid authentication token."},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user_id = claim.get("id")
        if not user_id:
            return JSONResponse(
                content={"detail": "Invalid authentication token."},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        db = SessionLocal()
        try:
            user = crud.user.get_by_id(db, user_id)
            if not user:
                return JSONResponse(
                    content={"detail": "User not found."},
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            request.state.current_user = user
        except Exception as e:
            return JSONResponse(
                content={"detail": f"Internal Server Error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            db.close()

        return await call_next(request)
