from app.services.data_import.cleaner import DataCleaner
from app.services.data_import.mapper import ColumnMapper
from app.services.data_import.parser import FileParser
from app.services.data_import.types import CleanImportRow


class ImportService:
    def __init__(
        self,
        parser: FileParser,
        cleaner: DataCleaner,
        mapper: ColumnMapper,
    ):
        self.parser = parser
        self.cleaner = cleaner
        self.mapper = mapper

    def process(self, file_path: str) -> list[dict]:
        rows = self.parser.parse(file_path)
        cleaned_rows: list[CleanImportRow] = self.cleaner.clean(rows)

        return self.mapper.map(cleaned_rows)
