from sqlalchemy.orm import Session
from sqlalchemy import func
from services.stone_model_resolver import get_stone_model

class SellingPriceService:

    @staticmethod
    def apply_margin(
        db: Session,
        store_id: str,
        shopify_name: str,
        stone_type: str,
        unit: str,
        start: float,
        end: float,
        margin: float
    ) -> int:

        Model = get_stone_model(stone_type)

        query = db.query(Model).filter(
            Model.store_id == store_id,
            Model.shopify_name == shopify_name,
            func.lower(Model.type) == stone_type.lower(),
            Model.status == 1
        )

        if unit == "price":
            query = query.filter(Model.price >= start, Model.price <= end)
        elif unit == "carat":
            query = query.filter(Model.carat >= start, Model.carat <= end)
        else:
            raise ValueError("Unit must be price or carat")

        stones = query.all()
        if not stones:
            return 0

        for stone in stones:
            stone.selling_price = round(
                stone.price + (stone.price * margin / 100), 2
            )
            db.add(stone)

        db.commit()
        return len(stones)
