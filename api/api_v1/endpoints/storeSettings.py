import crud
from sqlalchemy.orm import Session
from api.dependencies import get_db
from fastapi import APIRouter, Depends, Request
from schemas.storesttings import StoreSettingsCreate

router = APIRouter()

# CRUD Store Settings
@router.post("/store-settings", status_code=201)
def create_store( request: Request, data: StoreSettingsCreate, db: Session = Depends(get_db)):
    store_id = request.state.store_name
    return crud.storesettings.create(db=db, payload=data, store_id=store_id)

# Get Store Settings
@router.get("/store-settings", response_model=dict)
def get_store_settings(request: Request, db: Session = Depends(get_db)):
    store_id = request.state.store_name
    store = crud.storesettings.get_by_store_id(db=db, store_id=store_id)

    response = {
        "success": True,
        "settings": store.settings,
        "custom_feed": store.custom_feed
    }
    return response

# Delete Store Settings
@router.delete("/store-settings", status_code=200)
def delete_store_settings(request: Request, db: Session = Depends(get_db)):
    store_id = request.state.store_name
    store = crud.storesettings.delete_by_store_id(db=db, store_id=store_id)

    return {"success": True, "message": "Store settings deleted successfully", "store_id": store_id}
