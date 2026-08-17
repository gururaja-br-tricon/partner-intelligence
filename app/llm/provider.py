from abc import ABC, abstractmethod


class ChatMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def to_dict(self):
        return {"role": self.role, "content": self.content}


class LLMProvider(ABC):
    @abstractmethod
    def chat(
        self,
        messages,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str:
        ...

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        ...

    @abstractmethod
    def embed_many(self, texts: list[str]) -> list[list[float]]:
        ...