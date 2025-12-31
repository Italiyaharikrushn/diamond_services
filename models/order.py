import uuid, hashlib
from db.base_class import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, JSON, Text, Boolean

def generate_md5_uuid():
    return hashlib.md5(uuid.uuid4().bytes).hexdigest()

class Order(Base):
    id = Column(String(32), primary_key=True, default=generate_md5_uuid)
    order_id = Column(String(100), nullable=False)
    store_id = Column(String(100), nullable=False)
    shopify_app = Column(String(255), nullable=True)
    order_name = Column(String(50), nullable=False)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    currency_code = Column(String(50), nullable=False)
    total_amount = Column(DECIMAL(10,2), nullable=False)
    products = Column(JSON, nullable=False)
    order_notes = Column(Text, nullable=True)
    source_name = Column(String(50), nullable=True)
    app_used = Column(Boolean, default=False)
    referring_site = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    diamonds_price = Column(DECIMAL(10,2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
