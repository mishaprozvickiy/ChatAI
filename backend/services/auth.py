from config import ACCESS_TOKEN_LIFESPAN_MINUTES, REFRESH_TOKEN_LIFESPAN_DAYS
from settings import settings
from authx import AuthX, AuthXConfig
from datetime import timedelta

config = AuthXConfig()

config.JWT_SECRET_KEY = settings.jwt_secret_key
config.JWT_TOKEN_LOCATION = ["cookies"]

config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=ACCESS_TOKEN_LIFESPAN_MINUTES)

config.JWT_REFRESH_COOKIE_NAME = "refresh_token"
config.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=REFRESH_TOKEN_LIFESPAN_DAYS)

config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_COOKIE_SECURE = False

security = AuthX(config=config)


class AuthService:
    @classmethod
    def refresh_access_token(cls, user_id: str) -> str:
        new_access_token = security.create_access_token(uid=user_id)
        return new_access_token