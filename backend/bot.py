import ollama
from typing import Generator


class ChatBot:
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model
        self.system_prompt = "Ты полезный ассистент. Тебя зовут ChatAI. Отвечай по делу и на русском языке."
        self.history: list[dict[str, str]] = []

    def ask(self, message: str) -> Generator[str, None, None]:
        self.history.append({"role": "user", "content": message})
        messages = [{"role": "system", "content": self.system_prompt}] + self.history
        response = ollama.chat(model=self.model, messages=messages, stream=True)
        assistant_reply = ""

        for chunk in response:
            delta = chunk.get("message", {}).get("content", "")
            assistant_reply += delta
            yield delta

        self.history.append({"role": "assistant", "content": assistant_reply})


chatbot = ChatBot()