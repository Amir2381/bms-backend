from pathlib import Path

from app.services.data_import.csv_parser import CsvFileParser
from app.services.data_import.excel_parser import ExcelFileParser
from app.services.data_import.parser import FileParser


def get_parser(file_path: str) -> FileParser:
    extension = Path(file_path).suffix.lower()

    if extension == ".csv":
        return CsvFileParser()

    if extension == ".xlsx":
        return ExcelFileParser()

    raise ValueError(f"Unsupported file extension: {extension}")
