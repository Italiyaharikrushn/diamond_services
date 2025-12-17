from pydantic import BaseModel
from typing import Optional, Dict, Any

class StoreSettingsBase(BaseModel):
    shopify_name: str
    custom_feed: Optional[bool] = False
    settings: Optional[Dict[str, Any]] = None
    feed_config: Dict[str, Any]

class StoreSettingsCreate(StoreSettingsBase):
    pass
