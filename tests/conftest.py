import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_db
from app.models import Base, Operator, Source, Lead, OperatorWeight

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=connection
    )
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# Фикстуры с тестовыми данными
@pytest.fixture
def test_operator(test_db):
    operator = Operator(
        name="Test Operator",
        is_active=True,
        max_load=5
    )
    test_db.add(operator)
    test_db.commit()
    test_db.refresh(operator)
    return operator


@pytest.fixture
def test_operators(test_db):
    operators = [
        Operator(name="Operator 1", is_active=True, max_load=5),
        Operator(name="Operator 2", is_active=True, max_load=10),
        Operator(name="Operator 3", is_active=False, max_load=3),
    ]
    for op in operators:
        test_db.add(op)
    test_db.commit()
    for op in operators:
        test_db.refresh(op)
    return operators


@pytest.fixture
def test_source(test_db):
    source = Source(
        name="Test Source",
        description="Test description"
    )
    test_db.add(source)
    test_db.commit()
    test_db.refresh(source)
    return source


@pytest.fixture
def test_source_with_weights(test_db, test_operators, test_source):
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
    return test_source


@pytest.fixture
def test_lead(test_db):
    lead = Lead(
        external_id="test_lead_123",
        name="Test Lead",
        phone="+79991234567",
        email="test@example.com"
    )
    test_db.add(lead)
    test_db.commit()
    test_db.refresh(lead)
    return lead
