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
            client, "search_partners", {"status": "Active"}
        )
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
    
    async def run(self, question: str, jwt: str) -> str:
        async with MCPClient(self.mcp_url, auth_token=jwt) as client:
            tools = await client.list_tools()
            llm_tools = client.to_llm_tools(tools)

            system_prompt = self._system_prompt(
                "You are the Partner Growth Agent.\n\n"
                "Your job is to answer questions about which partners are "
                "most likely to grow, should be recruited, deserve investment, "
                "or about a specific partner's growth.\n\n"
                "You have access to MCP tools that provide partner data. "
                "Choose the most appropriate tool based on the user's question.\n\n"
                "Use the structured partner tools when the question requires "
                "partner attributes, revenue, employees, capabilities, "
                "certifications, partner tier, vendor programs, status, or "
                "other structured partner information.\n\n"
                "Use the partner document search tool when the question asks "
                "about information contained in partner documents or PDFs.\n\n"
                "Do not invent figures or facts. Only use information returned "
                "by the selected tool.\n\n"
                "If the available data does not contain enough information to "
                "answer the question, say so clearly."
            )
            print(f"USER QUESTION: {question}")

            messages = [system_prompt, self._chat_user(question)]

            MAX_TOOL_HOPS = 20

            for _ in range(MAX_TOOL_HOPS):
                print(f"Tool request iteration {_ + 1} for question: {question}")
                response = self.llm.chat(messages, temperature=0.0, tools=llm_tools)

                if not response.tool_calls:
                    answer = response.content or "I could not determine an answer."
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
            answer = final_response or "I could not determine an answer."
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