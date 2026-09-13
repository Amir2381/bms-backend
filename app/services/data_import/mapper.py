from typing import Protocol

from app.services.data_import.types import CleanImportRow


class ColumnMapper(Protocol):
    def map(self, rows: list[CleanImportRow]) -> list[dict]: ...
