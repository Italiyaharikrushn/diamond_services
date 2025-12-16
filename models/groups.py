from sqlalchemy import Column, Integer, String, Float, DateTime, func
from db.base_class import Base

class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key = True, index=True)
    store_id = Column(String(50), nullable=True, index=True)
    shopify_name = Column(String(100), nullable=True)
    group_name = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
