import os

from mcp.server import MCPServer

from app.repository.partner_repository import PartnerRepository
from app.repository.snowflake_partner_repository import SnowflakePartnerRepository


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "generated")

# repository = PartnerRepository(DATA_DIR)
repository = SnowflakePartnerRepository()
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
    Search partner organizations using company attributes,
    capabilities, partner programs, and classifications.
    """

    return repository.search_partners(
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
    )


@mcp.tool()
def get_partner_profile(partner_id: str) -> dict | None:
    """
    Get a complete structured profile for a partner,
    including company attributes, capabilities,
    partner programs, and classifications.
    """

    return repository.get_partner_profile(partner_id)


if __name__ == "__main__":
    mcp.run()
