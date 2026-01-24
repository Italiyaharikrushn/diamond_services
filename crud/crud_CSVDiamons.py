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
from models.stone_margin import StoneMargin
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
    def create(self, db: Session, obj_in: CSVDiamondCreate, store_id: str, shopify_name: str = None):
        csv_reader = csv.DictReader(StringIO(obj_in.csv_data))
        model_fields = set(CSVDiamond.__table__.columns.keys())

        added_count = 0

        try:
            margins = db.query(StoneMargin).filter(StoneMargin.store_id == store_id).all()
            margin_map = {}
            for m in margins:
                margin_map.setdefault(m.type.lower(), []).append(m)

            for row in csv_reader:
                row_cleaned = {k.lower().strip().replace(" ", "_"): v for k, v in row.items()}
                mapped = {}

                field_mapping = {
                    "stone_no": "s_no",
                    "availability": "is_available",
                    "measurement": "measurements",
                }

                for k, value in row_cleaned.items():
                    db_key = field_mapping.get(k, k)
                    if db_key in model_fields:
                        if db_key in {"carat", "price", "selling_price", "table", "depth"}:
                            value = self.safe_float(value)
                            mapped[db_key] = value if value is not None else 0.0
                        elif db_key == "type":
                            mapped[db_key] = value.lower().strip() if value else "natural"
                        else:
                            mapped[db_key] = value.strip() if value not in ("", None, "None") else ""

                for num_field in ["table", "depth", "carat", "price", "selling_price"]:
                    if mapped.get(num_field) is None:
                        mapped[num_field] = 0.0

                mandatory_strings = {
                    "lab": "None",
                    "image_source": "",
                    "video_source": "",
                    "description": "No description",
                    "origin": "Unknown",
                    "measurements": "-",
                    "fluorescence": "None",
                    "polish": "None",
                    "symmetry": "None",
                    "shape": "Round",
                    "color": "-",
                    "clarity": "-"
                }

                for field, default in mandatory_strings.items():
                    if not mapped.get(field):
                        mapped[field] = default


                stone_type = mapped.get("type", "natural").lower()
                base_price = mapped.get("price", 0.0)
                carat = mapped.get("carat", 0.0)

                if stone_type in margin_map:
                    applied_margin = 0
                    for m in margin_map[stone_type]:
                        check_val = carat if m.unit == "carat" else base_price
                        if m.start <= check_val < m.end:
                            applied_margin = m.margin
                            break
                    
                    if applied_margin > 0:
                        mapped["selling_price"] = base_price + (base_price * applied_margin / 100)
                    else:
                        mapped["selling_price"] = base_price
                else:
                    mapped["selling_price"] = base_price

                cert_no = mapped.get("certificate_no") or mapped.get("s_no")
                if not cert_no:
                    continue
                mapped["certificate_no"] = str(cert_no)

                mapped.update({
                    "store_id": store_id,
                    "shopify_name": shopify_name,
                    "status": 1,
                    "is_available": mapped.get("is_available") or "Yes"
                })

                existing = db.query(CSVDiamond).filter_by(
                    certificate_no=mapped["certificate_no"], 
                    store_id=store_id
                ).first()

                if existing:
                    changed = False
                    for key, value in mapped.items():
                        if hasattr(existing, key) and getattr(existing, key) != value:
                            setattr(existing, key, value)
                            changed = True
                    if changed:
                        any_change = True
                else:
                    db.add(CSVDiamond(**mapped))
                    added_count += 1
                    any_change = True

            db.commit()
            return {"success": True, "message": f"Successfully processed {added_count} diamonds"}

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": str(e)
            }

    # get All CSV Data
    def get_all( self, db: Session, store_id: str, stone_type: str | None = None,
                color: str | None = None, clarity: str | None = None,
                price_min: Optional[float] = None, price_max: Optional[float] = None,
                carat_min: Optional[float] = None, carat_max: Optional[float] = None ):
        if not store_id:
            return []

        query = db.query(CSVDiamond).filter(CSVDiamond.store_id == store_id)

        if stone_type:
            query = query.filter(CSVDiamond.type == stone_type)
        if color:
            query = query.filter(CSVDiamond.color == color)
        if clarity:
            query = query.filter(CSVDiamond.clarity == clarity)

        if price_min is not None:
            query = query.filter(CSVDiamond.selling_price >= price_min)
        if price_max is not None:
            query = query.filter(CSVDiamond.selling_price <= price_max)

        if carat_min is not None:
            query = query.filter(CSVDiamond.carat >= carat_min)
        if carat_max is not None:
            query = query.filter(CSVDiamond.carat <= carat_max)

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
    def delete_all(self, db: Session, store_id: str, shopify_name: str, stone_type: str = None):
        try:
            query = db.query(CSVDiamond).filter(
                    CSVDiamond.store_id == store_id,
                    func.lower(CSVDiamond.shopify_name) == shopify_name.lower())
            if stone_type:
                query = query.filter(func.lower(CSVDiamond.type) == stone_type.lower())
            
            deleted = query.delete(synchronize_session=False)
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
