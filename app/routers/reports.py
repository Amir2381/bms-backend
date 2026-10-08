from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.security import get_current_user
from app.worker.celery_app import celery_app

router = APIRouter(
    prefix="/reports", tags=["Reports"], dependencies=[Depends(get_current_user)]
)


@router.get("/status/{job_id}")
def get_report_status(job_id: str):
    result = celery_app.AsyncResult(job_id)
    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "SUCCESS":
        return {"status": "completed", "download_url": f"/reports/download/{job_id}"}
    elif result.state == "FAILURE":
        return {"status": "failed", "error": str(result.info)}
    return {"status": result.state}


@router.get("/download/{job_id}")
def download_report(job_id: str):
    result = celery_app.AsyncResult(job_id)
    if result.state != "SUCCESS":
        raise HTTPException(
            status_code=400, detail="Report is not ready yet or failed."
        )

    file_path = result.result.get("file_path")
    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found.")

    filename = Path(file_path).name
    return FileResponse(
        path=file_path, filename=filename, content_disposition_type="attachment"
    )
