from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Operator, Appeal
from app.schemas.operator import OperatorCreate, OperatorUpdate


class OperatorRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, operator_data: OperatorCreate) -> Operator:
        operator = Operator(**operator_data.model_dump())
        self.db.add(operator)
        self.db.commit()
        self.db.refresh(operator)
        return operator

    def get_by_id(self, operator_id: int) -> Optional[Operator]:
        return self.db.query(Operator).filter(
            Operator.id == operator_id
        ).first()

    def get_all(self) -> List[Operator]:
        return self.db.query(Operator).all()

    def update(self, operator_id: int, operator_data: OperatorUpdate) -> \
            Optional[Operator]:
        operator = self.get_by_id(operator_id)
        if not operator:
            return None

        update_data = operator_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(operator, field, value)

        self.db.commit()
        self.db.refresh(operator)
        return operator

    def get_current_load(self, operator_id: int) -> int:
        return self.db.query(Appeal).filter(
            Appeal.operator_id == operator_id,
            Appeal.status == "active"
        ).count()

    def get_all_with_load(self) -> List[dict]:
        operators = self.get_all()
        result = []
        for op in operators:
            result.append(
                {
                    "id": op.id,
                    "name": op.name,
                    "is_active": op.is_active,
                    "max_load": op.max_load,
                    "current_load": self.get_current_load(op.id)
                }
            )
        return result
