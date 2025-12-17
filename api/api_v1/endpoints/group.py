from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from api.dependencies import get_db, get_current_store
from schemas.groups import GroupCreate
import crud

router = APIRouter()

@router.post("/create-product", status_code=201)
def create_group(request: Request, payload: GroupCreate, db: Session = Depends(get_db)):
    group = crud.group.create(db=db, payload=payload, store_id=request.state.store_name)

    return {
        "message": "Group and group options created successfully",
        "group_id": group.id
    }

@router.get("/get-all", status_code=200)
def get_all_groups(db:Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    groups = crud.group.get_all(db=db, store_id = store_name)

    return groups

@router.get("/get-by-id/{group_id}", status_code=200)
def get_group_by_id(group_id: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    group = crud.group.get_by_id(db=db, store_id=store_name, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return group

@router.delete("/delete-by-id/{group_id}", status_code=200)
def delete_group_by_id(group_id: str, db: Session = Depends(get_db), store_name: str = Depends(get_current_store)):
    result = crud.group.delete_by_id(db=db, store_id=store_name, group_id=group_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Group not found or already deleted")
    return {"detail": "Group deleted successfully"}
