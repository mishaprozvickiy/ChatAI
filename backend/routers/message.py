from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends
from services.auth import security
from authx import TokenPayload
from repositories.message import MessageRepository
from schemas.message import SMessage, SMessageAdd
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api", tags=["Api"])

@router.get("/history")
async def get_history(
        token_payload: TokenPayload = Depends(security.access_token_required),
        session: AsyncSession = Depends(get_session)
) -> list[SMessage]:

    user_id = int(token_payload.sub)
    history = await MessageRepository.get_history(user_id, session)
    return history

@router.post("/chat")
async def add_message(
        message: SMessageAdd,
        token_payload: TokenPayload = Depends(security.access_token_required),
        session: AsyncSession = Depends(get_session)
) -> StreamingResponse:

    user_id = int(token_payload.sub)
    answer_generator = MessageRepository.add_message(message.content, user_id, session)
    return StreamingResponse(answer_generator, media_type="text/plain")

@router.delete("/clear")
async def delete_chat(
        token_payload: TokenPayload = Depends(security.access_token_required),
        session: AsyncSession = Depends(get_session)
) -> dict:

    user_id = int(token_payload.sub)
    response = await MessageRepository.delete_chat(user_id, session)
    return response