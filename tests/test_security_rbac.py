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


def test_salesperson_cannot_access_other_branch_sales(client):
    from app.main import app
    from app.models.branch import Branch
    from app.models.sales import Sale
    from tests.database import TestingSessionLocal

    db = TestingSessionLocal()
    try:
        other_branch = Branch(name="Other Branch", location="Remote")
        db.add(other_branch)
        db.commit()
        db.refresh(other_branch)

        other_user = User(
            full_name="Other",
            email="other@example.com",
            hashed_password="hash",
            role=UserRole.SALESPERSON,
            branch_id=other_branch.id,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        other_sale = Sale(user_id=other_user.id, branch_id=other_branch.id)
        db.add(other_sale)
        db.commit()
        db.refresh(other_sale)
        other_sale_id = other_sale.id
    finally:
        db.close()

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
        response = client.get(f"/sales/{other_sale_id}")
        assert response.status_code == 404
    finally:
        from tests.conftest import override_get_current_user

        app.dependency_overrides[get_current_user] = override_get_current_user
