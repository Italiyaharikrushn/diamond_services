import csv
from io import StringIO
from loguru import logger
from sqlalchemy import func
from typing import Optional
from crud.base import CRUDBase
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.csv_diamond import CSVDiamond
from schemas.CSVDiamons import CSVDiamondCreate
from models.storesettings import StoreSettings
from services.diamond_service import get_custom_diamonds_service

class CRUDDiamonds(CRUDBase):
    @staticmethod
    def safe_float(value: Optional[str], default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    # Create CSV Data
    def create(self, db: Session, obj_in: CSVDiamondCreate, store_id: str):
        try:
            csv_reader = csv.DictReader(StringIO(obj_in.csv_data))
            model_fields = set(CSVDiamond.__table__.columns.keys())

            diamonds = []
            updated_diamonds = []
            created_diamonds = []
            
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

                existing_diamond = db.query(CSVDiamond).filter_by(certificate_no=mapped["certificate_no"], store_id=store_id).first()

                if existing_diamond:
                    updated = False

                    for key, value in mapped.items():
                        if key == "certificate_no":
                            continue

                        old_value = getattr(existing_diamond, key, None)

                        if value != old_value:
                            setattr(existing_diamond, key, value)
                            updated = True

                    if not updated:
                        # SAME DATA + SAME CERTIFICATE + SAME STORE
                        raise HTTPException(
                            status_code=400,
                            detail=f"Duplicate certificate '{mapped['certificate_no']}' not allowed for this store"
                        )

                    updated_diamonds.append(existing_diamond)
                    diamonds.append(existing_diamond)
                else:
                    new_diamond = CSVDiamond(**mapped)
                    created_diamonds.append(new_diamond)
                    diamonds.append(new_diamond)

            db.bulk_save_objects(diamonds)
            db.commit()

            response = {
                "created_diamonds": [
                {
                    "certificate_no": d.certificate_no,
                    "s_no": d.s_no,
                    "carat": d.carat,
                    "price": d.price,
                    "selling_price": d.selling_price,
                    "description": d.description,
                    "origin": d.origin,
                } for d in created_diamonds
            ],
            "updated_diamonds": [
                {
                    "id": d.id,
                    "certificate_no": d.certificate_no,
                    "s_no": d.s_no,
                    "carat": d.carat,
                    "price": d.price,
                    "selling_price": d.selling_price,
                    "description": d.description,
                    "origin": d.origin,
                } for d in updated_diamonds
            ],
            }

            return response

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating diamonds: {str(e)}")

    # get All CSV Data
    def get_all(self, db: Session, store_id: str):
        return db.query(CSVDiamond).filter(CSVDiamond.store_id == store_id).all()

    # get filter Diamonds
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
    
    # Bulk Delete Diamonds
    def delete_diamonds(self, db: Session, store_id: str, shopify_app: str, ids: list[int]):
        try:
            deleted = (
                db.query(CSVDiamond).filter(CSVDiamond.id.in_(ids), CSVDiamond.store_id == store_id, CSVDiamond.shopify_name == shopify_app).delete(synchronize_session=False)
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
    
    # All Delete Diamonds
    def all_delete_diamonds(self, db: Session, store_id: str, shopify_app: str):
        try:
            deleted = (
                db.query(CSVDiamond).filter(CSVDiamond.store_id == store_id,func.lower(CSVDiamond.shopify_name) == shopify_app.lower(),CSVDiamond.status == 1).delete(synchronize_session=False))

            db.commit()

            return {
                "success": True, "Updated_count": deleted
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False, "error": str(e)
            }

    # Add Diamonds 
    async def get_diamonds(
        self,
        db: Session,
        store_id: str,
        shopify_name: str | None,
        query_params: dict
    ):
        if not store_id:
            return {"error": True, "status": 400, "message": "Store_id is required"}
        
        store_settings = (
            db.query(StoreSettings).filter(StoreSettings.store_id == store_id).first()
        )
        if not store_settings:
                    return {
                        "error": True, "status": 404, "message": "Store settings not found"
                    }

        logger.info(f"STORE={store_id} | CUSTOM_FEED={store_settings.custom_feed}")
        if not store_settings.custom_feed:
            stone_type = query_params.get("type")
            if not stone_type:
                return {
                    "error": True, "status": 400, "message": "'type' parameter is required"
                }
        else:
            stone_type = query_params.get("type")

        result = await get_custom_diamonds_service(db=db, store_id=store_id, query_params=query_params)
        return result

diamonds = CRUDDiamonds(CSVDiamond)
