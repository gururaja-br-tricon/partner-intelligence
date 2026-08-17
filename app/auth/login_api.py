"""
Small login API. POST /login -> verifies email+password, returns a
signed JWT carrying user_id and roles. No session store, no stateful
login server needed — the JWT itself is the credential the Streamlit
app holds for the rest of the conversation.
"""

from __future__ import annotations

import datetime
import os

import bcrypt
import jwt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.auth.user_store import get_user_by_email

app = FastAPI()

JWT_SECRET = os.environ["JWT_SECRET"]  # same value the MCP-side middleware reads — set once, share via env
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 8


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    roles: list[str]


@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest) -> LoginResponse:
    user = get_user_by_email(req.email)

    # Deliberately identical error for "no such user" and "wrong password" —
    # distinguishing them lets an attacker enumerate valid emails.
    invalid = HTTPException(status_code=401, detail="Invalid email or password")

    if user is None:
        raise invalid
    if not bcrypt.checkpw(req.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise invalid

    payload = {
        "user_id": user.user_id,
        "roles": sorted(user.roles),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return LoginResponse(token=token, roles=sorted(user.roles))
