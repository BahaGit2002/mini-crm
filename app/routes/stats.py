from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.repositories.appeal import AppealRepository
from app.services.distribution import DistributionService

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/distribution")
def get_distribution_stats(db: Session = Depends(get_db)):
    repo = AppealRepository(db)
    return repo.get_distribution_stats()


@router.get("/sources/{source_id}/operators")
def get_available_operators(source_id: int, db: Session = Depends(get_db)):
    service = DistributionService(db)
    return service.get_available_operators_info(source_id)
