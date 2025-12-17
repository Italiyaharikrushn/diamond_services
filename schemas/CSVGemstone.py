from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CSVGemstoneBase(BaseModel):
    s_no: Optional[str] = None
    lab: str
    type: str
    # store_id: Optional[str] = None
    # shopify_name: Optional[str] = None
    carat: float
    color: str
    clarity: str
    cut: Optional[str] = None
    shape: str
    price: float
    selling_price: Optional[float] = None
    certificate_no: str
    origin: Optional[str] = None
    description: Optional[str] = None
    image_source: str
    video_source: str
    is_available: str
    vendor: str
    measurements: str
    polish: Optional[str] = None
    symmetry: Optional[str] = None
    fluorescence: Optional[str] = None
    table: float
    depth: float
    girdle: Optional[str] = None
    bgm: Optional[str] = None
    treatment: Optional[str] = None
    culet: Optional[str] = None
    location: str

class CSVGemstoneCreate(BaseModel):
    csv_data: str

class CSVGemstone(CSVGemstoneBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BulkDeleteRequest(BaseModel):
    ids: List[int]
