from typing import Optional
import crud
from sqlalchemy.orm import Session
from api.dependencies import get_db, get_current_store
from middlewares.check_feed import check_feed
from schemas.CSVGemstone import CSVGemstoneCreate, BulkDeleteRequest
from fastapi import APIRouter, Depends, HTTPException, Request, Query
router = APIRouter()

# Create CSV Data
@router.post("/csv/upload-gemstones", status_code=201)
def create_gemstone(request: Request, gemstones: CSVGemstoneCreate, db: Session = Depends(get_db)):
    created_gemstone = crud.gemstone.create(db=db, obj_in=gemstones, store_id=request.state.store_name, shopify_name=request.state.shopify_name)
    return created_gemstone

# Get All CSV Data
@router.get("/all-gemstones", status_code=200)
def get_all(color: Optional[str] = None, clarity: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, min_carat: Optional[float] = None, max_carat: Optional[float] = None, db:Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    data = crud.gemstone.get_all(db=db, store_id = store_name, color=color, clarity=clarity, stone_type=None, price_min=min_price, price_max=max_price, carat_min=min_carat, carat_max=max_carat)
    return data

# Get Filter Data
@router.get("/filters", status_code=200)
def gemstone_filters(shopify_name: Optional[str] = None, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    result = crud.gemstone.get_gemstone_filter(db, store_name, shopify_name)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result

# Delete Bulk Data
@router.delete("/bulk-delete", status_code=200)
def bulk_delete_gemstones(payload: BulkDeleteRequest, shopify_name: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    result = crud.gemstone.bulk_delete_gemstones(db=db, store_id=store_name, shopify_name=shopify_name, ids=payload.ids)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

# Delete All Data
@router.delete("/all-delete", status_code=200)
def soft_delete_all_gemstones( shopify_name: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    result = crud.gemstone.all_delete_gemstones( db=db, store_id=store_name, shopify_name=shopify_name)

    return result

# Public gemstones
@router.get("/public/gemstones", status_code=200)
async def get_gemstones( request: Request, _: None = Depends(check_feed), store_id: str | None = Query(None), db: Session = Depends(get_db)):
    store_id = store_id or getattr(request.state, "store_id", None)
    shopify_name = getattr(request.state, "shopify_name", None)
    feed_config = request.state.feed_config

    result = await crud.gemstone.get_gemstones( db=db, store_id=store_id, shopify_name=shopify_name, query_params=dict(request.query_params),feed_config=feed_config)

    if result["error"]:
        return {
            "success": False,
            "message": result.get("message", "Something went wrong")
        }

    return {
        "success": True,
        "data": result
    }

# Public gemstone filters
@router.get("/public/gemstones/filters", status_code=200)
async def gemstone_filters( request: Request, _: None = Depends(check_feed), store_id: str | None = Query(None), db: Session = Depends(get_db)):
    store_id = store_id or getattr(request.state, "store_id", None)
    shopify_name = getattr(request.state, "shopify_name", None)

    if not store_id:
        return {
            "success": False,
            "message": "store_id is required"
        }

    result = await crud.gemstone.get_gemstone_filters(
        db=db,
        store_id=store_id,
        shopify_name=shopify_name,
    )

    if result["error"]:
        return {
            "success": False,
            "message": result.get("message", "Something went wrong")
        }

    return {
        "success": True,
        "data": result["data"]
    }

# Public get gemstone by id
@router.get("/public/gemstones/get-gemstone", status_code=200)
async def get_gemstone( request: Request, _: None = Depends(check_feed), id: int | None = Query(None), stone_type: str | None = Query(None), store_id: str | None = Query(None), db: Session = Depends(get_db),):
    store_id = store_id or getattr(request.state, "store_id", None)
    shopify_name = getattr(request.state, "shopify_name", None)
    custom_feed = request.state.custom_feed
    feed_config = request.state.feed_config

    if not id:
        return {
            "success": False,
            "message": "id is required"
        }

    result = await crud.gemstone.get_gemstone_by_id( db=db, id=id, store_id=store_id, shopify_name=shopify_name, stone_type=stone_type, custom_feed=custom_feed, feed_config=feed_config)

    if result["error"]:
        return {
            "success": False,
            "message": result.get("message", "Something went wrong")
        }

    return {
        "success": True,
        "data": result["data"]
    }
