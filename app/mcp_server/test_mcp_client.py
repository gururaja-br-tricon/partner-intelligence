import asyncio

from app.mcp_server.client import MCPClient


async def main():
    client = MCPClient()

    await client.connect()
    
    tools = await client.list_tools()

    print("\n" + "=" * 100)
    tests = [
        ("search_partners", {"headquarters_state": "California", "industry": "Technology", "status": "Active", "capability": "Cloud", "limit": 10}),
        ("get_partner_profile", {"partner_id": "P001"}),
        ("search_partner_documents", {"query": "cloud security", "partner_id": None, "top_k": 3}),
        ("search_partner_growth", {"performance_year": 2026, "min_revenue_growth_pct": 10, "min_pipeline_growth_pct": 15, "min_health_score": 75, "performance_status": "Growing", "limit": 10}),
        ("search_markets", {"region": "North America", "technology": "Generative AI", "limit": 10}),
        ("get_market_intelligence", {"market_id": "M001", "analysis_year": 2026, "limit": 10}),
        ("compare_markets", {"market_ids": ["M001", "M002"], "analysis_year": 2026}),
        ("search_events", {"region": "North America", "limit": 10}),
        ("get_event_participants", {"event_id": "E001", "limit": 100}),
        ("find_partner_matches", {"market_id": "M001", "min_match_score": 70, "match_status": "Recommended", "limit": 10}),
        ("explain_partner_match", {"match_id": "MM001"}),
        ("search_gtm_opportunities", {"analysis_year": 2026, "priority": "High", "min_win_probability": 60, "min_opportunity_value": 10000000, "opportunity_status": "Open", "limit": 10}),
        ("get_gtm_recommendations", {"market_id": "M001", "min_recommendation_score": 70, "status": "Active", "limit": 10}),
        # ("get_gtm_recommendations", {"industry": "Technology", "min_recommendation_score": 70, "limit": 10},),
        # ("get_gtm_recommendations", {"min_recommendation_score": 80, "status": "Active", "limit": 10}),
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
        # print(f"ARGUMENTS: {arguments}")
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
