from fastapi import APIRouter
from .endpoints import auth , user, StoneMargin, CSVGemstone, CSVDiamonds, token
route_v1 = APIRouter()

route_v1.include_router((token.router), prefix='/token', tags=['token'])
route_v1.include_router((CSVDiamonds.router), prefix='/diamonds', tags=['diamonds'])
route_v1.include_router((CSVGemstone.router), prefix='/gemstones', tags=['gemstones'])
route_v1.include_router((StoneMargin.router), prefix='/margin', tags=['margin'])
route_v1.include_router((auth.router), prefix='/auth', tags=['auth'])
route_v1.include_router((user.router), prefix='/user', tags=['user'])
