from pydantic import BaseModel
from typing import Optional, Dict, Any

class StoreSettingsBase(BaseModel):
    # shopify_name: str
    settings: Optional[Dict[str, Any]]

class StoreSettingsCreate(StoreSettingsBase):
    pass
