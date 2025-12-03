import pytest
from app.models import Operator, Source, Lead, Appeal, OperatorWeight


class TestOperatorModel:

    def test_create_operator(self, test_db):
        operator = Operator(
            name="John Doe",
            is_active=True,
            max_load=10
        )
        test_db.add(operator)
        test_db.commit()
        test_db.refresh(operator)

        assert operator.id is not None
        assert operator.name == "John Doe"
        assert operator.is_active is True
        assert operator.max_load == 10

    def test_operator_defaults(self, test_db):
        operator = Operator(name="Jane Doe")
        test_db.add(operator)
        test_db.commit()
        test_db.refresh(operator)

        assert operator.is_active is True
        assert operator.max_load == 10


class TestSourceModel:

    def test_create_source(self, test_db):
        source = Source(
            name="Telegram Bot",
            description="Main bot"
        )
        test_db.add(source)
        test_db.commit()
        test_db.refresh(source)

        assert source.id is not None
        assert source.name == "Telegram Bot"
        assert source.description == "Main bot"

    def test_source_unique_name(self, test_db):
        source1 = Source(name="Bot1")
        test_db.add(source1)
        test_db.commit()

        source2 = Source(name="Bot1")
        test_db.add(source2)

        with pytest.raises(Exception):
            test_db.commit()


class TestLeadModel:

    def test_create_lead(self, test_db):
        lead = Lead(
            external_id="tg_user_123",
            name="Alice",
            phone="+79991234567",
            email="alice@example.com"
        )
        test_db.add(lead)
        test_db.commit()
        test_db.refresh(lead)

        assert lead.id is not None
        assert lead.external_id == "tg_user_123"
        assert lead.name == "Alice"

    def test_lead_unique_external_id(self, test_db):
        lead1 = Lead(external_id="user_123", name="User1")
        test_db.add(lead1)
        test_db.commit()

        lead2 = Lead(external_id="user_123", name="User2")
        test_db.add(lead2)

        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestOperatorWeightModel:

    def test_create_weight(self, test_db, test_operator, test_source):
        weight = OperatorWeight(
            operator_id=test_operator.id,
            source_id=test_source.id,
            weight=50
        )
        test_db.add(weight)
        test_db.commit()
        test_db.refresh(weight)

        assert weight.id is not None
        assert weight.operator_id == test_operator.id
        assert weight.source_id == test_source.id
        assert weight.weight == 50

    def test_weight_default(self, test_db, test_operator, test_source):
        weight = OperatorWeight(
            operator_id=test_operator.id,
            source_id=test_source.id
        )
        test_db.add(weight)
        test_db.commit()
        test_db.refresh(weight)

        assert weight.weight == 1


class TestAppealModel:

    def test_create_appeal(
        self, test_db, test_lead, test_source, test_operator
    ):
        """Тест создания обращения"""
        appeal = Appeal(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id,
            message="Hello!",
            status="active"
        )
        test_db.add(appeal)
        test_db.commit()
        test_db.refresh(appeal)

        assert appeal.id is not None
        assert appeal.lead_id == test_lead.id
        assert appeal.operator_id == test_operator.id
        assert appeal.status == "active"
        assert appeal.created_at is not None

    def test_appeal_without_operator(self, test_db, test_lead, test_source):
        appeal = Appeal(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=None,
            message="No operator"
        )
        test_db.add(appeal)
        test_db.commit()
        test_db.refresh(appeal)

        assert appeal.operator_id is None
        assert appeal.status == "active"


class TestRelationships:

    def test_operator_appeals_relationship(
        self, test_db, test_operator, test_lead, test_source
    ):
        appeal1 = Appeal(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id
        )
        appeal2 = Appeal(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id
        )
        test_db.add_all([appeal1, appeal2])
        test_db.commit()

        assert len(test_operator.appeals) == 2

    def test_lead_appeals_relationship(
        self, test_db, test_lead, test_source, test_operator
    ):
        appeal1 = Appeal(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id
        )
        appeal2 = Appeal(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id
        )
        test_db.add_all([appeal1, appeal2])
        test_db.commit()

        assert len(test_lead.appeals) == 2

    def test_source_weights_relationship(
        self, test_db, test_source, test_operators
    ):
        weight1 = OperatorWeight(
            operator_id=test_operators[0].id,
            source_id=test_source.id,
            weight=10
        )
        weight2 = OperatorWeight(
            operator_id=test_operators[1].id,
            source_id=test_source.id,
            weight=20
        )
        test_db.add_all([weight1, weight2])
        test_db.commit()

        assert len(test_source.weights) == 2
