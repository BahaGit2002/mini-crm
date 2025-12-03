from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.services.appeal import AppealService
from app.repositories.lead import LeadRepository
from app.schemas.appeal import (
    AppealCreate,
    AppealResponse,
    LeadResponse,
    LeadAppealResponse
)

router = APIRouter(prefix="/appeals", tags=["appeals"])


@router.post("/", response_model=AppealResponse, status_code=201)
def create_appeal(
    appeal_data: AppealCreate,
    db: Session = Depends(get_db)
):
    service = AppealService(db)
    return service.create_appeal(appeal_data)


@router.patch("/{appeal_id}/close")
def close_appeal(appeal_id: int, db: Session = Depends(get_db)):
    service = AppealService(db)
    service.close_appeal(appeal_id)
    return {"message": "Appeal closed successfully"}


@router.get("/leads", response_model=List[LeadResponse])
def list_leads(db: Session = Depends(get_db)):
    repo = LeadRepository(db)
    return repo.get_all_with_appeals_count()


@router.get("/leads/{lead_id}/appeals", response_model=List[LeadAppealResponse])
def get_lead_appeals(lead_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    repo = LeadRepository(db)

    lead = repo.get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    appeals = repo.get_lead_appeals(lead_id)

    return [
        LeadAppealResponse(
            id=appeal.id,
            source=appeal.source.name,
            operator=appeal.operator.name if appeal.operator else None,
            status=appeal.status,
            created_at=appeal.created_at
        )
        for appeal in appeals
    ]