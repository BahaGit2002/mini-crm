from sqlalchemy.orm import Session
from typing import Optional
from app.models import Appeal, Source, Operator


class AppealRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        lead_id: int,
        source_id: int,
        operator_id: Optional[int],
        message: Optional[str] = None
    ) -> Appeal:
        appeal = Appeal(
            lead_id=lead_id,
            source_id=source_id,
            operator_id=operator_id,
            message=message,
            status="active"
        )
        self.db.add(appeal)
        self.db.commit()
        self.db.refresh(appeal)
        return appeal

    def get_by_id(self, appeal_id: int) -> Optional[Appeal]:
        return self.db.query(Appeal).filter(Appeal.id == appeal_id).first()

    def close(self, appeal_id: int) -> bool:
        appeal = self.get_by_id(appeal_id)
        if not appeal:
            return False

        appeal.status = "closed"
        self.db.commit()
        return True

    def get_distribution_stats(self) -> list:
        sources = self.db.query(Source).all()
        result = []

        for source in sources:
            appeals = self.db.query(Appeal).filter(
                Appeal.source_id == source.id
            ).all()

            operator_counts = {}
            for appeal in appeals:
                if appeal.operator_id:
                    operator_counts[appeal.operator_id] = operator_counts.get(
                        appeal.operator_id, 0
                    ) + 1

            operators_stats = []
            for operator_id, count in operator_counts.items():
                operator = self.db.query(Operator).filter(
                    Operator.id == operator_id
                ).first()
                if operator:
                    operators_stats.append(
                        {
                            "operator_id": operator_id,
                            "operator_name": operator.name,
                            "appeals_count": count
                        }
                    )

            result.append(
                {
                    "source_id": source.id,
                    "source_name": source.name,
                    "total_appeals": len(appeals),
                    "operators": operators_stats
                }
            )

        return result
