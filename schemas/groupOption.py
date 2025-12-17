from pydantic import BaseModel
from typing import Optional

class GroupOptionBase(BaseModel):
    # store_id: Optional[str] = None
    # shopify_name: Optional[str] = None
    product_id: str
    color_code: Optional[str] = None
    image_url: Optional[str] = None
    position: int

class GroupOptionCreate(GroupOptionBase):
    pass
