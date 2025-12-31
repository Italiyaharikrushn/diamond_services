from datetime import datetime
from models.order import Order
from crud.base import CRUDBase
from typing import Optional, List
from sqlalchemy.orm import Session
from schemas.order import OrderCreate

class CRUDOrder(CRUDBase):

    def create_order(self, db: Session, order: OrderCreate):
        app_used = False
        diamonds_price = 0

        if order.line_items:
            for item in order.line_items:
                if item.vendor == "Diamond Selector":
                    app_used = True
                    diamonds_price = float(item.price or 0)
                    break

        address = ""
        if order.shipping_address:
            parts = [
                order.shipping_address.address1,
                order.shipping_address.address2,
                order.shipping_address.city,
                order.shipping_address.province,
                order.shipping_address.postal_code,
                order.shipping_address.country
            ]
            address = ", ".join(filter(None, [p.strip() for p in parts if p]))

        # Convert order_date to datetime if it's a string
        order_date = order.order_date
        if isinstance(order_date, str):
            # Remove 'Z' if present and parse
            order_date = order_date.rstrip("Z")
            order_date = datetime.fromisoformat(order_date)

        db_order = Order(
            order_id=order.order_id,
            store_id=order.store_id,
            shopify_app=order.shopify_app,
            order_name=order.order_name,
            order_date=order_date,
            currency_code=order.currency_code,
            total_amount=order.total_amount,
            products=[item.dict() for item in order.line_items] if order.line_items else [],
            order_notes=order.order_notes,
            source_name=order.source_name,
            app_used=app_used,
            referring_site=order.referring_site,
            address=address,
            diamonds_price=diamonds_price
        )

        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    
    def get_orders(
        self,
        db: Session,
        store_id: str,
        shopify_app: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Order]:
        query = db.query(Order).filter(Order.store_id == store_id)

        if shopify_app:
            query = query.filter(Order.shopify_app == shopify_app)

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
            except ValueError:
                raise ValueError("Invalid start_date format")
            start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Order.order_date >= start_dt)

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
            except ValueError:
                raise ValueError("Invalid end_date format")
            end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(Order.order_date <= end_dt)

        orders = query.order_by(Order.order_date.asc()).all()
        return orders

order = CRUDOrder(Order)
