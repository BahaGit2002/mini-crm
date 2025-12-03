from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.repositories.source import SourceRepository
from app.schemas.source import (
    SourceCreate,
    SourceResponse,
    WeightConfig,
)

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/", response_model=SourceResponse, status_code=201)
def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db)
):
    repo = SourceRepository(db)
    source = repo.create(source_data)
    return source


@router.get("/", response_model=List[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    repo = SourceRepository(db)
    return repo.get_all()


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: int, db: Session = Depends(get_db)):
    repo = SourceRepository(db)
    source = repo.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.post("/{source_id}/weights", status_code=200)
def configure_weights(
    source_id: int,
    weights: List[WeightConfig],
    db: Session = Depends(get_db)
):
    repo = SourceRepository(db)

    try:
        success = repo.configure_weights(source_id, weights)
        if not success:
            raise HTTPException(status_code=404, detail="Source not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"message": "Weights configured successfully"}


@router.get("/{source_id}/weights")
def get_weights(source_id: int, db: Session = Depends(get_db)):
    repo = SourceRepository(db)
    source = repo.get_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    weights = repo.get_weights(source_id)
    return [
        {
            "operator_id": w.operator_id,
            "operator_name": w.operator.name,
            "weight": w.weight
        }
        for w in weights
    ]
