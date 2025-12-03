from sqlalchemy.orm import Session
from typing import Optional
import random
from app.models import OperatorWeight, Operator, Appeal


class DistributionService:

    def __init__(self, db: Session):
        self.db = db

    def select_operator(self, source_id: int) -> Optional[int]:
        weights = self.db.query(OperatorWeight).filter(
            OperatorWeight.source_id == source_id
        ).all()

        if not weights:
            return None

        available_operators = []
        operator_weights = []

        for weight in weights:
            operator = weight.operator

            if not operator.is_active:
                continue

            current_load = self._get_operator_load(operator.id)
            if current_load >= operator.max_load:
                continue

            available_operators.append(operator.id)
            operator_weights.append(weight.weight)

        if not available_operators:
            return None

        total_weight = sum(operator_weights)
        probabilities = [w / total_weight for w in operator_weights]

        selected_operator_id = random.choices(
            available_operators,
            weights=probabilities
        )[0]

        return selected_operator_id

    def _get_operator_load(self, operator_id: int) -> int:
        return self.db.query(Appeal).filter(
            Appeal.operator_id == operator_id,
            Appeal.status == "active"
        ).count()

    def get_available_operators_info(self, source_id: int) -> dict:
        weights = self.db.query(OperatorWeight).filter(
            OperatorWeight.source_id == source_id
        ).all()

        result = {
            "source_id": source_id,
            "operators": []
        }

        for weight in weights:
            operator = weight.operator
            current_load = self._get_operator_load(operator.id)
            is_available = (
                    operator.is_active and
                    current_load < operator.max_load
            )

            result["operators"].append(
                {
                    "id": operator.id,
                    "name": operator.name,
                    "weight": weight.weight,
                    "is_active": operator.is_active,
                    "current_load": current_load,
                    "max_load": operator.max_load,
                    "is_available": is_available
                }
            )

        return result
