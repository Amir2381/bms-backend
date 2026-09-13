from typing import Protocol

from app.services.data_import.types import RawImportRow


class FileParser(Protocol):
    def parse(self, file_path: str) -> list[RawImportRow]: ...
