import asyncio
import datetime
import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

import bcrypt
import jwt
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from app.auth.user_store import get_user_by_email
from app.config import settings

from app.orchestrator.orchestrator import Orchestrator

JWT_SECRET = os.environ[
    "JWT_SECRET"
]  # must match what JWTRoleVerifier verifies against
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 8

DEMO_QUESTIONS = [
    "Which partners are most likely to grow?",
    "Which technologies are gaining momentum in Texas?",
    "Which partners should I recruit, and which regions should I prioritize for them?",
]

ROUTE_LABELS = {
    "partner_growth": "Partner Growth",
    "market_gtm": "Market/GTM",
}


def do_login(email: str, password: str) -> bool:
    user = get_user_by_email(email)
    if user is None or not bcrypt.checkpw(
        password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        return False

    payload = {
        "user_id": user.user_id,
        "roles": sorted(user.roles),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    st.session_state["jwt"] = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    st.session_state["email"] = email
    st.session_state["roles"] = sorted(user.roles)
    return True


def login_screen() -> None:
    st.title("TCC Partner Intelligence — Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

        if submitted:
            if do_login(email, password):
                st.rerun()
            else:
                # Same message for "no such user" and "wrong password" —
                # deliberate, so this page doesn't reveal which emails are
                # registered. New-user provisioning happens via the admin
                # tool (admin_app.py), not through this page.
                st.error("Invalid email or password.")

    st.caption("Need an account?")
    # admin_app.py runs as a SEPARATE streamlit process on its own port —
    # adjust ADMIN_APP_URL to match wherever you actually run it.
    ADMIN_APP_URL = os.environ.get("ADMIN_APP_URL", "http://localhost:8502")
    st.link_button("Create/Update new user (Admin)", ADMIN_APP_URL)


@st.cache_resource
def get_orchestrator() -> Orchestrator:
    return Orchestrator(mcp_url=settings.mcp_url)


def run_answer(orchestrator: Orchestrator, question: str, jwt_token: str):
    async def _run():
        return await orchestrator.answer(question, jwt=jwt_token)

    return asyncio.run(_run())


def reset_conversation() -> None:
    st.session_state["messages"] = []
    st.cache_resource.clear()


st.set_page_config(page_title="TCC Partner Intelligence", layout="wide")

if "jwt" not in st.session_state:
    login_screen()
    st.stop()

st.title("TCC Partner Intelligence — POC")
st.caption("Context Layer · Multi-Agent Orchestrator · LLM Router")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

orchestrator = get_orchestrator()

with st.sidebar:
    st.caption(
        f"Logged in as {st.session_state['email']} ({', '.join(st.session_state['roles'])})"
    )
    if st.button("Log out", use_container_width=True):
        for key in ("jwt", "email", "roles", "messages"):
            st.session_state.pop(key, None)
        st.rerun()

    st.divider()
    st.subheader("Demo Questions")
    for question in DEMO_QUESTIONS:
        if st.button(question, use_container_width=True):
            st.session_state["chat_input"] = question
            st.rerun()

    if st.button("Reset conversation", use_container_width=True):
        reset_conversation()

    st.divider()
    st.subheader("Diagnostics")
    metadata = st.empty()

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input(
    "Ask about partners, growth, or market momentum...",
    key="chat_input",
)

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Routing intent and querying agents..."):
            answer = run_answer(orchestrator, prompt, st.session_state["jwt"])

        st.markdown(answer)

        route_text = " + ".join(ROUTE_LABELS.get(a, a) for a in orchestrator.last_route)
        cache_status = (
            "cache hit (from semantic cache)"
            if orchestrator.last_cache_hit
            else "cache miss (fresh computation)"
        )
        cache_stats = "cache miss (fresh computation)"

        st.caption(f"Route: {route_text} | {cache_status}")

    st.session_state["messages"].append({"role": "assistant", "content": answer})

with st.sidebar:
    cache_stats = orchestrator.cache.stats()
    metadata.info(
        f"Cache entries: {cache_stats['entries']}\n\n"
        f"Hits: {cache_stats['hits']}\n\n"
        f"Misses: {cache_stats['misses']}"
    )
