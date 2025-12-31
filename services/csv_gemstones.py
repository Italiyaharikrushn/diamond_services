import math
import logging
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from models.csv_gemstones import CSVGemstone

logger = logging.getLogger(__name__)

# Get CSV Gemstones
async def get_csv_gemstones( db: Session, store_id: str, shopify_app: str | None, query_params: dict):
    try:
        page = int(query_params.get("page", 1))
        limit = int(query_params.get("limit", 10))
        offset = (page - 1) * limit

        query = db.query(CSVGemstone).filter(
            CSVGemstone.store_id == store_id
        )

        if shopify_app:
            query = query.filter(CSVGemstone.shopify_name == shopify_app)

        # filters
        if query_params.get("carat_min"):
            query = query.filter(CSVGemstone.carat >= float(query_params["carat_min"]))

        if query_params.get("carat_max"):
            query = query.filter(CSVGemstone.carat <= float(query_params["carat_max"]))

        if query_params.get("price_min"):
            query = query.filter(
                CSVGemstone.selling_price >= float(query_params["price_min"])
            )

        if query_params.get("price_max"):
            query = query.filter(
                CSVGemstone.selling_price <= float(query_params["price_max"])
            )

        if query_params.get("color"):
            colors = [c.strip().upper() for c in query_params["color"].split(",")]
            query = query.filter(CSVGemstone.color.in_(colors))

        if query_params.get("clarity"):
            clarities = [c.strip().upper() for c in query_params["clarity"].split(",")]
            query = query.filter(CSVGemstone.clarity.in_(clarities))

        if query_params.get("shape"):
            shapes = [s.strip().lower() for s in query_params["shape"].split(",")]
            query = query.filter(CSVGemstone.shape.in_(shapes))

        # sorting
        sort = query_params.get("sort")
        if sort == "price_asc":
            query = query.order_by(asc(CSVGemstone.selling_price))
        elif sort == "price_desc":
            query = query.order_by(desc(CSVGemstone.selling_price))
        elif sort == "carat_asc":
            query = query.order_by(asc(CSVGemstone.carat))
        elif sort == "carat_desc":
            query = query.order_by(desc(CSVGemstone.carat))
        else:
            query = query.order_by(desc(CSVGemstone.id))

        total_items = query.count()

        gemstones = query.offset(offset).limit(limit).all()

        data = []
        for g in gemstones:
            data.append({
                "type": g.type,
                "sub_type": g.sub_type,
                "carat": g.carat,
                "color": g.color,
                "clarity": g.clarity,
                "shape": g.shape,
                "selling_price": g.selling_price,
                "image_source": g.image_source or "",
                "video_source": g.video_source,
                "fluorescence": g.fluorescence,
                "is_available": g.is_available,
            })

        return {
            "error": False,
            "gemstones": data,
            "pagination": {
                "currentPage": page,
                "totalPages": math.ceil(total_items / limit),
                "totalItems": total_items,
                "itemsPerPage": limit,
            }
        }

    except Exception as e:
        logger.error("Get CSV gemstones error", exc_info=True)
        return {
            "error": True,
            "message": str(e)
        }
