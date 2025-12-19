from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.CSVGemstone import CSVGemstoneCreate, BulkDeleteRequest
from api.dependencies import get_db, get_current_store
from sqlalchemy.orm import Session
import crud
router = APIRouter()

# Create CSV Data
@router.post("/csv/upload-gemstones", status_code=201)
def create_gemstone(request: Request, gemstones: CSVGemstoneCreate, db: Session = Depends(get_db)):
    created_gemstone = crud.gemstone.create(db=db, obj_in=gemstones, store_id=request.state.store_name)
    return created_gemstone

# Get All CSV Data
@router.get("/gemstones", status_code=200)
def get_all(db:Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    data = crud.gemstone.get_all(db=db, store_id = store_name)
    return data

# Get Filter Data
@router.get("/gemstones/filters", status_code=200)
def gemstone_filters(shopify_app: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    store_id = store_name 
    result = crud.gemstone.get_gemstone_filter(db, store_id, shopify_app)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result

# Delete Bulk Data
@router.delete("/gemstones/bulk", status_code=200)
def bulk_delete_gemstones(payload: BulkDeleteRequest, shopify_app: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    result = crud.gemstone.bulk_delete_gemstones(db=db, store_id=store_name, shopify_app=shopify_app, ids=payload.ids)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

# Delete All Data
@router.delete("/gemstones/all", status_code=200)
def soft_delete_all_gemstones( shopify_app: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    result = crud.gemstone.all_delete_gemstones( db=db, store_id=store_name, shopify_app=shopify_app)

    return result
