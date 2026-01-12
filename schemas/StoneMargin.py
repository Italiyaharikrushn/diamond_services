from pydantic import BaseModel
from typing import List, Optional

class StoneMarginBase(BaseModel):
    start: float
    end: float
    margin: float

    class Config:
        orm_mode = True

class StoneMarginCreate(BaseModel):
    shopify_name: str
    type: str
    unit: str
    ranges: List[StoneMarginBase]
    store_id: Optional[str] = None

class StoneMarginMarkup(BaseModel):
    start: float
    end: float
    markup: float

class StoneMarginResponse(BaseModel):
    message: str
    count: int

    class Config:
        orm_mode = True
