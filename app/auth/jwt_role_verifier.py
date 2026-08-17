"""
Replaces role_middleware.py entirely. Uses the mcp SDK's built-in bearer
auth support instead of custom ASGI middleware — pass this to
MCPServer(token_verifier=JWTRoleVerifier()) and the SDK handles header
extraction, wiring, and exposing the result to tools via get_access_token().
"""

from __future__ import annotations

import os

import jwt
from dotenv import load_dotenv
from mcp.server.auth.provider import AccessToken, TokenVerifier

load_dotenv()

JWT_SECRET = os.environ["JWT_SECRET"]  # same value login_api.py/chat_app.py sign with
JWT_ALGORITHM = "HS256"


class JWTRoleVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.InvalidTokenError:
            return (
                None  # invalid/expired -> SDK treats as unauthenticated, fails closed
            )

        roles = payload.get("roles", [])
        return AccessToken(
            token=token,
            client_id=payload.get("user_id", "unknown"),
            scopes=roles,  # <- roles reused as OAuth-style scopes
            expires_at=payload.get("exp"),
        )
