import json

from app.llm.provider import ChatMessage, LLMProvider

AGENT_OPTIONS = ["partner_growth", "market_gtm"]


class IntentClassifier:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def classify(self, question: str) -> list[str]:
        prompt = (
            "Classify the user's partner-intelligence question into the "
            f"agents that can answer it. Allowed agents: "
            f"{', '.join(AGENT_OPTIONS)}.\n\n"
            "Rules:\n"
            "- partner_growth: asks about which partners are likely to "
            "grow, should be recruited, or deserve investment.\n"
            "- market_gtm: asks about regions or technologies gaining "
            "momentum, market prioritization, or where to focus.\n"
            "- If the question spans both, return both.\n"
            "- Return ONLY valid JSON: {\"agents\": [...]}\n\n"
            "User question: " + question
        )

        raw = self.llm.chat(
            [ChatMessage("user", prompt)], temperature=0.0, json_mode=True
        )

        return self._parse(raw)

    def _parse(self, raw: str) -> list[str]:
        try:
            cleaned = raw.strip().strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            data = {}

        agents = data.get("agents", [])

        return [a for a in agents if a in AGENT_OPTIONS] or ["partner_growth"]