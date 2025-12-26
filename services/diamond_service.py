import math
from loguru import logger
from sqlalchemy import asc, desc, and_
from sqlalchemy.orm import Session, aliased
from models.csv_diamond import CSVDiamond
from models.storesettings import StoreSettings
from models.diamond_pricing import DiamondPricing
from models.ingested_diamonds import IngestedDiamonds

async def get_custom_diamonds_service(db: Session, store_id: str, query_params: dict):
    try:
        if not store_id:
            return {"error": True, "status": 400, "message": "store_id is required"}

        store_setting = (
            db.query(StoreSettings)
            .filter(StoreSettings.store_id == store_id)
            .first()
        )

        if not store_setting:
            return {"error": True, "status": 404, "message": "Store setting not found"}

        page = int(query_params.get("page", 1))
        limit = int(query_params.get("limit", 10))
        offset = (page - 1) * limit

        if store_setting.custom_feed:
            Model = IngestedDiamonds
            query = db.query(Model).filter(Model.store_id == store_id)
        else:
            stone_type = query_params.get("type")
            if not stone_type:
                return {
                    "error": True,
                    "status": 400,
                    "message": "type parameter is required"
                }

            Model = CSVDiamond
            query = db.query(Model).filter(
                Model.store_id == store_id,
                Model.type == stone_type.lower()
            )

        Pricing = aliased(DiamondPricing)

        query = query.outerjoin(
            Pricing,
            and_(
                Pricing.diamond_id == Model.id,
                Pricing.store_id == store_id
            )
        )

        if query_params.get("carat_min"):
            query = query.filter(Model.carat >= float(query_params["carat_min"]))

        if query_params.get("carat_max"):
            query = query.filter(Model.carat <= float(query_params["carat_max"]))

        if query_params.get("price_min"):
            query = query.filter(Pricing.selling_price >= float(query_params["price_min"]))

        if query_params.get("price_max"):
            query = query.filter(Pricing.selling_price <= float(query_params["price_max"]))

        if query_params.get("color"):
            colors = [c.strip().upper() for c in query_params["color"].split(",")]
            query = query.filter(Model.color.in_(colors))

        if query_params.get("clarity"):
            clarities = [c.strip().upper() for c in query_params["clarity"].split(",")]
            query = query.filter(Model.clarity.in_(clarities))

        if query_params.get("cut"):
            cuts = [c.strip().lower() for c in query_params["cut"].split(",")]
            query = query.filter(Model.cut.in_(cuts))

        if query_params.get("shape"):
            shapes = [s.strip().lower() for s in query_params["shape"].split(",")]
            query = query.filter(Model.shape.in_(shapes))

        if query_params.get("fluorescence"):
            fls = [f.strip().lower() for f in query_params["fluorescence"].split(",")]
            query = query.filter(Model.fluorescence.in_(fls))

        if query_params.get("report"):
            labs = [r.strip().lower() for r in query_params["report"].split(",")]
            query = query.filter(Model.lab.in_(labs))

        sort = query_params.get("sort")
        if sort == "price_asc":
            query = query.order_by(asc(Pricing.selling_price))
        elif sort == "price_desc":
            query = query.order_by(desc(Pricing.selling_price))
        elif sort == "carat_asc":
            query = query.order_by(asc(Model.carat))
        elif sort == "carat_desc":
            query = query.order_by(desc(Model.carat))
        else:
            query = query.order_by(asc(Model.color), asc(Model.clarity))

        total_items = query.count()

        diamonds = (
            query
            .add_columns(Pricing.selling_price)
            .offset(offset)
            .limit(limit)
            .all()
        )

        diamond_list = []
        for d, selling_price in diamonds:
            diamond_list.append({
                "id": d.id,
                "lab": d.lab,
                "type": d.type,
                "carat": d.carat,
                "color": d.color,
                "clarity": d.clarity,
                "cut": d.cut,
                "shape": d.shape,
                "selling_price": float(selling_price) if selling_price else None,
                "certificate_number": d.certificate_no,
                "origin": d.origin,
                "description": d.description,
                "image_source": d.image_source or "",
                "video_source": d.video_source,
                "is_available": d.is_available,
                "fluorescence": d.fluorescence,
                "s_no": getattr(d, "s_no", None),
            })

        return {
            "error": False,
            "diamonds": diamond_list,
            "pagination": {
                "currentPage": page,
                "totalPages": math.ceil(total_items / limit),
                "totalItems": total_items,
                "itemsPerPage": limit,
            }
        }

    except Exception as e:
        logger.error("Get custom diamonds error", exc_info=True)
        return {"error": True, "message": str(e)}
