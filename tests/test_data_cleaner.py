from datetime import datetime

import pytest

from app.services.data_import.cleaner import BasicDataCleaner
from app.services.data_import.exceptions import InvalidImportValueError
from app.services.data_import.report import CleaningReport


def test_clean_valid_rows():
    cleaner = BasicDataCleaner()

    rows = [
        {
            "date": "2026-09-10",
            "product": " Laptop ",
            "quantity": "2",
            "unit_price": "1200",
            "seller": " Amir ",
            "category": " electronics ",
        }
    ]

    result = cleaner.clean(rows)

    assert result == [
        {
            "date": datetime(2026, 9, 10),
            "product": "Laptop",
            "quantity": 2,
            "unit_price": 1200.0,
            "cost_price": None,
            "seller": "Amir",
            "customer_phone": "",
            "category": "Electronics",
        }
    ]


def test_clean_allows_empty_seller():
    cleaner = BasicDataCleaner()

    rows = [
        {
            "date": "2026-09-10",
            "product": "Laptop",
            "quantity": "2",
            "unit_price": "1200",
            "seller": "",
            "category": "",
        }
    ]

    result = cleaner.clean(rows)

    assert result[0]["seller"] == ""


@pytest.mark.parametrize(
    "field,value",
    [
        ("date", "invalid-date"),
        ("quantity", "abc"),
        ("unit_price", "abc"),
    ],
)
def test_clean_rejects_invalid_values(field, value):
    cleaner = BasicDataCleaner()
    report = CleaningReport()

    row = {
        "date": "2026-09-10",
        "product": "Laptop",
        "quantity": "2",
        "unit_price": "1200",
        "seller": "",
        "category": "",
    }
    row[field] = value

    result = cleaner.clean([row], report)

    assert result == []
    assert report.total_rows == 1
    assert report.cleaned_rows == 0
    assert report.invalid_rows == 1
    assert len(report.errors) == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("quantity", "0"),
        ("quantity", "-1"),
        ("unit_price", "-10"),
    ],
)
def test_clean_rejects_invalid_numeric_values(field, value):
    cleaner = BasicDataCleaner()
    report = CleaningReport()

    row = {
        "date": "2026-09-10",
        "product": "Laptop",
        "quantity": "2",
        "unit_price": "1200",
        "seller": "",
        "category": "",
    }
    row[field] = value

    result = cleaner.clean([row], report)

    assert result == []
    assert report.total_rows == 1
    assert report.cleaned_rows == 0
    assert report.invalid_rows == 1
    assert len(report.errors) == 1


def test_clean_rejects_empty_product():
    cleaner = BasicDataCleaner()
    report = CleaningReport()

    row = {
        "date": "2026-09-10",
        "product": "   ",
        "quantity": "2",
        "unit_price": "1200",
        "seller": "",
        "category": "",
    }

    result = cleaner.clean([row], report)

    assert result == []
    assert report.total_rows == 1
    assert report.cleaned_rows == 0
    assert report.invalid_rows == 1
    assert report.errors == ["Row 1: Product is required."]


def test_clean_report_tracks_invalid_rows():
    cleaner = BasicDataCleaner()
    report = CleaningReport()

    rows = [
        {
            "date": "2026-09-10",
            "product": "Laptop",
            "quantity": "2",
            "unit_price": "1200",
            "seller": "",
            "category": "",
        },
        {
            "date": "invalid",
            "product": "Mouse",
            "quantity": "1",
            "unit_price": "25",
            "seller": "",
            "category": "",
        },
    ]

    result = cleaner.clean(rows, report)

    assert len(result) == 1
    assert report.total_rows == 2
    assert report.cleaned_rows == 1
    assert report.invalid_rows == 1
    assert report.duplicate_rows == 0
    assert report.errors == ["Row 2: Invalid date value: 'invalid'"]


def test_clean_report_tracks_duplicates():
    cleaner = BasicDataCleaner()
    report = CleaningReport()

    row = {
        "date": "2026-09-10",
        "product": "Laptop",
        "quantity": "2",
        "unit_price": "1200",
        "seller": "",
        "category": "",
    }

    rows = [row, row.copy()]

    result = cleaner.clean(rows, report)

    assert len(result) == 1
    assert report.total_rows == 2
    assert report.cleaned_rows == 1
    assert report.duplicate_rows == 1
    assert report.invalid_rows == 0
    assert report.errors == []
