from io import StringIO
import csv
from crud.base import CRUDBase
from sqlalchemy.orm import Session
from models.csv_gemstones import CSVGemstone
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import func
from schemas.CSVGemstone import CSVGemstoneCreate

class CRUDGemstones(CRUDBase):
    @staticmethod
    def safe_float(value: Optional[str], default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    # Create CSV Data
    def create(self, db: Session, obj_in: CSVGemstoneCreate, store_id: str):
        try:
            csv_reader = csv.DictReader(StringIO(obj_in.csv_data))
            model_fields = set(CSVGemstone.__table__.columns.keys())

            gemstones = []
            updated_gemstones = []
            created_gemstones = []

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

                mapped["store_id"] = store_id

                existing_gemstone = db.query(CSVGemstone).filter_by(certificate_no=mapped["certificate_no"], store_id=store_id).first()

                if existing_gemstone:
                    updated = False

                    for key, value in mapped.items():
                        if key == "certificate_no":
                            continue

                        old_value = getattr(existing_gemstone, key, None)

                        if value != old_value:
                            setattr(existing_gemstone, key, value)
                            updated = True

                    if not updated:
                        # SAME DATA + SAME CERTIFICATE + SAME STORE
                        raise HTTPException(
                            status_code=400,
                            detail=f"Duplicate certificate '{mapped['certificate_no']}' not allowed for this store"
                        )

                    updated_gemstones.append(existing_gemstone)
                    gemstones.append(existing_gemstone)
                else:
                    new_gemstone = CSVGemstone(**mapped)
                    created_gemstones.append(new_gemstone)
                    gemstones.append(new_gemstone)

            db.bulk_save_objects(gemstones)  
            db.commit()

            response = {
                "created_gemstones": [
                    {
                        "certificate_no": g.certificate_no,
                        "s_no": g.s_no,
                        "carat": g.carat,
                        "price": g.price,
                        "selling_price": g.selling_price,
                        "description": g.description,
                        "origin": g.origin,
                        # Add any other fields you want in the response
                    } for g in created_gemstones
                ],
                "updated_gemstones": [
                    {
                        "id": g.id,
                        "certificate_no": g.certificate_no,
                        "s_no": g.s_no,
                        "carat": g.carat,
                        "price": g.price,
                        "selling_price": g.selling_price,
                        "description": g.description,
                        "origin": g.origin,
                        # Add any other fields you want in the response
                    } for g in updated_gemstones
                ],
            }

            return response

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating gemstones: {str(e)}")

    # Get All CSV Data
    def get_all(self, db: Session, store_id: str):
        return db.query(CSVGemstone).filter(CSVGemstone.store_id == store_id).all()

    # get Filter gemstone
    def get_gemstone_filter(self, db: Session, store_id: str, shopify_app: str):
        try:
            Base_filter = [
                CSVGemstone.store_id == store_id,
                CSVGemstone.shopify_name == shopify_app
            ]

            colors = (
                db.query(func.distinct(CSVGemstone.color).label("color")).filter(*Base_filter).order_by(CSVGemstone.color.asc()).all()
            )

            clarities = (
                db.query(func.distinct(CSVGemstone.clarity).label("clarity")).filter(*Base_filter).order_by(CSVGemstone.clarity.asc()).all()
            )

            price_min, price_max = (
                db.query(func.min(CSVGemstone.price), func.max(CSVGemstone.price)).filter(*Base_filter).first()
            )

            carat_min, carat_max = (
                db.query(func.min(CSVGemstone.carat), func.max(CSVGemstone.carat)).filter(*Base_filter).first()
            )

            filterData = {
                "colors" : [c.color for c in colors if c.color],
                "clarities" : [c.clarity for c in clarities if c.clarity],
                "price_ranges" : {
                    "min" : float(price_min or 0),
                    "max" : float(price_max or 0)
                },
                "carat_ranges" : {
                    "min" : float(carat_min or 0),
                    "max" : float(carat_max or 0)
                }
            }
            return { "success": True, "data": filterData }
        
        except Exception as e:
            return {
                "success" : False, "message" : "Error fecthing filters", "error": str(e)
            }

    # Bulk Delete Gemstone
    def bulk_delete_gemstones(self, db: Session, store_id: str, shopify_app: str, ids: list[int]):
        try:
            deleted = (
                db.query(CSVGemstone).filter(CSVGemstone.id.in_(ids), CSVGemstone.store_id == store_id, CSVGemstone.shopify_name == shopify_app).delete(synchronize_session=False)
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
        
    # All Delete Gemstone
    def all_delete_gemstones(self, db: Session, store_id: str, shopify_app: str):
        try:
            deleted = (
                db.query(CSVGemstone).filter(CSVGemstone.store_id == store_id,func.lower(CSVGemstone.shopify_name) == shopify_app.lower(),CSVGemstone.status == 1).delete(synchronize_session=False)
            )

            db.commit()

            return {
                "success": True, "Updated_count": deleted
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False, "error": str(e)
            }


gemstone = CRUDGemstones(CSVGemstone)
