import crud
from typing import Optional
from sqlalchemy.orm import Session
from api.dependencies import get_db
from schemas.order import OrderCreate
from fastapi import APIRouter, Depends, HTTPException, Query


router = APIRouter()


@router.post("/public/create-order", status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    if not order.store_id or not order.shopify_app:
        raise HTTPException(status_code=400, detail="Missing store_id or shopify_app")

    db_order = crud.order.create_order(db, order)
    return {
        "success": True,
        "data": {
            "order_id": db_order.order_id,
            "store_id": db_order.store_id,
            "shopify_app": db_order.shopify_app,
            "order_name": db_order.order_name,
            "order_date": db_order.order_date,
            "currency_code": db_order.currency_code,
            "total_amount": float(db_order.total_amount),
            "app_used": db_order.app_used,
            "diamonds_price": float(db_order.diamonds_price or 0),
            "address": db_order.address
        }
    }

@router.get("/public/get-orders")
def get_orders(
    store_id: Optional[str] = Query(None),
    shopify_app: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if not store_id:
        raise HTTPException(status_code=400, detail="store_id is required")

    try:
        orders = crud.order.get_orders(
            db=db,
            store_id=store_id,
            shopify_app=shopify_app,
            start_date=start_date,
            end_date=end_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"success": True, "data": [o.__dict__ for o in orders]}
