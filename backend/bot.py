from ollama import AsyncClient
from sqlalchemy import RowMapping
from typing import AsyncGenerator, Sequence
from config import MODEL, OLLAMA_HOST, SYSTEM_PROMPT


class ChatBot:
    def __init__(self):
        self.model = MODEL
        self.system_prompt = SYSTEM_PROMPT

    async def ask(self, messages: Sequence[RowMapping]) -> AsyncGenerator[str, None]:
        client = AsyncClient(host=OLLAMA_HOST)
        response = await client.chat(model=self.model, messages=messages, stream=True)

        async for chunk in response:
            delta = chunk.get("message", {}).get("content", "")
            yield delta


chatbot = ChatBot()