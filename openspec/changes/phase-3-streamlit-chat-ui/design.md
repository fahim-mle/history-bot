## Context

Phase 2 produced `chat.py` with a working `ConversationalRetrievalChain`. The chain is fully encapsulated: `get_vector_store()`, `build_chain()`, and `format_sources()` are importable. Phase 3 wraps these in a Streamlit page (`app.py`) that gives the bot a browser UI. Streamlit's execution model reruns the entire script on every user interaction, so state (chain instance, message history) must be held in `st.session_state`.

## Goals / Non-Goals

**Goals:**
- Render conversation history using `st.chat_message` on every rerun
- Accept new input via `st.chat_input` (pinned to page bottom)
- Show source documents in a collapsible expander below each assistant turn
- Initialise the chain once per session using `st.session_state`; reuse on subsequent reruns
- Provide a sidebar "Clear conversation" button that resets both the LangChain memory and the display history

**Non-Goals:**
- File upload or ingestion from the UI
- User login / authentication
- Persisting conversation history across browser sessions or restarts
- Streaming token output
- Multi-session or multi-user support

## Decisions

### D1: Import `get_vector_store`, `build_chain`, `format_sources` directly from `chat.py`

`chat.py` already encapsulates all chain logic. Importing from it avoids duplicating code and keeps the UI a thin wrapper. If `chat.py` changes (e.g., swaps the chain for LCEL in phase 4), `app.py` picks up the change automatically.

*Alternatives considered*: Copy chain setup into `app.py`. Rejected — creates two sources of truth.

### D2: Initialise chain once with `st.session_state` guard

Streamlit reruns the full script on every interaction. Without a guard, `build_chain()` would be called on every keystroke, rebuilding the chain and wiping memory. The pattern:

```python
if "chain" not in st.session_state:
    st.session_state.chain = build_chain(get_vector_store())
    st.session_state.messages = []
```

ensures the chain and message list are created exactly once per browser session.

*Alternatives considered*: `@st.cache_resource` for the vector store, separate guard for the chain. More granular but adds complexity for no gain at this scale.

### D3: Store display history as a list of dicts in `st.session_state.messages`

Each message is `{"role": "user"|"assistant", "content": str, "sources": list|None}`. This mirrors the OpenAI message format Streamlit's `st.chat_message` expects, and cleanly carries source docs alongside assistant turns without a separate parallel list.

### D4: Sources in `st.expander`, not inline

Inline sources add visual noise for every message. An expander labelled "Sources (N)" keeps the chat readable while making provenance one click away. Collapsed by default.

### D5: Clear button rebuilds chain from scratch (not just clears memory)

Calling `memory.clear()` on the existing chain resets LangChain's buffer, but rebuilding the chain object is safer (avoids any internal state in the chain object). On "Clear", we delete the session_state keys and trigger a rerun — the init guard then recreates everything cleanly.

## Risks / Trade-offs

- **Streamlit rerun latency** → Every submit triggers a full script rerun before the LLM call. Adds ~100–200ms of overhead. Acceptable for local use; streaming (phase 4) would address this.
- **chain init on first load** → First page load initialises the vector store and chain, which takes a few seconds. Mitigation: `st.spinner` during init.
- **`chat.py` warning suppression** → `chat.py` suppresses `LangChainDeprecationWarning` at import time; importing it in `app.py` carries that suppression over, which is the desired behaviour.
- **Single-user assumption** → `st.session_state` is per-browser-tab, not shared. Fine for local single-user deployment; would need a session key strategy for multi-user.
