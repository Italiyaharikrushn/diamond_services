from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Any

class StoneType(str, Enum):
    natural = "natural"
    lab = "lab"
    gemstones = "gemstones"

class Color(str, Enum):
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"

class Clarity(str, Enum):
    FL = "FL"
    IF = "IF"
    VVS1 = "VVS1"
    VVS2 = "VVS2"
    VS1 = "VS1"
    VS2 = "VS2"
    SI1 = "SI1"
    SI2 = "SI2"
    I1 = "I1"
    I2 = "I2"
    I3 = "I3"

class IngestedDiamondBase(BaseModel):
    source_diamond_id: str
    source_name: str
    source_stock_id: str | None = None
    lab: Optional[str] = None
    type: StoneType
    store_id: str | None = None
    carat: float
    color: Color
    clarity: Clarity
    cut: Optional[str] = None
    shape: str
    price: float
    certificate_no: Optional[str] = None
    origin: Optional[str] = None
    description: Optional[str] = None
    image_source: Optional[str] = None
    video_source: Optional[str] = None
    is_available: Optional[bool] = None
    vendor: Optional[str] = None
    mesurements: Optional[str] = None
    polish: Optional[str] = None
    symmetry: Optional[str] = None
    fluorescence: Optional[str] = None
    table: Optional[float] = None
    depth: Optional[float] = None
    girdle: Optional[str] = None
    bgm: Optional[str] = None
    treatment: Optional[str] = None
    culet: Optional[str] = None
    location: Optional[str] = None

class IngestedDiamondCreate(IngestedDiamondBase):
    pass

class IngestionProcessSchema(BaseModel):
    id: int
    process_type: str
    source_name: Optional[str]
    status: str
    total_items: int
    processed_items: int
    logs: Optional[List[Any]] = None
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True
