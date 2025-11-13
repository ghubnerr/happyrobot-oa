"""
Load management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Load
from app.schemas import LoadCreate, LoadResponse, LoadSearchParams
from app.config import settings
from app.retrievers import HybridLoadRetriever

router = APIRouter()


def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from header."""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@router.post("/", response_model=LoadResponse, dependencies=[Depends(verify_api_key)])
def create_load(load: LoadCreate, db: Session = Depends(get_db)):
    """Create a new load."""
    db_load = Load(**load.model_dump())
    db.add(db_load)
    db.commit()
    db.refresh(db_load)
    return db_load


@router.get(
    "/", response_model=List[LoadResponse], dependencies=[Depends(verify_api_key)]
)
def search_loads(
    params: LoadSearchParams = Depends(),
    db: Session = Depends(get_db),
):
    """Search for available loads using hybrid BM25 + embedding retrieval."""
    query = db.query(Load)

    if params.available_only:
        query = query.filter(Load.is_available)

    loads = query.all()

    if not loads:
        return []

    query_dict = {}
    if params.origin:
        query_dict["origin"] = params.origin
    if params.destination:
        query_dict["destination"] = params.destination
    if params.equipment_type:
        query_dict["equipment_type"] = params.equipment_type
    if params.commodity_type:
        query_dict["commodity_type"] = params.commodity_type

    if not query_dict:
        if params.min_rate:
            loads = [x for x in loads if x.loadboard_rate >= params.min_rate]
        if params.max_rate:
            loads = [x for x in loads if x.loadboard_rate <= params.max_rate]
        return loads

    retriever = HybridLoadRetriever(loads)
    top_k = params.top_k or 10
    results = retriever.search(query_dict, top_k=top_k)

    matched_loads = [load for load, score in results]

    if params.min_rate:
        matched_loads = [
            x for x in matched_loads if x.loadboard_rate >= params.min_rate
        ]
    if params.max_rate:
        matched_loads = [
            x for x in matched_loads if x.loadboard_rate <= params.max_rate
        ]

    return matched_loads


@router.get(
    "/{load_id}", response_model=LoadResponse, dependencies=[Depends(verify_api_key)]
)
def get_load(load_id: str, db: Session = Depends(get_db)):
    """Get a specific load by ID."""
    load = db.query(Load).filter(Load.load_id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    return load


@router.put(
    "/{load_id}", response_model=LoadResponse, dependencies=[Depends(verify_api_key)]
)
def update_load(
    load_id: str,
    load_update: dict,
    db: Session = Depends(get_db),
):
    """Update a load."""
    load = db.query(Load).filter(Load.load_id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")

    for key, value in load_update.items():
        setattr(load, key, value)

    db.commit()
    db.refresh(load)
    return load


@router.delete("/{load_id}", dependencies=[Depends(verify_api_key)])
def delete_load(load_id: str, db: Session = Depends(get_db)):
    """Delete a load."""
    load = db.query(Load).filter(Load.load_id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")

    db.delete(load)
    db.commit()
    return {"message": "Load deleted successfully"}
