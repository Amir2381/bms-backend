from typing import Protocol

from app.services.data_import.types import CleanImportRow, RawImportRow


class DataCleaner(Protocol):
    def clean(self, rows: list[RawImportRow]) -> list[CleanImportRow]: ...
