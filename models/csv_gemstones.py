from sqlalchemy import Column, Integer, String, Float, DateTime, func, UniqueConstraint
from db.base_class import Base


class CSVGemstone(Base):
    __tablename__ = 'csv_gemstones'

    __table_args__ = (
        UniqueConstraint('store_id', 'certificate_no', name='uq_store_certificate'),
    )

    id = Column(Integer, primary_key=True)
    s_no = Column(String(100), nullable=True)
    lab = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    sub_type = Column(String(50), nullable=True)
    store_id = Column(String(50), nullable=False)
    shopify_name = Column(String(100), nullable=True)
    carat = Column(Float, nullable=False)
    color = Column(String(10), nullable=False)
    clarity = Column(String(20), nullable=False)
    cut = Column(String(20), nullable=True)
    shape = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=True)
    certificate_no = Column(String(50), nullable=False)
    origin = Column(String(50), nullable=True)
    description = Column(String(255), nullable=True)
    image_source = Column(String(255), nullable=False)
    video_source = Column(String(255), nullable=True)
    is_available = Column(String(10), nullable=False)
    vendor = Column(String(50), nullable=False)
    measurements = Column(String(50), nullable=True)
    polish = Column(String(20), nullable=True)
    symmetry = Column(String(20), nullable=True)
    fluorescence = Column(String(20), nullable=True)
    table = Column(Float, nullable=False)
    depth = Column(Float, nullable=False)
    girdle = Column(String(100), nullable=True)
    bgm = Column(String(50), nullable=True)
    treatment = Column(String(50), nullable=True)
    culet = Column(String(20), nullable=True)
    location = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
