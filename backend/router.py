from fastapi.responses import StreamingResponse
from fastapi import APIRouter
from repository import MessageRepository
from schema import SMessageAdd

router = APIRouter(prefix="/api", tags=["Api"])

@router.get("/history")
async def get_history() -> list[dict]:
    history = await MessageRepository.get_history()
    return history

@router.post("/chat")
async def add_message(message: SMessageAdd) -> StreamingResponse:
    answer_generator = MessageRepository.add_message(message.message)
    return StreamingResponse(answer_generator, media_type="text/plain")

@router.delete("/clear")
async def delete_chat() -> dict[str, str]:
    await MessageRepository.delete_chat()
    return {"status": "ok"}