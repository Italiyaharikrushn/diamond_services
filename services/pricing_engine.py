from datetime import datetime
from sqlalchemy.orm import Session
from models.stone_margin import StoneMargin
from models.diamond_pricing import DiamondPricing

def calculate_selling_price(db: Session, diamond, store_id: str):
    base_price = float(diamond.price)
    margin_value = 0

    margins = db.query(StoneMargin).filter(
        StoneMargin.store_id == store_id,
        StoneMargin.type == diamond.type
    ).all()

    for m in margins:
        compare_value = base_price if m.unit.value == "price" else float(diamond.carat)
        if m.start <= compare_value <= m.end:
            margin_value = float(m.margin)
            break

    # selling_price = base_price + margin_value
    selling_price = base_price + (base_price * margin_value / 100)
    return base_price, selling_price


def generate_diamond_pricing(db: Session, diamonds, store_id: str):
    now = datetime.utcnow()

    for diamond in diamonds:
        base_price, selling_price = calculate_selling_price(
            db, diamond, store_id
        )

        db.add(
            DiamondPricing(
                diamond_id=diamond.id,
                store_id=store_id,
                base_price=base_price,
                selling_price=selling_price,
                created_at=now,
                updated_at=now
            )
        )

    db.commit()
