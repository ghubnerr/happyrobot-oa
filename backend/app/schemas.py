"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class LoadBase(BaseModel):
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None


class LoadCreate(LoadBase):
    load_id: str


class LoadResponse(LoadBase):
    load_id: str
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoadSearchParams(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[str] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    available_only: bool = True


class FMCSAVerifyRequest(BaseModel):
    mc_number: str = Field(..., description="Motor Carrier number to verify")


class FMCSAVerifyResponse(BaseModel):
    mc_number: str
    is_valid: bool
    carrier_name: Optional[str] = None
    operating_status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class CallCreate(BaseModel):
    call_id: str
    carrier_mc_number: str
    carrier_name: Optional[str] = None
    phone_number: Optional[str] = None


class CallUpdate(BaseModel):
    load_id: Optional[str] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    initial_rate: Optional[float] = None
    final_rate: Optional[float] = None
    negotiation_rounds: Optional[int] = None


class CallResponse(BaseModel):
    id: int
    call_id: str
    carrier_mc_number: str
    carrier_name: Optional[str] = None
    phone_number: Optional[str] = None
    load_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    initial_rate: Optional[float] = None
    final_rate: Optional[float] = None
    negotiation_rounds: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NegotiationCreate(BaseModel):
    call_id: int
    round_number: int
    offer_type: str
    rate: float
    notes: Optional[str] = None


class NegotiationResponse(BaseModel):
    id: int
    call_id: int
    round_number: int
    offer_type: str
    rate: float
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MetricsResponse(BaseModel):
    total_calls: int
    calls_by_outcome: Dict[str, int]
    calls_by_sentiment: Dict[str, int]
    average_duration_seconds: Optional[float] = None
    average_negotiation_rounds: Optional[float] = None
    conversion_rate: Optional[float] = None
    total_loads_available: int
    total_loads_matched: int
    average_rate: Optional[float] = None
    calls_today: int
    calls_this_week: int
    calls_this_month: int


class HappyRobotWebhook(BaseModel):
    workflow_id: Optional[str] = None
    run_id: Optional[str] = None
    call_id: Optional[str] = None
    transcript: Optional[str] = None
    classification: Optional[Dict[str, Any]] = None
    extracted_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
