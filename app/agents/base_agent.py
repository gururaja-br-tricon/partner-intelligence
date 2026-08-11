import json

from app.agents.mcp_client import MCPClient
from app.context.context_builder import ContextBuilder
from app.llm.provider import ChatMessage, LLMProvider
from app.utils import parse_concatenated


class BaseAgent:
    name = "base"

    def __init__(
        self,
        llm: LLMProvider,
        mcp_url: str,
        context: ContextBuilder | None = None,
    ):
        self.llm = llm
        self.mcp_url = mcp_url
        self.context = context or ContextBuilder()
        self.trace: list[dict] = []

    def _log_tool_call(self, name: str, arguments: dict, result: str):
        self.trace.append(
            {
                "agent": self.name,
                "tool": name,
                "arguments": arguments,
                "result_preview": result[:500],
            }
        )

    async def _call_mcp(self, client: MCPClient, name: str, arguments: dict):
        result = await client.call_tool(name, arguments)
        self._log_tool_call(name, arguments, result)
        return parse_concatenated(result)

    async def run(self, question: str) -> str:
        raise NotImplementedError

    def _chat(
        self,
        messages,
        json_mode: bool = False,
    ) -> str:
        return self.llm.chat(messages, temperature=0.0, json_mode=json_mode)

    def _system_prompt(self, agent_instructions: str) -> ChatMessage:
        return ChatMessage("system", agent_instructions)