import pytest
from app.repositories import (
    OperatorRepository,
    SourceRepository,
    LeadRepository,
    AppealRepository,
)
from app.schemas.operator import OperatorCreate, OperatorUpdate
from app.schemas.source import SourceCreate, WeightConfig
from app.models import Appeal


class TestOperatorRepository:

    def test_create_operator(self, test_db):
        repo = OperatorRepository(test_db)
        operator_data = OperatorCreate(
            name="New Operator",
            is_active=True,
            max_load=15
        )

        operator = repo.create(operator_data)

        assert operator.id is not None
        assert operator.name == "New Operator"
        assert operator.max_load == 15

    def test_get_by_id(self, test_db, test_operator):
        repo = OperatorRepository(test_db)

        operator = repo.get_by_id(test_operator.id)

        assert operator is not None
        assert operator.id == test_operator.id
        assert operator.name == test_operator.name

    def test_get_by_id_not_found(self, test_db):
        repo = OperatorRepository(test_db)

        operator = repo.get_by_id(9999)

        assert operator is None

    def test_get_all(self, test_db, test_operators):
        repo = OperatorRepository(test_db)

        operators = repo.get_all()

        assert len(operators) == 3

    def test_update_operator(self, test_db, test_operator):
        repo = OperatorRepository(test_db)
        update_data = OperatorUpdate(
            is_active=False,
            max_load=20
        )

        updated = repo.update(test_operator.id, update_data)

        assert updated is not None
        assert updated.is_active is False
        assert updated.max_load == 20
        assert updated.name == test_operator.name

    def test_get_current_load(
        self, test_db, test_operator, test_lead, test_source
    ):
        repo = OperatorRepository(test_db)

        for i in range(3):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source.id,
                operator_id=test_operator.id,
                status="active"
            )
            test_db.add(appeal)

        closed_appeal = Appeal(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id,
            status="closed"
        )
        test_db.add(closed_appeal)
        test_db.commit()

        load = repo.get_current_load(test_operator.id)

        assert load == 3

    def test_get_all_with_load(
        self, test_db, test_operators, test_lead, test_source
    ):
        repo = OperatorRepository(test_db)

        for i in range(2):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source.id,
                operator_id=test_operators[0].id,
                status="active"
            )
            test_db.add(appeal)
        test_db.commit()

        operators_with_load = repo.get_all_with_load()

        assert len(operators_with_load) == 3
        assert operators_with_load[0]["current_load"] == 2
        assert operators_with_load[1]["current_load"] == 0


class TestSourceRepository:

    def test_create_source(self, test_db):
        repo = SourceRepository(test_db)
        source_data = SourceCreate(
            name="WhatsApp Bot",
            description="WhatsApp channel"
        )

        source = repo.create(source_data)

        assert source.id is not None
        assert source.name == "WhatsApp Bot"
        assert source.description == "WhatsApp channel"

    def test_get_by_id(self, test_db, test_source):
        repo = SourceRepository(test_db)

        source = repo.get_by_id(test_source.id)

        assert source is not None
        assert source.id == test_source.id

    def test_get_all(self, test_db, test_source):
        repo = SourceRepository(test_db)

        source2 = SourceCreate(name="Source 2")
        repo.create(source2)

        sources = repo.get_all()

        assert len(sources) == 2

    def test_configure_weights(self, test_db, test_source, test_operators):
        repo = SourceRepository(test_db)

        weights = [
            WeightConfig(operator_id=test_operators[0].id, weight=10),
            WeightConfig(operator_id=test_operators[1].id, weight=30),
        ]

        success = repo.configure_weights(test_source.id, weights)

        assert success is True

        saved_weights = repo.get_weights(test_source.id)
        assert len(saved_weights) == 2
        assert saved_weights[0].weight in [10, 30]

    def test_configure_weights_replaces_old(
        self, test_db, test_source_with_weights, test_operators
    ):
        repo = SourceRepository(test_db)

        old_weights = repo.get_weights(test_source_with_weights.id)
        assert len(old_weights) == 2

        new_weights = [
            WeightConfig(operator_id=test_operators[0].id, weight=50),
        ]
        repo.configure_weights(test_source_with_weights.id, new_weights)

        saved_weights = repo.get_weights(test_source_with_weights.id)
        assert len(saved_weights) == 1
        assert saved_weights[0].weight == 50

    def test_configure_weights_invalid_operator(self, test_db, test_source):
        repo = SourceRepository(test_db)

        weights = [
            WeightConfig(operator_id=9999, weight=10),
        ]

        with pytest.raises(ValueError):
            repo.configure_weights(test_source.id, weights)


class TestLeadRepository:

    def test_get_or_create_new_lead(self, test_db):
        repo = LeadRepository(test_db)

        lead = repo.get_or_create(
            external_id="new_user_456",
            name="New User",
            phone="+79991234567"
        )

        assert lead.id is not None
        assert lead.external_id == "new_user_456"
        assert lead.name == "New User"

    def test_get_or_create_existing_lead(self, test_db, test_lead):
        repo = LeadRepository(test_db)

        lead = repo.get_or_create(
            external_id=test_lead.external_id,
            name="Different Name"
        )

        assert lead.id == test_lead.id
        assert lead.name == test_lead.name

    def test_get_by_id(self, test_db, test_lead):
        repo = LeadRepository(test_db)

        lead = repo.get_by_id(test_lead.id)

        assert lead is not None
        assert lead.id == test_lead.id

    def test_get_all_with_appeals_count(
        self, test_db, test_lead, test_source, test_operator
    ):
        repo = LeadRepository(test_db)

        for i in range(3):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source.id,
                operator_id=test_operator.id
            )
            test_db.add(appeal)
        test_db.commit()

        leads = repo.get_all_with_appeals_count()

        assert len(leads) == 1
        assert leads[0]["id"] == test_lead.id
        assert leads[0]["appeals_count"] == 3

    def test_get_lead_appeals(
        self, test_db, test_lead, test_source, test_operator
    ):
        repo = LeadRepository(test_db)

        for i in range(2):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source.id,
                operator_id=test_operator.id
            )
            test_db.add(appeal)
        test_db.commit()

        appeals = repo.get_lead_appeals(test_lead.id)

        assert len(appeals) == 2
        assert all(a.lead_id == test_lead.id for a in appeals)


class TestAppealRepository:

    def test_create_appeal(
        self, test_db, test_lead, test_source, test_operator
    ):
        repo = AppealRepository(test_db)

        appeal = repo.create(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id,
            message="Test message"
        )

        assert appeal.id is not None
        assert appeal.lead_id == test_lead.id
        assert appeal.operator_id == test_operator.id
        assert appeal.status == "active"

    def test_create_appeal_without_operator(
        self, test_db, test_lead, test_source
    ):
        repo = AppealRepository(test_db)

        appeal = repo.create(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=None,
            message="No operator available"
        )

        assert appeal.id is not None
        assert appeal.operator_id is None
        assert appeal.status == "active"

    def test_get_by_id(self, test_db, test_lead, test_source, test_operator):
        repo = AppealRepository(test_db)

        appeal = repo.create(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id
        )

        found = repo.get_by_id(appeal.id)

        assert found is not None
        assert found.id == appeal.id

    def test_close_appeal(
        self, test_db, test_lead, test_source, test_operator
    ):
        repo = AppealRepository(test_db)

        appeal = repo.create(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id
        )

        success = repo.close(appeal.id)

        assert success is True

        closed = repo.get_by_id(appeal.id)
        assert closed.status == "closed"

    def test_close_nonexistent_appeal(self, test_db):
        repo = AppealRepository(test_db)

        success = repo.close(9999)

        assert success is False

    def test_get_distribution_stats(
        self, test_db, test_source, test_operators, test_lead
    ):
        repo = AppealRepository(test_db)

        for i in range(3):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source.id,
                operator_id=test_operators[0].id
            )
            test_db.add(appeal)

        for i in range(2):
            appeal = Appeal(
                lead_id=test_lead.id,
                source_id=test_source.id,
                operator_id=test_operators[1].id
            )
            test_db.add(appeal)
        test_db.commit()

        stats = repo.get_distribution_stats()

        assert len(stats) == 1
        assert stats[0]["source_id"] == test_source.id
        assert stats[0]["total_appeals"] == 5
        assert len(stats[0]["operators"]) == 2
