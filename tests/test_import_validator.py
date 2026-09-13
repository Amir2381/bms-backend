import pytest

from app.services.data_import.exceptions import MissingRequiredColumnError
from app.services.data_import.validator import BasicImportValidator


def test_validate_accepts_required_columns():
    validator = BasicImportValidator()

    headers = [
        "date",
        "product",
        "quantity",
        "unit_price",
    ]

    validator.validate(headers)


def test_validate_accepts_column_aliases():
    validator = BasicImportValidator()

    headers = [
        "sale_date",
        "product_name",
        "qty",
        "price",
    ]

    validator.validate(headers)


def test_validate_accepts_case_and_whitespace_variations():
    validator = BasicImportValidator()

    headers = [
        " DATE ",
        " Product ",
        " QUANTITY ",
        " UNIT_PRICE ",
    ]

    validator.validate(headers)


def test_validate_allows_missing_optional_seller():
    validator = BasicImportValidator()

    headers = [
        "date",
        "product",
        "quantity",
        "unit_price",
    ]

    validator.validate(headers)


@pytest.mark.parametrize(
    "missing_column",
    [
        "date",
        "product",
        "quantity",
        "unit_price",
    ],
)
def test_validate_rejects_missing_required_column(missing_column):
    validator = BasicImportValidator()

    headers = [
        "date",
        "product",
        "quantity",
        "unit_price",
    ]
    headers.remove(missing_column)

    with pytest.raises(MissingRequiredColumnError):
        validator.validate(headers)


def test_validate_reports_multiple_missing_columns():
    validator = BasicImportValidator()

    headers = [
        "date",
        "product",
    ]

    with pytest.raises(
        MissingRequiredColumnError,
        match="quantity.*unit_price",
    ):
        validator.validate(headers)
