from fastapi import APIRouter
from app.api.routes.auth import router as auth_router

__all__ = ("api_router",)


api_router = APIRouter()
api_router.include_router(auth_router)
