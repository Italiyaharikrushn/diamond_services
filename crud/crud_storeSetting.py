from crud.base import CRUDBase
from models.storesettings import StoreSettings
from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.storesttings import StoreSettingsCreate, StoreSettingsBase
from sqlalchemy import func

class CRUDStoresetting(CRUDBase):
    def create(self, db: Session, payload: StoreSettingsCreate, store_id: str):
        store_setting = StoreSettings(
            store_id=store_id,
            shopify_name=payload.shopify_name,
            custom_feed=payload.custom_feed,
            settings=payload.settings,
            feed_config=payload.feed_config
        )
        db.add(store_setting)
        db.commit()
        db.refresh(store_setting)
        return store_setting
    
    def get_by_store_id(self, db: Session, store_id: str):
        store_setting = db.query(StoreSettings).filter(StoreSettings.store_id == store_id).first()
        if not store_setting:
            raise HTTPException(status_code=404, detail="Store settings not found")
        return store_setting
    
    def delete_by_store_id(self, db: Session, store_id: str):
        store_setting = db.query(StoreSettings).filter(StoreSettings.store_id == store_id).first()
        if not store_setting:
            raise HTTPException(status_code=404, detail="Store settings not found")
        db.delete(store_setting)
        db.commit()
        return store_setting

storesettings = CRUDStoresetting(StoreSettings)
