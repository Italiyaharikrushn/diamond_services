import json
import logging
from sqlalchemy.orm import Session
from api.dependencies import get_db
from models.storesettings import StoreSettings
from fastapi import Request, HTTPException, Depends

logger = logging.getLogger(__name__)

# Middleware to check feed configuration
async def check_feed(request: Request, db: Session = Depends(get_db)):
    store_id = (
        request.query_params.get("store_id")
        or getattr(request.state, "store_id", None)
    )

    shopify_app = getattr(request.state, "shopify_app", None)

    if not store_id:
        raise HTTPException(status_code=400, detail="store_id not found")

    query = db.query(StoreSettings).filter(StoreSettings.store_id == store_id)

    if shopify_app:
        query = query.filter(StoreSettings.shopify_name == shopify_app)

    store_settings = query.first()

    if not store_settings:
        raise HTTPException(status_code=404, detail="Store settings not found")
    
    if store_settings.custom_feed == 1:
        raise HTTPException(
            status_code=400,
            detail="Custom feed not yet supported for gemstones"
        )

    try:
        settings = (
            json.loads(store_settings.settings)
            if isinstance(store_settings.settings, str)
            else store_settings.settings
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid settings format")

    feed_config = {}
    stone_types = (
        settings.get("general", {})
        .get("stone_config", {})
        .get("stone_types", [])
    )

    for stone in stone_types:
        if stone.get("id") and stone.get("enabled"):
            feed_config[stone["id"]] = {
                "type": stone.get("feed_type", "CSV"),
                "config": stone.get("feed_config", {})
            }

    request.state.feed_config = feed_config
    request.state.custom_feed = store_settings.custom_feed
