from fastapi import APIRouter
from routers.message import router as message_router

router = APIRouter()

router.include_router(message_router)