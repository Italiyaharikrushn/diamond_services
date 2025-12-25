import crud
import httpx, asyncio
from db.database import SessionLocal
from services import finalize_ingestion
from schemas import IngestedDiamondCreate
from util.utils import build_basic_auth_header, normalize_color, normalize_clarity, AARUSH_BASE_URL, AARUSH_USERNAME, AARUSH_PASSWORD

async def fetch_aarush_page(page: int):
    print("CALLING AARUSH API PAGE:", page)

    headers = build_basic_auth_header(AARUSH_USERNAME, AARUSH_PASSWORD)
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{AARUSH_BASE_URL}?page={page}",
            headers=headers
        )

        resp.raise_for_status()
        data = resp.json()

        return data.get("data", []), data.get("next_page_url")

def map_aarush_item_to_diamond(item: dict, store_id: str):
    if not item or not item.get("cert_num"):
        return None

    color = normalize_color(item.get("color"))
    clarity = normalize_clarity(item.get("clarity"))

    if not color or not clarity:
        return None

    mesurements = "x".join(str(item.get(f"meas_{k}"))
        for k in ["length", "width", "depth"]
        if item.get(f"meas_{k}")
        )

    return IngestedDiamondCreate(
        source_diamond_id=item.get("stock_num",""),
        source_name="Aarush",
        store_id=store_id,
        lab=item.get("lab","").upper(),
        type="lab",
        carat=float(item.get("size") or 0),
        color=color,
        clarity=clarity,
        cut=item.get("cut"),
        shape=item.get("shape"),
        price=float(item.get("total_sales_price") or item.get("sell_price") or 0),
        certificate_no=item.get("cert_num"),
        origin=item.get("country"),
        description=item.get("description") or item.get("comments"),
        image_source=item.get("image_url"),
        video_source=item.get("video_url"),
        is_available=(item.get("availability","").upper()=="AV"),
        vendor="Aarush",
        mesurements=mesurements,
        polish=item.get("polish"),
        symmetry=item.get("symmetry"),
        fluorescence=item.get("fluor_intensity") or item.get("fluor_color"),
        table=float(item.get("table_percent")) if item.get("table_percent") else None,
        depth=float(item.get("depth_percent")) if item.get("depth_percent") else None,
        girdle=item.get("girdle_max") or item.get("girdle_condition"),
        bgm=item.get("bgm"),
        treatment=item.get("treatment"),
        culet=item.get("culet_size") or item.get("culet_condition"),
        location=", ".join(filter(None,[item.get("city"),item.get("state"),item.get("country")]))
    )

async def ingest_aarush_diamonds( process_id: int, process_starting_time, store_id: str):
    db = SessionLocal()
    try:
        page = 1
        total_processed = 0
        errors = []

        while True:
            items, next_url = await fetch_aarush_page(page)
            if not items:
                break

            diamonds = []
            for item in items:
                d = map_aarush_item_to_diamond(item, store_id)
                if d:
                    diamonds.append(d)

            if diamonds:
                result = crud.diamond.bulk_upsert_diamonds(db, diamonds)
                total_processed += result["upserted"]

                crud.diamond.update_ingestion_process(
                    db,
                    process_id,
                    {
                        "processed_items": total_processed,
                        "total_items": total_processed
                    }
                )

            if not next_url:
                break

            page += 1
            await asyncio.sleep(0.2)

        await finalize_ingestion.finalize_diamond_ingestion(
            db,
            process_id,
            process_starting_time,
            "Aarush",
            total_processed,
            errors,
            store_id
        )
    finally:
        db.close()
