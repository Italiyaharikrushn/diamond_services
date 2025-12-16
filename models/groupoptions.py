import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, VARCHAR
from db.base_class import Base

class GroupOptions(Base):
    __tablename__ = "group_options"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    store_id = Column(String(50), nullable=False, index=True)
    shopify_name = Column(String(100), nullable=True)
    group_id = Column(VARCHAR(36), ForeignKey("groups.id"), nullable=False)
    product_id = Column(String(50), nullable=False)
    color_code = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
