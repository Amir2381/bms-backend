import csv

from app.services.data_import.types import RawImportRow


class CsvFileParser:
    def parse(self, file_path: str) -> list[RawImportRow]:
        with open(
            file_path,
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            return [
                {key: value or "" for key, value in row.items() if key is not None}
                for row in reader
            ]
