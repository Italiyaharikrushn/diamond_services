import json
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class MediaImage(BaseModel):
    url: str

class Media(BaseModel):
    typename: str = Field(alias="__typename")
    image: MediaImage

class Variant(BaseModel):
    id: str
    title: str
    price: float
    compare_at: Optional[float] = None
    image: str
    selectedOptions: Dict[str, str]
    selectedOptionsKey: str

class ShapeOption(BaseModel):
    option_title: str
    variant_id: str

class ShapesGroup(BaseModel):
    group_name: str
    options: List[ShapeOption]

class ProductOption(BaseModel):
    name: str
    values: List[str]

class StoneType(BaseModel):
    key: str
    value: List[str]

class Product(BaseModel):
    id: str
    title: str
    description: str
    options: List[ProductOption]
    variants: List[Variant]
    media: List[Media]
    current_stone_shape: str
    shapes_group: ShapesGroup
    stone_types: List[StoneType]

class RingDataBase(BaseModel):
    product: Product

class RingDataCreate(RingDataBase):
    pass
