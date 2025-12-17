from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.CSVDiamons import CSVDiamondCreate, BulkDeleteRequest
from api.dependencies import get_db, get_current_store
from sqlalchemy.orm import Session
import crud
router = APIRouter()

# Create CSV Data
@router.post("/create-diamonds", status_code=201)
def create_diamonds(request: Request, diamonds: CSVDiamondCreate, db: Session = Depends(get_db)):
    created_diamonds = crud.diamonds.create(db=db, obj_in=diamonds, store_id=request.state.store_name)
    return created_diamonds

# Get All CSV Data
@router.get("/get-all", status_code=200)
def get_all(db:Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    data = crud.diamonds.get_all(db=db, store_id = store_name)
    return data

# Get Filter Data
@router.get("/diamonds-filters", status_code=200)
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
@router.delete("/delete-all", status_code=200)
def all_delete_diamonds( shopify_app: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    result = crud.diamonds.all_delete_diamonds( db=db, store_id=store_name, shopify_app=shopify_app)

    return result