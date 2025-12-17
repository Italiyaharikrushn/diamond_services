from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from schemas.groupOption import GroupOptionCreate

class GroupBase(BaseModel):
    # store_id: Optional[str] = None
    shopify_name: Optional[str] = None
    group_name: str
    type: str

class GroupCreate(GroupBase):
    options: List[GroupOptionCreate]
