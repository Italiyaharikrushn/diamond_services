from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.dependencies import get_db
from schemas.ringData import RingDataCreate
from crud.crud_ring_data import ringData

router = APIRouter()

@router.post("/public/ring")
def create(ring: RingDataCreate, db: Session = Depends(get_db)):
    return ringData.create_ring_data(db, ring)

@router.get("/public/get-ring")
def get_ring_data(db: Session = Depends(get_db)):
    return ringData.get_ring_data(db)

@router.get("/public/get-single-ring/{ring_id}")
def get_single_ring(ring_id: int, db: Session = Depends(get_db)):
    return ringData.get_single_ring(db, ring_id)
