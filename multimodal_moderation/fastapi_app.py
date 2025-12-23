from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from multimodal_moderation.env import get_default_model_choice, USER_API_KEY
from multimodal_moderation.configs import settings
from multimodal_moderation.api.v1 import api_router


# Standard auth scheme using -H "Authorization: Bearer <api_key>" header.
security = HTTPBearer()


# NOTE: this is a simple check against a static key. In a production setting, this should be more sophisticated.
def validate_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != USER_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid user API key")
    return credentials.credentials


# Using `dependencies` to apply the API key validation to all endpoints.
app = FastAPI(dependencies=[Depends(validate_api_key)])
app.include_router(api_router, prefix=settings.API_V1_STR)


# Default model settings
default_model_choice = get_default_model_choice()


def main():
    import uvicorn

    uvicorn.run("multimodal_moderation.fastapi_app:app", host="0.0.0.0", port=8000, reload=True, log_level="trace")


if __name__ == "__main__":
    main()
