import asyncio

from app.agents.market_gtm_agent import MarketGtmAgent
from app.agents.partner_growth_agent import PartnerGrowthAgent
from app.context.context_builder import ContextBuilder
from app.context.semantic_cache import SemanticCache
from app.llm.openai_compatible import get_provider
from app.orchestrator.intent_classifier import IntentClassifier


class Orchestrator:
    def __init__(self, mcp_url: str, context: ContextBuilder | None = None):
        self.mcp_url = mcp_url
        self.llm = get_provider()
        self.context = context or ContextBuilder()
        self.cache = self.context.cache
        self.intent_classifier = IntentClassifier(self.llm)
        self.last_route: list[str] = []
        self.last_cache_hit: bool = False

    def _build_agent(self, name: str):
        if name == "partner_growth":
            return PartnerGrowthAgent(
                self.llm, self.mcp_url, context=self.context
            )
        if name == "market_gtm":
            return MarketGtmAgent(self.llm, self.mcp_url, context=self.context)
        raise ValueError(f"Unknown agent: {name}")

    async def answer(self, question: str) -> str:
        cached = self.cache.get(question)

        if cached is not None:
            self.last_cache_hit = True
            return cached

        self.last_cache_hit = False

        agents = self.intent_classifier.classify(question)
        self.last_route = agents

        tasks = [self._build_agent(a).run(question) for a in agents]

        answers = await asyncio.gather(*tasks)

        final_answer = self._merge(agents, answers)

        self.context.remember_user(question)
        self.context.remember_assistant(final_answer)

        # self.cache.put(question, final_answer)

        return final_answer

    def _merge(self, agents: list[str], answers: list[str]) -> str:
        if len(answers) == 1:
            return answers[0]

        labels = {
            "partner_growth": "Partner Growth",
            "market_gtm": "Market/GTM",
        }

        sections = []
        for agent, answer in zip(agents, answers):
            sections.append(f"## {labels.get(agent, agent)}\n{answer}")

        return (
            "Here is the combined view across agents.\n\n"
            + "\n\n".join(sections)
            + "\n\nI've merged insights from both the Partner Growth and "
            "Market/GTM analyses above."
        )