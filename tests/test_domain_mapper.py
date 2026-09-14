from datetime import datetime

from app.services.data_import.domain_mapper import BasicDomainMapper
from app.services.data_import.types import ImportedSaleInput


def test_map_clean_rows_to_imported_sale_input():
    mapper = BasicDomainMapper()

    sale_date = datetime(2026, 9, 10)

    rows = [
        {
            "date": sale_date,
            "product": "Laptop",
            "quantity": 2,
            "unit_price": 1200.0,
            "seller": "Amir",
        }
    ]

    result = mapper.map(rows)

    assert result == [
        ImportedSaleInput(
            sale_date=sale_date,
            product="Laptop",
            quantity=2,
            unit_price=1200.0,
            seller="Amir",
        )
    ]


def test_map_allows_missing_seller():
    mapper = BasicDomainMapper()

    sale_date = datetime(2026, 9, 10)

    rows = [
        {
            "date": sale_date,
            "product": "Laptop",
            "quantity": 2,
            "unit_price": 1200.0,
        }
    ]

    result = mapper.map(rows)

    assert result == [
        ImportedSaleInput(
            sale_date=sale_date,
            product="Laptop",
            quantity=2,
            unit_price=1200.0,
            seller="",
        )
    ]


def test_map_empty_rows():
    mapper = BasicDomainMapper()

    assert mapper.map([]) == []
