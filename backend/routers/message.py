from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends
from services.auth import security
from authx import TokenPayload
from repositories.message import MessageRepository
from schemas.message import SMessage, SMessageAdd

router = APIRouter(prefix="/api", tags=["Api"])

@router.get("/history")
async def get_history(
        token_payload: TokenPayload = Depends(security.access_token_required)
) -> list[SMessage]:
    user_id = str(token_payload.sub)
    history = await MessageRepository.get_history(user_id)
    return history

@router.post("/chat")
async def add_message(
        message: SMessageAdd,
        token_payload: TokenPayload = Depends(security.access_token_required)
) -> StreamingResponse:
    user_id = str(token_payload.sub)
    answer_generator = MessageRepository.add_message(message.message, user_id)
    return StreamingResponse(answer_generator, media_type="text/plain")

@router.delete("/clear")
async def delete_chat(
        token_payload: TokenPayload = Depends(security.access_token_required)
) -> dict:
    user_id = str(token_payload.sub)
    response = await MessageRepository.delete_chat(user_id)
    return response