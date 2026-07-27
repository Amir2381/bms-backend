import uuid

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.security import (
    get_current_user,
)
from app.models.user import User
from app.routers import auth, products, sales, users

app = FastAPI()
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(users.router)

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
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Invalid input",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(Exception)
def general_error_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
        },
    )


@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())

    print(f"[{request.state.request_id}] Request: {request.method} {request.url}")

    response = await call_next(request)

    print(f"[{request.state.request_id}] Response status: {response.status_code}")

    return response


@app.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


x = 1
