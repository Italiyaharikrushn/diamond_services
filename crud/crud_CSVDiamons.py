import csv
from io import StringIO
from loguru import logger
from sqlalchemy import func
from typing import Optional
from crud.base import CRUDBase
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.csv_diamond import CSVDiamond
from models.storesettings import StoreSettings
from schemas.CSVDiamons import CSVDiamondCreate
from services.diamond_service import get_custom_diamonds_service, custom_filter_query, csv_filter_query, get_single_diamonds_service

class CRUDDiamonds(CRUDBase):
    @staticmethod
    def safe_float(value: Optional[str], default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    # Create CSV Data
    def create(self, db: Session, obj_in: CSVDiamondCreate, store_id: str):
        csv_reader = csv.DictReader(StringIO(obj_in.csv_data))
        model_fields = set(CSVDiamond.__table__.columns.keys())

        duplicate_found = False
        any_change = False

        try:
            for row in csv_reader:
                mapped = {}

                for key, value in row.items():
                    k = key.lower().replace(" ", "_")

                    if k in model_fields:
                        if k in {"carat", "price", "selling_price", "table", "depth"}:
                            mapped[k] = self.safe_float(value)
                        else:
                            mapped[k] = value if value not in ("", None, "None") else None

                if not mapped.get("certificate_no"):
                    continue

                mapped.setdefault("origin", "Unknown")
                mapped.setdefault("description", "No description")
                mapped.setdefault("selling_price", mapped.get("price"))
                mapped.setdefault("is_available", "Yes")
                mapped.setdefault("status", 1)

                mapped["store_id"] = store_id

                existing = (db.query(CSVDiamond).filter_by(certificate_no=mapped["certificate_no"], store_id=store_id).first())

                if existing:
                    changed = False

                    for key, value in mapped.items():
                        if hasattr(existing, key) and getattr(existing, key) != value:
                            setattr(existing, key, value)
                            changed = True

                    if changed:
                        any_change = True
                    else:
                        duplicate_found = True

                else:
                    db.add(CSVDiamond(**mapped))
                    any_change = True

            db.commit()

            if any_change:
                return {
                    "success": True,
                    "message": "CSV uploaded successfully"
                }

            if duplicate_found:
                return {
                    "success": False,
                    "message": "Already exists"
                }

            return {
                "success": True,
                "message": "CSV processed"
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": str(e)
            }

    # get All CSV Data
    def get_all( self, db: Session, store_id: str, stone_type: str | None = None, color: str | None = None, clarity: str | None = None ):
        query = db.query(CSVDiamond).filter(CSVDiamond.store_id == store_id)

        if stone_type:
            query = query.filter(CSVDiamond.type == stone_type)

        if color:
            query = query.filter(CSVDiamond.color == color)

        if clarity:
            query = query.filter(CSVDiamond.clarity == clarity)

        return query.all()

    # get filter Diamonds
    def get_diamonds_filter( self, db: Session, store_id: str, shopify_name: str | None = None, stone_type: str | None = None,):
        try:
            base_filters = [
                CSVDiamond.store_id == store_id
            ]

            if shopify_name:
                base_filters.append(CSVDiamond.shopify_name == shopify_name)

            if stone_type:
                base_filters.append(CSVDiamond.type == stone_type)

            colors = (
                db.query(func.distinct(CSVDiamond.color))
                .filter(*base_filters)
                .order_by(CSVDiamond.color.asc())
                .all()
            )

            clarities = (
                db.query(func.distinct(CSVDiamond.clarity))
                .filter(*base_filters)
                .order_by(CSVDiamond.clarity.asc())
                .all()
            )

            price_min, price_max = (
                db.query(
                    func.min(CSVDiamond.selling_price),
                    func.max(CSVDiamond.selling_price),
                )
                .filter(*base_filters)
                .first()
            )

            carat_min, carat_max = (
                db.query(
                    func.min(CSVDiamond.carat),
                    func.max(CSVDiamond.carat),
                )
                .filter(*base_filters)
                .first()
            )

            return {
                "success": True,
                "data": {
                    "colors": [c[0] for c in colors if c[0]],
                    "clarities": [c[0] for c in clarities if c[0]],
                    "price_range": {
                        "min": float(price_min or 0),
                        "max": float(price_max or 0),
                    },
                    "carat_range": {
                        "min": float(carat_min or 0),
                        "max": float(carat_max or 0),
                    },
                },
            }

        except Exception as e:
            print("FILTER ERROR:", e)
            return {
                "success": False,
                "message": "Failed to fetch filters",
            }
    
    # Bulk Delete Diamonds
    def delete_diamonds(self, db: Session, store_id: str, shopify_name: str, ids: list[int]):
        if not ids:
            return {"success": False, "error": "No IDs provided"}

        try:
            deleted = (
                db.query(CSVDiamond)
                .filter(
                    CSVDiamond.id.in_(ids),
                    CSVDiamond.store_id == store_id,
                    func.lower(CSVDiamond.shopify_name) == shopify_name.lower()
                )
                .delete(synchronize_session=False)
            )

            db.commit()
            return {"success": True, "deleted_count": deleted}

        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    # All Delete Diamonds
    def delete_all(self, db: Session, store_id: str, shopify_name: str):
        try:
            deleted = (
                db.query(CSVDiamond)
                .filter(
                    CSVDiamond.store_id == store_id,
                    func.lower(CSVDiamond.shopify_name) == shopify_name.lower()
                )
                .delete(synchronize_session=False)
            )

            db.commit()
            return {"success": True, "deleted_count": deleted}

        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}

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

    # get diamonds with filter for store_id & type
    async def get_diamond_filter(self, db: Session, store_id: str, query_params: dict):
        if not store_id:
            raise {"error" : True, "message" : "store_id is required"}
        
        stone_type = query_params.get("type")
        if not stone_type:
            return {"error": True, "message": "'type' parameter is required"}
        
        store_settings = (db.query(StoreSettings).filter(StoreSettings.store_id == store_id).first())

        if not store_settings:
            return {"error": True, "message": "Store Settings not found"}

        if store_settings.custom_feed:
            (
                colors,
                clarities,
                carat_min,
                carat_max,
                price_min,
                price_max
            ) = custom_filter_query(db, store_id, stone_type)

        else:
            (
                colors,
                clarities,
                carat_min,
                carat_max,
                price_min,
                price_max
            ) = csv_filter_query(db, store_id, stone_type)

        return {
        "error": False,
        "data": {
            "colors": sorted(colors),
            "clarities": sorted(clarities),
            "price_range": {
                "min": float(price_min) if price_min else 0,
                "max": float(price_max) if price_max else 0
            },
            "carat_range": {
                "min": carat_min or 0,
                "max": carat_max or 0
            }
        }
    }

    # get diamonds with filter for store_id & type & id
    async def get_diamond( self, db: Session, store_id: str, shopify_name: str | None, query_params: dict):
        if not store_id:
            return {"error": True, "status": 400, "message": "Store_id is required"}

        store_settings = ( db.query(StoreSettings) .filter(StoreSettings.store_id == store_id) .first())

        if not store_settings:
            return {
                "error": True,
                "status": 404,
                "message": "Store settings not found"
            }

        logger.info(
            f"STORE={store_id} | CUSTOM_FEED={store_settings.custom_feed}"
        )

        stone_type = query_params.get("stone_type")
        diamond_id = query_params.get("id")

        # MAIN FIX → ID COMPULSORY
        if not diamond_id:
            return {
                "error": True,
                "status": 400,
                "message": "'id' parameter is required"
            }

        # CSV feed ma stone_type compulsory
        if not store_settings.custom_feed:
            if not stone_type:
                return {
                    "error": True,
                    "status": 400,
                    "message": "'stone_type' parameter is required"
                }

        return await get_single_diamonds_service(
            db=db,
            store_id=store_id,
            query_params=query_params
        )

diamonds = CRUDDiamonds(CSVDiamond)
