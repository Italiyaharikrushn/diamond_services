from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, func
from db.base_class import Base
import enum

class StoneType(str, enum.Enum):
    natural = "natural"
    lab = "lab"
    gemstones = "gemstones"


class StoneUnit(str, enum.Enum):
    carat = "carat"
    price = "price"


class StoneMargin(Base):
    __tablename__ = "stone_margin"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(255), nullable=False)
    shopify_name = Column(String(255), nullable=False)
    type = Column(Enum(StoneType, name="stone_type"),nullable=False)
    unit = Column(Enum(StoneUnit, name="stone_unit"),nullable=False)
    start = Column(Float, nullable=False)
    end = Column(Float, nullable=False)
    margin = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)
