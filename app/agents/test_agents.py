import asyncio
import json
import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)


class StubLLM:
    def chat(self, messages, temperature=0.0, json_mode=False, **kwargs):
        return "Based on the ranked profile signals, Nexora (P001) is the top growth candidate."

    def embed(self, text):
        return [0.1, 0.2]

    def embed_many(self, texts):
        return [[0.1, 0.2] for _ in texts]


class FakeMCPClient:
    def __init__(self, profiles=None):
        self.profiles = profiles or {}
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))

        if name == "search_partners":
            return (
                '[{"partner_id": "P001", "partner_name": "Nexora", '
                '"annual_revenue": 180000000, "employee_count": 850, '
                '"headquarters_state": "Texas"}]'
            )

        if name == "get_partner_profile":
            profile = self.profiles.get(arguments["partner_id"])
            return json.dumps(profile or {})

        return "[]"

    async def list_tools(self):
        return ["search_partners", "get_partner_profile"]


def sample_profile():
    return {
        "partner": {
            "partner_id": "P001",
            "partner_name": "Nexora",
            "annual_revenue": 180000000,
            "employee_count": 850,
            "headquarters_state": "Texas",
        },
        "capabilities": [
            {
                "capability": "AI",
                "proficiency_level": "Expert",
                "certification_count": 20,
            }
        ],
        "programs": [
            {"vendor": "Microsoft", "partner_tier": "Gold"},
            {"vendor": "AWS", "partner_tier": "Advanced"},
        ],
        "classifications": [{"classification": "MSP"}],
    }


def test_partner_growth_agent_gather_and_score():
    from app.agents.partner_growth_agent import PartnerGrowthAgent

    agent = PartnerGrowthAgent(StubLLM(), "http://x")
    fake = FakeMCPClient({"P001": sample_profile()})

    records = asyncio.run(agent._gather_data(fake))

    assert len(records) == 1
    assert records[0]["partner_id"] == "P001"
    assert "_profile" in records[0]

    tool_names = [c[0] for c in fake.calls]
    assert "search_partners" in tool_names
    assert tool_names.count("get_partner_profile") == 1

    scored = agent._score_partner(records[0])
    assert scored["partner_id"] == "P001"
    assert scored["score"] > 1.0


def test_market_gtm_agent_gather_and_aggregate():
    from app.agents.market_gtm_agent import MarketGtmAgent

    agent = MarketGtmAgent(StubLLM(), "http://x")
    fake = FakeMCPClient({"P001": sample_profile()})

    records = asyncio.run(agent._gather_data(fake))

    aggregate = agent._aggregate(records)

    assert aggregate["technologies"][0]["name"] == "AI"
    assert aggregate["regions"][0]["name"] == "Texas"
    assert aggregate["regions"][0]["partner_count"] == 1