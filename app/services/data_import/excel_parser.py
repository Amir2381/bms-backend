from openpyxl import load_workbook

from app.services.data_import.types import ParsedImportData, RawImportRow


class ExcelFileParser:
    def parse(self, file_path: str) -> ParsedImportData:
        workbook = load_workbook(
            filename=file_path,
            read_only=True,
            data_only=True,
        )

        try:
            worksheet = workbook.active
            rows = worksheet.iter_rows(values_only=True)

            headers = next(rows, None)

            if not headers:
                return ParsedImportData(
                    headers=[],
                    rows=[],
                )

            normalized_headers = [
                str(header).strip() if header is not None else "" for header in headers
            ]

            result: list[RawImportRow] = []

            for row in rows:
                result.append(
                    {
                        header: str(value) if value is not None else ""
                        for header, value in zip(normalized_headers, row)
                        if header
                    }
                )

            return ParsedImportData(
                headers=normalized_headers,
                rows=result,
            )

        finally:
            workbook.close()
