"""
User table + role storage — Snowflake-backed.

Uses a DEDICATED Snowflake role (AUTH_DOMAIN_ROLE / AUTH_SVC user, see
auth_role.sql) scoped only to USER_DATA.USERS. Deliberately NOT reusing
any of the 4 domain roles (PARTNER_DOMAIN_ROLE etc.) — those have no
business seeing auth data, and this connection has no business seeing
domain data. Same isolation principle as the domain repositories.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from dotenv import load_dotenv
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from app.auth.domains import VALID_DOMAINS

load_dotenv()


def _load_private_key():
    key_path = os.environ["SNOWFLAKE_AUTH_PRIVATE_KEY_PATH"]
    with open(key_path, "rb") as f:
        p_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )
    return p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


@contextmanager
def get_connection():
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_AUTH_USER"],
        private_key=_load_private_key(),
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="USER_DATA",
        role=os.environ["SNOWFLAKE_AUTH_ROLE"],  # AUTH_DOMAIN_ROLE
    )
    try:
        yield conn
    finally:
        conn.close()


@dataclass
class User:
    user_id: str
    email: str
    password_hash: str
    roles: frozenset[str]


def get_user_by_email(email: str) -> User | None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT USER_ID, EMAIL, PASSWORD_HASH, ROLES FROM USERS WHERE EMAIL = %s",
            (email,),
        )
        row = cur.fetchone()
    if row is None:
        return None
    user_id, email, password_hash, roles_str = row
    return User(
        user_id=user_id,
        email=email,
        password_hash=password_hash,
        roles=frozenset(roles_str.split(",")) if roles_str else frozenset(),
    )


def create_user(
    user_id: str, email: str, password_hash: str, roles: list[str], name: str = ""
) -> None:
    unknown = set(roles) - VALID_DOMAINS
    if unknown:
        raise ValueError(
            f"Unknown domain(s) in roles: {unknown}. Valid: {sorted(VALID_DOMAINS)}"
        )
    with get_connection() as conn:
        conn.cursor().execute(
            "INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, NAME, ROLES) VALUES (%s, %s, %s, %s, %s)",
            (user_id, email, password_hash, name, ",".join(roles)),
        )


def update_user_roles(user_id: str, roles: list[str]) -> None:
    unknown = set(roles) - VALID_DOMAINS
    if unknown:
        raise ValueError(
            f"Unknown domain(s) in roles: {unknown}. Valid: {sorted(VALID_DOMAINS)}"
        )
    with get_connection() as conn:
        conn.cursor().execute(
            "UPDATE USERS SET ROLES = %s WHERE USER_ID = %s",
            (",".join(roles), user_id),
        )


def update_user_password(user_id: str, new_password_hash: str) -> None:
    with get_connection() as conn:
        conn.cursor().execute(
            "UPDATE USERS SET PASSWORD_HASH = %s WHERE USER_ID = %s",
            (new_password_hash, user_id),
        )


def delete_user(user_id: str) -> None:
    # Note: this does NOT invalidate any JWT already issued to this user —
    # tokens remain valid (up to JWT_EXPIRY_HOURS) until they expire, since
    # verification only checks the signature, not current DB state. If
    # immediate revocation matters, that needs a separate mechanism
    # (e.g. a revocation list checked in JWTRoleVerifier) — not built yet.
    with get_connection() as conn:
        conn.cursor().execute("DELETE FROM USERS WHERE USER_ID = %s", (user_id,))


def list_all_users() -> list[User]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT USER_ID, EMAIL, PASSWORD_HASH, ROLES FROM USERS ORDER BY EMAIL")
        rows = cur.fetchall()
    return [
        User(
            user_id=r[0],
            email=r[1],
            password_hash=r[2],
            roles=frozenset(r[3].split(",")) if r[3] else frozenset(),
        )
        for r in rows
    ]
