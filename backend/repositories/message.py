from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from models.message import MessageOrm
from schemas.message import SMessage, RoleEnum
from bot import chatbot
from config import UPDATE_EXCEPTION
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

        user_date = datetime.now(timezone.utc)

        new_message = [
            {
                "role": RoleEnum.user,
                "content": message
            }
        ]

        messages = await cls.get_messages(user_id, session) + new_message
        answer = ""

        async for part_answer in chatbot.ask(messages):
            yield part_answer
            answer += part_answer

        assistant_date = datetime.now(timezone.utc)
        yield f"\n[DATE:{assistant_date.isoformat()}]"

        user_message_model = MessageOrm(
            user_id=user_id,
            role=RoleEnum.user,
            content=message,
            date=user_date
        )

        assistant_message_model = MessageOrm(
            user_id=user_id,
            role=RoleEnum.assistant,
            content=answer,
            date=assistant_date
        )

        session.add(user_message_model)
        session.add(assistant_message_model)

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

        return {"status": "ok"}

    @classmethod
    async def update_message(
            cls,
            message: str,
            user_id: int,
            session: AsyncSession
    ) -> AsyncGenerator[str, None]:

        query = (
            select(MessageOrm.id)
            .where(MessageOrm.user_id == user_id, MessageOrm.role == RoleEnum.user)
            .order_by(MessageOrm.id.desc())
            .limit(1)
        )

        response = await session.execute(query)
        message_id = response.scalar_one_or_none()

        if not message_id:
            raise UPDATE_EXCEPTION

        new_date = datetime.now(timezone.utc)
        query = update(MessageOrm).where(MessageOrm.id == message_id).values(content=message, date=new_date)
        await session.execute(query)

        query = (
            select(MessageOrm)
            .where(
                MessageOrm.id > message_id,
                MessageOrm.user_id == user_id,
                MessageOrm.role == RoleEnum.assistant
            )
            .order_by(MessageOrm.id.asc())
            .limit(1)
        )

        response = await session.execute(query)
        assistant_message = response.scalar_one_or_none()

        if assistant_message:
            await session.delete(assistant_message)

        await session.commit()

        messages = await cls.get_messages(user_id, session)
        answer = ""

        async for part_answer in chatbot.ask(messages):
            yield part_answer
            answer += part_answer

        assistant_date = datetime.now(timezone.utc)
        yield f"\n[DATE:{assistant_date.isoformat()}]"

        assistant_message_model = MessageOrm(
            user_id=user_id,
            role=RoleEnum.assistant,
            content=answer,
            date=assistant_date
        )

        session.add(assistant_message_model)
        await session.commit()