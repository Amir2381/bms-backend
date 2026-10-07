import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_auth_context, AuthContext
from app.db.database import Base, get_db
from app.main import app
from app.models.branch import Branch
from app.models.product import Product
from app.models.user import User, UserRole
from tests.database import TestingSessionLocal, override_get_db, test_engine
from app.worker.celery_app import celery_app


def override_get_current_user():
    return User(
        id=1,
        full_name="Test User",
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.ADMIN,
        branch_id=1,
    )


def override_get_auth_context():
    user = override_get_current_user()
    return AuthContext(user=user)


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_auth_context] = override_get_auth_context


@pytest.fixture(autouse=True)
def mock_background_db_session(monkeypatch):
    from app.worker import tasks

    monkeypatch.setattr(tasks, "SessionLocal", TestingSessionLocal)
    celery_app.conf.update(task_always_eager=True)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

    Base.metadata.create_all(bind=test_engine)

    db: Session = TestingSessionLocal()

    test_branch = Branch(name="Main Branch", location="Headquarters")
    db.add(test_branch)
    db.flush()

    test_user = User(
        full_name="Test User",
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.SALESPERSON,
        branch_id=test_branch.id,
    )

    test_product = Product(
        name="Test Product",
        price=100.00,
        stock=10,
    )

    db.add_all([test_user, test_product])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
