## Why

Phase 2 delivered a working RAG chain accessible only via a CLI loop. A chat UI makes history-bot usable for actual reading sessions — browsing answers, reviewing sources, and holding multi-turn conversations without touching a terminal.

## What Changes

- New `app.py` single-page Streamlit application that wraps `chat.py` directly
- Chat messages rendered with `st.chat_message` (user bubbles + assistant bubbles)
- `st.session_state` persists the chain instance and display history across Streamlit reruns, so follow-up questions continue working
- Sources for each answer shown in a collapsible `st.expander` below the assistant bubble
- "Clear conversation" button in the sidebar resets both session memory and the visible chat history
- `streamlit` added as a project dependency

## Capabilities

### New Capabilities

- `streamlit-chat-ui`: Browser-based chat interface that wraps the RAG chain with message history display, per-answer source expanders, and a session reset control

### Modified Capabilities

## Impact

- **New files**: `app.py`
- **Modified files**: `pyproject.toml` (add `streamlit`)
- **No changes** to `chat.py`, `ingest.py`, or `config.py`
- **Run command**: `streamlit run app.py`
- **No breaking changes** — CLI (`python chat.py`) continues to work unchanged
