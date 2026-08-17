import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from app.config import settings

from app.agents.mcp_client import MCPClient


class StubLLM:
    def chat(self, messages, temperature=0.0, json_mode=False, **kwargs):
        return "ok"

    def embed(self, text):
        return [1.0, 0.0]

    def embed_many(self, texts):
        return [[1.0, 0.0] for _ in texts]


class FakeMCPClient:
    def __init__(self):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return "{}"

    async def list_tools(self):
        return ["search_partners", "get_partner_profile", "search_partner_documents"]


def test_embed_deterministic():
    assert StubLLM().embed("anything") == [1.0, 0.0]


def test_connect_fails_gracefully():
    import asyncio

    async def _try_connect():
        client = MCPClient(url="http://127.0.0.1:9/mcp")
        try:
            await client.connect()
            return "connected"
        except Exception:
            return "failed"

    result = asyncio.run(_try_connect())
    # No server is running on port 9, so this must be 'failed'.
    assert result == "failed"