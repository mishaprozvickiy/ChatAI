from fastapi import APIRouter, Response, Depends
from authx import TokenPayload
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.auth import AuthRepository
from schemas.user import SUserAdd
from database import get_session
from services.auth import AuthService, security

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(
        credentials: SUserAdd,
        response: Response,
        session: AsyncSession = Depends(get_session)
) -> dict:
    response = await AuthRepository.register(credentials, response, session)
    return response

@router.post("/login")
async def login(
        credentials: SUserAdd,
        response: Response,
        session: AsyncSession = Depends(get_session)
) -> dict:
    response = await AuthRepository.login(credentials, response, session)
    return response

@router.post("/logout")
async def logout(response: Response) -> dict:
    security.unset_access_cookies(response)
    security.unset_refresh_cookies(response)
    return {"status": "ok"}

@router.post("/refresh")
async def refresh(
        response: Response,
        token_payload: TokenPayload = Depends(security.refresh_token_required)
) -> dict:
    user_id = token_payload.sub
    new_access_token = AuthService.refresh_access_token(user_id)
    security.set_access_cookies(new_access_token, response)
    return {"status": "ok"}

@router.get("/me")
async def check_auth(
        token_payload: TokenPayload = Depends(security.access_token_required),
        session: AsyncSession = Depends(get_session)
) -> dict:
    user_id = int(token_payload.sub)
    response = await AuthRepository.check(user_id, session)
    return response