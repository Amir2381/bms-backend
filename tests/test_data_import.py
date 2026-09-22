from io import BytesIO

from tests.database import TestingSessionLocal
from app.models.sales import Sale, SaleItem


def test_upload_csv_file(client):
    response = client.post(
        "/import/sales",
        files={
            "file": (
                "sales.csv",
                BytesIO(b"date,product,quantity,unit_price\n"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "sales.csv"


def test_reject_unsupported_file_type(client):
    response = client.post(
        "/import/sales",
        files={
            "file": (
                "sales.txt",
                BytesIO(b"test"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_reject_empty_file(client):
    response = client.post(
        "/import/sales",
        files={
            "file": (
                "sales.csv",
                BytesIO(b""),
                "text/csv",
            )
        },
    )

    assert response.status_code == 400


def test_reject_file_larger_than_max_size(client, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "import_max_file_size", 10)

    response = client.post(
        "/import/sales",
        files={
            "file": (
                "sales.csv",
                BytesIO(b"12345678901"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 413


def test_import_sales_rolls_back_entire_batch_when_domain_error_occurs(client):
    csv_content = (
        "date,product,quantity,unit_price\n"
        "2026-09-12,Test Product,2,75.50\n"
        "2026-09-12,Unknown Product,3,80.00\n"
        "2026-09-12,Test Product,1,90.00\n"
    )

    response = client.post(
        "/import/sales",
        files={"file": ("sales.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert "Unknown Product" in data["error"]

    db = TestingSessionLocal()

    try:
        assert db.query(Sale).count() == 0
        assert db.query(SaleItem).count() == 0
    finally:
        db.close()


def test_import_sales_with_category_creates_and_links_category(client):
    csv_content = (
        "date,product,quantity,unit_price,category\n"
        "2026-09-12,Test Product,2,75.50, electronics \n"
    )

    response = client.post(
        "/import/sales",
        files={
            "file": (
                "sales.csv",
                csv_content,
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    db = TestingSessionLocal()
    try:
        from app.models.category import Category
        from app.models.product import Product

        category = db.query(Category).filter_by(name="Electronics").first()
        assert category is not None

        product = db.query(Product).filter_by(name="Test Product").first()
        assert product is not None
        assert product.category_id == category.id
    finally:
        db.close()
