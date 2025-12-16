import uuid
from sqlalchemy import Column, String, DateTime, func, VARCHAR
from db.base_class import Base

class Groups(Base):
    __tablename__ = "groups"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    store_id = Column(String(50), nullable=True, index=True)
    shopify_name = Column(String(100), nullable=True)
    group_name = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
