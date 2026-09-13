from app.services.data_import.mapper import BasicColumnMapper


def test_map_standard_columns():
    mapper = BasicColumnMapper()

    rows = [
        {
            "date": "2026-09-10",
            "product": "Laptop",
            "quantity": "2",
            "unit_price": "1200",
            "seller": "Amir",
        }
    ]

    result = mapper.map(rows)

    assert result == rows


def test_map_aliases_to_standard_columns():
    mapper = BasicColumnMapper()

    rows = [
        {
            "sale_date": "2026-09-10",
            "product_name": "Laptop",
            "qty": "2",
            "price": "1200",
            "user": "Amir",
        }
    ]

    result = mapper.map(rows)

    assert result == [
        {
            "date": "2026-09-10",
            "product": "Laptop",
            "quantity": "2",
            "unit_price": "1200",
            "seller": "Amir",
        }
    ]


def test_map_allows_missing_optional_seller():
    mapper = BasicColumnMapper()

    rows = [
        {
            "date": "2026-09-10",
            "product": "Laptop",
            "quantity": "2",
            "unit_price": "1200",
        }
    ]

    result = mapper.map(rows)

    assert result == [
        {
            "date": "2026-09-10",
            "product": "Laptop",
            "quantity": "2",
            "unit_price": "1200",
        }
    ]


def test_map_empty_rows():
    mapper = BasicColumnMapper()

    assert mapper.map([]) == []
