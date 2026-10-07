from fastapi import APIRouter
from app.api.router import router

api_router = APIRouter(prefix="/api")
api_router.include_router(router)
