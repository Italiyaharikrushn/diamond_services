import crud
import asyncio
from sqlalchemy.orm import Session
from api.dependencies import get_db
from fastapi import APIRouter, Depends
from services.aarush_service import ingest_aarush_diamonds

router = APIRouter()

@router.post("/ingest/aarush")
async def ingest_aarush(db: Session = Depends(get_db)):
    process = crud.diamond.create_ingestion_process( db, process_type="diamond-ingestion", origin="API", processSubType="Aarush")

    asyncio.create_task( ingest_aarush_diamonds( process.id, process.started_at))

    return {
        "process_id": process.id,
        "status": "running"
    }
