from fastapi import APIRouter, Depends, HTTPException, Request, Query
from schemas.CSVDiamons import CSVDiamondCreate, BulkDeleteRequest
from api.dependencies import get_db, get_current_store
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import crud
router = APIRouter()

# Create CSV Data
@router.post("/csv/upload", status_code=201)
def create_diamonds(request: Request, diamonds: CSVDiamondCreate, db: Session = Depends(get_db)):
    created_diamonds = crud.diamonds.create(db=db, obj_in=diamonds, store_id=request.state.store_name)
    return created_diamonds

# Get All CSV Data
@router.get("/all-diamonds", status_code=200)
def get_all(db:Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    data = crud.diamonds.get_all(db=db, store_id = store_name)
    return data

# Get Filter Data
@router.get("/filters", status_code=200)
def diamonds_filters( stone_type: str, shopify_app: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    store_id = store_name
    result = crud.diamonds.get_diamonds_filter(db, store_id, shopify_app, stone_type,)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("message"))

    return result

# Delete Bulk Data
@router.delete("/bulk-delete", status_code=200)
def bulk_delete_diamonds(payload: BulkDeleteRequest, shopify_app: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    result = crud.diamonds.delete_diamonds(db=db, store_id=store_name, shopify_app=shopify_app, ids=payload.ids)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

# Delete All Data
@router.delete("/all-delete", status_code=200)
def all_delete_diamonds( shopify_app: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    result = crud.diamonds.all_delete_diamonds( db=db, store_id=store_name, shopify_app=shopify_app)

    return result

# get diamonds public routes
@router.get("/public/diamonds", status_code=200)
async def get_diamonds(request: Request, store_id: str | None = Query(None), db: Session = Depends(get_db)):
    store_id = store_id or getattr(request.state, "store_id", None)
    shopify_app = getattr(request.state, "shopify_app", None)

    result = await crud.diamonds.get_diamonds(
        db=db,
        store_id=store_id,
        shopify_name=shopify_app,
        query_params=dict(request.query_params)
    )

    if result["error"]:
        return {"success": False, "message": result["message"]}

    return {
        "success": True,
        "data": result["data"]
    }
