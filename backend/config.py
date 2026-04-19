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