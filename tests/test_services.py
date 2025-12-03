import pytest
from app.services import DistributionService, AppealService
from app.schemas.appeal import AppealCreate
from app.models import Appeal, OperatorWeight


class TestDistributionService:

    def test_select_operator_basic(
        self, test_db, test_source_with_weights, test_operators
    ):
        service = DistributionService(test_db)

        operator_id = service.select_operator(test_source_with_weights.id)

        assert operator_id in [test_operators[0].id, test_operators[1].id]
        assert operator_id is not None

    def test_select_operator_respects_weights(
        self, test_db, test_source, test_operators
    ):
        service = DistributionService(test_db)

        weight = OperatorWeight(
            operator_id=test_operators[1].id,
            source_id=test_source.id,
            weight=100
        )
        test_db.add(weight)
        test_db.commit()

        selections = []
        for _ in range(10):
            operator_id = service.select_operator(test_source.id)
            selections.append(operator_id)

        assert all(op_id == test_operators[1].id for op_id in selections)

    def test_select_operator_excludes_inactive(
        self, test_db, test_source, test_operators
    ):
        service = DistributionService(test_db)

        weights = [
            OperatorWeight(
                operator_id=test_operators[0].id, source_id=test_source.id,
                weight=50
            ),
            OperatorWeight(
                operator_id=test_operators[2].id, source_id=test_source.id,
                weight=50
            ),
        ]
        for w in weights:
            test_db.add(w)
        test_db.commit()

        for _ in range(5):
            operator_id = service.select_operator(test_source.id)
            assert operator_id == test_operators[0].id

    def test_select_operator_respects_max_load(
        self, test_db, test_source, test_operators, test_lead
    ):
        service = DistributionService(test_db)

        weights = [
            OperatorWeight(
                operator_id=test_operators[0].id, source_id=test_source.id,
                weight=50
            ),
            OperatorWeight(
                operator_id=test_operators[1].id, source_id=test_source.id,
                weight=50
            ),
        ]
        for w in weights:
            test_db.add(w)
        test_db.commit()

        for i in range(5):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source.id,
                operator_id=test_operators[0].id,
                status="active"
            )
            test_db.add(appeal)
        test_db.commit()

        for _ in range(5):
            operator_id = service.select_operator(test_source.id)
            assert operator_id == test_operators[1].id

    def test_select_operator_no_available(
        self, test_db, test_source, test_operators, test_lead
    ):
        service = DistributionService(test_db)

        weight = OperatorWeight(
            operator_id=test_operators[0].id,
            source_id=test_source.id,
            weight=100
        )
        test_db.add(weight)
        test_db.commit()

        for i in range(test_operators[0].max_load):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source.id,
                operator_id=test_operators[0].id,
                status="active"
            )
            test_db.add(appeal)
        test_db.commit()

        operator_id = service.select_operator(test_source.id)
        assert operator_id is None

    def test_select_operator_no_weights_configured(self, test_db, test_source):
        service = DistributionService(test_db)

        operator_id = service.select_operator(test_source.id)

        assert operator_id is None

    def test_closed_appeals_not_counted(
        self, test_db, test_source, test_operators, test_lead
    ):
        service = DistributionService(test_db)

        weight = OperatorWeight(
            operator_id=test_operators[0].id,
            source_id=test_source.id,
            weight=100
        )
        test_db.add(weight)
        test_db.commit()

        for i in range(10):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source.id,
                operator_id=test_operators[0].id,
                status="closed"
            )
            test_db.add(appeal)
        test_db.commit()

        operator_id = service.select_operator(test_source.id)
        assert operator_id == test_operators[0].id

    def test_get_available_operators_info(
        self, test_db, test_source_with_weights, test_operators, test_lead
    ):
        service = DistributionService(test_db)

        for i in range(2):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source_with_weights.id,
                operator_id=test_operators[0].id,
                status="active"
            )
            test_db.add(appeal)
        test_db.commit()

        info = service.get_available_operators_info(
            test_source_with_weights.id
        )

        assert info["source_id"] == test_source_with_weights.id
        assert len(info["operators"]) == 2

        op1_info = next(
            op for op in info["operators"] if op["id"] == test_operators[0].id
        )
        assert op1_info["current_load"] == 2
        assert op1_info["is_available"] is True


class TestAppealService:

    def test_create_appeal_new_lead(self, test_db, test_source_with_weights):
        service = AppealService(test_db)

        appeal_data = AppealCreate(
            lead_external_id="new_lead_999",
            source_id=test_source_with_weights.id,
            message="Hello!",
            lead_name="New Lead",
            lead_phone="+79991234567"
        )

        result = service.create_appeal(appeal_data)

        assert result.appeal_id is not None
        assert result.lead_external_id == "new_lead_999"
        assert result.operator is not None

    def test_create_appeal_existing_lead(
        self, test_db, test_lead, test_source_with_weights
    ):
        service = AppealService(test_db)

        appeal_data = AppealCreate(
            lead_external_id=test_lead.external_id,
            source_id=test_source_with_weights.id,
            message="Another message"
        )

        result = service.create_appeal(appeal_data)

        assert result.lead_id == test_lead.id

    def test_create_appeal_invalid_source(self, test_db):
        service = AppealService(test_db)

        appeal_data = AppealCreate(
            lead_external_id="lead_123",
            source_id=9999,
            message="Test"
        )

        with pytest.raises(Exception):  # HTTPException
            service.create_appeal(appeal_data)

    def test_create_appeal_no_available_operators(self, test_db, test_source):
        service = AppealService(test_db)

        appeal_data = AppealCreate(
            lead_external_id="lead_456",
            source_id=test_source.id,
            message="No operators"
        )

        result = service.create_appeal(appeal_data)

        assert result.appeal_id is not None
        assert result.operator is None

    def test_create_multiple_appeals_same_lead(
        self, test_db, test_source_with_weights
    ):
        service = AppealService(test_db)

        appeal1_data = AppealCreate(
            lead_external_id="lead_multi",
            source_id=test_source_with_weights.id,
            message="First",
            lead_name="Multi User"
        )
        result1 = service.create_appeal(appeal1_data)

        appeal2_data = AppealCreate(
            lead_external_id="lead_multi",
            source_id=test_source_with_weights.id,
            message="Second"
        )
        result2 = service.create_appeal(appeal2_data)

        assert result1.lead_id == result2.lead_id
        assert result1.appeal_id != result2.appeal_id

    def test_close_appeal(
        self, test_db, test_lead, test_source, test_operator
    ):
        service = AppealService(test_db)

        from app.repositories import AppealRepository
        repo = AppealRepository(test_db)
        appeal = repo.create(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id
        )

        result = service.close_appeal(appeal.id)

        assert result is True

    def test_close_nonexistent_appeal(self, test_db):
        service = AppealService(test_db)

        with pytest.raises(Exception):
            service.close_appeal(9999)


class TestDistributionFairness:

    def test_distribution_proportions(
        self, test_db, test_source, test_operators
    ):
        service = DistributionService(test_db)

        weights = [
            OperatorWeight(
                operator_id=test_operators[0].id, source_id=test_source.id,
                weight=10
            ),
            OperatorWeight(
                operator_id=test_operators[1].id, source_id=test_source.id,
                weight=30
            ),
        ]
        for w in weights:
            test_db.add(w)
        test_db.commit()

        selections = []
        for _ in range(100):
            operator_id = service.select_operator(test_source.id)
            selections.append(operator_id)

        count_op1 = selections.count(test_operators[0].id)
        count_op2 = selections.count(test_operators[1].id)

        assert 15 < count_op1 < 35
        assert 65 < count_op2 < 85
        assert count_op1 + count_op2 == 100
