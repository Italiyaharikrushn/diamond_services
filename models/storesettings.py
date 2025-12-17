from sqlalchemy import Column, Integer, String, Boolean, JSON
from db.base_class import Base

class StoreSettings(Base):
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(255), nullable=False)
    shopify_name = Column(String(255), nullable=False)
    custom_feed = Column(Boolean, nullable=False, default=False)
    settings = Column(JSON, nullable=True)
    feed_config = Column(JSON, nullable=False)
