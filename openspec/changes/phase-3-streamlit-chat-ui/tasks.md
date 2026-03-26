## 1. Setup

- [x] 1.1 Add `streamlit` to `pyproject.toml` dependencies and run `uv sync`
- [x] 1.2 Set `st.set_page_config(page_title="History Bot", layout="centered")` as the first Streamlit call in `app.py`

## 2. Session State Initialisation

- [x] 2.1 In `app.py`, import `get_vector_store`, `build_chain`, and `format_sources` from `chat.py`
- [x] 2.2 Add session state guard: if `"chain"` not in `st.session_state`, initialise chain with `st.spinner("Loading model…")` and set `st.session_state.messages = []`

## 3. Chat History Rendering

- [x] 3.1 Iterate `st.session_state.messages` and render each with `st.chat_message(role)` — user messages as plain text, assistant messages with answer text **and** `render_sources()` called for every assistant turn (history replay must show sources too, not only new responses)

## 4. Sources Expander

- [x] 4.1 Implement `render_sources(sources)` — renders an `st.expander(f"Sources ({len(sources)})")` containing the `format_sources()` output as preformatted text; renders nothing if sources list is empty

## 5. Input and Response

- [x] 5.1 Capture input with `st.chat_input("Ask a history question…")`
- [x] 5.2 On submit: append user message to `st.session_state.messages`, render it immediately with `st.chat_message("user")`
- [x] 5.3 Invoke chain inside `st.spinner("Thinking…")`, extract `answer` and `source_documents` from result
- [x] 5.4 Append assistant message dict `{"role": "assistant", "content": answer, "sources": source_documents}` to `st.session_state.messages`
- [x] 5.5 Render assistant reply with `st.chat_message("assistant")` and call `render_sources(source_documents)`

## 6. Clear Conversation

- [x] 6.1 Add `st.sidebar` with `st.button("Clear conversation")`
- [x] 6.2 On click: delete `st.session_state.chain` and `st.session_state.messages`, then call `st.rerun()` to trigger re-initialisation

## 7. Verification

- [x] 7.1 Run `streamlit run app.py`, ask a question — confirm answer appears in assistant bubble with sources expander
- [x] 7.2 Ask a follow-up question — confirm answer is coherent with prior exchange (chain memory working)
- [x] 7.3 Click "Clear conversation" — confirm chat area empties and a fresh question has no prior context
