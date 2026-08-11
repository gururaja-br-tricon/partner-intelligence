import os

from mcp.server import MCPServer

from app.repository.partner_repository import PartnerRepository
from app.repository.snowflake_partner_repository import SnowflakePartnerRepository
from app.rag.context import RAGContextBuilder

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "generated")

# repository = PartnerRepository(DATA_DIR)
repository = SnowflakePartnerRepository()
rag_context_builder = RAGContextBuilder()
mcp = MCPServer("partner-intelligence")


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
) -> list[dict]:
    """
    Search structured partner data from Snowflake.

    SOURCE:
        snowflake

    USE THIS TOOL WHEN:
        The user asks for structured partner attributes,
        capabilities, programs, classifications, status,
        location, industry, tier, etc.

    """

    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "search_partners",
        "data": repository.search_partners(
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
    return {
        "source": "snowflake",
        "source_type": "structured",
        "tool": "get_partner_profile",
        "data": repository.get_partner_profile(partner_id),
    }


@mcp.tool()
def search_partner_documents( query: str,partner_id: str | None = None,top_k: int = 5,) -> dict:
    """
    Search partner PDF documents using semantic search.

    SOURCE:
        pinecone

    Use this tool to retrieve information from
    partner documents and unstructured document content.
    """

    return {
        "source": "pinecone",
        "source_type": "unstructured",
        "tool": "search_partner_documents",
        "data": rag_context_builder.build_context(
            query=query,
            top_k=top_k,
            partner_id=partner_id,
        ),
    }


if __name__ == "__main__":
    mcp.run()