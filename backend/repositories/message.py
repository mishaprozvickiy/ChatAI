from sqlalchemy import select, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from models.message import MessageOrm
from schemas.message import SMessage
from bot import chatbot
from config import FIRST_BOT_MESSAGE
from typing import AsyncGenerator, Any


class MessageRepository:
    @classmethod
    async def get_history(
            cls,
            user_id: int,
            session: AsyncSession
    ) -> list[SMessage]:

        query = select(MessageOrm).where(MessageOrm.user_id == user_id)
        messages = await session.execute(query)

        message_models = messages.scalars().all()
        message_schemas = [SMessage.model_validate(message).model_dump() for message in message_models]

        return message_schemas

    @classmethod
    async def get_messages(
            cls,
            user_id: int,
            session: AsyncSession
    ) -> list[dict[str, Any]]:

        query = select(MessageOrm.role, MessageOrm.content).where(MessageOrm.user_id == user_id)
        result = await session.execute(query)

        messages = [
            {
                "role": row.role.value,
                "content": row.content
            }
            for row in result.mappings().all()
        ]

        return messages

    @classmethod
    async def add_message(
            cls,
            message: str,
            user_id: int,
            session: AsyncSession
    ) -> AsyncGenerator[str, None]:

        date = datetime.now()
        message_model = MessageOrm(user_id=user_id, role="user", content=message, date=date)

        session.add(message_model)
        await session.commit()

        messages = await cls.get_messages(user_id, session)
        answer = ""

        async for part_answer in chatbot.ask(messages):
            yield part_answer
            answer += part_answer

        date = datetime.now()
        yield f"\n[DATE:{date}]"

        date = datetime.now()
        message_model = MessageOrm(user_id=user_id, role="assistant", content=answer, date=date)

        session.add(message_model)
        await session.commit()

    @classmethod
    async def delete_chat(
            cls,
            user_id: int,
            session: AsyncSession
    ) -> dict:

        query = delete(MessageOrm).where(MessageOrm.user_id == user_id)
        await session.execute(query)
        await session.commit()
        await cls.add_first_message(session)

        return {"status": "ok"}

    @classmethod
    async def add_first_message(
            cls,
            session: AsyncSession
    ) -> None:

        query = select(exists().where(MessageOrm.id.is_not(None)))
        result = await session.execute(query)

        have_records = result.scalar()

        if have_records:
            return

        date = datetime.now()
        message_model = MessageOrm(role="assistant", message=FIRST_BOT_MESSAGE, date=date)

        session.add(message_model)
        await session.commit()