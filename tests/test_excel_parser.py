from openpyxl import Workbook

from app.services.data_import.excel_parser import ExcelFileParser


def test_parse_excel_file(tmp_path):
    excel_file = tmp_path / "sales.xlsx"

    workbook = Workbook()
    worksheet = workbook.active

    worksheet.append(["date", "product", "quantity", "unit_price", "seller"])
    worksheet.append(["2026-09-10", "Laptop", 2, 1200, "Amir"])
    worksheet.append(["2026-09-11", "Mouse", 5, 25, "Reza"])

    workbook.save(excel_file)
    workbook.close()

    parser = ExcelFileParser()

    result = parser.parse(str(excel_file))

    assert result.headers == [
        "date",
        "product",
        "quantity",
        "unit_price",
        "seller",
    ]

    assert result.rows == [
        {
            "date": "2026-09-10",
            "product": "Laptop",
            "quantity": "2",
            "unit_price": "1200",
            "seller": "Amir",
        },
        {
            "date": "2026-09-11",
            "product": "Mouse",
            "quantity": "5",
            "unit_price": "25",
            "seller": "Reza",
        },
    ]
