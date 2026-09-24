from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_admin_user
from app.db.database import get_db
from app.models.user import User
from app.services.data_import.cleaner import BasicDataCleaner
from app.services.data_import.domain_mapper import BasicDomainMapper
from app.services.data_import.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from app.services.data_import.file_validator import validate_file
from app.services.data_import.import_sale_service import ImportSaleService
from app.services.data_import.mapper import BasicColumnMapper
from app.services.data_import.parser_factory import get_parser
from app.services.data_import.service import ImportService
from app.services.data_import.validator import BasicImportValidator

router = APIRouter(
    prefix="/import",
    tags=["Data Import"],
)

CHUNK_SIZE = 1024 * 1024


def create_import_service(file_path: str) -> ImportService:
    return ImportService(
        parser=get_parser(file_path),
        validator=BasicImportValidator(),
        mapper=BasicColumnMapper(),
        cleaner=BasicDataCleaner(),
        domain_mapper=BasicDomainMapper(),
        sale_service=ImportSaleService(),
    )


@router.post("/sales")
async def import_sales(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
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

        import_service = create_import_service(temporary_file_path)

        result = import_service.process(
            file_path=temporary_file_path,
            db=db,
            current_user=current_user,
        )

        return {
            "message": "Sales imported successfully.",
            "filename": file.filename,
            "size": total_size,
            "imported_rows": len(result.rows),
            "cleaning_report": {
                "total_rows": result.report.total_rows,
                "cleaned_rows": result.report.cleaned_rows,
                "duplicate_rows": result.report.duplicate_rows,
                "invalid_rows": result.report.invalid_rows,
                "errors": result.report.errors,
            },
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

    finally:
        if temporary_file_path:
            Path(temporary_file_path).unlink(missing_ok=True)
