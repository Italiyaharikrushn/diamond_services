from pydantic import BaseModel
from typing import Optional, List, Any
from enum import Enum
from datetime import datetime

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
    lab: Optional[str]
    type: StoneType
    store_id: str | None = None
    carat: float
    color: Color
    clarity: Clarity
    cut: Optional[str]
    shape: str
    price: float
    certificate_no: Optional[str]
    origin: Optional[str]
    description: Optional[str]
    image_source: Optional[str]
    video_source: Optional[str]
    is_available: Optional[bool]
    vendor: Optional[str]
    mesurements: Optional[str]
    polish: Optional[str]
    symmetry: Optional[str]
    fluorescence: Optional[str]
    table: Optional[float]
    depth: Optional[float]
    girdle: Optional[str]
    bgm: Optional[str]
    treatment: Optional[str]
    culet: Optional[str]
    location: Optional[str]

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

