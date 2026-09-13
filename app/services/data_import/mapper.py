from typing import Protocol

from app.services.data_import.types import RawImportRow
from app.services.data_import.validator import COLUMN_ALIASES


class ColumnMapper(Protocol):
    def map(self, rows: list[RawImportRow]) -> list[RawImportRow]: ...


class BasicColumnMapper:
    def map(self, rows: list[RawImportRow]) -> list[RawImportRow]:
        mapped_rows = []

        for row in rows:
            mapped_row: RawImportRow = {}

            normalized_row = {key.strip().lower(): value for key, value in row.items()}

            for standard_name, aliases in COLUMN_ALIASES.items():
                for alias in aliases:
                    if alias in normalized_row:
                        mapped_row[standard_name] = normalized_row[alias]
                        break

            mapped_rows.append(mapped_row)

        return mapped_rows
