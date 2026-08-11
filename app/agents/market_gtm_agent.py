import json
import re

from app.agents.base_agent import BaseAgent
from app.agents.mcp_client import MCPClient

PROFICIENCY_RANK = {"Advanced": 2, "Expert": 3}


class MarketGtmAgent(BaseAgent):
    name = "market_gtm"

    def __init__(self, llm, mcp_url, context=None):
        super().__init__(llm, mcp_url, context)
        self.max_profiles = 10

    async def _gather_data(self, client: MCPClient) -> list[dict]:
        search_result = await self._call_mcp(
            client,
            "search_partners",
            {},
        )

        records = search_result

        # for record in search_result[: self.max_profiles]:
        #     profile = await self._call_mcp(
        #         client,
        #         "get_partner_profile",
        #         {"partner_id": record["partner_id"]},
        #     )

        #     record["_profile"] = profile

        return records

    def _aggregate(self, records: list[dict]) -> dict:
        regions: dict[str, dict] = {}
        technologies: dict[str, dict] = {}

        for record in records:
            partner = record.get("partner", record)
            profile = record.get("_profile") or {}

            region = partner.get("headquarters_state") or partner.get(
                "headquarters_country"
            )

            capabilities = profile.get("capabilities") or []
            programs = profile.get("programs") or []

            for capability in capabilities:
                tech = capability.get("capability", "Unknown")
                proficiency = capability.get("proficiency_level", "")
                weight = PROFICIENCY_RANK.get(proficiency, 1)

                technologies.setdefault(
                    tech, {"partners": set(), "weighted": 0.0}
                )
                technologies[tech]["partners"].add(partner.get("partner_id"))
                technologies[tech]["weighted"] += weight

            if region:
                regions.setdefault(
                    region, {"partners": set(), "weighted": 0.0}
                )
                regions[region]["partners"].add(partner.get("partner_id"))

                vendor_count = len({p.get("vendor") for p in programs})
                regions[region]["weighted"] += 1 + min(vendor_count, 3) * 0.5

        def serialize(group):
            return [
                {
                    "name": name,
                    "partner_count": len(meta["partners"]),
                    "weighted_strength": round(meta["weighted"], 2),
                }
                for name, meta in sorted(
                    group.items(),
                    key=lambda item: (item[1]["weighted"], item[1]["partners"]),
                    reverse=True,
                )
            ]

        return {
            "regions": serialize(regions),
            "technologies": serialize(technologies),
        }

    async def run(self, question: str) -> str:
        async with MCPClient(self.mcp_url) as client:
            records = await self._gather_data(client)

        if not records:
            return "No partner records found."

        aggregate = self._aggregate(records)

        data_output = json.dumps(aggregate, indent=2, default=str)

        system_prompt = self._system_prompt(
            "You are the Market / GTM Agent. The user asked "
            "about which regions or technologies are gaining momentum.\n\n"
            "The aggregated data below is a static snapshot of current "
            "partner capability strength per region and per technology "
            "('weighted_strength' combines proficiency and vendor-program "
            "reach). It is a proxy for momentum; there is no time-series "
            "growth data in the POC dataset.\n\n"
            "Your job: write a concise natural-language answer that (1) "
            "names the leading regions and technologies, (2) cites the "
            "partner counts and strengths from the data, and (3) states "
            "that this reflects current strength as a momentum proxy.\n\n"
            "Do not invent figures.\n\n"
            "Aggregated data:\n" + data_output
        )

        from app.llm.provider import ChatMessage

        answer = self.llm.chat(
            [system_prompt, ChatMessage("user", question)],
            temperature=0.0,
        )

        if self.context:
            self.context.remember_user(question)
            self.context.remember_assistant(answer)

        return answer