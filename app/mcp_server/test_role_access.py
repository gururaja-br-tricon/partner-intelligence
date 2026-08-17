"""
Standalone test — verifies check_domain() actually enforces role-based
access, independent of whether the agents/orchestrator are finished.

Usage:
    python test_role_access.py <email> <password>

Logs in as the given user, then attempts one tool call per domain
(partner, market, event, gtm) and prints whether each was allowed or
denied — compare that against what the user's actual roles in the
USERS table should permit.
"""

import asyncio
import sys

import bcrypt
import jwt as jwt_lib
from dotenv import load_dotenv

load_dotenv()

import datetime
import os

from app.agents.mcp_client import MCPClient
from app.auth.user_store import get_user_by_email

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
MCP_URL = os.environ.get("MCP_URL", "http://127.0.0.1:8000/mcp")

# One representative, cheap tool call per domain — doesn't matter if the
# arguments return real data, only whether check_domain() lets it through.
PROBE_CALLS = {
    "partner": ("search_partners", {}),
    "market": ("search_markets", {}),
    "event": ("search_events", {}),
    "gtm": ("search_gtm_opportunities", {}),
}


def issue_jwt(email: str, password: str) -> tuple[str, list[str]]:
    user = get_user_by_email(email)
    if user is None:
        raise SystemExit(f"No such user: {email}")
    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise SystemExit("Wrong password.")

    payload = {
        "user_id": user.user_id,
        "roles": sorted(user.roles),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    token = jwt_lib.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, sorted(user.roles)


async def probe(token: str, domain: str, tool_name: str, args: dict):
    async with MCPClient(MCP_URL, auth_token=token) as client:
        result = await client.call_tool(tool_name, args)
    denied = '"error": "permission_denied"' in result or "permission_denied" in result
    return domain, ("DENIED" if denied else "ALLOWED"), result[:150]


async def main():
    if len(sys.argv) != 3:
        print("Usage: python test_role_access.py <email> <password>")
        sys.exit(1)

    email, password = sys.argv[1], sys.argv[2]
    token, actual_roles = issue_jwt(email, password)

    print(f"Logged in as {email}")
    print(f"Roles in USERS table: {actual_roles}")
    print()
    print(f"{'Domain':<10} {'Expected':<10} {'Actual':<10} Result preview")
    print("-" * 70)

    for domain, (tool_name, args) in PROBE_CALLS.items():
        expected = "ALLOWED" if domain in actual_roles else "DENIED"
        try:
            _, actual, preview = await probe(token, domain, tool_name, args)
        except Exception as e:
            actual, preview = "ERROR", str(e)[:150]

        flag = "  <-- MISMATCH" if actual != expected else ""
        print(f"{domain:<10} {expected:<10} {actual:<10} {preview}{flag}")


if __name__ == "__main__":
    asyncio.run(main())