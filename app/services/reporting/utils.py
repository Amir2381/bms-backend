from typing import Any, Iterable

from fastapi.responses import StreamingResponse

from app.services.reporting.csv_strategy import CsvReportStrategy
from app.services.reporting.excel_strategy import (
    ExcelReportStrategy,
    MultiSheetExcelReportStrategy,
)
from app.services.reporting.generator import ReportGenerator


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
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def stream_multi_sheet_excel_response(
    sheets_data: dict[str, dict[str, Any]],
    filename_prefix: str,
) -> StreamingResponse:
    strategy = MultiSheetExcelReportStrategy()
    filename = f"{filename_prefix}.xlsx"
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return StreamingResponse(
        strategy.generate_multi_sheet(sheets_data),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
