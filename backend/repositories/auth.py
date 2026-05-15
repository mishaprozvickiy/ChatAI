from fastapi import Response
from schemas.user import SUser, SUserAdd
from models.user import UserOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import CREDS_EXCEPTION, USERNAME_EXISTS_EXCEPTION
from services.auth import security
import bcrypt


class AuthRepository:
    @classmethod
    async def register(
            cls,
            credentials: SUserAdd,
            response: Response,
            session: AsyncSession
    ) -> dict:
        query = select(UserOrm).where(UserOrm.username == credentials.username)
        result = await session.execute(query)
        user_model = result.scalar_one_or_none()

        if user_model is not None:
            raise USERNAME_EXISTS_EXCEPTION

        password = credentials.password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        credentials.password = hashed_password.decode()

        creds_json = credentials.model_dump()
        user_model = UserOrm(**creds_json)

        session.add(user_model)
        await session.commit()

        credentials.password = password
        await cls.login(credentials, response, session)

        return {"status": "ok"}

    @classmethod
    async def login(
            cls,
            credentials: SUserAdd,
            response: Response,
            session: AsyncSession
    ) -> dict:
        query = select(UserOrm).where(UserOrm.username == credentials.username)
        result = await session.execute(query)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            raise CREDS_EXCEPTION

        user = SUser.model_validate(user_model)

        if not bcrypt.checkpw(credentials.password.encode(), user.password.encode()):
            raise CREDS_EXCEPTION

        user_id = str(user.id)

        access_token = security.create_access_token(uid=user_id)
        refresh_token = security.create_refresh_token(uid=user_id)

        security.set_access_cookies(access_token, response)
        security.set_refresh_cookies(refresh_token, response)

        return {"status": "ok"}

    @classmethod
    async def check(cls, user_id: int, session: AsyncSession) -> dict:
        query = select(UserOrm.username).where(UserOrm.id == user_id)
        result = await session.execute(query)
        username = result.scalar_one()

        return {"status": "ok", "username": username}