from db.base_class import Base
from sqlalchemy import Column, Integer, String, DECIMAL

class DiamondPricing(Base):
    id = Column(Integer, primary_key=True, index=True)
    diamond_id = Column(Integer, nullable=False)
    store_id = Column(String(50), nullable=False)
    base_price = Column(DECIMAL(15, 2), nullable=False)
    selling_price = Column(DECIMAL(15, 2), nullable=False)
