import asyncio

from app.mcp_server.client import MCPClient


async def main():
    client = MCPClient()

    await client.connect()

    print("\n" + "=" * 100)
    print("AVAILABLE MCP TOOLS")
    print("=" * 100)

    tools = await client.list_tools()

    for tool in tools:
        print(f"\nName: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Input Schema: {tool.input_schema}")

    # -------------------------------------------------------------------------
    # BUSINESS TEST CASES
    #
    # Each test represents a question that a real user could ask the LLM.
    # The arguments below represent the filters the LLM would eventually
    # extract from the user's question.
    # -------------------------------------------------------------------------

    tests = [
        # # =====================================================================
        # # PARTNER GROWTH
        # # =====================================================================
        # # User question:
        # # "Which partners are most likely to grow?"
        # (
        #     "search_partner_growth",
        #     {
        #         "performance_year": 2026,
        #         "min_revenue_growth_pct": 10,
        #         "min_pipeline_growth_pct": 15,
        #         "min_partner_health_score": 75,
        #         "performance_status": "Growing",
        #         "limit": 10,
        #     },
        # ),
        # # User question:
        # # "Which partners are growing strongly but are still relatively small?"
        # (
        #     "search_partner_growth",
        #     {
        #         "performance_year": 2026,
        #         "min_revenue_growth_pct": 12,
        #         "min_pipeline_growth_pct": 15,
        #         "max_revenue": 100000000,
        #         "min_partner_health_score": 75,
        #         "limit": 10,
        #     },
        # ),
        # # User question:
        # # "Which partners should we consider for investment based on growth,
        # # pipeline and partner health?"
        # (
        #     "search_partner_growth",
        #     {
        #         "performance_year": 2026,
        #         "min_revenue_growth_pct": 10,
        #         "min_pipeline_growth_pct": 15,
        #         "min_win_rate_pct": 60,
        #         "min_partner_health_score": 80,
        #         "limit": 10,
        #     },
        # ),
        # # User question:
        # # "Which partners resemble our top-performing partners?"
        # (
        #     "search_partner_growth",
        #     {
        #         "performance_year": 2026,
        #         "min_revenue_growth_pct": 10,
        #         "min_employee_growth_pct": 7,
        #         "min_retention_rate_pct": 95,
        #         "min_win_rate_pct": 60,
        #         "min_partner_health_score": 78,
        #         "limit": 10,
        #     },
        # ),
        # # User question:
        # # "Which partners have high pipeline growth but relatively low
        # # current revenue?"
        # (
        #     "search_partner_growth",
        #     {
        #         "performance_year": 2026,
        #         "min_pipeline_growth_pct": 20,
        #         "max_revenue": 100000000,
        #         "limit": 10,
        #     },
        # ),
        # =====================================================================
        # PARTNER PROFILE / STRUCTURED PARTNER SEARCH
        # =====================================================================
        # User question:
        # "Show me technology partners in California that are active and
        # have a specific capability."
        (
            "search_partners",
            {
                "headquarters_state": "California",
                "industry": "Technology",
                "status": "Active",
                "capability": "Cloud",
                "limit": 10,
            },
        ),
        # User question:
        # "Find high-tier partners in the United States with strong
        # capabilities in AI."
        (
            "search_partners",
            {
                "headquarters_country": "United States",
                "capability": "Artificial Intelligence",
                "partner_tier": "Gold",
                "status": "Active",
                "limit": 10,
            },
        ),
        # # User question:
        # # "Give me the complete profile of partner P001."
        # (
        #     "get_partner_profile",
        #     {
        #         "partner_id": "P001",
        #     },
        # ),
        # # =====================================================================
        # # MARKET INTELLIGENCE
        # # =====================================================================
        # # User question:
        # # "Which regions are growing fastest?"
        # (
        #     "search_markets",
        #     {
        #         "analysis_year": 2026,
        #         "min_growth_rate_pct": 10,
        #         "limit": 10,
        #     },
        # ),
        # # User question:
        # # "Which technologies are gaining momentum?"
        # (
        #     "search_markets",
        #     {
        #         "analysis_year": 2026,
        #         "technology": "Generative AI",
        #         "min_growth_rate_pct": 10,
        #         "limit": 10,
        #     },
        # ),
        # # User question:
        # # "Which opportunities are underserved in North America?"
        # (
        #     "search_markets",
        #     {
        #         "analysis_year": 2026,
        #         "region": "North America",
        #         "market_status": "Underserved",
        #         "limit": 10,
        #     },
        # ),
        # # User question:
        # # "Show me fast-growing technology markets in North America."
        # (
        #     "search_markets",
        #     {
        #         "analysis_year": 2026,
        #         "region": "North America",
        #         "min_growth_rate_pct": 10,
        #         "limit": 10,
        #     },
        # ),
        # # User question:
        # # "Give me detailed intelligence for market M001."
        # (
        #     "get_market_intelligence",
        #     {
        #         "market_id": "M001",
        #         "analysis_year": 2026,
        #     },
        # ),
        # # User question:
        # # "Compare the two most important markets and show which one
        # # has better growth potential."
        # (
        #     "compare_markets",
        #     {
        #         "market_ids": [
        #             "M001",
        #             "M002",
        #         ],
        #         "analysis_year": 2026,
        #     },
        # ),
        # =====================================================================
        # EVENTS & MATCHMAKING
        # =====================================================================
        # User question:
        # "Which events should we prioritize in North America?"
        (
            "search_events",
            {
                "region": "North America",
                # "analysis_year": 2026,
                "limit": 10,
            },
        ),
        # User question:
        # "Which technology events have the strongest partner opportunity?"
        (
            "search_events",
            {
                "industry": "Technology",
                "min_expected_attendees": 100,
                # "analysis_year": 2026,
                "limit": 10,
            },
        ),
        # User question:
        # "Who is attending event E001?"
        (
            "get_event_participants",
            {
                "event_id": "E001",
            },
        ),
        # User question:
        # "Which partners are the best matches for market M001?"
        (
            "find_partner_matches",
            {
                "market_id": "M001",
                "min_match_score": 70,
                "match_status": "Recommended",
                "limit": 10,
            },
        ),
        # # User question:
        # # "Find strong partner matches for Generative AI in North America."
        # (
        #     "find_partner_matches",
        #     {
        #         "region": "North America",
        #         "technology": "Generative AI",
        #         "min_match_score": 75,
        #         "limit": 10,
        #     },
        # ),
        # User question:
        # "Which partners have strong capability and geographic fit for
        # this market?"
        (
            "find_partner_matches",
            {
                "market_id": "M001",
                "min_match_score": 75,
                "limit": 10,
            },
        ),
        # User question:
        # "Why was match MM001 recommended?"
        (
            "explain_partner_match",
            {
                "match_id": "MM001",
            },
        ),
        # # User question:
        # # "Why is partner P001 a good match for market M001?"
        # (
        #     "explain_partner_match",
        #     {
        #         "partner_id": "P001",
        #         "market_id": "M001",
        #     },
        # ),
        # =====================================================================
        # GTM OPTIMIZATION
        # =====================================================================
        # User question:
        # "Which GTM opportunities should we prioritize?"
        (
            "search_gtm_opportunities",
            {
                "analysis_year": 2026,
                "priority": "High",
                "min_win_probability": 60,
                "min_opportunity_value": 10000000,
                "opportunity_status": "Open",
                "limit": 10,
            },
        ),
        # User question:
        # "Which opportunities have high market growth and strong partner fit?"
        (
            "search_gtm_opportunities",
            {
                "analysis_year": 2026,
                "min_opportunity_value": 10000000,
                "min_win_probability": 60,
                "limit": 10,
            },
        ),
        # User question:
        # "Which GTM opportunities should we pursue for Generative AI?"
        (
            "search_gtm_opportunities",
            {
                "analysis_year": 2026,
                "technology": "Generative AI",
                "min_win_probability": 50,
                "min_opportunity_value": 5000000,
                "limit": 10,
            },
        ),
        # # User question:
        # # "Which opportunities in North America have high partner fit
        # # and low competitive intensity?"
        # (
        #     "search_gtm_opportunities",
        #     {
        #         "analysis_year": 2026,
        #         "region": "North America",
        #         "min_win_probability": 60,
        #         "limit": 10,
        #     },
        # ),
        # User question:
        # "What GTM recommendations do we have for market M001?"
        (
            "get_gtm_recommendations",
            {
                "market_id": "M001",
                "min_recommendation_score": 70,
                "status": "Active",
                "limit": 10,
            },
        ),
        # User question:
        # "What GTM actions should we take for our technology partners?"
        (
            "get_gtm_recommendations",
            {
                "industry": "Technology",
                "min_recommendation_score": 70,
                "limit": 10,
            },
        ),
        # User question:
        # "Which GTM recommendations have the highest expected impact?"
        (
            "get_gtm_recommendations",
            {
                "min_recommendation_score": 80,
                "status": "Active",
                "limit": 10,
            },
        ),
    ]

    # -------------------------------------------------------------------------
    # EXECUTE TESTS
    # -------------------------------------------------------------------------

    print("\n" + "=" * 100)
    print("RUNNING BUSINESS TEST CASES")
    print("=" * 100)

    passed = 0
    failed = 0

    for index, (tool_name, arguments) in enumerate(tests, start=1):

        print("\n")
        print("=" * 100)
        print(f"TEST {index}/{len(tests)}")
        print(f"TOOL: {tool_name}")
        print(f"ARGUMENTS: {arguments}")
        print("=" * 100)

        try:
            result = await client.call_tool(
                tool_name,
                arguments,
            )
            print("\nRESULT:")
            print(result)
            if result.is_error == False:
                passed += 1
            else:
                failed += 1
                print("\nSTATUS: FAILED")
                print(f"ERROR TYPE: {type(result.error).__name__}")
                print(f"ERROR: {result.error}")

            print("\nSTATUS: PASSED")

        except Exception as exc:
            failed += 1

            print("\nSTATUS: FAILED")
            print(f"ERROR TYPE: {type(exc).__name__}")
            print(f"ERROR: {exc}")

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------

    print("\n")
    print("=" * 100)
    print("TEST SUMMARY")
    print("=" * 100)

    print(f"Total tests : {len(tests)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")

    if failed == 0:
        print("\nALL MCP BUSINESS TESTS PASSED")
    else:
        print("\nSOME MCP BUSINESS TESTS FAILED")

    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())
