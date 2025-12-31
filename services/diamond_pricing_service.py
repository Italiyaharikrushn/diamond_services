from datetime import datetime
from sqlalchemy.orm import Session
from models.diamond_pricing import DiamondPricing
from services.pricing_engine import calculate_selling_price

# Create Diamond Pricing
def create_diamond_pricing(db: Session, diamonds, store_id: str, shopify_name: str):
    now = datetime.utcnow()

    for diamond in diamonds:
        base_price, selling_price = calculate_selling_price(db, diamond, store_id)

        pricing = DiamondPricing(
            diamond_id=diamond.id,
            store_id=store_id,
            base_price=base_price,
            selling_price=selling_price,
            created_at=now,
            updated_at=now
        )

        db.add(pricing)

    db.commit()