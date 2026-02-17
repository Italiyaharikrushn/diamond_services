from crud.base import CRUDBase
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.storesettings import StoreSettings
from schemas.storesttings import StoreSettingsCreate

class CRUDStoresetting(CRUDBase):
    
    # Create Store Settings
    def create(self, db: Session, payload: StoreSettingsCreate, store_id: str):
        existing_setting = db.query(StoreSettings).filter(StoreSettings.store_id == store_id).first()

        if existing_setting:
            existing_setting.settings = payload.settings
            db.commit()
            db.refresh(existing_setting)
            return existing_setting
        
        else:
            new_store_setting = StoreSettings(
                store_id=store_id,
                settings=payload.settings
            )
            db.add(new_store_setting)
            db.commit()
            db.refresh(new_store_setting)
            return new_store_setting
    
    # Get Store Settings by Store ID
    def get_by_store_id(self, db: Session, store_id: str):
        store_setting = db.query(StoreSettings).filter(StoreSettings.store_id == store_id).first()
        if not store_setting:
            raise HTTPException(status_code=404, detail="Store settings not found")
        return store_setting
    
    # Delete Store Settings by Store ID
    def delete_by_store_id(self, db: Session, store_id: str):
        store_setting = db.query(StoreSettings).filter(StoreSettings.store_id == store_id).first()
        if not store_setting:
            raise HTTPException(status_code=404, detail="Store settings not found")
        db.delete(store_setting)
        db.commit()
        return store_setting
    
    def get_store_id(self, db: Session, store_id: str):
        store_settings = db.query(StoreSettings).filter(StoreSettings.store_id == store_id).first()

        if not store_settings :
            raise HTTPException(status_code=404, detail="Store settings not Found")
        
        return store_settings

storesettings = CRUDStoresetting(StoreSettings)
