from pathlib import Path

from app.core.config import settings
from app.services.data_import.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


def validate_file(filename: str | None) -> None:
    if not filename:
        raise UnsupportedFileTypeError("File name is required.")

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            "Only CSV and XLSX files are supported.",
        )


def validate_file_size(file_size: int) -> None:
    if file_size == 0:
        raise EmptyFileError("The uploaded file is empty.")

    if file_size > settings.import_max_file_size:
        raise FileTooLargeError(
            "The uploaded file exceeds the maximum allowed size.",
        )
