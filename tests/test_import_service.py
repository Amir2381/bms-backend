from datetime import datetime

from app.models.sales import Sale, SaleItem
from app.models.user import User
from app.repositories import product_repository
from tests.database import TestingSessionLocal
from app.services.data_import.cleaner import BasicDataCleaner
from app.services.data_import.csv_parser import CsvFileParser
from app.services.data_import.domain_mapper import BasicDomainMapper
from app.services.data_import.import_sale_service import ImportSaleService
from app.services.data_import.mapper import BasicColumnMapper
from app.services.data_import.service import ImportService
from app.services.data_import.validator import BasicImportValidator
from app.services.data_import.types import ImportedSaleInput


class FakeImportSaleService(ImportSaleService):
    def create_sales(
        self,
        db,
        sale_inputs,
        current_user,
    ):
        return sale_inputs


def create_import_service() -> ImportService:
    return ImportService(
        parser=CsvFileParser(),
        validator=BasicImportValidator(),
        mapper=BasicColumnMapper(),
        cleaner=BasicDataCleaner(),
        domain_mapper=BasicDomainMapper(),
        sale_service=FakeImportSaleService(),
    )


def test_import_service_processes_csv_with_aliases(tmp_path):
    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "sale_date,product_name,qty,price,user,category\n"
        "2026-09-10,Laptop,2,1200,Amir,electronics\n"
        "2026-09-11,Mouse,5,25,Reza, accessories \n",
        encoding="utf-8",
    )

    service = create_import_service()

    result = service.process(
        file_path=str(csv_file),
        db=None,
        current_user=None,
    )

    assert result.rows == [
        ImportedSaleInput(
            sale_date=datetime(2026, 9, 10),
            product="Laptop",
            quantity=2,
            unit_price=1200.0,
            seller="Amir",
            category="Electronics",
        ),
        ImportedSaleInput(
            sale_date=datetime(2026, 9, 11),
            product="Mouse",
            quantity=5,
            unit_price=25.0,
            seller="Reza",
            category="Accessories",
        ),
    ]

    assert result.report.total_rows == 2
    assert result.report.cleaned_rows == 2
    assert result.report.duplicate_rows == 0
    assert result.report.invalid_rows == 0
    assert result.report.errors == []


def test_import_service_reports_invalid_rows(tmp_path):
    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "date,product,quantity,unit_price,seller\n"
        "2026-09-10,Laptop,2,1200,Amir\n"
        "invalid,Mouse,5,25,Reza\n",
        encoding="utf-8",
    )

    service = create_import_service()

    result = service.process(
        file_path=str(csv_file),
        db=None,
        current_user=None,
    )

    assert len(result.rows) == 1
    assert result.report.total_rows == 2
    assert result.report.cleaned_rows == 1
    assert result.report.invalid_rows == 1
    assert result.report.duplicate_rows == 0
    assert len(result.report.errors) == 1


def test_import_service_creates_sales_in_database(tmp_path):
    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "date,product,quantity,unit_price\n" "2026-09-10,Test Product,2,75.50\n",
        encoding="utf-8",
    )

    db = TestingSessionLocal()

    try:
        current_user = db.query(User).filter_by(email="test@example.com").first()

        product = product_repository.get_product_by_name(
            db,
            "Test Product",
        )

        service = ImportService(
            parser=CsvFileParser(),
            validator=BasicImportValidator(),
            mapper=BasicColumnMapper(),
            cleaner=BasicDataCleaner(),
            domain_mapper=BasicDomainMapper(),
            sale_service=ImportSaleService(),
        )

        result = service.process(
            file_path=str(csv_file),
            db=db,
            current_user=current_user,
        )

        sale = db.query(Sale).first()
        sale_item = db.query(SaleItem).first()

        assert sale is not None
        assert sale.user_id == current_user.id

        assert sale_item is not None
        assert sale_item.product_id == product.id
        assert sale_item.quantity == 2
        assert float(sale_item.unit_price) == 75.50

        db.refresh(product)
        assert product.stock == 10

        assert len(result.rows) == 1

    finally:
        db.close()


def test_import_sales_endpoint_creates_sale_in_database(client):
    csv_content = (
        "date,product,quantity,unit_price\n" "2026-09-12,Test Product,2,75.50\n"
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

    data = response.json()

    assert data["message"] == "Sales imported successfully."
    assert data["filename"] == "sales.csv"
    assert data["imported_rows"] == 1

    db = TestingSessionLocal()

    try:
        sale = db.query(Sale).first()
        sale_item = db.query(SaleItem).first()

        assert sale is not None
        assert sale.user_id == 1

        assert sale_item is not None
        assert sale_item.quantity == 2
        assert float(sale_item.unit_price) == 75.50

        product = product_repository.get_product_by_name(
            db,
            "Test Product",
        )

        assert product is not None
        assert product.stock == 10

    finally:
        db.close()


def test_import_sales_returns_404_when_product_not_found(client):
    csv_content = (
        "date,product,quantity,unit_price\n" "2026-09-12,Unknown Product,2,75.50\n"
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


def test_import_sales_rejects_missing_required_column(client):
    csv_content = "date,product,quantity\n" "2026-09-12,Test Product,2\n"

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

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert "unit_price" in data["error"]


def test_import_sales_rejects_invalid_quantity(client):
    csv_content = (
        "date,product,quantity,unit_price\n" "2026-09-12,Test Product,invalid,75.50\n"
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

    data = response.json()

    assert data["imported_rows"] == 0
    assert data["cleaning_report"]["invalid_rows"] == 1
    assert len(data["cleaning_report"]["errors"]) == 1

    db = TestingSessionLocal()

    try:
        assert db.query(Sale).count() == 0
        assert db.query(SaleItem).count() == 0
    finally:
        db.close()


def test_import_sales_rolls_back_when_seller_not_found(client):
    csv_content = (
        "date,product,quantity,unit_price,seller\n"
        "2026-09-12,Test Product,2,75.50,unknown@example.com\n"
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

    assert response.status_code == 404

    db = TestingSessionLocal()

    try:
        assert db.query(Sale).count() == 0
        assert db.query(SaleItem).count() == 0
    finally:
        db.close()
