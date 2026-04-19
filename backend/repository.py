from sqlalchemy import select, delete, exists
from datetime import datetime
from database import MessageOrm, new_session
from schema import SMessage
from bot import chatbot
from config import FIRST_BOT_MESSAGE
from typing import AsyncGenerator


class MessageRepository:
    @classmethod
    async def get_history(cls) -> list[SMessage]:
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

        date = datetime.now()
        yield f"\n[DATE:{date}]"

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
            await cls.add_first_message()

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