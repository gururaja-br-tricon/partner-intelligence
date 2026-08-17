import json

from app.agents.base_agent import BaseAgent
from app.agents.mcp_client import MCPClient


class PartnerGrowthAgent(BaseAgent):
    name = "partner_growth"

    TOOLS = [
        "search_partners",
        "get_partner_profile",
        "search_partner_growth",
        "find_partner_matches",
        "explain_partner_match",
        "search_partner_documents",
    ]

    def __init__(self, llm, mcp_url, context=None):
        super().__init__(llm, mcp_url, context)
    
    async def run(self, question: str, jwt: str) -> str:
        async with MCPClient(self.mcp_url, auth_token=jwt) as client:
            tools = await client.list_tools()
            tools = [t for t in tools if t["name"] in self.TOOLS]
            llm_tools = client.to_llm_tools(tools)

            system_prompt = self._system_prompt(
                "You are the Partner Growth Agent.\n\n"
                "Your job is to answer questions about which partners are "
                "most likely to grow, should be recruited, deserve investment, "
                "or about a specific partner's growth.\n\n"
                "You have access to MCP tools that provide partner data. "
                "Choose the most appropriate tool based on the user's question.\n\n"
                "Use search_partners and get_partner_profile when the question "
                "requires partner attributes, revenue, employees, capabilities, "
                "certifications, partner tier, vendor programs, status, or "
                "other structured partner information.\n\n"
                "Use search_partner_growth when the question asks about revenue "
                "growth, pipeline growth, partner health, performance status, or "
                "which partners are growing or declining.\n\n"
                "Use find_partner_matches and explain_partner_match when the "
                "question asks which partners fit a market or why a partner was "
                "recommended.\n\n"
                "Use the partner document search tool when the question asks "
                "about information contained in partner documents or PDFs.\n\n"
                "Do not invent figures or facts. Only use information returned "
                "by the selected tool.\n\n"
                "GUARDRAILS:\n"
                "- If you do not know the answer or the tools returned no "
                "relevant data, respond with exactly: \"I don't know\"\n"
                "- Never guess, estimate, or fabricate data values. If a "
                "calculation needs data (e.g. growth rate, revenue, counts) "
                "that is missing, incomplete, or unavailable, do NOT compute "
                "or estimate the number. Instead, state clearly which piece of "
                "required data is missing and ask for it or say the data is "
                "not available.\n"
                "- Do not extrapolate beyond what the tools returned."
            )
            print(f"USER QUESTION: {question}")

            messages = [system_prompt, self._chat_user(question)]

            MAX_TOOL_HOPS = 20

            for _ in range(MAX_TOOL_HOPS):
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

                # Execute EVERY tool call the model made, not just [0]
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

            # Hit MAX_TOOL_HOPS — force a final text-only answer
            final_response = self.llm.chat(
                messages, temperature=0.0, tools=llm_tools, tool_choice="none"
            )
            answer = final_response or "I don't know."
            self._store_answer(answer, question)
            print("*"*40)
            return answer
        
    def _chat_user(self, question):
        from app.llm.provider import ChatMessage

        return ChatMessage("user", question)

    def _store_answer(self, answer: str, question: str):
        from app.context.context_builder import ContextBuilder

        if self.context:
            self.context.remember_user(question)
            self.context.remember_assistant(answer)