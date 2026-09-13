import csv

from app.services.data_import.types import ParsedImportData, RawImportRow


class CsvFileParser:
    def parse(self, file_path: str) -> ParsedImportData:
        with open(
            file_path,
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            headers = reader.fieldnames or []

            rows: list[RawImportRow] = [
                {key: value or "" for key, value in row.items() if key is not None}
                for row in reader
            ]

            return ParsedImportData(
                headers=headers,
                rows=rows,
            )
