"""
Replaces the custom @require_domain decorator. One function, called as
the first line of each tool body — no decorator machinery.

    from app.auth.check_domain import check_domain

    @mcp.tool()
    def search_partners(...) -> dict:
        denied = check_domain("partner")
        if denied:
            return denied
        ...
"""

from mcp.server.auth.middleware.auth_context import get_access_token

from app.auth.domains import Domain, VALID_DOMAINS


def check_domain(domain: str) -> dict | None:
    """Returns a denial dict if the caller lacks `domain`, else None.

    `domain` should be a Domain enum value (Domain.PARTNER.value or just
    "partner" — same thing at runtime). Passing an unrecognized string
    raises immediately rather than silently always-denying, since that
    kind of bug is much easier to catch at call time than by noticing
    every request to a tool mysteriously gets rejected.
    """
    if domain not in VALID_DOMAINS:
        raise ValueError(
            f"check_domain() called with unknown domain '{domain}'. Valid: {sorted(VALID_DOMAINS)}"
        )

    token = get_access_token()
    if token is None or domain not in token.scopes:
        return {
            "error": "permission_denied",
            "message": "You don't have access to this information.",
        }
    return None
