from fastapi import APIRouter, Depends
from app.api.routes.auth import router as auth_router
from fastapi.security import HTTPBearer

http_bearer = HTTPBearer(auto_error=False)

__all__ = ("api_router",)


api_router = APIRouter(
    dependencies=[Depends(http_bearer)],
)
api_router.include_router(auth_router)
