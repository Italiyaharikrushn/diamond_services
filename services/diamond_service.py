import math
from loguru import logger
from sqlalchemy import asc, desc, and_, func
from sqlalchemy.orm import Session, aliased
from models.csv_diamond import CSVDiamond
from models.storesettings import StoreSettings
from models.diamond_pricing import DiamondPricing
from models.ingested_diamonds import IngestedDiamonds

# get diamonds with filter for store_id & type
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

# get diamonds with filter for store_id & type & Id
async def get_single_diamonds_service(
    db: Session,
    store_id: str,
    query_params: dict
):
    stone_type = query_params.get("stone_type")
    diamond_id = query_params.get("id")

    store_settings = (
        db.query(StoreSettings)
        .filter(StoreSettings.store_id == store_id)
        .first()
    )

    # ---------- MODEL SELECTION ----------
    if store_settings.custom_feed:
        Model = IngestedDiamonds
        query = db.query(Model).filter(Model.store_id == store_id)

        if stone_type:
            query = query.filter(Model.type == stone_type)

    else:
        Model = CSVDiamond
        query = db.query(Model).filter(
            Model.store_id == store_id,
            Model.type == stone_type
        )

    # ---------- ID FILTER (MAIN REQUIREMENT) ----------
    if diamond_id:
        if not str(diamond_id).isdigit():
            return {
                "error": True,
                "status": 400,
                "message": "Invalid diamond id"
            }

        query = query.filter(Model.id == int(diamond_id))

    diamond = query.first()

    if not diamond:
        return {
            "error": True,
            "status": 404,
            "message": "Diamond not found"
        }

    return {
        "error": False,
        "diamond": {
            "id": diamond.id,
            "type": diamond.type,
            "carat": diamond.carat,
            "color": diamond.color,
            "clarity": diamond.clarity,
            "cut": diamond.cut,
            "shape": diamond.shape,
            "lab": diamond.lab,
            "certificate_number": diamond.certificate_no,
            "origin": diamond.origin,
            "description": diamond.description,
            "image_source": diamond.image_source or "",
            "video_source": diamond.video_source,
            "fluorescence": diamond.fluorescence,
            "is_available": diamond.is_available,
        }
    }

def csv_filter_query(db: Session, store_id: str, stone_type: str):
    base_query = db.query(CSVDiamond).filter(
        CSVDiamond.store_id == store_id,
        CSVDiamond.type == stone_type
    )

    colors = [
        c[0] for c in
        base_query.with_entities(CSVDiamond.color).distinct().all()
        if c[0]
    ]

    clarities = [
        c[0] for c in
        base_query.with_entities(CSVDiamond.clarity).distinct().all()
        if c[0]
    ]

    carat_min, carat_max = base_query.with_entities(
        func.min(CSVDiamond.carat),
        func.max(CSVDiamond.carat)
    ).first()

    price_min, price_max = base_query.with_entities(
        func.min(CSVDiamond.selling_price),
        func.max(CSVDiamond.selling_price)
    ).first()

    return colors, clarities, carat_min, carat_max, price_min, price_max

def custom_filter_query(db: Session, store_id: str, stone_type: str):
    diamond_query = db.query(IngestedDiamonds).filter(
        IngestedDiamonds.store_id == store_id,
        IngestedDiamonds.type == stone_type
    )

    colors = [
        c[0].value for c in
        diamond_query.with_entities(IngestedDiamonds.color).distinct().all()
    ]

    clarities = [
        c[0].value for c in
        diamond_query.with_entities(IngestedDiamonds.clarity).distinct().all()
    ]

    carat_min, carat_max = diamond_query.with_entities(
        func.min(IngestedDiamonds.carat),
        func.max(IngestedDiamonds.carat)
    ).first()

    price_min, price_max = (
        db.query(
            func.min(DiamondPricing.selling_price),
            func.max(DiamondPricing.selling_price)
        )
        .join(
            IngestedDiamonds,
            IngestedDiamonds.id == DiamondPricing.diamond_id
        )
        .filter(
            DiamondPricing.store_id == store_id,
            IngestedDiamonds.type == stone_type
        )
        .first()
    )

    return colors, clarities, carat_min, carat_max, price_min, price_max
