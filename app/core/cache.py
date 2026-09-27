from fastapi import Request, Response
from fastapi_cache import FastAPICache


def branch_key_builder(
    func,
    namespace: str = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    prefix = FastAPICache.get_prefix()

    current_user = kwargs.get("current_user")
    branch_id = current_user.branch_id if current_user else "all"

    query = request.url.query if request else ""

    return f"{prefix}:{namespace}:{func.__name__}:branch:{branch_id}:{query}"
