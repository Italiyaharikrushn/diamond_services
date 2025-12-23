import math
from loguru import logger
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from models.csv_diamond import CSVDiamond

async def get_custom_diamonds_service(db: Session, store_id: str, query_params: dict):
    try:
        if not store_id:
            return {"error": True, "status": 400, "message": "store_id is required"}

        page = int(query_params.get("page", 1))
        limit = int(query_params.get("limit", 10))
        offset = (page - 1) * limit

        carat_min = query_params.get("carat_min")
        carat_max = query_params.get("carat_max")
        price_min = query_params.get("price_min")
        price_max = query_params.get("price_max")
        color = query_params.get("color")
        clarity = query_params.get("clarity")
        cut = query_params.get("cut")
        shape = query_params.get("shape")
        stone_type = query_params.get("type")
        fluorescence = query_params.get("fluorescence")
        report = query_params.get("report")
        sort = query_params.get("sort")

        query = db.query(CSVDiamond).filter(CSVDiamond.store_id == store_id)

        if carat_min:
            query = query.filter(CSVDiamond.carat >= float(carat_min))
        if carat_max:
            query = query.filter(CSVDiamond.carat <= float(carat_max))
        if price_min:
            query = query.filter(CSVDiamond.selling_price >= float(price_min))
        if price_max:
            query = query.filter(CSVDiamond.selling_price <= float(price_max))
        if color:
            color_list = [c.strip().upper() for c in color.split(",")]
            query = query.filter(CSVDiamond.color.in_(color_list))
        if clarity:
            clarity_list = [c.strip().upper() for c in clarity.split(",")]
            query = query.filter(CSVDiamond.clarity.in_(clarity_list))
        if cut:
            cut_list = [c.strip().lower() for c in cut.split(",")]
            query = query.filter(CSVDiamond.cut.in_(cut_list))
        if shape:
            shape_list = [s.strip().lower() for s in shape.split(",")]
            query = query.filter(CSVDiamond.shape.in_(shape_list))
        if stone_type:
            query = query.filter(CSVDiamond.type == stone_type.lower())
        if fluorescence:
            fluorescence_list = [f.strip().lower() for f in fluorescence.split(",")]
            query = query.filter(CSVDiamond.fluorescence.in_(fluorescence_list))
        if report:
            report_list = [r.strip().lower() for r in report.split(",")]
            query = query.filter(CSVDiamond.lab.in_(report_list))

        if sort == "price_asc":
            query = query.order_by(asc(CSVDiamond.selling_price))
        elif sort == "price_desc":
            query = query.order_by(desc(CSVDiamond.selling_price))
        elif sort == "carat_asc":
            query = query.order_by(asc(CSVDiamond.carat))
        elif sort == "carat_desc":
            query = query.order_by(desc(CSVDiamond.carat))
        else:
            query = query.order_by(asc(CSVDiamond.color), asc(CSVDiamond.clarity))

        total_items = query.count()

        diamonds = query.offset(offset).limit(limit).all()

        diamond_list = []
        for d in diamonds:
            diamond_list.append({
                "id": d.id,
                "lab": d.lab,
                "type": d.type,
                "carat": d.carat,
                "color": d.color,
                "clarity": d.clarity,
                "cut": d.cut,
                "shape": d.shape,
                "selling_price": d.selling_price,
                "certificate_number": d.certificate_no,
                "origin": d.origin,
                "description": d.description,
                "image_source": d.image_source or "",
                "video_source": d.video_source,
                "is_available": d.is_available,
                "fluorescence": d.fluorescence,
                "s_no": d.s_no,
            })

        total_pages = math.ceil(total_items / limit)

        return {
            "error": False,
            "diamonds": diamond_list,
            "pagination": {
                "currentPage": page,
                "totalPages": total_pages,
                "totalItems": total_items,
                "itemsPerPage": limit,
            }
        }

    except Exception as e:
        logger.error("Get custom diamonds error", exc_info=True)
        return {"error": True, "message": str(e)}
