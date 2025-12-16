from crud.base import CRUDBase
from models.stone_margin import StoneMargin
from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.StoneMargin import StoneMarginCreate, StoneMarginResponse
from sqlalchemy import func
from services.selling_price_service import SellingPriceService

class CRUDStonemargin(CRUDBase):

    def create(self, db: Session, obj_in: StoneMarginCreate) -> StoneMarginResponse:
        if not obj_in.store_id:
            raise HTTPException(status_code=400, detail="store_id is required")

        if obj_in.type.lower() not in ["lab", "natural", "gemstones"]:
            raise HTTPException(status_code=400, detail="Invalid stone type")

        if obj_in.start >= obj_in.end:
            raise HTTPException(status_code=400, detail="Start must be less than end")

        try:
            # Check if same margin range already exists
            existing = (
                db.query(StoneMargin)
                .filter(
                    StoneMargin.store_id == obj_in.store_id,
                    StoneMargin.shopify_name == obj_in.shopify_name,
                    StoneMargin.type == obj_in.type,
                    StoneMargin.unit == obj_in.unit,
                    func.round(StoneMargin.start, 2) == round(obj_in.start, 2),
                    func.round(StoneMargin.end, 2) == round(obj_in.end, 2),
                )
                .first()
            )

            # Update margin if exists
            if existing:
                existing.margin = obj_in.margin
                db.commit()
                db.refresh(existing)

                # Recalculate selling_price
                SellingPriceService.apply_margin(
                    db=db,
                    store_id=obj_in.store_id,
                    shopify_name=obj_in.shopify_name,
                    stone_type=obj_in.type,
                    unit=obj_in.unit,
                    start=obj_in.start,
                    end=obj_in.end,
                    margin=obj_in.margin
                )

                # Return response as StoneMarginResponse
                return StoneMarginResponse(
                    stone_type=existing.type,
                    unit=existing.unit,
                    markups=[{
                        "start": existing.start,
                        "end": existing.end,
                        "markup": existing.margin
                    }]
                )

            # Create new margin
            db_obj = StoneMargin(
                store_id=obj_in.store_id,
                shopify_name=obj_in.shopify_name,
                type=obj_in.type,
                unit=obj_in.unit,
                start=obj_in.start,
                end=obj_in.end,
                margin=obj_in.margin
            )

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

            # Apply margin to matching stones
            SellingPriceService.apply_margin(
                db=db,
                store_id=obj_in.store_id,
                shopify_name=obj_in.shopify_name,
                stone_type=obj_in.type,
                unit=obj_in.unit,
                start=obj_in.start,
                end=obj_in.end,
                margin=obj_in.margin
            )

            # Return response as StoneMarginResponse
            return StoneMarginResponse(
                stone_type=db_obj.type,
                unit=db_obj.unit,
                markups=[{
                    "start": db_obj.start,
                    "end": db_obj.end,
                    "markup": db_obj.margin
                }]
            )

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

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
