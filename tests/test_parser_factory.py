from app.services.data_import.csv_parser import CsvFileParser
from app.services.data_import.excel_parser import ExcelFileParser
from app.services.data_import.parser_factory import get_parser


def test_get_csv_parser():
    parser = get_parser("sales.csv")

    assert isinstance(parser, CsvFileParser)


def test_get_excel_parser():
    parser = get_parser("sales.xlsx")

    assert isinstance(parser, ExcelFileParser)


def test_get_parser_is_case_insensitive():
    parser = get_parser("sales.XLSX")

    assert isinstance(parser, ExcelFileParser)


def test_get_parser_rejects_unsupported_extension():
    try:
        get_parser("sales.txt")
    except ValueError as exc:
        assert "Unsupported file extension" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
