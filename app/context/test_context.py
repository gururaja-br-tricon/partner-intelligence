import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from app.context.conversation_memory import ConversationMemory
from app.context.semantic_cache import SemanticCache


def test_memory_keeps_last_n_turns():
    memory = ConversationMemory(max_turns=4)
    for i in range(6):
        memory.add_user(f"q{i}")
        memory.add_assistant(f"a{i}")

    messages = memory.messages()
    assert len(messages) == 4
    assert messages[0]["content"] == "q4"
    assert messages[-1]["content"] == "a5"


def test_semantic_cache_miss_then_hit(tmp_path):
    cache = SemanticCache(
        path=str(tmp_path / "cache.json"),
    )

    first = cache.get("Which partners are most likely to grow?")
    assert first is None

    cache.put("Which partners are most likely to grow?", "cached answer")

    second = cache.get("Which partners are most likely to grow?")
    assert second is not None
    assert second == "cached answer"


def test_semantic_cache_normalized_string_hits(tmp_path):
    cache = SemanticCache(
        path=str(tmp_path / "cache.json"),
    )
    cache.put("Which technologies are gaining momentum in Texas?", "answer")

    hit = cache.get("  which technologies are gaining momentum in texas?  ")
    assert hit is not None
    assert hit == "answer"


def test_semantic_cache_paraphrase_misses(tmp_path):
    cache = SemanticCache(
        path=str(tmp_path / "cache.json"),
    )
    cache.put("Which partners are most likely to grow?", "answer")

    miss = cache.get("Tell me about high-potential growth partners")
    assert miss is None