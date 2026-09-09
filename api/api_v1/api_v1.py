from fastapi import APIRouter
from .endpoints import diamonds , StoneMargin, CSVGemstone, CSVDiamonds, token, group, storeSettings, order, ringData
route_v1 = APIRouter()

route_v1.include_router((token.router), prefix='/token', tags=['token'])
route_v1.include_router((CSVDiamonds.router), prefix='/diamonds', tags=['diamonds'])
route_v1.include_router((diamonds.router), prefix='/diamond', tags=['diamond'])
route_v1.include_router((CSVGemstone.router), prefix='/gemstones', tags=['gemstones'])
route_v1.include_router((StoneMargin.router), prefix='/margin', tags=['margin'])
route_v1.include_router((group.router), prefix='/group', tags=['group'])
route_v1.include_router((order.router), prefix='/order', tags=['order'])
route_v1.include_router((storeSettings.router), prefix='/storeSetting', tags=['storesetting'])
route_v1.include_router((ringData.router), prefix='/ring', tags=['Rings'])
