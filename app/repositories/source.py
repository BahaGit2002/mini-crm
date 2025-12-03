from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Source, OperatorWeight, Operator
from app.schemas.source import SourceCreate, WeightConfig


class SourceRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, source_data: SourceCreate) -> Source:
        source = Source(**source_data.model_dump())
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_by_id(self, source_id: int) -> Optional[Source]:
        return self.db.query(Source).filter(Source.id == source_id).first()

    def get_all(self) -> List[Source]:
        return self.db.query(Source).all()

    def configure_weights(
        self, source_id: int, weights: List[WeightConfig]
    ) -> bool:
        source = self.get_by_id(source_id)
        if not source:
            return False

        self.db.query(OperatorWeight).filter(
            OperatorWeight.source_id == source_id
        ).delete()

        for weight_config in weights:
            operator = self.db.query(Operator).filter(
                Operator.id == weight_config.operator_id
            ).first()
            if not operator:
                self.db.rollback()
                raise ValueError(
                    f"Operator {weight_config.operator_id} not found"
                )

            weight = OperatorWeight(
                operator_id=weight_config.operator_id,
                source_id=source_id,
                weight=weight_config.weight
            )
            self.db.add(weight)

        self.db.commit()
        return True

    def get_weights(self, source_id: int) -> List[OperatorWeight]:
        return self.db.query(OperatorWeight).filter(
            OperatorWeight.source_id == source_id
        ).all()
