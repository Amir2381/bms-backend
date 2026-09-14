from datetime import datetime

from app.models.product import Product
from app.models.user import User
from app.models.sales import Sale
from app.services.data_import.import_sale_service import ImportSaleService
from app.services.data_import.types import ImportedSaleInput
from tests.database import TestingSessionLocal
from app.services.data_import.exceptions import (
    ImportedProductNotFoundError,
    ImportedSellerNotFoundError,
)


def test_create_imported_sale_preserves_price_and_stock():
    db = TestingSessionLocal()

    try:
        user = db.query(User).filter(User.email == "test@example.com").first()
        product = db.query(Product).filter(Product.name == "Test Product").first()

        service = ImportSaleService()

        sale_input = ImportedSaleInput(
            sale_date=datetime(2026, 9, 10),
            product="Test Product",
            quantity=2,
            unit_price=75.0,
            seller="",
        )

        sale = service.create_sale(
            db=db,
            sale_input=sale_input,
            current_user=user,
        )

        db.commit()
        db.refresh(sale)

        assert sale.user_id == user.id
        assert sale.sale_date == datetime(2026, 9, 10)

        assert len(sale.items) == 1
        assert sale.items[0].product_id == product.id
        assert sale.items[0].quantity == 2
        assert float(sale.items[0].unit_price) == 75.0

        db.refresh(product)
        assert product.stock == 10

    finally:
        db.close()


def test_create_imported_sale_with_seller():
    db = TestingSessionLocal()

    try:
        current_user = db.query(User).filter(User.email == "test@example.com").first()

        seller = User(
            full_name="Imported Seller",
            email="seller@example.com",
            hashed_password="hashed",
        )

        db.add(seller)
        db.commit()
        db.refresh(seller)

        service = ImportSaleService()

        sale_input = ImportedSaleInput(
            sale_date=datetime(2026, 9, 10),
            product="Test Product",
            quantity=2,
            unit_price=75.0,
            seller="seller@example.com",
        )

        sale = service.create_sale(
            db=db,
            sale_input=sale_input,
            current_user=current_user,
        )

        assert sale.user_id == seller.id

    finally:
        db.rollback()
        db.close()


def test_create_imported_sale_product_not_found():
    db = TestingSessionLocal()

    try:
        current_user = db.query(User).filter(User.email == "test@example.com").first()

        service = ImportSaleService()

        sale_input = ImportedSaleInput(
            sale_date=datetime(2026, 9, 10),
            product="Unknown Product",
            quantity=2,
            unit_price=75.0,
        )

        try:
            service.create_sale(
                db=db,
                sale_input=sale_input,
                current_user=current_user,
            )
            assert False
        except ImportedProductNotFoundError as exc:
            assert str(exc) == "Product 'Unknown Product' not found."

    finally:
        db.rollback()
        db.close()


def test_create_imported_sale_seller_not_found():
    db = TestingSessionLocal()

    try:
        current_user = db.query(User).filter(User.email == "test@example.com").first()

        service = ImportSaleService()

        sale_input = ImportedSaleInput(
            sale_date=datetime(2026, 9, 10),
            product="Test Product",
            quantity=2,
            unit_price=75.0,
            seller="unknown@example.com",
        )

        try:
            service.create_sale(
                db=db,
                sale_input=sale_input,
                current_user=current_user,
            )
            assert False
        except ImportedSellerNotFoundError as exc:
            assert str(exc) == "Seller 'unknown@example.com' not found."

    finally:
        db.rollback()
        db.close()


def test_create_sales_is_atomic():
    db = TestingSessionLocal()

    try:
        current_user = db.query(User).filter(User.email == "test@example.com").first()

        service = ImportSaleService()

        sale_inputs = [
            ImportedSaleInput(
                sale_date=datetime(2026, 9, 10),
                product="Test Product",
                quantity=2,
                unit_price=75.0,
            ),
            ImportedSaleInput(
                sale_date=datetime(2026, 9, 11),
                product="Unknown Product",
                quantity=1,
                unit_price=80.0,
            ),
        ]

        try:
            service.create_sales(
                db=db,
                sale_inputs=sale_inputs,
                current_user=current_user,
            )
            assert False
        except ImportedProductNotFoundError:
            pass

        db.expire_all()

        sales = db.query(Sale).all()

        assert sales == []

    finally:
        db.rollback()
        db.close()
