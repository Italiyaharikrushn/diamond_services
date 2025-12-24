from db.base_class import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class User(Base):
    id = Column(Integer, primary_key=True)
    first_name = Column((String(32)), nullable=False)
    last_name = Column((String(32)), nullable=False)
    password = Column((String(255)), nullable=False)
    email = Column((String(256)), unique=True, nullable=False)
    phone = Column((String(15)), nullable=True)
    gender = Column((String(15)), nullable=True)
    created_by = Column(Integer, nullable=True)
    is_super_admin = Column(Boolean, nullable=False, default=False)
    modified_by = Column(Integer, nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
