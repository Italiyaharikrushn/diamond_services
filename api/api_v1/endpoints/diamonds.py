import crud
import asyncio
from sqlalchemy.orm import Session
from api.dependencies import get_db
from fastapi import APIRouter, Depends, Query
from services.aarush_service import ingest_aarush_diamonds
from services.vdb_service import ingest_vdb_diamonds

router = APIRouter()

@router.get("/public/ingest/all")
async def ingest_all_diamonds(db: Session = Depends(get_db), store_id: str | None = Query(None)):
    running_process = crud.diamond.get_running_process(db)
    if running_process:
        return {
            "success": False,
            "message": "Another ingestion process is already running. Please try again later.",
            "process_id": running_process.id,
            "status": "running"
        }
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

@router.get("/public/ingest/process/{process_id}")
async def get_ingestion_process(process_id: int, db: Session = Depends(get_db)):
    process = crud.diamond.get_ingestion_process(db, process_id)

    if not process:
        return {
            "success": False,
            "message": "Process not found"
        }

    return {
        "success": True,
        "process_id": process.id,
        "process_type": process.process_type,
        "status": process.status,
        "started_at": process.started_at,
        "completed_at": process.completed_at,
        "total_items": process.total_items,
        "processed_items": process.processed_items,
        "logs": process.logs,
        "progress_percentage": (process.processed_items / process.total_items * 100) if process.total_items > 0 else 0,
    }

@router.get("/public/ingest/processes")
async def get_ingestion_processes(db: Session = Depends(get_db)):
    processes = crud.diamond.get_ingestion_processes(db)

    if not processes:
        return {
            "success": False,
            "message": "Process not found"
        }

    return {
        "success": True,
        "processes": [
            {
                "process_id": p.id,
                "process_type": p.process_type,
                "status": p.status,
                "started_at": p.started_at,
                "completed_at": p.completed_at,
                "total_items": p.total_items,
                "processed_items": p.processed_items,
                "logs": p.logs,
                "progress_percentage": (p.processed_items / p.total_items * 100) if p.total_items > 0 else 0,

            }
            for p in processes
        ]
    }
