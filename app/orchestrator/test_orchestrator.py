import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from app.orchestrator.intent_classifier import IntentClassifier


class StubLLM:
    def __init__(self, response: str):
        self.response = response

    def chat(self, messages, temperature=0.0, json_mode=False, **kwargs):
        return self.response

    def embed(self, text):
        return [0.0]

    def embed_many(self, texts):
        return [[0.0] for _ in texts]


def test_classify_growth():
    classifier = IntentClassifier(StubLLM('{"agents": ["partner_growth"]}'))
    assert classifier.classify("Which partners will grow?") == [
        "partner_growth"
    ]


def test_classify_growth_and_gtm():
    classifier = IntentClassifier(
        StubLLM('{"agents": ["partner_growth", "market_gtm"]}')
    )
    agents = classifier.classify("Who should I recruit and where?")
    assert "partner_growth" in agents
    assert "market_gtm" in agents


def test_classify_falls_back_to_growth_on_invalid_json():
    classifier = IntentClassifier(StubLLM("not json at all"))
    assert classifier.classify("anything") == ["partner_growth"]


def test_classify_ignores_unknown_agent():
    classifier = IntentClassifier(
        StubLLM('{"agents": ["unknown_agent", "market_gtm"]}')
    )
    assert classifier.classify("any") == ["market_gtm"]