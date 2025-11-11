"""
Webhook endpoints for HappyRobot integration.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Call
from app.schemas import HappyRobotWebhook, CallCreate, CallUpdate
from app.config import settings

router = APIRouter()


@router.post("/happyrobot")
async def happyrobot_webhook(
    webhook_data: HappyRobotWebhook,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Receive webhook from HappyRobot after call completion.

    This endpoint processes:
    - Call transcripts
    - AI classifications (outcome, sentiment)
    - Extracted data
    - Call metadata
    """
    # Verify webhook secret if configured
    if settings.HAPPYROBOT_WEBHOOK_SECRET:
        secret = request.headers.get("X-Webhook-Secret")
        if secret != settings.HAPPYROBOT_WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")

    call_id = webhook_data.call_id
    if not call_id:
        raise HTTPException(status_code=400, detail="call_id is required")

    # Find or create call record
    call = db.query(Call).filter(Call.call_id == call_id).first()

    if not call:
        # Create new call record if it doesn't exist
        # Extract MC number from extracted_data if available
        mc_number = None
        if webhook_data.extracted_data:
            mc_number = webhook_data.extracted_data.get("mc_number")

        if not mc_number:
            raise HTTPException(
                status_code=400, detail="MC number required to create call record"
            )

        call = Call(
            call_id=call_id,
            carrier_mc_number=mc_number,
            carrier_name=webhook_data.extracted_data.get("carrier_name"),
            phone_number=webhook_data.metadata.get("phone_number")
            if webhook_data.metadata
            else None,
        )
        db.add(call)
        db.commit()
        db.refresh(call)

    # Update call with webhook data
    update_data = {}

    if webhook_data.transcript:
        update_data["transcript"] = webhook_data.transcript

    if webhook_data.classification:
        update_data["outcome"] = webhook_data.classification.get("outcome")
        update_data["sentiment"] = webhook_data.classification.get("sentiment")

    if webhook_data.extracted_data:
        update_data["extracted_data"] = webhook_data.extracted_data
        update_data["load_id"] = webhook_data.extracted_data.get("load_id")
        update_data["initial_rate"] = webhook_data.extracted_data.get("initial_rate")
        update_data["final_rate"] = webhook_data.extracted_data.get("final_rate")
        update_data["negotiation_rounds"] = webhook_data.extracted_data.get(
            "negotiation_rounds", 0
        )

    if webhook_data.metadata:
        if "ended_at" in webhook_data.metadata:
            update_data["ended_at"] = datetime.fromisoformat(
                webhook_data.metadata["ended_at"]
            )
        if "duration_seconds" in webhook_data.metadata:
            update_data["duration_seconds"] = webhook_data.metadata["duration_seconds"]

    # Apply updates
    for key, value in update_data.items():
        if value is not None:
            setattr(call, key, value)

    db.commit()
    db.refresh(call)

    return {
        "status": "success",
        "call_id": call.id,
        "message": "Call data updated successfully",
    }


@router.post("/calls", response_model=dict)
def create_call(
    call_data: CallCreate,
    db: Session = Depends(get_db),
):
    call = Call(**call_data.model_dump())
    db.add(call)
    db.commit()
    db.refresh(call)
    return {"id": call.id, "call_id": call.call_id, "status": "created"}


@router.put("/calls/{call_id}", response_model=dict)
def update_call(
    call_id: str,
    call_update: CallUpdate,
    db: Session = Depends(get_db),
):
    call = db.query(Call).filter(Call.call_id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    update_dict = call_update.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(call, key, value)

    db.commit()
    db.refresh(call)
    return {"id": call.id, "call_id": call.call_id, "status": "updated"}
