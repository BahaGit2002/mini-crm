from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.repositories.operator import OperatorRepository
from app.schemas.operator import (
    OperatorCreate,
    OperatorUpdate,
    OperatorResponse,
    OperatorWithLoad,
)

router = APIRouter(prefix="/operators", tags=["operators"])


@router.post("/", response_model=OperatorResponse, status_code=201)
def create_operator(
    operator_data: OperatorCreate,
    db: Session = Depends(get_db)
):
    repo = OperatorRepository(db)
    operator = repo.create(operator_data)
    return operator


@router.get("/", response_model=List[OperatorWithLoad])
def list_operators(db: Session = Depends(get_db)):
    repo = OperatorRepository(db)
    return repo.get_all_with_load()


@router.get("/{operator_id}", response_model=OperatorResponse)
def get_operator(operator_id: int, db: Session = Depends(get_db)):
    repo = OperatorRepository(db)
    operator = repo.get_by_id(operator_id)
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    return operator


@router.patch("/{operator_id}", response_model=OperatorResponse)
def update_operator(
    operator_id: int,
    operator_data: OperatorUpdate,
    db: Session = Depends(get_db)
):
    repo = OperatorRepository(db)
    operator = repo.update(operator_id, operator_data)
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    return operator
