import crud
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from api.dependencies import get_db, get_current_store
from schemas.StoneMargin import StoneMarginCreate, StoneMarginResponse

router = APIRouter()

# CRUD Stone Margin
@router.post("/stone_margin", status_code=201, response_model=StoneMarginResponse)
def crud_stone_margin(data: StoneMarginCreate, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    data.store_id = store_name
    margin = crud.margin.create(db=db, obj_in=data)
    return margin

# Get Stone Margin
@router.get("/stone_margin", status_code=200, response_model=dict)
def get_stone_margin(db: Session = Depends(get_db),store_name: str = Depends(get_current_store)):
    margins = crud.margin.get_stone(db=db, store_id=store_name)
    return {"Success" : True, "Data" : margins}
