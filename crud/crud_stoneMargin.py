from sqlalchemy import func
from crud.base import CRUDBase
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.stone_margin import StoneMargin
from services.selling_price_service import SellingPriceService
from schemas.StoneMargin import StoneMarginCreate, StoneMarginResponse

class CRUDStonemargin(CRUDBase):

    # Create Stone Margin
    def create(self, db: Session, obj_in: StoneMarginCreate):
        stone_type = obj_in.type.lower()
        total_updated = 0
        db.query(StoneMargin).filter(
            StoneMargin.store_id == obj_in.store_id,
            StoneMargin.type == stone_type,
        ).delete(synchronize_session=False)

        for r in obj_in.ranges:
            if r.start >= r.end:
                continue
            new_margin = StoneMargin(
                store_id=obj_in.store_id,
                type=stone_type,
                unit=obj_in.unit,
                start=r.start,
                end=r.end,
                margin=r.margin
            )
            db.add(new_margin)

            total_updated += SellingPriceService.apply_margin(
                db=db,
                store_id=obj_in.store_id,
                stone_type=stone_type,
                unit=obj_in.unit,
                start=r.start,
                end=r.end,
                margin=r.margin
            )

        db.commit()
        db.expire_all()

        return StoneMarginResponse(
            message="Margins updated successfully",
            count=total_updated
        )

    # Get Stone Margins
    def get_stone(self, db: Session, store_id: str):
        margins = db.query(StoneMargin).filter(
            StoneMargin.store_id == store_id
        ).all()

        grouped = {}
        for m in margins:
            grouped.setdefault(m.type, {})
            grouped[m.type].setdefault(m.unit, [])

            grouped[m.type][m.unit].append({
                "start": m.start,
                "end": m.end,
                "markup": m.margin
            })

        result = []
        for stone_type, units in grouped.items():
            for unit, markups in units.items():
                result.append({
                    "stone_type": stone_type,
                    "unit": unit,
                    "markups": markups
                })

        return result

margin = CRUDStonemargin(StoneMargin)
