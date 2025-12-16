from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.dependencies import get_db
from schemas.groups import GroupCreate
import crud

router = APIRouter()

@router.post("/groups", status_code=201)
def create_group( payload: GroupCreate, db: Session = Depends(get_db)):
    group = crud.group.create(db=db, payload=payload)

    return {
        "message": "Group and group options created successfully",
        "group_id": group.id
    }
