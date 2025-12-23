from fastapi import APIRouter
from pydantic import BaseModel
from util.token import create_custom_token

router = APIRouter()

class StoreNameSchema(BaseModel):
    store_name: str

@router.post("/generate-token", tags=["token"])
def generate_token(data: StoreNameSchema):
    token = create_custom_token(data.store_name)
    return {"token": token}
