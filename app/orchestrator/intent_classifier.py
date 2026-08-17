import json

from app.agents.market_gtm_agent import MarketGtmAgent
from app.agents.partner_growth_agent import PartnerGrowthAgent
from app.llm.provider import ChatMessage, LLMProvider

AGENT_OPTIONS = ["partner_growth", "market_gtm"]

AGENT_CONTEXT = {
    "partner_growth": {
        "tools": PartnerGrowthAgent.TOOLS,
        "handles": [
            "Which partners are growing, declining, healthy, or stagnant",
            "Which partners should be recruited, invested in, or onboarded",
            "Partner attributes: revenue, employees, capabilities, certifications, "
            "tier, vendor programs, classification, status, location",
            "Revenue growth, pipeline growth, and partner health scores",
            "Why a partner fits (or doesn't fit) a market — match scores",
            "Information inside partner documents / PDFs",
        ],
        "questions": [
            "Which partners are growing fastest?",
            "Which partners should be recruited?",
            "Which partners deserve more investment?",
            "Which partners are declining?",
            "What is partner X's revenue and tier?",
            "Why was partner X recommended?",
        ],
        "keywords": [
            "grow", "growth", "recruit", "recruitment", "invest", "onboard",
            "decline", "declining", "healthy", "health", "performance",
            "revenue", "pipeline", "employees", "capabilities", "certifications",
            "tier", "partner tier", "vendor", "program", "status", "match",
            "recommended", "partner fit", "profile",
        ],
    },
    "market_gtm": {
        "tools": MarketGtmAgent.TOOLS,
        "handles": [
            "Market definitions, size, growth, demand, adoption",
            "TAM, SAM, SOM and market prioritization",
            "Comparing two or more markets or technologies",
            "GTM opportunities and recommended actions",
            "Events, conferences, attendance, and pipeline generated from events",
            "Regions or technologies gaining momentum and where to focus GTM effort",
        ],
        "questions": [
            "Which technologies are gaining momentum in North America?",
            "Compare cybersecurity and generative AI markets.",
            "Which market has the highest TAM?",
            "What GTM actions should we take in Europe?",
            "Which partners attended the industry summit and what pipeline was generated?",
            "Where should the business focus its go-to-market effort?",
        ],
        "keywords": [
            "market", "markets", "region", "regions", "technology", "technologies",
            "momentum", "size", "growth", "demand", "adoption", "tam", "sam", "som",
            "compare", "opportunity", "opportunities", "gtm", "go-to-market", "recommendation",
            "focus", "priority", "prioritize", "event", "events", "conference", "summit",
            "attendees", "participants", "pipeline",
        ],
    },
}


class IntentClassifier:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def classify(self, question: str) -> list[str]:
        prompt = self._build_prompt(question)

        raw = self.llm.chat(
            [ChatMessage("user", prompt)], temperature=0.0, json_mode=True
        )

        return self._parse(raw)

    def _build_prompt(self, question: str) -> str:
        sections = []
        for agent in AGENT_OPTIONS:
            info = AGENT_CONTEXT[agent]
            # handles = "\n".join(f"      - {h}" for h in info["handles"])
            # questions = "\n".join(f"      - {q}" for q in info["questions"])
            # keywords = ", ".join(info["keywords"])
            tools = ", ".join(info["tools"])
            sections.append(
                f"  '" + agent + "':\n"
                f"    TOOLS IT CAN USE: {tools}\n"
                # f"    FUNCTIONALITY / WHAT IT HANDLES:\n{handles}\n"
                # f"    EXAMPLE QUESTIONS IT ANSWERS:\n{questions}\n"
                # f"    TRIGGER KEYWORDS: {keywords}"
            )

        return (
            "You are an intent router for a partner-intelligence system. "
            "Classify the user's question into the agent(s) that can answer it.\n\n"
            "Allowed agents:\n"
            + "\n".join(f"  - {a}" for a in AGENT_OPTIONS)
            + "\n\n"
            "AGENT CAPABILITIES (tools available, functionality handled, "
            "example questions, and trigger keywords):\n\n"
            + "\n\n".join(sections)
            + "\n\n"
            "ROUTING RULES:\n"
            "- Choose an agent when the question falls under its functionality "
            "or its tools can retrieve the required data.\n"
            "- If the question involves partner identity, partner attributes, "
            "growth/decline, recruiting, or partner-market fit, include "
            "'partner_growth'.\n"
            "- If the question involves markets, market intelligence, GTM "
            "opportunities/actions, events, or regional/technology momentum, "
            "include 'market_gtm'.\n"
            "- Questions may overlap (many partner tools are shared). If the "
            "question spans both agents, return BOTH.\n"
            "- Do NOT invent agents. Only use the allowed agent names.\n"
            "- Return ONLY valid JSON, with no other text:\n"
            '  {"agents": ["<agent>", ...]}\n\n'
            "EXAMPLES:\n"
            '  Q: "Which partners are growing fastest?" -> '
            '{"agents": ["partner_growth"]}\n'
            '  Q: "What is the TAM for cybersecurity in North America?" -> '
            '{"agents": ["market_gtm"]}\n'
            '  Q: "Who should I recruit and which regions should I prioritize?" -> '
            '{"agents": ["partner_growth", "market_gtm"]}\n\n'
            "User question: " + question
        )

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