from sqlalchemy import select, delete
from datetime import datetime
from database import MessageOrm, new_session
from schema import SMessage
from bot import chatbot
from typing import AsyncGenerator


class MessageRepository:
    @classmethod
    async def get_history(cls) -> list[dict]:
        async with new_session() as session:
            query = select(MessageOrm)
            messages = await session.execute(query)
            message_models = messages.scalars().all()
            message_schemas = [SMessage.model_validate(message).model_dump() for message in message_models]
            return message_schemas

    @classmethod
    async def add_message(cls, message: str) -> AsyncGenerator[str, None]:
        async with new_session() as session:
            date = datetime.now()
            message_model = MessageOrm(role="user", message=message, date=date)
            session.add(message_model)
            await session.commit()

        answer = ""

        for part_answer in chatbot.ask(message):
            yield part_answer
            answer += part_answer

        async with new_session() as session:
            date = datetime.now()
            message_model = MessageOrm(role="assistant", message=answer, date=date)
            session.add(message_model)
            await session.commit()

    @classmethod
    async def delete_chat(cls) -> None:
        async with new_session() as session:
            await session.execute(delete(MessageOrm))
            await session.commit()