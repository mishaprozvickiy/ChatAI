from fastapi import APIRouter
from routers.message import router as message_router
from routers.auth import router as auth_router

router = APIRouter()

router.include_router(message_router)
router.include_router(auth_router)