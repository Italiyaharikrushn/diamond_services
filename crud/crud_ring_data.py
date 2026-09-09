from sqlalchemy.orm import Session
from models.ring_data import RingData
from schemas.ringData import RingDataBase

class CRUDRingData:
    def create_ring_data(self, db: Session, ring_data: RingDataBase):
        db_ring = RingData(
            title=ring_data.product.title,
            data=ring_data.product.dict(exclude={"title"})
        )
        db.add(db_ring)
        db.commit()
        db.refresh(db_ring)
        return db_ring
    
    def get_ring_data(self, db: Session):
        return db.query(RingData).all()
    
    def get_single_ring(self, db: Session, ring_id: int):
        return db.query(RingData).filter(RingData.id == ring_id).first()

ringData = CRUDRingData()
