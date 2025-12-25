import crud
import asyncio
from sqlalchemy.orm import Session
from api.dependencies import get_db, get_current_store
from fastapi import APIRouter, Depends
from services.aarush_service import ingest_aarush_diamonds
from services.vdb_service import ingest_vdb_diamonds

router = APIRouter()

@router.post("/ingest/all")
async def ingest_all_diamonds(db: Session = Depends(get_db), store_id: str = Depends(get_current_store)):
    processes = []

    # ---- VDB PROCESS ----
    vdb_process = crud.diamond.create_ingestion_process( db, process_type="diamond-ingestion", processSubType="VDB", origin="API")

    asyncio.create_task(ingest_vdb_diamonds(vdb_process.id, vdb_process.started_at, store_id))

    processes.append({
        "source": "VDB",
        "process_id": vdb_process.id
    })

    # ---- AARUSH PROCESS ----
    aarush_process = crud.diamond.create_ingestion_process( db, process_type="diamond-ingestion", processSubType="Aarush", origin="API")

    asyncio.create_task(ingest_aarush_diamonds(aarush_process.id, aarush_process.started_at, store_id))

    processes.append({
        "source": "Aarush",
        "process_id": aarush_process.id
    })

    return {
        "processes": processes,
        "status": "running"
    }
