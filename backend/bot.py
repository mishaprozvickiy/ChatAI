import ollama
from typing import Generator


class ChatBot:
    def __init__(self, model: str = "qwen2.5:7b", name: str | None = "ChatAI"):
        self.model = model
        self.system_prompt = "Ты полезный ассистент. Отвечай кратко, по делу и на языке пользователя. " \
                             "Отвечай только на русском языке, без иностранных слов."
        self.history: list[dict[str, str]] = []
        self.name = name
        self.text_name = self.name + ": "

    def ask(self, message: str) -> Generator[str, None, None]:
        self.history.append({"role": "user", "content": message})
        messages = [{"role": "system", "content": self.system_prompt}] + self.history
        response = ollama.chat(model=self.model, messages=messages, stream=True)
        assistant_reply = self.text_name

        for chunk in response:
            delta = chunk.get("message", {}).get("content", "")
            assistant_reply += delta
            yield delta

        self.history.append({"role": "assistant", "content": assistant_reply})

    def clear_history(self):
        self.history.clear()

    def get_history(self) -> list[dict[str, str]]:
        return self.history.copy()


chatbot = ChatBot()