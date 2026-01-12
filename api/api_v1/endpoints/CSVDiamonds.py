import crud
from sqlalchemy.orm import Session
from api.dependencies import get_db, get_current_store
from schemas.CSVDiamons import CSVDiamondCreate, BulkDeleteRequest
from fastapi import APIRouter, Depends, HTTPException, Request, Query
router = APIRouter()

# Create CSV Data
@router.post("/csv/upload", status_code=201)
def create_diamonds(request: Request, diamonds: CSVDiamondCreate, db: Session = Depends(get_db)):
    created_diamonds = crud.diamonds.create(db=db, obj_in=diamonds, store_id=request.state.store_name)
    return created_diamonds

# Get All CSV Data
@router.get("/all-diamonds", status_code=200)
def get_all(
    db:Session = Depends(get_db),
    stone_type: str | None = None,
    color: str | None = None,
    clarity: str | None = None,
    store_name: str = Depends(get_current_store),
):
    data = crud.diamonds.get_all(
        db=db,
        store_id=store_name,
        stone_type=stone_type,
        color=color,
        clarity=clarity,
    )
    return data

# Get Filter Data
@router.get("/filters")
def diamonds_filters( db: Session = Depends(get_db), store_name: str = Depends(get_current_store), stone_type: str | None = None, shopify_name: str | None = None,):
    return crud.diamonds.get_diamonds_filter(
        db=db,
        store_id=store_name,
        shopify_name=shopify_name or None,
        stone_type=stone_type or None,
    )

# Delete Bulk Data
@router.delete("/bulk-delete", status_code=200)
def bulk_delete_diamonds( payload: BulkDeleteRequest, shopify_name: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    return crud.diamonds.delete_diamonds(db, store_name, shopify_name, payload.ids)

# Delete All Data
@router.delete("/all-delete", status_code=200)
def all_delete_diamonds( shopify_name: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    return crud.diamonds.delete_all(db, store_name, shopify_name)

# get diamonds public routes
@router.get("/public/diamonds", status_code=200)
async def get_diamonds(request: Request, store_id: str | None = Query(None), db: Session = Depends(get_db)):
    store_id = store_id or getattr(request.state, "store_id", None)
    shopify_app = getattr(request.state, "shopify_app", None)

    result = await crud.diamonds.get_diamonds( db=db, store_id=store_id, shopify_name=shopify_app, query_params=dict(request.query_params))

    if result["error"]:
        return {"success": False, "message": result["message"]}

    return {
        "success": True,
        "data": result
    }

# get diamonds with filter for store_id & type
@router.get("/public/diamonds/filters", status_code=200)
async def get_diamond_filters( request: Request, store_id: str | None = Query(None), db: Session = Depends(get_db)):
    store_id = store_id or getattr(request.state, "store_id", None)

    result = await crud.diamonds.get_diamond_filter( db=db, store_id=store_id, query_params=dict(request.query_params))

    if result["error"]:
        return {"success": False, "message": result["message"]}

    return {
        "success": True,
        "data": result["data"]
    }

# get diamonds with filter for store_id & type & id
@router.get("/public/get-diamond", status_code=200)
async def get_diamonds(
    request: Request,
    store_id: str | None = Query(None),
    db: Session = Depends(get_db)
):
    store_id = store_id or getattr(request.state, "store_id", None)
    shopify_app = getattr(request.state, "shopify_app", None)

    result = await crud.diamonds.get_diamond(
        db=db,
        store_id=store_id,
        shopify_name=shopify_app,
        query_params=dict(request.query_params)
    )

    if result["error"]:
        return {"success": False, "message": result["message"]}

    return {
        "success": True,
        "data": result
    }
