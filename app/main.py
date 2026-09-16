import logging
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.logging import setup_logging
from app.core.security import get_current_user
from app.models.user import User
from app.routers import auth, data_import, products, sales, users
from app.services.data_import.exceptions import (
    ImportError,
    ImportedProductNotFoundError,
    ImportedSellerNotFoundError,
)

setup_logging()

logger = logging.getLogger("bms")

app = FastAPI()

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(users.router)
app.include_router(data_import.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
def http_error_handler(
    request: Request,
    exc: HTTPException,
):
    logger.warning(
        "HTTP error",
        extra={
            "request_id": request.state.request_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc.detail),
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    logger.warning(
        "Validation error",
        extra={
            "request_id": request.state.request_id,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Invalid input",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(ImportedProductNotFoundError)
def imported_product_not_found_handler(
    request: Request,
    exc: ImportedProductNotFoundError,
):
    logger.warning(
        "Import product not found",
        extra={
            "request_id": request.state.request_id,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
        },
    )

    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": str(exc),
        },
    )


@app.exception_handler(ImportedSellerNotFoundError)
def imported_seller_not_found_handler(
    request: Request,
    exc: ImportedSellerNotFoundError,
):
    logger.warning(
        "Import seller not found",
        extra={
            "request_id": request.state.request_id,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
        },
    )

    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": str(exc),
        },
    )


@app.exception_handler(ImportError)
def import_error_handler(
    request: Request,
    exc: ImportError,
):
    logger.warning(
        "Import error",
        extra={
            "request_id": request.state.request_id,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
        },
    )

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": str(exc),
        },
    )


@app.exception_handler(Exception)
def general_error_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception",
        extra={
            "request_id": request.state.request_id,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
        },
    )


@app.middleware("http")
async def log_request_middleware(
    request: Request,
    call_next,
):
    request.state.request_id = str(uuid.uuid4())

    logger.info(
        "Request started",
        extra={
            "request_id": request.state.request_id,
            "method": request.method,
            "path": request.url.path,
        },
    )

    response = await call_next(request)

    logger.info(
        "Request completed",
        extra={
            "request_id": request.state.request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )

    return response


@app.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
