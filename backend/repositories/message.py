from sqlalchemy import select, delete, exists
from datetime import datetime
from models.message import MessageOrm
from database import new_session
from schemas.message import SMessage
from bot import chatbot
from config import FIRST_BOT_MESSAGE
from typing import AsyncGenerator


class MessageRepository:
    @classmethod
    async def get_history(cls, user_id: int) -> list[SMessage]:
        async with new_session() as session:
            query = select(MessageOrm).where(MessageOrm.user_id == user_id)
            messages = await session.execute(query)
            message_models = messages.scalars().all()
            message_schemas = [SMessage.model_validate(message).model_dump() for message in message_models]
            return message_schemas

    @classmethod
    async def add_message(cls, message: str, user_id: int) -> AsyncGenerator[str, None]:
        async with new_session() as session:
            date = datetime.now()
            message_model = MessageOrm(user_id=user_id, role="user", message=message, date=date)
            session.add(message_model)
            await session.commit()

        answer = ""

        for part_answer in chatbot.ask(message):
            yield part_answer
            answer += part_answer

        date = datetime.now()
        yield f"\n[DATE:{date}]"

        async with new_session() as session:
            date = datetime.now()
            message_model = MessageOrm(user_id=user_id, role="assistant", message=answer, date=date)
            session.add(message_model)
            await session.commit()

    @classmethod
    async def delete_chat(cls, user_id: int) -> dict:
        async with new_session() as session:
            query = delete(MessageOrm).where(MessageOrm.user_id == user_id)
            await session.execute(query)
            await session.commit()
            await cls.add_first_message()
            return {"status": "ok"}

    @classmethod
    async def add_first_message(cls) -> None:
        async with new_session() as session:
            query = select(exists().where(MessageOrm.id.is_not(None)))
            result = await session.execute(query)
            has_records = result.scalar()
            date = datetime.now()
            message_model = MessageOrm(role="assistant", message=FIRST_BOT_MESSAGE, date=date)

            if not has_records:
                session.add(message_model)
                await session.commit()