from db.base_class import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import JSON

class RingData(Base):
    __tablename__ = "ring_data"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    data = Column(JSON, nullable=False)
