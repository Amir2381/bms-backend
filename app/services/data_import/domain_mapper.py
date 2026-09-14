from typing import Protocol

from app.services.data_import.types import CleanImportRow, ImportedSaleInput


class DomainMapper(Protocol):
    def map(self, rows: list[CleanImportRow]) -> list[ImportedSaleInput]: ...


class BasicDomainMapper:
    def map(
        self,
        rows: list[CleanImportRow],
    ) -> list[ImportedSaleInput]:
        return [
            ImportedSaleInput(
                sale_date=row["date"],
                product=row["product"],
                quantity=row["quantity"],
                unit_price=row["unit_price"],
                seller=row.get("seller", ""),
            )
            for row in rows
        ]
