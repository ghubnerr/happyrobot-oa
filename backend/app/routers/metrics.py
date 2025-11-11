"""
Metrics and analytics endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Call, Load
from app.schemas import MetricsResponse

router = APIRouter()


@router.get("/", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    """Get comprehensive metrics for the dashboard."""

    total_calls = db.query(Call).count()

    calls_by_outcome = (
        db.query(Call.outcome, func.count(Call.id))
        .filter(Call.outcome.isnot(None))
        .group_by(Call.outcome)
        .all()
    )
    outcome_dict = {outcome: count for outcome, count in calls_by_outcome}

    calls_by_sentiment = (
        db.query(Call.sentiment, func.count(Call.id))
        .filter(Call.sentiment.isnot(None))
        .group_by(Call.sentiment)
        .all()
    )
    sentiment_dict = {sentiment: count for sentiment, count in calls_by_sentiment}

    avg_duration = (
        db.query(func.avg(Call.duration_seconds))
        .filter(Call.duration_seconds.isnot(None))
        .scalar()
    )

    avg_rounds = (
        db.query(func.avg(Call.negotiation_rounds))
        .filter(Call.negotiation_rounds > 0)
        .scalar()
    )

    accepted_calls = db.query(Call).filter(Call.outcome == "accepted").count()
    conversion_rate = (accepted_calls / total_calls * 100) if total_calls > 0 else None

    total_loads_available = db.query(Load).filter(Load.is_available).count()
    total_loads_matched = (
        db.query(Call).filter(Call.load_id.isnot(None)).distinct(Call.load_id).count()
    )

    avg_rate = (
        db.query(func.avg(Call.final_rate)).filter(Call.final_rate.isnot(None)).scalar()
    )

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)

    calls_today = db.query(Call).filter(Call.created_at >= today_start).count()
    calls_this_week = db.query(Call).filter(Call.created_at >= week_start).count()
    calls_this_month = db.query(Call).filter(Call.created_at >= month_start).count()

    return MetricsResponse(
        total_calls=total_calls,
        calls_by_outcome=outcome_dict,
        calls_by_sentiment=sentiment_dict,
        average_duration_seconds=float(avg_duration) if avg_duration else None,
        average_negotiation_rounds=float(avg_rounds) if avg_rounds else None,
        conversion_rate=conversion_rate,
        total_loads_available=total_loads_available,
        total_loads_matched=total_loads_matched,
        average_rate=float(avg_rate) if avg_rate else None,
        calls_today=calls_today,
        calls_this_week=calls_this_week,
        calls_this_month=calls_this_month,
    )


@router.get("/calls")
def get_calls(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get recent calls with pagination."""
    calls = (
        db.query(Call)
        .order_by(Call.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return calls
