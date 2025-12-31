from datetime import datetime
from datetime import datetime
from crud.base import CRUDBase
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from models.ingested_diamonds import IngestedDiamonds
from models.ingestion_process import IngestionProcess

class CRUDDiamond(CRUDBase):

    # Get Running Ingestion Process
    def get_running_process(self, db: Session):
        return db.query(IngestionProcess).filter(
            IngestionProcess.process_type == "diamond-ingestion",
            IngestionProcess.status.in_(["running", "price_calculation"])
        ).first()
    
    # Get Ingestion Process by ID
    def get_ingestion_process(self, db: Session, process_id: int):
        return db.query(IngestionProcess).filter(
            IngestionProcess.id == process_id
        ).first()

    # Get All Ingestion Processes
    def get_ingestion_processes(self, db: Session):
        return db.query(IngestionProcess).all()

    # Create Ingestion Process
    def create_ingestion_process(self, db: Session, process_type: str, processSubType: str, origin: str):
        process = IngestionProcess(
            process_type=process_type,
            process_sub_type= processSubType,
            origin=origin,
            status="running",
            total_items=0,
            processed_items=0,
            logs = None,
            started_at=datetime.utcnow(),
        )

        db.add(process)
        db.commit()
        db.refresh(process)
        return process
    
    # Update Ingestion Process
    def update_ingestion_process( self, db: Session, process_id: int, updates: dict):
        db.query(IngestionProcess).filter(
            IngestionProcess.id == process_id
        ).update(updates, synchronize_session=False)

        db.commit()

    # Bulk Upsert Diamonds
    def bulk_upsert_diamonds(self, db: Session, diamonds):
        if not diamonds:
            return {"upserted": 0, "errors": []}

        now = datetime.utcnow()
        rows = [d.dict() for d in diamonds]
        for row in rows:
            row["created_at"] = now
            row["updated_at"] = now

        stmt = insert(IngestedDiamonds).values(rows)

        db.execute(stmt)
        db.commit()
        return {"upserted": len(rows), "errors": []}
    
diamond = CRUDDiamond(IngestedDiamonds)
