from collections import deque


class ConversationMemory:
    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self.turns: deque = deque(maxlen=max_turns)

    def add_user(self, text: str) -> None:
        self.turns.append({"role": "user", "content": text})

    def add_assistant(self, text: str) -> None:
        self.turns.append({"role": "assistant", "content": text})

    def add(self, role: str, content: str) -> None:
        if role == "user":
            self.add_user(content)
        elif role == "assistant":
            self.add_assistant(content)
        else:
            self.turns.append({"role": role, "content": content})

    def messages(self) -> list[dict]:
        return list(self.turns)

    def clear(self) -> None:
        self.turns.clear()

    def __len__(self):
        return len(self.turns)