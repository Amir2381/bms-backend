import os
from tempfile import NamedTemporaryFile
from typing import Any, Iterable

from fastapi import BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse

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
    background_tasks: BackgroundTasks,
) -> FileResponse:
    strategy = MultiSheetExcelReportStrategy()
    filename = f"{filename_prefix}.xlsx"
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    temp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
    for chunk in strategy.generate_multi_sheet(sheets_data):
        temp_file.write(chunk)
    temp_file.close()

    background_tasks.add_task(cleanup_temp_file, temp_file.name)

    return FileResponse(
        path=temp_file.name,
        media_type=media_type,
        filename=filename,
    )
