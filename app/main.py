import logging
import uuid
import sys
import time

from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.core.config import settings
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.logging import setup_logging
from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.models.user import User
from app.routers import (
    analytics,
    api_keys,
    auth,
    audit_logs,
    branches,
    categories,
    customers,
    data_import,
    products,
    reports,
    sales,
    system_alerts,
    users,
    webhooks,
    health,
)
from app.services.data_import.exceptions import (
    ImportError,
    ImportedProductNotFoundError,
    ImportedSellerNotFoundError,
)

setup_logging()

logger = logging.getLogger("bms")

tags_metadata = [
    {
        "name": "Auth",
        "description": "Operations with user authentication. Includes login, logout, and token refresh.",
    },
    {
        "name": "Users",
        "description": "User management operations. Restricted to Administrators.",
    },
    {
        "name": "Products",
        "description": "Manage products, inventory, and pricing.",
    },
    {
        "name": "Sales",
        "description": "Record and manage sales transactions securely.",
    },
    {
        "name": "analytics",
        "description": "Core BI features, dashboards, and AI-powered data insights.",
    },
    {
        "name": "Data Import",
        "description": "Batch processing and data importing from Excel/CSV files.",
    },
    {
        "name": "System Alerts",
        "description": "Critical inventory and system status notifications.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    if "pytest" in sys.modules:
        FastAPICache.init(InMemoryBackend(), prefix="bms-cache")
    else:
        redis = aioredis.from_url(settings.redis_url)
        FastAPICache.init(RedisBackend(redis), prefix="bms-cache")
    yield


app = FastAPI(
    title="BMS (Business Management System) API",
    description="A powerful, highly scalable Business Intelligence & Sales Management API.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Backend Team",
        "email": "dev@bms.local",
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Request completed",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
        },
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception",
        exc_info=exc,
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(ImportedProductNotFoundError)
async def imported_product_not_found_handler(
    request: Request, exc: ImportedProductNotFoundError
):
    return JSONResponse(status_code=404, content={"success": False, "error": str(exc)})


@app.exception_handler(ImportedSellerNotFoundError)
async def imported_seller_not_found_handler(
    request: Request, exc: ImportedSellerNotFoundError
):
    return JSONResponse(status_code=404, content={"success": False, "error": str(exc)})


@app.exception_handler(ImportError)
async def import_error_handler(request: Request, exc: ImportError):
    return JSONResponse(status_code=400, content={"success": False, "error": str(exc)})


app.include_router(auth.router)
app.include_router(api_keys.router)
app.include_router(audit_logs.router)
app.include_router(branches.router)
app.include_router(categories.router)
app.include_router(customers.router)
app.include_router(data_import.router)
app.include_router(products.router)
app.include_router(reports.router)
app.include_router(sales.router)
app.include_router(system_alerts.router)
app.include_router(users.router)
app.include_router(webhooks.router)
app.include_router(health.router)
app.include_router(analytics.router)
