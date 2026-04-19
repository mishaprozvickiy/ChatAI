import ollama
from typing import Generator
from config import MODEL, SYSTEM_PROMPT


class ChatBot:
    def __init__(self):
        self.model = MODEL
        self.system_prompt = SYSTEM_PROMPT
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