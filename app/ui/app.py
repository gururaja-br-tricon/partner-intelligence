import asyncio
import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

import streamlit as st

from app.config import settings

from app.orchestrator.orchestrator import Orchestrator

DEMO_QUESTIONS = [
    "Which partners are most likely to grow?",
    "Which technologies are gaining momentum in Texas?",
    "Which partners should I recruit, and which regions should I prioritize for them?",
]

ROUTE_LABELS = {
    "partner_growth": "Partner Growth",
    "market_gtm": "Market/GTM",
}


@st.cache_resource
def get_orchestrator() -> Orchestrator:
    return Orchestrator(mcp_url=settings.mcp_url)


def run_answer(orchestrator: Orchestrator, question: str):
    async def _run():
        return await orchestrator.answer(question)

    return asyncio.run(_run())


def reset_conversation() -> None:
    st.session_state["messages"] = []
    st.cache_resource.clear()


st.set_page_config(page_title="TCC Partner Intelligence", layout="wide")

st.title("TCC Partner Intelligence — POC")
st.caption("Context Layer · Multi-Agent Orchestrator · LLM Router")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

orchestrator = get_orchestrator()

with st.sidebar:
    st.subheader("Demo Questions")
    for question in DEMO_QUESTIONS:
        if st.button(question, use_container_width=True):
            st.session_state["messages"].append({"role": "user", "content": question})

    if st.button("Reset conversation", use_container_width=True):
        reset_conversation()

    st.divider()
    st.subheader("Diagnostics")
    metadata = st.empty()

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask about partners, growth, or market momentum...")

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Routing intent and querying agents..."):
            answer = run_answer(orchestrator, prompt)

        st.markdown(answer)

        route_text = " + ".join(
            ROUTE_LABELS.get(a, a) for a in orchestrator.last_route
        )
        cache_status = (
            "cache hit (from semantic cache)"
            if orchestrator.last_cache_hit
            else "cache miss (fresh computation)"
        )

        st.caption(f"Route: {route_text} | {cache_status}")

    st.session_state["messages"].append({"role": "assistant", "content": answer})

with st.sidebar:
    cache_stats = orchestrator.cache.stats()
    metadata.info(
        f"Cache entries: {cache_stats['entries']}\n\n"
        f"Hits: {cache_stats['hits']}\n\n"
        f"Misses: {cache_stats['misses']}"
)