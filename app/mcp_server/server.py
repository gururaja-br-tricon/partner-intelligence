import os

from mcp.server import MCPServer
from mcp.server.auth.settings import AuthSettings


from app.auth.jwt_role_verifier import JWTRoleVerifier
from app.auth.domains import Domain
from app.auth.check_domain import check_domain
from app.repository.partner_repository import PartnerRepository
from app.repository.snowflake_partner_repository import SnowflakePartnerRepository
from app.repository.snowflake_market_repository import SnowflakeMarketRepository
from app.repository.snowflake_event_repository import SnowflakeEventRepository
from app.repository.snowflake_gtm_repository import SnowflakeGTMRepository
from app.rag.context import RAGContextBuilder

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "generated")

# repository = PartnerRepository(DATA_DIR)
partner_repository = SnowflakePartnerRepository()
market_repository = SnowflakeMarketRepository()
event_repository = SnowflakeEventRepository()
gtm_repository = SnowflakeGTMRepository()

rag_context_builder = RAGContextBuilder()

mcp = MCPServer(
    "partner-intelligence",
    token_verifier=JWTRoleVerifier(),
    auth=AuthSettings(
        # Not a real OAuth issuer — we sign our own JWTs in login_api.py/
        # chat_app.py and verify them ourselves in JWTRoleVerifier. Both
        # URLs are only used for SDK metadata/discovery, required by the
        # SDK's pydantic model even though unused in our flow.
        issuer_url=os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000"),
        resource_server_url=os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000")
        + "/mcp",
    ),
)


@mcp.tool()
def search_partners(
    headquarters_state: str | None = None,
    headquarters_country: str | None = None,
    industry: str | None = None,
    status: str | None = None,
    capability: str | None = None,
    proficiency_level: str | None = None,
    vendor: str | None = None,
    program_name: str | None = None,
    partner_tier: str | None = None,
    classification: str | None = None,
) -> dict:
    """
    Search structured partner data from Snowflake.

    SOURCE:
        snowflake

    USE THIS TOOL WHEN:
        The user asks for structured partner attributes,
        capabilities, programs, classifications, status,
        location, industry, tier, etc.

    """

    denied = check_domain(Domain.PARTNER)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "search_partners",
        "data": partner_repository.search_partners(
            headquarters_state=headquarters_state,
            headquarters_country=headquarters_country,
            industry=industry,
            status=status,
            capability=capability,
            proficiency_level=proficiency_level,
            vendor=vendor,
            program_name=program_name,
            partner_tier=partner_tier,
            classification=classification,
        ),
    }


@mcp.tool()
def get_partner_profile(partner_id: str) -> dict | None:
    """
    Get a complete structured profile for a partner from Snowflake.

    SOURCE:
        snowflake

    Use this tool for structured partner information.
    """
    denied = check_domain(Domain.PARTNER)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "get_partner_profile",
        "data": partner_repository.get_partner_profile(partner_id),
    }


@mcp.tool()
def search_partner_documents(
    query: str,
    partner_id: str | None = None,
    top_k: int = 5,
) -> dict:
    """
    Search partner PDF documents using semantic search.

    SOURCE:
        pinecone(RAG)

    Use this tool to retrieve information from
    partner documents and unstructured document content.
    """

    denied = check_domain(Domain.PARTNER)
    if denied:
        return denied

    return {
        "source": "pinecone(RAG)",
        "source_type": "unstructured",
        "tool": "search_partner_documents",
        "data": rag_context_builder.build_context(
            query=query,
            top_k=top_k,
            partner_id=partner_id,
        ),
    }


@mcp.tool()
def search_partner_growth(
    min_revenue_growth_pct: float | None = None,
    min_pipeline_growth_pct: float | None = None,
    min_health_score: float | None = None,
    performance_status: str | None = None,
    performance_year: int | None = None,
    limit: int = 10,
) -> dict:
    """
    Search structured partner growth and performance data from Snowflake.

    SOURCE:
        snowflake.PARTNER_PERFORMANCE

    USE THIS TOOL WHEN:
        The user asks about partner growth, partner performance,
        growth trends, revenue growth, pipeline growth, partner
        health, business momentum, or identifying high-growth partners.

    THIS TOOL CAN ANSWER QUESTIONS SUCH AS:
        - Which partners are growing fastest?
        - Which partners have the highest revenue growth?
        - Which partners have strong pipeline growth?
        - Which partners have strong revenue and pipeline growth?
        - Which partners are declining?
        - Which partners have a high partner health score?
        - Which partners are showing strong growth in 2026?
        - Which partners have both revenue growth and pipeline growth?

    FILTERS:
        min_revenue_growth_pct:
            Minimum revenue growth percentage.

        min_pipeline_growth_pct:
            Minimum pipeline growth percentage.

        min_health_score:
            Minimum partner health score.

        performance_status:
            Filter by performance status, such as Growing,
            Stable, or Declining.

        performance_year:
            Filter results to a specific performance year.

        limit:
            Maximum number of results to return.

    IMPORTANT:
        This tool returns structured performance data.
        Use the returned metrics to compare and rank partners.
        Do not treat the tool as a predictive model unless
        predictive data or a prediction score is explicitly provided.
    """

    denied = check_domain(Domain.PARTNER)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "search_partner_growth",
        "data": partner_repository.search_partner_growth(
            min_revenue_growth_pct=min_revenue_growth_pct,
            min_pipeline_growth_pct=min_pipeline_growth_pct,
            min_health_score=min_health_score,
            performance_status=performance_status,
            performance_year=performance_year,
            limit=limit,
        ),
    }


@mcp.tool()
def search_markets(
    market_name: str | None = None,
    market_category: str | None = None,
    region: str | None = None,
    technology: str | None = None,
    limit: int = 100,
) -> dict:
    """
    Search the available market definitions.

    SOURCE:
        snowflake

    SOURCE_TYPE:
        structured

    USE THIS TOOL WHEN:
        The user asks what markets are available,
        what market categories exist,
        which markets cover a particular region,
        or which markets are associated with a technology.

    RETURNS:
        Stable market definitions such as market name,
        category, technologies, priority, and target regions.

    NOTE:
        Use get_market_intelligence for market size,
        growth, demand, adoption, TAM, SAM, SOM, or
        other analytical metrics.
    """

    denied = check_domain(Domain.MARKET)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "search_markets",
        "data": market_repository.search_markets(
            market_name=market_name,
            market_category=market_category,
            region=region,
            technology=technology,
            limit=limit,
        ),
    }


@mcp.tool()
def get_market_intelligence(
    market_id: str | None = None,
    region: str | None = None,
    country: str | None = None,
    industry: str | None = None,
    technology: str | None = None,
    analysis_year: int | None = None,
    demand_level: str | None = None,
    growth_level: str | None = None,
    limit: int = 100,
) -> dict:
    """
    Retrieve analytical market intelligence from Snowflake.

    SOURCE:
        snowflake

    SOURCE_TYPE:
        structured

    USE THIS TOOL WHEN:
        The user asks about market size, market growth,
        TAM, SAM, SOM, demand, technology adoption,
        competitive intensity, active partners, or
        market opportunities.

    RETURNS:
        Structured market intelligence records that can
        be used to compare markets and identify attractive
        market opportunities.
    """

    denied = check_domain(Domain.MARKET)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "get_market_intelligence",
        "data": market_repository.get_market_intelligence(
            market_id=market_id,
            region=region,
            country=country,
            industry=industry,
            technology=technology,
            analysis_year=analysis_year,
            demand_level=demand_level,
            growth_level=growth_level,
            limit=limit,
        ),
    }


@mcp.tool()
def compare_markets(
    market_ids: list[str],
    region: str | None = None,
    industry: str | None = None,
    technology: str | None = None,
    analysis_year: int | None = None,
) -> dict:
    """
    Compare multiple markets using structured market intelligence.

    SOURCE:
        snowflake

    SOURCE_TYPE:
        structured

    USE THIS TOOL WHEN:
        The user explicitly compares two or more markets,
        or asks which of several markets is more attractive.

    EXAMPLES:
        - Compare Cybersecurity and Generative AI.
        - Which market has higher growth?
        - Compare market demand in North America.
        - Compare TAM and competitive intensity.

    RETURNS:
        Comparable market metrics including market size,
        growth, TAM, SAM, SOM, demand, adoption,
        competition, partner count, and opportunity count.
    """

    denied = check_domain(Domain.MARKET)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "compare_markets",
        "data": market_repository.compare_markets(
            market_ids=market_ids,
            region=region,
            industry=industry,
            technology=technology,
            analysis_year=analysis_year,
        ),
    }


@mcp.tool()
def search_events(
    event_name: str | None = None,
    event_type: str | None = None,
    region: str | None = None,
    country: str | None = None,
    city: str | None = None,
    industry: str | None = None,
    market_name: str | None = None,
    technology: str | None = None,
    event_status: str | None = None,
    event_date: str | None = None,
    event_end_date: str | None = None,
    limit: int = 100,
) -> dict:
    """
    Search structured event data from Snowflake.

    SOURCE:
        snowflake

    SOURCE_TYPE:
        structured

    USE THIS TOOL WHEN:
        The user asks about events, conferences,
        partner events, industry events, technology events,
        event locations, upcoming events, or event objectives.

    FILTERS:
        Event name, event type, region, country, industry,
        technology, event status, and date range.

    RETURNS:
        Event details including location, dates, target
        partners, expected attendees, technologies,
        and event objectives.
    """

    denied = check_domain(Domain.EVENT)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "search_events",
        "data": event_repository.search_events(
            event_name=event_name,
            event_type=event_type,
            region=region,
            country=country,
            city=city,
            industry=industry,
            market_name=market_name,
            technology=technology,
            event_status=event_status,
            event_date=event_date,
            event_end_date=event_end_date,
            limit=limit,
        ),
    }


@mcp.tool()
def get_event_participants(
    event_id: str | None = None,
    partner_id: str | None = None,
    participation_type: str | None = None,
    limit: int = 100,
) -> dict:
    """
    Retrieve structured event participation data from Snowflake.

    SOURCE:
        snowflake

    SOURCE_TYPE:
        structured

    USE THIS TOOL WHEN:
        The user asks which partners attended an event,
        whether a partner participated in an event,
        event participation status, meetings, opportunities,
        pipeline generated, or event follow-up activity.

    FILTERS:
        Event, partner, participant type, and participation
        status.

    RETURNS:
        Event participation details including partners,
        attendance, meetings, opportunities, pipeline,
        and follow-up requirements.
    """

    denied = check_domain(Domain.EVENT)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "get_event_participants",
        "data": event_repository.get_event_participants(
            event_id=event_id,
            partner_id=partner_id,
            participation_type=participation_type,
            limit=limit,
        ),
    }


@mcp.tool()
def find_partner_matches(
    partner_id: str | None = None,
    market_id: str | None = None,
    region: str | None = None,
    industry: str | None = None,
    technology: str | None = None,
    min_match_score: int | None = None,
    match_status: str | None = None,
    limit: int = 100,
) -> dict:
    """
    Find partner-to-market matches from Snowflake.

    SOURCE:
        snowflake

    SOURCE_TYPE:
        structured

    USE THIS TOOL WHEN:
        The user asks which partners are a good fit for
        a market, region, industry, or technology.

    FILTERS:
        Partner, market, region, industry, technology,
        minimum match score, and match status.

    RETURNS:
        Match scores and the factors contributing to the
        partner-market fit, including capability fit,
        geographic fit, industry fit, growth momentum,
        partner health, overall match score, and recommendation.
    """

    denied = check_domain(Domain.EVENT)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "find_partner_matches",
        "data": event_repository.find_partner_matches(
            partner_id=partner_id,
            market_id=market_id,
            region=region,
            industry=industry,
            technology=technology,
            min_match_score=min_match_score,
            match_status=match_status,
            limit=limit,
        ),
    }


@mcp.tool()
def explain_partner_match(
    match_id: str | None = None,
    partner_id: str | None = None,
    market_id: str | None = None,
) -> dict:
    """
    Explain why a partner is a good match for a market.

    SOURCE:
        snowflake

    SOURCE_TYPE:
        structured

    USE THIS TOOL WHEN:
        The user asks why a partner was recommended,
        why a partner matches a market, or what factors
        contributed to the match score.

    RETURNS:
        The individual fit scores, overall match score,
        recommendation, and match status.
    """

    denied = check_domain(Domain.EVENT)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "explain_partner_match",
        "data": event_repository.explain_partner_match(
            match_id=match_id,
            partner_id=partner_id,
            market_id=market_id,
        ),
    }


@mcp.tool()
def search_gtm_opportunities(
    partner_id: str | None = None,
    market_id: str | None = None,
    region: str | None = None,
    industry: str | None = None,
    technology: str | None = None,
    opportunity_type: str | None = None,
    priority: str | None = None,
    opportunity_status: str | None = None,
    analysis_year: int | None = None,
    min_opportunity_value: int | None = None,
    min_win_probability: int | None = None,
    limit: int = 100,
) -> dict:
    """
    Search structured GTM opportunities from Snowflake.

    SOURCE:
        snowflake

    SOURCE_TYPE:
        structured

    USE THIS TOOL WHEN:
        The user asks about GTM opportunities,
        revenue opportunities, expansion opportunities,
        market opportunities, partner opportunities,
        or which opportunities should be pursued.

    FILTERS:
        Partner, market, region, industry, technology,
        opportunity type, priority, status, analysis year,
        opportunity value, and win probability.

    RETURNS:
        Opportunity value, market growth, demand growth,
        partner fit, competitive intensity, win probability,
        priority, recommended action, and opportunity status.
    """

    denied = check_domain(Domain.GTM)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "search_gtm_opportunities",
        "data": gtm_repository.search_gtm_opportunities(
            partner_id=partner_id,
            market_id=market_id,
            region=region,
            industry=industry,
            technology=technology,
            opportunity_type=opportunity_type,
            priority=priority,
            opportunity_status=opportunity_status,
            analysis_year=analysis_year,
            min_opportunity_value=min_opportunity_value,
            min_win_probability=min_win_probability,
            limit=limit,
        ),
    }


@mcp.tool()
def get_gtm_recommendations(
    partner_id: str | None = None,
    market_id: str | None = None,
    region: str | None = None,
    industry: str | None = None,
    technology: str | None = None,
    recommendation_type: str | None = None,
    status: str | None = None,
    min_recommendation_score: int | None = None,
    limit: int = 100,
) -> dict:
    """
    Retrieve structured GTM recommendations from Snowflake.

    SOURCE:
        snowflake

    SOURCE_TYPE:
        structured

    USE THIS TOOL WHEN:
        The user asks what GTM action should be taken,
        which markets or partners should be prioritized,
        what actions are recommended, or what the expected
        business impact is.

    FILTERS:
        Partner, market, region, industry, technology,
        recommendation type, status, and recommendation score.

    RETURNS:
        Recommendation score, rationale, expected impact,
        recommended timeframe, and recommendation status.
    """

    denied = check_domain(Domain.GTM)
    if denied:
        return denied

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "get_gtm_recommendations",
        "data": gtm_repository.get_gtm_recommendations(
            partner_id=partner_id,
            market_id=market_id,
            region=region,
            industry=industry,
            technology=technology,
            recommendation_type=recommendation_type,
            status=status,
            min_recommendation_score=min_recommendation_score,
            limit=limit,
        ),
    }


if __name__ == "__main__":
    mcp.run()
