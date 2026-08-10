import json

from app.agents.base_agent import BaseAgent
from app.agents.mcp_client import MCPClient

TIER_RANK = {"Silver": 1, "Gold": 2, "Platinum": 3}
PROFICIENCY_RANK = {"Advanced": 2, "Expert": 3}


class PartnerGrowthAgent(BaseAgent):
    name = "partner_growth"

    def __init__(self, llm, mcp_url, context=None):
        super().__init__(llm, mcp_url, context)
        self.max_profiles = 10

    async def _gather_data(self, client: MCPClient) -> list[dict]:
        search_result = await self._call_mcp(
            client,
            "search_partners",
            {"status": "Active"},
        )

        for record in search_result[: self.max_profiles]:
            profile = await self._call_mcp(
                client,
                "get_partner_profile",
                {"partner_id": record["partner_id"]},
            )

            record["_profile"] = profile

        return search_result

    def _score_partner(self, record: dict) -> dict:
        profile = record.get("_profile") or {}
        partner = profile.get("partner") or record

        capabilities = profile.get("capabilities") or []
        programs = profile.get("programs") or []
        classifications = profile.get("classifications") or []

        score = 0.0
        signals = []

        revenue = partner.get("annual_revenue") or 0
        employees = partner.get("employee_count") or 0

        revenue_factor = revenue / 200_000_000
        score += min(revenue_factor, 1.0) * 1.0
        signals.append(f"annual revenue ${revenue:,}")

        employee_factor = employees / 1000
        score += min(employee_factor, 1.0) * 0.5
        signals.append(f"{employees:,} employees")

        capabilities = capabilities if isinstance(capabilities, list) else []
        programs = programs if isinstance(programs, list) else []

        for capability in capabilities:
            proficiency = capability.get("proficiency_level", "")
            score += PROFICIENCY_RANK.get(proficiency, 0) * 0.15
            certifications = capability.get("certification_count") or 0
            score += min(certifications / 25, 1.0) * 0.15

        max_tier = 0
        for program in programs:
            tier = TIER_RANK.get(program.get("partner_tier", ""), 0)
            max_tier = max(max_tier, tier)

        score += max_tier * 0.4
        if max_tier:
            signals.append(f"top partner tier reached")

        vendor_count = len({p.get("vendor") for p in programs})
        score += min(vendor_count, 3) * 0.3
        signals.append(f"{vendor_count} vendor programs")

        if len(classifications) > 1:
            score += 0.1

        return {
            "partner_id": partner.get("partner_id"),
            "partner_name": partner.get("partner_name"),
            "score": round(score, 2),
            "revenue": revenue,
            "employees": employees,
            "signals": signals,
        }

    async def run(self, question: str) -> str:
        async with MCPClient(self.mcp_url) as client:
            records = await self._gather_data(client)

        if not records:
            return "No active partner records found."

        scored = [self._score_partner(record) for record in records]
        scored.sort(key=lambda x: x["score"], reverse=True)

        scored_output = json.dumps(scored, indent=2, default=str)

        system_prompt = self._system_prompt(
            "You are the Partner Growth Agent for TCC. The user asked a "
            "question about which partners are most likely to grow, should "
            "be recruited, or deserve investment.\n\n"
            "A deterministic scoring heuristic has already ranked the "
            "partners based on revenue, headcount, capability proficiency, "
            "certifications, partner tier, and vendor-program reach.\n\n"
            "Your job: turn the ranked data below into a concise, "
            "natural-language answer that (1) states the top candidates, "
            "(2) cites the concrete numbers behind each recommendation "
            "(revenue, employees, tier, capabilities, certifications), and "
            "(3) is explicit that 'growth potential' is inferred from "
            "current profile signals, not historical growth data.\n\n"
            "Do not invent figures. Only cite values present in the data.\n\n"
            "Ranked partners data:\n" + scored_output
        )

        answer = self.llm.chat(
            [system_prompt, self._chat_user(question)],
            temperature=0.0,
        )

        self._store_answer(answer, question)

        return answer

    def _chat_user(self, question):
        from app.llm.provider import ChatMessage

        return ChatMessage("user", question)

    def _store_answer(self, answer: str, question: str):
        from app.context.context_builder import ContextBuilder

        if self.context:
            self.context.remember_user(question)
            self.context.remember_assistant(answer)