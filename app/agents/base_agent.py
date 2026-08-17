import json

from app.agents.mcp_client import MCPClient
from app.context.context_builder import ContextBuilder
from app.llm.provider import ChatMessage, LLMProvider
from app.utils import parse_concatenated


class BaseAgent:
    MAX_TOOL_HOPS: int = 20
    name: str = "base"
    agent_instructions: str = ""

    def __init__(self, llm: LLMProvider, mcp_url: str, context: ContextBuilder | None = None):
        self.llm = llm
        self.mcp_url = mcp_url
        self.context = context or ContextBuilder()
        self.trace: list[dict] = []

    def _chat_user(self, question):
        return ChatMessage("user", question)

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

    def _chat(self, messages, json_mode: bool = False) -> str:
        return self.llm.chat(messages, temperature=0.0, json_mode=json_mode)

    def _system_prompt(self) -> ChatMessage:
        return ChatMessage("system", self.agent_instructions)


    def _store_answer(self, answer: str, question: str):
        from app.context.context_builder import ContextBuilder

        if self.context:
            self.context.remember_user(question)
            self.context.remember_assistant(answer)

    async def run(self, question: str) -> str:
        async with MCPClient(self.mcp_url) as client:
            tools = await client.list_tools()
            tools = [t for t in tools if t["name"] in self.TOOLS]
            llm_tools = client.to_llm_tools(tools)

            system_prompt = self._system_prompt()
            print(f"Using Agent: {self.name}")
            print(f"USER QUESTION: {question}")

            messages = [system_prompt, self._chat_user(question)]

            for _ in range(self.MAX_TOOL_HOPS):
                print(f"Tool request iteration {_ + 1} for question: {question}")
                response = self.llm.chat(messages, temperature=0.0, tools=llm_tools)

                if not response.tool_calls:
                    answer = response.content or "I don't know."
                    self._store_answer(answer, question)
                    return answer

                messages.append(
                    {
                        "role": "assistant",
                        "content": response.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in response.tool_calls
                        ],
                    }
                )

                for tc in response.tool_calls:
                    tool_name = tc.function.name
                    arguments = json.loads(tc.function.arguments)

                    print(f"TOOL CALLED: {tool_name}")
                    print(f"ARGUMENTS: {arguments}")

                    tool_result = await self._call_mcp(client, tool_name, arguments)

                    print(f"TOOL RESULT: {json.dumps(tool_result, default=str)}")

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(tool_result, default=str),
                        }
                    )

            final_response = self.llm.chat(
                messages, temperature=0.0, tools=llm_tools, tool_choice="none"
            )
            answer = final_response or "I don't know."
            self._store_answer(answer, question)
            print("*"*40)
            return answer
