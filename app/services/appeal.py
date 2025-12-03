from sqlalchemy.orm import Session
from app.repositories.lead import LeadRepository
from app.repositories.source import SourceRepository
from app.repositories.appeal import AppealRepository
from app.services.distribution import DistributionService
from app.schemas.appeal import AppealCreate, AppealResponse
from fastapi import HTTPException


class AppealService:

    def __init__(self, db: Session):
        self.db = db
        self.lead_repo = LeadRepository(db)
        self.source_repo = SourceRepository(db)
        self.appeal_repo = AppealRepository(db)
        self.distribution_service = DistributionService(db)

    def create_appeal(self, appeal_data: AppealCreate) -> AppealResponse:

        lead = self.lead_repo.get_or_create(
            external_id=appeal_data.lead_external_id,
            name=appeal_data.lead_name,
            phone=appeal_data.lead_phone,
            email=appeal_data.lead_email
        )

        source = self.source_repo.get_by_id(appeal_data.source_id)
        if not source:
            raise HTTPException(
                status_code=404,
                detail=f"Source with id {appeal_data.source_id} not found"
            )

        operator_id = self.distribution_service.select_operator(
            appeal_data.source_id
        )

        appeal = self.appeal_repo.create(
            lead_id=lead.id,
            source_id=appeal_data.source_id,
            operator_id=operator_id,
            message=appeal_data.message
        )

        operator_info = None
        if operator_id:
            from app.repositories.operator import OperatorRepository
            operator_repo = OperatorRepository(self.db)
            operator = operator_repo.get_by_id(operator_id)
            if operator:
                operator_info = {
                    "id": operator.id,
                    "name": operator.name
                }

        return AppealResponse(
            appeal_id=appeal.id,
            lead_id=lead.id,
            lead_external_id=lead.external_id,
            source_id=source.id,
            source_name=source.name,
            operator=operator_info,
            status=appeal.status,
            created_at=appeal.created_at
        )

    def close_appeal(self, appeal_id: int) -> bool:
        success = self.appeal_repo.close(appeal_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Appeal with id {appeal_id} not found"
            )
        return True
