from models.stone_margin import StoneMargin

def get_margin_for_diamond( db, store_id: str, shopify_name: str, stone_type: str, price: float, carat: float) -> float:

    margins = db.query(StoneMargin).filter( StoneMargin.store_id == store_id, StoneMargin.shopify_name == shopify_name, StoneMargin.type == stone_type).all()

    for m in margins:
        if m.unit == "price" and m.start <= price <= m.end:
            return m.margin

        if m.unit == "carat" and m.start <= carat <= m.end:
            return m.margin

    return 0.0
