from ollama import AsyncClient
from typing import AsyncGenerator
from config import MODEL, OLLAMA_HOST, SYSTEM_PROMPT


class ChatBot:
    def __init__(self):
        self.model = MODEL
        self.system_prompt = SYSTEM_PROMPT
        # TODO: self.history должен получать историю сообщений пользователя из бд, пока что вся история общая для всех
        self.history: list[dict[str, str]] = []

    async def ask(self, message: str) -> AsyncGenerator[str, None]:
        self.history.append({"role": "user", "content": message})
        messages = [{"role": "system", "content": self.system_prompt}] + self.history
        client = AsyncClient(host=OLLAMA_HOST)
        response = await client.chat(model=self.model, messages=messages, stream=True)
        assistant_reply = ""

        async for chunk in response:
            delta = chunk.get("message", {}).get("content", "")
            assistant_reply += delta
            yield delta

        self.history.append({"role": "assistant", "content": assistant_reply})


chatbot = ChatBot()