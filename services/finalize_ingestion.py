import crud
from datetime import datetime
from sqlalchemy.orm import Session
from models.diamond_pricing import DiamondPricing
from models.ingested_diamonds import IngestedDiamonds
from services.diamond_pricing_service import create_diamond_pricing

async def finalize_diamond_ingestion(
    db: Session,
    process_id: int,
    process_starting_time,
    source_name: str,
    total_processed: int,
    errors: list
):
    if errors:
        crud.diamond.update_ingestion_process(
            db,
            process_id,
            {
                "status": "failed",
                "logs": errors
            }
        )
        return

    old_diamonds = db.query(IngestedDiamonds).filter(
        IngestedDiamonds.updated_at < process_starting_time,
        IngestedDiamonds.source_name == source_name
    ).all()

    old_ids = [d.id for d in old_diamonds]

    if old_ids:
        db.query(DiamondPricing).filter(
            DiamondPricing.diamond_id.in_(old_ids)
        ).delete(synchronize_session=False)

        db.query(IngestedDiamonds).filter(
            IngestedDiamonds.id.in_(old_ids)
        ).delete(synchronize_session=False)

        db.commit()

    new_diamonds = db.query(IngestedDiamonds).filter(
        IngestedDiamonds.updated_at >= process_starting_time,
        IngestedDiamonds.source_name == source_name
    ).all()

    create_diamond_pricing(
        db=db,
        diamonds=new_diamonds,
        store_id="default_store",
        shopify_name="default_shop"
    )

    crud.diamond.update_ingestion_process(
        db,
        process_id,
        {
            "status": "complated",
            "completed_at": datetime.utcnow(),
            "logs": errors
        }
    )
