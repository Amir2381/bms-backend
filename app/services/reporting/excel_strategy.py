import io
from typing import Any, Iterable, Iterator

from openpyxl import Workbook


class ExcelReportStrategy:
    def generate(
        self,
        headers: list[str],
        data: Iterable[dict[str, Any]],
    ) -> Iterator[bytes]:
        workbook = Workbook()
        worksheet = workbook.active

        if worksheet is not None:
            worksheet.append(headers)

            for row in data:
                worksheet.append([row.get(header, "") for header in headers])

        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)

        yield output.getvalue()
