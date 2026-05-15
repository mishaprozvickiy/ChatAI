from fastapi import HTTPException

SYSTEM_PROMPT = "Ты полезный ассистент. " \
                "Тебя зовут ChatAI. " \
                "Отвечай по делу и на русском языке."

MODEL = "qwen2.5:7b"
FIRST_BOT_MESSAGE = "Привет! Чем могу помочь?"

CORS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

PORT = 8001

DB_URL = "sqlite+aiosqlite:///messages.db"

CREDS_EXCEPTION = HTTPException(status_code=401, detail="Incorrect login or password")
MISSING_TOKEN_EXCEPTION = HTTPException(status_code=401, detail="Missing refresh or access token")
FORBIDDEN_EXCEPTION = HTTPException(status_code=403, detail="Access denied")
RECORD_NOT_FOUND_EXCEPTION = HTTPException(status_code=404, detail="Record not found")
USERNAME_EXISTS_EXCEPTION = HTTPException(status_code=409, detail="Username is already exists")

ACCESS_TOKEN_LIFESPAN_MINUTES = 15
REFRESH_TOKEN_LIFESPAN_DAYS = 7