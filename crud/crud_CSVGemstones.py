import csv
import logging
from io import StringIO
from typing import Optional
from sqlalchemy import func
from crud.base import CRUDBase
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.csv_gemstones import CSVGemstone
from schemas.CSVGemstone import CSVGemstoneCreate
from services.csv_gemstones import get_csv_gemstones

logger = logging.getLogger(__name__)

class CRUDGemstones(CRUDBase):
    @staticmethod
    def safe_float(value: Optional[str], default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    # Create CSV Data
    def create(self, db: Session, obj_in: CSVGemstoneCreate, store_id: str, shopify_name: str = None):
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
                mapped["shopify_name"] = shopify_name

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
    def get_gemstone_filter(self, db: Session, store_id: str, shopify_name: str):
        try:
            Base_filter = [
                CSVGemstone.store_id == store_id,
                CSVGemstone.shopify_name == shopify_name
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
    def bulk_delete_gemstones(self, db: Session, store_id: str, shopify_name: str, ids: list[int]):
        try:
            deleted = (
                db.query(CSVGemstone).filter(CSVGemstone.id.in_(ids), CSVGemstone.store_id == store_id, CSVGemstone.shopify_name == shopify_name).delete(synchronize_session=False)
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
    def all_delete_gemstones(self, db: Session, store_id: str, shopify_name: str):
        try:
            deleted = (db.query(CSVGemstone).filter(CSVGemstone.store_id == store_id,func.lower(CSVGemstone.shopify_name) == shopify_name.lower(),CSVGemstone.status == 1).delete(synchronize_session=False))

            db.commit()

            return {
                "success": True, "Updated_count": deleted
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False, "error": str(e)
            }

    # Get Gemstones
    async def get_gemstones( self, db: Session, store_id: str, shopify_name: str | None, query_params: dict, feed_config: dict):
        stone_type = query_params.get("type")

        if not stone_type:
            return {"error": True, "message": "'type' is required"}

        if stone_type not in feed_config:
            return {
                "error": True,
                "message": f"feed_config not found for {stone_type}"
            }

        config_type = feed_config[stone_type]["type"]

        if config_type == "CSV":
            return await get_csv_gemstones( db=db, store_id=store_id, shopify_name=shopify_name, query_params=query_params)

        return {
            "error": True,
            "message": f"{config_type} feed not supported"
        }

    # Get Gemstone Filters
    async def get_gemstone_filters(
        self,
        db: Session,
        store_id: str,
        shopify_name: str | None,
    ):
        try:
            query = db.query(CSVGemstone).filter(
                CSVGemstone.store_id == store_id
            )

            if shopify_name:
                query = query.filter(CSVGemstone.shopify_name == shopify_name)

            colors = (
                query.with_entities(CSVGemstone.color)
                .distinct()
                .order_by(CSVGemstone.color.asc())
                .all()
            )

            clarities = (
                query.with_entities(CSVGemstone.clarity)
                .distinct()
                .order_by(CSVGemstone.clarity.asc())
                .all()
            )

            price_range = db.query(
                func.min(CSVGemstone.selling_price),
                func.max(CSVGemstone.selling_price)
            ).filter(
                CSVGemstone.store_id == store_id
            )

            if shopify_name:
                price_range = price_range.filter(
                    CSVGemstone.shopify_name == shopify_name
                )

            min_price, max_price = price_range.first()

            carat_range = db.query(
                func.min(CSVGemstone.carat),
                func.max(CSVGemstone.carat)
            ).filter(
                CSVGemstone.store_id == store_id
            )

            if shopify_name:
                carat_range = carat_range.filter(
                    CSVGemstone.shopify_name == shopify_name
                )

            min_carat, max_carat = carat_range.first()

            return {
                "error": False,
                "data": {
                    "colors": [c[0] for c in colors if c[0]],
                    "clarities": [c[0] for c in clarities if c[0]],
                    "price_range": {
                        "min": float(min_price) if min_price else 0,
                        "max": float(max_price) if max_price else 0
                    },
                    "carat_range": {
                        "min": float(min_carat) if min_carat else 0,
                        "max": float(max_carat) if max_carat else 0
                    }
                }
            }

        except Exception as e:
            logger.error("Get gemstone filters error", exc_info=True)
            return {
                "error": True,
                "message": str(e)
            }

    # Get Gemstone by ID
    async def get_gemstone_by_id(
        self,
        db: Session,
        id: int,
        store_id: str,
        shopify_name: str | None,
        stone_type: str | None,
        custom_feed: bool,
        feed_config: dict
    ):
        try:
            if custom_feed:
                logger.warning("Custom feed not yet supported for gemstones")
                return {
                    "error": True,
                    "message": "Custom feed not yet supported for gemstones"
                }

            if not stone_type:
                return {
                    "error": True,
                    "message": "stone_type is required"
                }

            if not feed_config or stone_type not in feed_config:
                logger.error(f"feed_config not found for stone_type: {stone_type}")
                return {
                    "error": True,
                    "message": f"feed_config not found for stone_type: {stone_type}"
                }

            config_type = feed_config[stone_type].get("type")

            if not config_type:
                return {
                    "error": True,
                    "message": f"stone_type not found in feed_config for stone_type: {stone_type}"
                }

            logger.info(
                f"Getting gemstone id={id}, store={store_id}, "
                f"stone_type={stone_type}, config_type={config_type}"
            )

            if config_type == "CSV":
                query = db.query(CSVGemstone).filter(
                    CSVGemstone.id == id,
                    CSVGemstone.store_id == store_id
                )

                if shopify_name:
                    query = query.filter(CSVGemstone.shopify_name == shopify_name)

                gemstone = query.first()

            elif config_type == "VDB":
                logger.warning("VDB feed not yet supported for gemstones")
                return {
                    "error": True,
                    "message": "VDB feed not yet supported for gemstones"
                }

            else:
                return {
                    "error": True,
                    "message": f"Unsupported config type: {config_type} for stone_type: {stone_type}"
                }

            if not gemstone:
                return {
                    "error": True,
                    "message": "gemstone not found"
                }

            data = {
                "id": gemstone.id,
                "lab": gemstone.lab,
                "type": gemstone.type,
                "sub_type": gemstone.sub_type,
                "carat": gemstone.carat,
                "color": gemstone.color,
                "clarity": gemstone.clarity,
                "cut": gemstone.cut,
                "shape": gemstone.shape,
                "selling_price": gemstone.selling_price,
                "certificate_number": gemstone.certificate_no,
                "origin": gemstone.origin,
                "description": gemstone.description,
                "image_source": gemstone.image_source or "",
                "video_source": gemstone.video_source,
                "is_available": gemstone.is_available,
                "fluorescence": gemstone.fluorescence,
                "table": gemstone.table,
                "depth": gemstone.depth,
                "girdle": gemstone.girdle,
                "bgm": gemstone.bgm,
                "treatment": gemstone.treatment,
                "culet": gemstone.culet,
                "measurements": gemstone.measurements,
                "polish": gemstone.polish,
                "symmetry": gemstone.symmetry,
            }

            return {
                "error": False,
                "data": data
            }

        except Exception as e:
            logger.error("Get gemstone error", exc_info=True)
            return {
                "error": True,
                "message": str(e)
            }

gemstone = CRUDGemstones(CSVGemstone)
