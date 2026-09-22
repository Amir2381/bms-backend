from datetime import datetime
from typing import Protocol

from app.services.data_import.exceptions import InvalidImportValueError
from app.services.data_import.report import CleaningReport
from app.services.data_import.types import CleanImportRow, RawImportRow


class DataCleaner(Protocol):
    def clean(
        self,
        rows: list[RawImportRow],
        report: CleaningReport | None = None,
    ) -> list[CleanImportRow]: ...


class BasicDataCleaner:
    def clean(
        self,
        rows: list[RawImportRow],
        report: CleaningReport | None = None,
    ) -> list[CleanImportRow]:
        if report is None:
            report = CleaningReport()

        report.total_rows = len(rows)

        cleaned_rows = []
        seen_rows = set()

        for row_number, row in enumerate(rows, start=1):
            try:
                cleaned_row = {
                    "date": self._parse_date(row.get("date", "")),
                    "product": self._clean_product(row.get("product", "")),
                    "quantity": self._parse_quantity(row.get("quantity", "")),
                    "unit_price": self._parse_unit_price(row.get("unit_price", "")),
                    "seller": self._clean_seller(row.get("seller", "")),
                    "category": self._clean_category(row.get("category", "")),
                }

                duplicate_key = (
                    cleaned_row["date"],
                    cleaned_row["product"],
                    cleaned_row["quantity"],
                    cleaned_row["unit_price"],
                    cleaned_row["seller"],
                    cleaned_row["category"],
                )

                if duplicate_key in seen_rows:
                    report.duplicate_rows += 1
                    continue

                seen_rows.add(duplicate_key)
                cleaned_rows.append(cleaned_row)
                report.cleaned_rows += 1

            except InvalidImportValueError as exc:
                report.invalid_rows += 1
                report.errors.append(f"Row {row_number}: {exc}")

        return cleaned_rows

    @staticmethod
    def _parse_date(value: str) -> datetime:
        try:
            return datetime.fromisoformat(value.strip())
        except ValueError as exc:
            raise InvalidImportValueError(f"Invalid date value: {value!r}") from exc

    @staticmethod
    def _parse_quantity(value: str) -> int:
        try:
            quantity = int(value.strip())
        except ValueError as exc:
            raise InvalidImportValueError(f"Invalid quantity value: {value!r}") from exc

        if quantity <= 0:
            raise InvalidImportValueError(
                f"Quantity must be greater than zero: {value!r}"
            )

        return quantity

    @staticmethod
    def _parse_unit_price(value: str) -> float:
        try:
            unit_price = float(value.strip())
        except ValueError as exc:
            raise InvalidImportValueError(
                f"Invalid unit price value: {value!r}"
            ) from exc

        if unit_price < 0:
            raise InvalidImportValueError(f"Unit price cannot be negative: {value!r}")

        return unit_price

    @staticmethod
    def _clean_product(value: str) -> str:
        product = value.strip()

        if not product:
            raise InvalidImportValueError("Product is required.")

        return product

    @staticmethod
    def _clean_seller(value: str) -> str:
        return value.strip()

    @staticmethod
    def _clean_category(value: str) -> str:
        if not value:
            return ""
        return value.strip().title()
