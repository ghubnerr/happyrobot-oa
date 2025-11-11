"""
SQLAlchemy database models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Load(Base):
    """Load model representing available freight loads."""
    
    __tablename__ = "loads"
    
    load_id = Column(String, primary_key=True, index=True)
    origin = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    pickup_datetime = Column(DateTime, nullable=False)
    delivery_datetime = Column(DateTime, nullable=False)
    equipment_type = Column(String, nullable=False)
    loadboard_rate = Column(Float, nullable=False)
    notes = Column(Text)
    weight = Column(Float)
    commodity_type = Column(String)
    num_of_pieces = Column(Integer)
    miles = Column(Float)
    dimensions = Column(String)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    calls = relationship("Call", back_populates="load")


class Call(Base):
    """Call model representing inbound carrier calls."""
    
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String, unique=True, index=True)  # From HappyRobot
    carrier_mc_number = Column(String, index=True)
    carrier_name = Column(String)
    phone_number = Column(String)
    
    # Load association
    load_id = Column(String, ForeignKey("loads.load_id"), nullable=True)
    load = relationship("Load", back_populates="calls")
    
    # Call metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    transcript = Column(Text)
    
    # Classification
    outcome = Column(String)  # "accepted", "rejected", "transferred", "no_match", etc.
    sentiment = Column(String)  # "positive", "neutral", "negative"
    
    # Extracted data
    extracted_data = Column(JSON)  # Store structured data from AI Extract
    
    # Negotiation
    initial_rate = Column(Float)
    final_rate = Column(Float)
    negotiation_rounds = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    negotiations = relationship("Negotiation", back_populates="call", cascade="all, delete-orphan")


class Negotiation(Base):
    """Negotiation round model for tracking offer/counter-offer history."""
    
    __tablename__ = "negotiations"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    call = relationship("Call", back_populates="negotiations")
    
    round_number = Column(Integer, nullable=False)
    offer_type = Column(String, nullable=False)  # "initial", "counter", "accepted", "rejected"
    rate = Column(Float, nullable=False)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

