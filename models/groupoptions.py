from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey
from db.base_class import Base

class GroupOptions(Base):
    __tablename__ = "group_options"

    id = Column(Integer, primary_key = True, index=True)
    store_id = Column(String(50), nullable=True, index=True)
    shopify_name = Column(String(100), nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable = False)
    product_id = Column(String(50), nullable = False)
    color_code = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
