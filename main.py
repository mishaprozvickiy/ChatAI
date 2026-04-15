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

    def ask(self, message: str, stream: bool = True) -> Generator[str, None, None]:
        self.history.append({"role": "user", "content": message})
        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        if stream:
            response = ollama.chat(model=self.model, messages=messages, stream=True)
            assistant_reply = self.text_name

            for chunk in response:
                delta = chunk.get("message", {}).get("content", "")
                assistant_reply += delta
                yield delta

            self.history.append({"role": "assistant", "content": assistant_reply})

        else:
            response = ollama.chat(model=self.model, messages=messages, stream=False)
            assistant_reply = self.text_name + response["message"]["content"]
            self.history.append({"role": "assistant", "content": assistant_reply})
            yield assistant_reply

    def print_answer(self, message):
        chat_message = self.ask(message)

        for msg in chat_message:
            print(end=msg)

        print()

    def clear_history(self):
        self.history.clear()

    def get_history(self) -> list[dict[str, str]]:
        return self.history.copy()


def run():
    chatbot = ChatBot()
    first_message = "Отправь короткое приветствие пользователю."
    chatbot.print_answer(first_message)

    while True:
        message = input("User: ")

        if message.lower() == "exit":
            exit()

        chatbot.print_answer(message)

if __name__ == "__main__":
    run()