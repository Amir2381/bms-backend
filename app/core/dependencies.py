from fastapi import Request


def log_request(request: Request):
    print(f"{request.method} {request.url.path}")
