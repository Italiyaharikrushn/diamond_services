from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from db.base_class import Base

class IngestionProcess(Base):
    id = Column(Integer, primary_key=True, index=True)
    process_type = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False, default="running")
    started_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_items = Column(Integer, default=0, nullable=True)
    processed_items = Column(Integer, default=0, nullable=True)
    logs = Column(JSON, nullable=True)
    process_sub_type = Column(String(50), nullable=True)
    store_id = Column(String(50), nullable=True)
    origin = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    modified_date = Column(DateTime, default=func.now())
