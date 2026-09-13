from datetime import datetime

from app.services.data_import.cleaner import BasicDataCleaner
from app.services.data_import.csv_parser import CsvFileParser
from app.services.data_import.mapper import BasicColumnMapper
from app.services.data_import.service import ImportService
from app.services.data_import.validator import BasicImportValidator


def create_import_service() -> ImportService:
    return ImportService(
        parser=CsvFileParser(),
        validator=BasicImportValidator(),
        mapper=BasicColumnMapper(),
        cleaner=BasicDataCleaner(),
    )


def test_import_service_processes_csv_with_aliases(tmp_path):
    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "sale_date,product_name,qty,price,user\n"
        "2026-09-10,Laptop,2,1200,Amir\n"
        "2026-09-11,Mouse,5,25,Reza\n",
        encoding="utf-8",
    )

    service = create_import_service()

    result = service.process(str(csv_file))

    assert result.rows == [
        {
            "date": datetime(2026, 9, 10),
            "product": "Laptop",
            "quantity": 2,
            "unit_price": 1200.0,
            "seller": "Amir",
        },
        {
            "date": datetime(2026, 9, 11),
            "product": "Mouse",
            "quantity": 5,
            "unit_price": 25.0,
            "seller": "Reza",
        },
    ]

    assert result.report.total_rows == 2
    assert result.report.cleaned_rows == 2
    assert result.report.duplicate_rows == 0
    assert result.report.invalid_rows == 0
    assert result.report.errors == []


def test_import_service_reports_invalid_rows(tmp_path):
    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "date,product,quantity,unit_price,seller\n"
        "2026-09-10,Laptop,2,1200,Amir\n"
        "invalid,Mouse,5,25,Reza\n",
        encoding="utf-8",
    )

    service = create_import_service()

    result = service.process(str(csv_file))

    assert len(result.rows) == 1
    assert result.report.total_rows == 2
    assert result.report.cleaned_rows == 1
    assert result.report.invalid_rows == 1
    assert result.report.duplicate_rows == 0
    assert len(result.report.errors) == 1
