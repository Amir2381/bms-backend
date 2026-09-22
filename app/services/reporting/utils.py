from typing import Any, Iterable

from fastapi.responses import StreamingResponse

from app.services.reporting.csv_strategy import CsvReportStrategy
from app.services.reporting.generator import ReportGenerator


def stream_csv_response(
    headers: list[str],
    data: Iterable[dict[str, Any]],
    filename: str,
) -> StreamingResponse:
    generator = ReportGenerator(CsvReportStrategy())

    return StreamingResponse(
        generator.generate(headers, data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
