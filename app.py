"""
history-bot Streamlit chat UI.

Usage:
    streamlit run app.py
"""

import streamlit as st

from chat import build_chain, format_sources, get_vector_store

# Task 1.2 — must be the first Streamlit call
st.set_page_config(page_title="History Bot", layout="centered")


# ---------------------------------------------------------------------------
# Source expander (task 4.1)
# ---------------------------------------------------------------------------

def render_sources(sources: list) -> None:
    """Render a collapsed expander with source filenames and excerpts."""
    if not sources:
        return
    with st.expander(f"Sources ({len(sources)})"):
        st.text(format_sources(sources))


# ---------------------------------------------------------------------------
# Session state initialisation (task 2.2)
# ---------------------------------------------------------------------------

if "chain" not in st.session_state:
    with st.spinner("Loading model…"):
        st.session_state.chain = build_chain(get_vector_store())
    st.session_state.messages = []


# ---------------------------------------------------------------------------
# Sidebar — clear button (tasks 6.1, 6.2)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("History Bot")
    if st.button("Clear conversation"):
        del st.session_state["chain"]
        del st.session_state["messages"]
        st.rerun()


# ---------------------------------------------------------------------------
# Chat history replay (task 3.1)
# — render_sources called for every assistant turn, including history replay
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            render_sources(msg.get("sources") or [])


# ---------------------------------------------------------------------------
# Input and response (tasks 5.1 – 5.5)
# ---------------------------------------------------------------------------

if prompt := st.chat_input("Ask a history question…"):
    # Append and render user message immediately (task 5.2)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Invoke chain (task 5.3)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            result = st.session_state.chain.invoke({"question": prompt})
        answer = result.get("answer", "")
        sources = result.get("source_documents", [])

        # Render reply and sources (task 5.5)
        st.markdown(answer)
        render_sources(sources)

    # Persist assistant message (task 5.4)
    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
