import os
from tempfile import NamedTemporaryFile
from typing import Any, Iterable, Iterator

from fastapi.responses import StreamingResponse

from app.services.reporting.csv_strategy import CsvReportStrategy
from app.services.reporting.excel_strategy import (
    ExcelReportStrategy,
    MultiSheetExcelReportStrategy,
)
from app.services.reporting.generator import ReportGenerator


def cleanup_temp_file(path: str) -> None:
    try:
        os.unlink(path)
    except Exception:
        pass


def iter_file_and_cleanup(path: str) -> Iterator[bytes]:
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                yield chunk
    finally:
        cleanup_temp_file(path)


def stream_report_response(
    headers: list[str],
    data: Iterable[dict[str, Any]],
    filename_prefix: str,
    export_format: str = "csv",
) -> StreamingResponse:
    if export_format.lower() == "excel":
        generator = ReportGenerator(ExcelReportStrategy())
        filename = f"{filename_prefix}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        generator = ReportGenerator(CsvReportStrategy())
        filename = f"{filename_prefix}.csv"
        media_type = "text/csv"
    return StreamingResponse(
        generator.generate(headers, data),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def stream_multi_sheet_excel_response(
    sheets_data: dict[str, dict[str, Any]],
    filename_prefix: str,
) -> StreamingResponse:
    strategy = MultiSheetExcelReportStrategy()
    filename = f"{filename_prefix}.xlsx"
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    temp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
    for chunk in strategy.generate_multi_sheet(sheets_data):
        temp_file.write(chunk)
    temp_file.close()

    return StreamingResponse(
        iter_file_and_cleanup(temp_file.name),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
