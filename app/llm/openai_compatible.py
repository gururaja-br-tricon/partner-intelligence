import os

from openai import OpenAI

from app.llm.provider import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        chat_model: str,
        embedding_model: str,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.chat_model = chat_model
        self.embedding_model = embedding_model

        if not api_key:
            raise ValueError(
                f"No API key configured for provider at {base_url}. "
                "Set the corresponding *_API_KEY in .env"
            )

        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def chat(
        self,
        messages,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        json_mode: bool = False,
        tools: list[dict] | None = None,
        tool_choice: str | None = None, 
        ) -> str:
        kwargs = {
            "model": self.chat_model,
            "messages": [m.to_dict() if hasattr(m, "to_dict") else m for m in messages],
            "temperature": temperature,
        }

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        if tools:
            kwargs["tools"] = tools
            if tool_choice is not None:
                kwargs["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        # Return the raw message when tools were offered on THIS call,
        # since callers need .tool_calls. Otherwise return plain text.
        if tools and tool_choice != "none":
            return message

        return message.content or ""

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.embedding_model, input=texts
        )

        ordered = sorted(response.data, key=lambda d: d.index)

        return [d.embedding for d in ordered]


def groq_provider():
    from app.config import settings

    return OpenAICompatibleProvider(
        base_url="https://api.groq.com/openai/v1",
        api_key=settings.groq_api_key,
        chat_model=settings.groq_chat_model,
        embedding_model=settings.groq_embedding_model,
    )


def qwen_provider():
    from app.config import settings

    if not settings.qwen_base_url:
        raise ValueError(
            "QWEN_BASE_URL is required when LLM_PROVIDER=qwen"
        )

    return OpenAICompatibleProvider(
        base_url=settings.qwen_base_url,
        api_key=settings.qwen_api_key,
        chat_model=settings.qwen_chat_model,
        embedding_model=settings.qwen_embedding_model,
    )


def get_provider() -> OpenAICompatibleProvider:
    from app.config import settings

    print(f"Configured LLM Provider: {settings.llm_provider}")

    if settings.llm_provider == "qwen":
        return qwen_provider()
    return groq_provider()
