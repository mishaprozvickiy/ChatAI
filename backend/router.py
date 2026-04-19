from fastapi.responses import StreamingResponse
from fastapi import APIRouter
from repository import MessageRepository
from schema import SMessage, SMessageAdd, SStatusOk

router = APIRouter(prefix="/api", tags=["Api"])

@router.get("/history")
async def get_history() -> list[SMessage]:
    history = await MessageRepository.get_history()
    return history

@router.post("/chat")
async def add_message(message: SMessageAdd) -> StreamingResponse:
    answer_generator = MessageRepository.add_message(message.message)
    return StreamingResponse(answer_generator, media_type="text/plain")

@router.delete("/clear")
async def delete_chat() -> SStatusOk:
    await MessageRepository.delete_chat()
    return SStatusOk()