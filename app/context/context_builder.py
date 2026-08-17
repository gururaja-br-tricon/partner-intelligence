from app.context.conversation_memory import ConversationMemory
from app.context.semantic_cache import SemanticCache


class ContextBuilder:
    def __init__(
        self,
        memory: ConversationMemory | None = None,
        cache: SemanticCache | None = None,
    ):
        self.memory = memory or ConversationMemory()
        self.cache = cache or SemanticCache()

    def build(self, question: str) -> list[dict]:
        messages = []

        messages.append(
            {
                "role": "system",
                "content": (
                    "You are a TCC partner intelligence assistant. Answer "
                    "with cited numbers from the retrieved partner data. "
                    "Be concise and factual."
                ),
            }
        )

        messages.extend(self.memory.messages())

        messages.append({"role": "user", "content": question})

        return messages

    def remember_user(self, question: str) -> None:
        self.memory.add_user(question)

    def remember_assistant(self, answer: str) -> None:
        self.memory.add_assistant(answer)