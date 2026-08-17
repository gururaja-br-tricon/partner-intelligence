import json

from app.agents.base_agent import BaseAgent
from app.agents.mcp_client import MCPClient


class MarketGtmAgent(BaseAgent):
    name = "market_gtm"

    TOOLS = [
        "search_partners",
        "get_partner_profile",
        "search_markets",
        "get_market_intelligence",
        "compare_markets",
        "find_partner_matches",
        "search_gtm_opportunities",
        "get_gtm_recommendations",
        "search_events",
        "get_event_participants",
        "search_partner_growth",
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
                "You are the Market / GTM Agent for TCC.\n\n"
                "Your job is to answer questions about which regions, markets, "
                "technologies, or market opportunities are gaining momentum, "
                "and where the business should focus its go-to-market effort.\n\n"
                "You have access to MCP tools that provide market, partner, "
                "event, and opportunity data. Choose the most appropriate tools "
                "based on the user's question.\n\n"
                "Use search_markets to see available market definitions.\n\n"
                "Use get_market_intelligence and compare_markets when the "
                "question asks about market size, growth, TAM/SAM/SOM, demand, "
                "adoption, or comparing markets.\n\n"
                "Use search_gtm_opportunities and get_gtm_recommendations when "
                "the question asks which opportunities to pursue or what action "
                "should be taken.\n\n"
                "Use search_events and get_event_participants when the question "
                "asks about events, conferences, attendance, or pipeline "
                "generated from events.\n\n"
                "Use search_partner_growth, find_partner_matches, and "
                "search_partners when the question asks which partners are "
                "gaining momentum or fit a market.\n\n"
                "Use the partner document search tool when the question asks "
                "about information contained in partner documents or PDFs.\n\n"
                "Do not invent figures or facts. Only use information returned "
                "by the selected tools.\n\n"
                "GUARDRAILS:\n"
                "- If you do not know the answer or the tools returned no "
                "relevant data, respond with exactly: \"I don't know\"\n"
                "- Never guess, estimate, or fabricate data values. If a "
                "calculation needs data (e.g. market size, growth, TAM/SAM/SOM, "
                "counts) that is missing, incomplete, or unavailable, do NOT "
                "compute or estimate the number. Instead, state clearly which "
                "piece of required data is missing and ask for it or say the "
                "data is not available.\n"
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
            print("*" * 40)
            return answer

    def _chat_user(self, question):
        from app.llm.provider import ChatMessage

        return ChatMessage("user", question)

    def _store_answer(self, answer: str, question: str):
        from app.context.context_builder import ContextBuilder

        if self.context:
            self.context.remember_user(question)
            self.context.remember_assistant(answer)
