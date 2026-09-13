from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.services.data_import.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from app.services.data_import.file_validator import validate_file

router = APIRouter(
    prefix="/import",
    tags=["Data Import"],
)

CHUNK_SIZE = 1024 * 1024


@router.post("/sales")
async def import_sales(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    temporary_file_path = None

    try:
        validate_file(file.filename)

        total_size = 0

        with NamedTemporaryFile(
            suffix=Path(file.filename).suffix,
            delete=False,
        ) as temporary_file:
            temporary_file_path = temporary_file.name

            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > settings.import_max_file_size:
                    raise FileTooLargeError(
                        "The uploaded file exceeds the maximum allowed size."
                    )

                temporary_file.write(chunk)

        if total_size == 0:
            raise EmptyFileError("The uploaded file is empty.")

        return {
            "message": "File accepted and ready for parsing.",
            "filename": file.filename,
            "size": total_size,
        }

    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except EmptyFileError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=413,
            detail=str(exc),
        ) from exc
