from ollama import AsyncClient
from typing import AsyncGenerator, Any
from config import MODEL, OLLAMA_HOST, SYSTEM_PROMPT


class ChatBot:
    def __init__(self):
        self.model = MODEL
        self.system_prompt = SYSTEM_PROMPT

    async def ask(self, messages: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
        full_messages = [
            {
                "role": "system",
                "content": self.system_prompt}
        ] + messages

        client = AsyncClient(host=OLLAMA_HOST)
        response = await client.chat(model=self.model, messages=full_messages, stream=True)

        async for chunk in response:
            delta = chunk.get("message", {}).get("content", "")
            yield delta


chatbot = ChatBot()