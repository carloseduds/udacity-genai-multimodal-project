import time
import uuid
import logging

from fastapi import Request
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from multimodal_moderation.env import get_default_model_choice, USER_API_KEY
from multimodal_moderation.configs import settings
from multimodal_moderation.api.v1 import api_router
from multimodal_moderation.logging_config import set_request_id, setup_logging


# Standard auth scheme using -H "Authorization: Bearer <api_key>" header.
security = HTTPBearer()


# NOTE: this is a simple check against a static key. In a production setting, this should be more sophisticated.
def validate_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != USER_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid user API key")
    return credentials.credentials

setup_logging()

# Using `dependencies` to apply the API key validation to all endpoints.
app = FastAPI(dependencies=[Depends(validate_api_key)])
app.include_router(api_router, prefix=settings.API_V1_STR)

http_logger = logging.getLogger("multimodal_moderation.http")

@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    set_request_id(request_id)

    start = time.perf_counter()
    response = None

    try:
        response = await call_next(request)
        return response
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        status_code = getattr(response, "status_code", 500)

        http_logger.info(
            "http_request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "latency_ms": round(elapsed_ms, 2),
                "client_ip": request.client.host if request.client else None,
            },
        )

        if response is not None:
            response.headers["X-Request-ID"] = request_id

        # opcional: limpar contexto após resposta
        set_request_id(None)


# Default model settings
default_model_choice = get_default_model_choice()


def main():
    import uvicorn

    uvicorn.run("multimodal_moderation.fastapi_app:app", host="0.0.0.0", port=8000, reload=True, log_level="trace")


if __name__ == "__main__":
    main()
