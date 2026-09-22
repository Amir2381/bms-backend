from typing import Protocol

from app.services.data_import.exceptions import MissingRequiredColumnError

COLUMN_ALIASES = {
    "date": {
        "date",
        "sale_date",
        "transaction_date",
    },
    "product": {
        "product",
        "product_name",
    },
    "quantity": {
        "quantity",
        "qty",
        "count",
    },
    "unit_price": {
        "unit_price",
        "price",
        "sale_price",
    },
    "seller": {
        "seller",
        "user",
        "user_id",
        "salesperson",
    },
    "category": {
        "category",
        "category_name",
        "group",
        "type",
    },
}

REQUIRED_COLUMNS = {
    "date",
    "product",
    "quantity",
    "unit_price",
}


class ImportValidator(Protocol):
    def validate(self, headers: list[str]) -> None: ...


class BasicImportValidator:
    def validate(self, headers: list[str]) -> None:
        normalized_headers = {
            header.strip().lower() for header in headers if header.strip()
        }

        missing_columns = []

        for required_column in REQUIRED_COLUMNS:
            aliases = COLUMN_ALIASES[required_column]

            if not normalized_headers.intersection(aliases):
                missing_columns.append(required_column)

        if missing_columns:
            raise MissingRequiredColumnError(
                f"Missing required columns: {', '.join(sorted(missing_columns))}"
            )
