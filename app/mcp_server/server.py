import os

from mcp.server import MCPServer
from mcp.server.auth.settings import AuthSettings


from app.auth.jwt_role_verifier import JWTRoleVerifier
from app.auth.domains import Domain
from app.auth.check_domain import check_domain
from app.repository.snowflake_partner_repository import SnowflakePartnerRepository
from app.repository.snowflake_market_repository import SnowflakeMarketRepository
from app.repository.snowflake_event_repository import SnowflakeEventRepository
from app.repository.snowflake_gtm_repository import SnowflakeGTMRepository
from app.rag.context import RAGContextBuilder

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "generated")

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


# ============================================================================
# PARTNER DOMAIN TOOLS (consolidated from 3 → 2)
# ============================================================================

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
    # NEW: Performance/growth filters (consolidated from search_partner_growth)
    min_revenue_growth_pct: float | None = None,
    min_pipeline_growth_pct: float | None = None,
    min_health_score: float | None = None,
    performance_status: str | None = None,
    performance_year: int | None = None,
) -> dict:
    """
    Search partners with optional growth/performance filtering.

    SOURCE:
        snowflake

    USE THIS TOOL WHEN:
        The user asks for structured partner attributes,
        capabilities, programs, classifications, status,
        location, industry, tier, growth metrics,
        health scores, or performance trends.

    FILTERS (Basic Partner Attributes):
        headquarters_state, headquarters_country, industry, status,
        capability, proficiency_level, vendor, program_name,
        partner_tier, classification

    FILTERS (Performance & Growth - NEW):
        min_revenue_growth_pct: Minimum revenue growth percentage
        min_pipeline_growth_pct: Minimum pipeline growth percentage
        min_health_score: Minimum partner health score
        performance_status: Filter by Growing, Stable, or Declining
        performance_year: Specific year of performance data

    EXAMPLES:
        - "Find growing partners in tech" 
          → industry="tech", min_revenue_growth_pct=10
        - "Which partners have strong health scores?"
          → min_health_score=80
        - "Top performing partners in 2026"
          → performance_year=2026, min_revenue_growth_pct=15
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
            min_revenue_growth_pct=min_revenue_growth_pct,
            min_pipeline_growth_pct=min_pipeline_growth_pct,
            min_health_score=min_health_score,
            performance_status=performance_status,
            performance_year=performance_year,
        ),
    }


@mcp.tool()
def get_partner_profile(partner_id: str) -> dict | None:
    """
    Get a complete structured profile for a partner from Snowflake.

    SOURCE:
        snowflake

    RETURNS:
        Partner master data, capabilities, programs, classifications,
        and full performance history.

    USE THIS WHEN:
        User needs complete partner context for a specific partner ID.
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

    USE THIS TOOL WHEN:
        You need information from partner documents and unstructured
        document content (case studies, whitepapers, contracts, etc).

    FILTERS:
        query: Semantic search query for document content
        partner_id: Restrict search to specific partner (optional)
        top_k: Number of results to return (default 5)
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


# ============================================================================
# MARKET DOMAIN TOOLS (consolidated from 2 → 1)
# ============================================================================

@mcp.tool()
def search_markets(
    market_name: str | None = None,
    market_category: str | None = None,
    region: str | None = None,
    technology: str | None = None,
    # NEW: Intelligence filters (consolidated from get_market_intelligence)
    market_id: str | None = None,
    country: str | None = None,
    industry: str | None = None,
    analysis_year: int | None = None,
    demand_level: str | None = None,
    growth_level: str | None = None,
    include_intelligence: bool = False,
) -> dict:
    """
    Search market definitions with optional intelligence data.

    SOURCE:
        snowflake

    

    USE THIS TOOL WHEN:
        - User asks about available markets, market definitions, categories
        - User wants market size, growth, TAM/SAM/SOM, demand, adoption
        - User needs competitive analysis, partner counts, opportunity counts

    FILTERS (Market Definition):
        market_name, market_category, region, technology

    FILTERS (Intelligence & Analytics - NEW):
        market_id: Specific market to analyze
        country: Country-specific analysis
        industry: Industry vertical
        analysis_year: Year for historical comparison
        demand_level: Low, Medium, High
        growth_level: Low, Medium, High
        include_intelligence: Set True to get size/growth/TAM metrics

    EXAMPLES:
        - "What markets exist in the cloud space?"
          → technology="Cloud"
        - "Which markets are growing fastest in EMEA?"
          → region="EMEA", include_intelligence=True
        - "Market size and TAM for AI opportunities"
          → technology="AI", include_intelligence=True, analysis_year=2026
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
            market_id=market_id,
            country=country,
            industry=industry,
            analysis_year=analysis_year,
            demand_level=demand_level,
            growth_level=growth_level,
            include_intelligence=include_intelligence,
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
    Compare multiple markets side-by-side using intelligence metrics.

    SOURCE:
        snowflake

    USE THIS TOOL WHEN:
        User needs to compare 2+ markets on metrics like size,
        growth, TAM, demand, adoption, competitive intensity.

    FILTERS:
        market_ids: List of market IDs to compare (required)
        region, industry, technology, analysis_year: Context filters

    RETURNS:
        Side-by-side comparison with all intelligence metrics.

    EXAMPLES:
        - "Compare markets M1, M2, M3 by growth rate"
          → market_ids=["M1", "M2", "M3"]
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


# ============================================================================
# EVENT DOMAIN TOOLS (consolidated from 3 → 2, removed explain_partner_match)
# ============================================================================

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
    # NEW: Participant filters (consolidated from get_event_participants)
    participant_type: str | None = None,
    include_participants: bool = False,
) -> dict:
    """
    Search events with optional participant/attendance data.

    SOURCE:
        snowflake

    

    USE THIS TOOL WHEN:
        - User asks about events, conferences, meetings, webinars
        - User wants to know which partners attended an event
        - User needs event participation, meetings, leads generated
        - User wants event engagement metrics

    FILTERS (Event Attributes):
        event_name, event_type, region, country, city, industry,
        market_name, technology, event_status, event_date, event_end_date

    FILTERS (Participation - NEW):
        participant_type: Sponsor, Exhibitor, Attendee, Speaker, etc
        include_participants: Set True to get attendance details

    RETURNS:
        Event details with optional participant metrics (booth,
        meetings, leads, engagement score).

    EXAMPLES:
        - "Upcoming tech conferences in EMEA"
          → technology="Tech", region="EMEA", event_status="Upcoming"
        - "Which partners sponsored the conference?"
          → event_type="Conference", participant_type="Sponsor",
            include_participants=True
        - "Events with high engagement in our target markets"
          → include_participants=True
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
            participant_type=participant_type,
            include_participants=include_participants,
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
    match_id: str | None = None,
) -> dict:
    """
    Find partner-to-market matches with scoring breakdown.

    SOURCE:
        snowflake

    

    USE THIS TOOL WHEN:
        - User asks which partners fit a market well
        - User wants to understand match scoring factors
        - User needs capability, geographic, industry fit scores
        - User asks "why is this partner a good match?"

    FILTERS:
        partner_id: Specific partner to match
        market_id: Specific market to evaluate
        region, industry, technology: Context filters
        min_match_score: Minimum overall fit (0-100)
        match_status: Active, Inactive, etc
        match_id: Specific match record

    RETURNS:
        Match scores (capability, geographic, industry, growth, health),
        overall score, recommendation, and status.

    NOTE:
        Old explain_partner_match is removed. This tool already returns
        all scoring details. The LLM can filter to one record if needed.

    EXAMPLES:
        - "Which partners fit market M1?"
          → market_id="M1"
        - "Why is P123 a good fit for tech opportunities?"
          → partner_id="P123", technology="Tech"
        - "Partners with score > 80"
          → min_match_score=80
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
            match_id=match_id,
        ),
    }


# ============================================================================
# GTM DOMAIN TOOLS (consolidated from 2 → 1)
# ============================================================================

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
    # NEW: Recommendation filters (consolidated from get_gtm_recommendations)
    recommendation_type: str | None = None,
    recommendation_status: str | None = None,
    min_recommendation_score: int | None = None,
    include_recommendations: bool = False,
) -> dict:
    """
    Search GTM opportunities with optional recommendation/action data.

    SOURCE:
        snowflake

    

    USE THIS TOOL WHEN:
        - User asks about opportunities, revenue potential, market fit
        - User wants recommended GTM actions, priorities, tactics
        - User needs win probability, competitive context
        - User asks "what should we do about this opportunity?"

    FILTERS (Opportunity Attributes):
        partner_id, market_id, region, industry, technology,
        opportunity_type, priority, opportunity_status, analysis_year,
        min_opportunity_value, min_win_probability

    FILTERS (Recommendations - NEW):
        recommendation_type: Expansion, Retention, Upsell, etc
        recommendation_status: Pending, Active, Completed
        min_recommendation_score: Quality threshold (0-100)
        include_recommendations: Set True to get action/impact data

    RETURNS:
        Opportunity value, growth, fit, win probability, and optional
        recommendation details (rationale, expected impact, timeframe).

    EXAMPLES:
        - "High-priority opportunities for partner P123"
          → partner_id="P123", priority="High"
        - "Where should we focus expansion?"
          → include_recommendations=True, recommendation_type="Expansion"
        - "Opportunities > $1M with expansion recommendations"
          → min_opportunity_value=1000000, include_recommendations=True
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
            recommendation_type=recommendation_type,
            recommendation_status=recommendation_status,
            min_recommendation_score=min_recommendation_score,
            include_recommendations=include_recommendations,
        ),
    }


if __name__ == "__main__":
    mcp.run()