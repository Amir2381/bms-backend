import pytest
from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.db.database import Base, get_db
from app.main import app
from app.models.user import User
from tests.database import override_get_db, test_engine


def override_get_current_user():
    return User(
        id=1,
        full_name="Test User",
        email="test@example.com",
        hashed_password="hashed_password",
    )


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)
