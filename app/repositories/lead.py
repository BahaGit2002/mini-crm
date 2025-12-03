from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Lead, Appeal


class LeadRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_or_create(
        self,
        external_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> Lead:
        lead = self.db.query(Lead).filter(
            Lead.external_id == external_id
        ).first()

        if not lead:
            lead = Lead(
                external_id=external_id,
                name=name,
                phone=phone,
                email=email
            )
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)

        return lead

    def get_by_id(self, lead_id: int) -> Optional[Lead]:
        return self.db.query(Lead).filter(Lead.id == lead_id).first()

    def get_all(self) -> List[Lead]:
        return self.db.query(Lead).all()

    def get_all_with_appeals_count(self) -> List[dict]:
        leads = self.get_all()
        result = []
        for lead in leads:
            appeals_count = self.db.query(Appeal).filter(
                Appeal.lead_id == lead.id
            ).count()
            result.append(
                {
                    "id": lead.id,
                    "external_id": lead.external_id,
                    "name": lead.name,
                    "phone": lead.phone,
                    "email": lead.email,
                    "appeals_count": appeals_count
                }
            )
        return result

    def get_lead_appeals(self, lead_id: int) -> List[Appeal]:
        return self.db.query(Appeal).filter(Appeal.lead_id == lead_id).all()
