from app.core.security import get_current_user
from app.models.user import User, UserRole


def test_salesperson_cannot_access_admin_endpoints(client):
    from app.main import app

    def override_get_salesperson():
        return User(
            id=2,
            full_name="Sales Person",
            email="sales@example.com",
            hashed_password="hashed",
            role=UserRole.SALESPERSON,
            branch_id=1,
        )

    app.dependency_overrides[get_current_user] = override_get_salesperson

    try:
        category_response = client.get("/categories")
        assert category_response.status_code == 403

        users_response = client.get("/users")
        assert users_response.status_code == 403

        analytics_response = client.get("/analytics/salespersons/performance")
        assert analytics_response.status_code == 403

    finally:
        from tests.conftest import override_get_current_user

        app.dependency_overrides[get_current_user] = override_get_current_user
