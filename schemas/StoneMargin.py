from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StoneMarginBase(BaseModel):
    store_id: Optional[str] = None
    shopify_name: Optional[str] = None
    type: str
    unit: str
    start: float
    end: float
    margin: float

    class Config:
        orm_mode = True

class StoneMarginCreate(StoneMarginBase):
    pass

class StoneMarginMarkup(BaseModel):
    start: float
    end: float
    markup: float

class StoneMarginResponse(BaseModel):
    stone_type : str
    unit: str
    markups: List[StoneMarginMarkup]

    class Config:
        orm_mode = True
