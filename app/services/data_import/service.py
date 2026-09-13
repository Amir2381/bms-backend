from app.services.data_import.cleaner import DataCleaner
from app.services.data_import.mapper import ColumnMapper
from app.services.data_import.parser import FileParser
from app.services.data_import.report import CleaningReport, ImportResult
from app.services.data_import.validator import ImportValidator


class ImportService:
    def __init__(
        self,
        parser: FileParser,
        validator: ImportValidator,
        mapper: ColumnMapper,
        cleaner: DataCleaner,
    ):
        self.parser = parser
        self.validator = validator
        self.mapper = mapper
        self.cleaner = cleaner

    def process(self, file_path: str) -> ImportResult:
        parsed_data = self.parser.parse(file_path)

        self.validator.validate(parsed_data.headers)

        mapped_rows = self.mapper.map(parsed_data.rows)

        report = CleaningReport()

        cleaned_rows = self.cleaner.clean(
            mapped_rows,
            report,
        )

        return ImportResult(
            rows=cleaned_rows,
            report=report,
        )
