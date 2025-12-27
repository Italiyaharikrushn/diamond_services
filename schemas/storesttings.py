from pydantic import BaseModel
from typing import Optional, Dict, Any

class StoreSettingsBase(BaseModel):
    shopify_name: str
    custom_feed: Optional[bool] = False
    feed_config: Dict[str, Any]
    settings: Optional[Dict[str, Any]]

class StoreSettingsCreate(StoreSettingsBase):
    pass
