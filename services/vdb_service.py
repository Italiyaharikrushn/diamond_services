import crud
import httpx
import asyncio
from datetime import datetime
from db.database import SessionLocal
from schemas import IngestedDiamondCreate
from services import finalize_ingestion

VDB_API_URL = "https://apiservices.vdbapp.com/v2/diamonds"

VDB_API_KEY = "pct_Akg7zZ0009eFf9JBV00zsw"
VDB_ACCESS_TOKEN = "00WyNRCJ_qXV2mtSPS1vPWMzbH9LW4zUGGnAuEHKsjg"


def get_vdb_auth_header():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Token token={VDB_ACCESS_TOKEN}, api_key={VDB_API_KEY}"
    }


def map_vdb_item_to_diamond(item: dict, store_id: str):
    try:
        cert = item.get("cert_num")
        if not cert:
            return None

        return IngestedDiamondCreate(
            source_diamond_id=str(item.get("id")),
            source_name="VDB",
            source_stock_id=str(item.get("stock_num")) if item.get("stock_num") else None,
            store_id=store_id,

            lab=item.get("lab") or None,
            type="lab" if item.get("type") == "lab_grown_diamond" else "natural",
            carat=float(item.get("size") or 0),

            color=item.get("color"),
            clarity=item.get("clarity"),
            cut=item.get("cut"),
            shape=item.get("shape"),

            price=float(item.get("total_sales_price") or 0),
            certificate_no=cert,

            vendor=str(item.get("vendor_id")) if item.get("vendor_id") else "VDB",

            is_available=True,

            origin=item.get("origin"),
            mesurements=item.get("measurement"),
            polish=item.get("polish"),
            symmetry=item.get("symmetry"),
            fluorescence=item.get("fluorescence_intensity_short"),
            table=float(item.get("table")) if item.get("table") else None,
            depth=float(item.get("depth")) if item.get("depth") else None,
            girdle=item.get("girdle"),
            bgm=item.get("bgm"),
            treatment=item.get("treatment"),
            culet=item.get("culet"),
            location=item.get("item_location"),
        )

    except Exception as e:
        return None

async def ingest_vdb_diamonds( process_id: int, process_starting_time: datetime, store_id: str):
    
    page = 1
    page_size = 150
    total_processed = 0
    errors = []

    db = SessionLocal()

    try:
        while True:
            params = {
                "show_unavailable": "false",
                "type": "lab_grown_diamond",
                "color_from": "J",
                "color_to": "D",
                "clarity_from": "SI3",
                "clarity_to": "FL",
                "page_number": page,
                "page_size": page_size,
                "shapes[]": [
                    "Round", "Oval", "Princess", "Cushion", "Radiant",
                    "Emerald", "Heart", "Marquise", "Pear", "Asscher"
                ]
            }

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(
                    VDB_API_URL,
                    headers=get_vdb_auth_header(),
                    params=params
                )

            if response.status_code != 200:
                errors.append({
                    "page": page,
                    "error": response.text
                })
                page += 1
                continue

            data = response.json()
            body = data.get("response", {}).get("body", {})
            diamonds = body.get("diamonds", [])
            total_found = body.get("total_diamonds_found", 0)

            if not diamonds:
                break

            mapped_diamonds = []
            for item in diamonds:
                d = map_vdb_item_to_diamond(item, store_id)
                if d:
                    mapped_diamonds.append(d)

            print(f"[VDB] Page {page} → API diamonds: {len(diamonds)}")
            print(f"[VDB] Page {page} → Mapped diamonds: {len(mapped_diamonds)}")

            if mapped_diamonds:
                crud.diamond.bulk_upsert_diamonds(db, mapped_diamonds)
                total_processed += len(mapped_diamonds)

                crud.diamond.update_ingestion_process(
                    db,
                    process_id,
                    {
                        "processed_items": total_processed,
                        "total_items": total_found or total_processed
                    }
                )

            if len(diamonds) < page_size:
                break

            page += 1
            await asyncio.sleep(0.1)

        await finalize_ingestion.finalize_diamond_ingestion(
            db,
            process_id,
            process_starting_time,
            "VDB",
            total_processed,
            errors,
            store_id
        )

    except Exception as e:
        crud.diamond.update_ingestion_process(
            db,
            process_id,
            {
                "status": "failed",
                "logs": [{"fatal_error": str(e)}]
            }
        )
        raise
    finally:
        db.close()
