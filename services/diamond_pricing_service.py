from datetime import datetime
from models.diamond_pricing import DiamondPricing
from services.margin_resolver import get_margin_for_diamond

def create_diamond_pricing( db, diamonds, store_id: str, shopify_name: str):
    now = datetime.utcnow()

    pricing_rows = []

    for d in diamonds:
        base_price = float(d.price or 0)

        margin = get_margin_for_diamond( db=db, store_id=store_id, shopify_name=shopify_name, stone_type=d.type, price=base_price, carat=float(d.carat or 0))

        selling_price = round(
            base_price + (base_price * margin / 100), 2
        )

        pricing_rows.append(
            DiamondPricing( diamond_id=d.id, store_id=store_id, base_price=base_price, selling_price=selling_price, created_at=now, updated_at=now)
        )

    if pricing_rows:
        db.bulk_save_objects(pricing_rows)
        db.commit()
