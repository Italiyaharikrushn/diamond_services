from io import StringIO
import csv
from crud.base import CRUDBase
from sqlalchemy.orm import Session
from models.csv_diamond import CSVDiamond
from typing import Any, Optional
from fastapi import HTTPException
from schemas.CSVDiamons import CSVDiamondCreate
from sqlalchemy import func

class CRUDDiamonds(CRUDBase):
    @staticmethod
    def safe_float(value: Optional[str], default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    # Create CSV Data
    def create(self, db: Session, obj_in: CSVDiamondCreate):
        try:
            csv_reader = csv.DictReader(StringIO(obj_in.csv_data))
            model_fields = set(CSVDiamond.__table__.columns.keys())

            diamonds = []
            for row in csv_reader:
                mapped = {}

                for key, value in row.items():
                    k = key.lower().replace(" ", "_")

                    if k in model_fields:
                        mapped[k] = self.safe_float(value) if k in {"carat", "price", "selling_price", "table", "depth"} else (
                            None if value in (None, "", "None") else value
                        )

                mapped["s_no"] = row.get("Stone No") if row.get("Stone No") else None

                mapped.setdefault("origin", "Unknown")
                mapped.setdefault("description", "No description available")
                mapped.setdefault("selling_price", mapped.get("price"))
                mapped.setdefault("is_available", "Yes")
                mapped.setdefault("status", 1)

                diamonds.append(CSVDiamond(**mapped))

            db.bulk_save_objects(diamonds)  
            db.commit()

            return diamonds

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating diamonds: {str(e)}")

    # get All CSV Data
    def get_all(self, db: Session, store_id: str):
        return db.query(CSVDiamond).filter(CSVDiamond.store_id == store_id).all()

    # get filter diamonds
    def get_diamonds_filter(self, db: Session, store_id: str, shopify_app: str, stone_type: str):
        try:
            feed_type = "CSV"
            filter_data = {}
            base_filter = [
                CSVDiamond.store_id == store_id,
                CSVDiamond.shopify_name == shopify_app,
            ]

            if stone_type:
                base_filter.append(CSVDiamond.type == stone_type.lower())


            if feed_type == "CUSTOM":
                colors = db.query(func.distinct(CSVDiamond.color).label("color")).filter(*base_filter).all()
                clarities = db.query(func.distinct(CSVDiamond.clarity).label("clarity")).filter(*base_filter).all()
            else:
                colors = db.query(func.distinct(CSVDiamond.color)).filter(*base_filter).order_by(CSVDiamond.color.asc()).all()
                clarities = db.query(func.distinct(CSVDiamond.clarity)).filter(*base_filter).order_by(CSVDiamond.clarity.asc()).all()

            price_min, price_max = db.query(func.min(CSVDiamond.price), func.max(CSVDiamond.price)).filter(*base_filter).first()
            carat_min, carat_max = db.query(func.min(CSVDiamond.carat), func.max(CSVDiamond.carat)).filter(*base_filter).first()

            filter_data = {
                "colors": [c[0] for c in colors if c[0]],
                "clarities": [c[0] for c in clarities if c[0]],
                "price_range": {"min": float(price_min or 0), "max": float(price_max or 0)},
                "carat_range": {"min": float(carat_min or 0), "max": float(carat_max or 0)},
            }

            return { "success" : True, "data" : filter_data }
        except Exception as e:
            print(f"Error: {str(e)}")  # or use logging
            return { "success" : False, "Message" : "Error fetching filters", "error" : str(e) }
    
    # Bulk Delete diamonds
    def delete_diamonds(self, db: Session, store_id: str, shopify_app: str, ids: list[int]):
        try:
            deleted = (
                db.query(CSVDiamond).filter(CSVDiamond.id.in_(ids), CSVDiamond.store_id == store_id, CSVDiamond.shopify_name == shopify_app).update({"status": 0}, synchronize_session=False)
            )
            db.commit()
            return {
                "success" : True, "Deleted_cont" : deleted
            }
        except Exception as e :
            db.rollback()
            return {
                "Success" : False, "error" : str(e)
            }
    
    def all_delete_diamonds(self, db: Session, store_id: str, shopify_app: str):
        try:
            deleted = (
                db.query(CSVDiamond).filter(CSVDiamond.store_id == store_id,func.lower(CSVDiamond.shopify_name) == shopify_app.lower(),CSVDiamond.status == 1).update({"status": 0}, synchronize_session=False))

            db.commit()

            return {
                "success": True, "Updated_count": deleted
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False, "error": str(e)
            }
diamonds = CRUDDiamonds(CSVDiamond)
