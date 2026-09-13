from app.services.data_import.csv_parser import CsvFileParser


def test_parse_csv_file(tmp_path):
    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        "date,product,quantity,unit_price,seller\n"
        "2026-09-10,Laptop,2,1200,Amir\n"
        "2026-09-11,Mouse,5,25,Reza\n",
        encoding="utf-8",
    )

    parser = CsvFileParser()

    result = parser.parse(str(csv_file))

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
