## Context

Phase 1 produced a populated ChromaDB collection (`vector_store/`) with embedded history document chunks. The bot has no way to query that collection yet. This design adds `chat.py`: a self-contained conversational retrieval module that uses the same collection, the same embedding model, and Ollama for generation. No UI is added in this phase — interaction happens via a CLI loop to validate the chain before investing in frontend work.

## Goals / Non-Goals

**Goals:**
- Load the existing ChromaDB collection as the retriever for LangChain
- Condense multi-turn follow-up questions into standalone queries before retrieval
- Generate answers strictly grounded in retrieved context using `llama3.2:3b`
- Surface source filenames and chunk excerpts alongside each answer
- Provide a REPL-style CLI for manual testing

**Non-Goals:**
- Streamlit or any web UI
- Persistent memory across restarts (session-only)
- Re-ranking retrieved chunks
- New ingestion or document management
- Streaming responses

## Decisions

### D1: `ConversationalRetrievalChain` over a manual chain

LangChain's `ConversationalRetrievalChain` bundles the condense-question step, the retriever call, and the QA step in one object. Building these manually would require more code for no benefit at this stage.

*Alternatives considered*: Manual `LCEL` pipeline. More flexible, but the added complexity is not warranted until we need streaming or reranking (phase 3).

### D2: `ConversationBufferMemory` for session history

Stores the full conversation as a string buffer. Simple and correct for short sessions with a small context-window model like `llama3.2:3b`. Memory resets on process restart — intentional per spec.

*Alternatives considered*: `ConversationSummaryMemory` to compress long histories. Rejected — unnecessary complexity for a CLI test harness; revisit when sessions grow long.

### D3: Separate condense-question LLM call (same model)

The condense step rewrites "what happened next?" into "what happened after the fall of Rome?" before hitting the retriever. Using the same `llama3.2:3b` for both condense and QA avoids adding a second Ollama model dependency.

*Alternatives considered*: Skip condense step, pass raw history to retriever. Rejected because follow-up questions with pronouns ("he", "it", "they") will return irrelevant chunks without rewriting.

### D4: Strict "answer only from context" system prompt

The prompt explicitly instructs the model to say "I don't know based on the available sources" when context is insufficient. This prevents hallucination on topics not in the ingested corpus.

*Alternatives considered*: Permissive prompt that allows model's own knowledge as fallback. Rejected — history-bot is specifically a retrieval-grounded system; mixing model knowledge with document knowledge undermines trust in answers.

### D5: `return_source_documents=True` for source attribution

LangChain's `ConversationalRetrievalChain` can return the retrieved `Document` objects alongside the answer. We extract `metadata["source"]` (filename) and a truncated excerpt to build the source list shown to the user.

### D6: `chat.py` as a flat module, no package split

Same rationale as `ingest.py` in Phase 1 (D1 from ingestion design). A single file is sufficient until a UI layer requires proper module separation.

## Risks / Trade-offs

- **`llama3.2:3b` context window (~4k tokens)** → With k=5 chunks at ~700 chars each, retrieved context is ~3.5k chars — close to the limit when combined with chat history. Mitigation: keep `RETRIEVAL_K` default at 5; users with long sessions can reduce it via `.env`.
- **Condense step latency** → Every query makes two LLM calls (condense + generate). On a local CPU, this may be slow. Mitigation: document in README; streaming can be added in phase 3.
- **ConversationalRetrievalChain deprecation trajectory** → LangChain is moving toward LCEL-first patterns. Mitigation: acceptable for phase 2; phase 3 can migrate to LCEL if needed.
- **Empty ChromaDB collection** → If the user runs `chat.py` before ingesting, retrieval returns nothing and every answer will be "I don't know". Mitigation: check collection count at startup and warn if zero.
