## Why

Phase 1 built a working ingestion pipeline but history-bot still can't answer questions — there is no retrieval or reasoning layer. Phase 2 adds the conversational RAG chain that reads from the populated ChromaDB collection and answers history questions with source attribution.

## What Changes

- New `chat.py` module with a `ConversationalRetrievalChain` backed by the Phase 1 ChromaDB collection
- Condense-question step rewrites follow-up questions using chat history before retrieval, so "what happened next?" resolves correctly
- Strict system prompt constrains the LLM to answer only from retrieved context; returns "I don't know" when context is insufficient
- Answer includes source references (filename + chunk excerpt) for each response
- Simple CLI input loop for interactive testing — no UI
- New config keys: `RETRIEVAL_K` (top-k chunks) and `LLM_MODEL` (Ollama model name)

## Capabilities

### New Capabilities

- `rag-chain`: Conversational retrieval chain that queries ChromaDB, condenses follow-up questions, generates grounded answers, and returns source references

### Modified Capabilities

## Impact

- **New files**: `chat.py`
- **Modified files**: `config.py` (two new settings), `.env.example`
- **Dependencies added**: no new packages — `langchain`, `langchain-community`, `langchain-ollama`, `chromadb` already installed in Phase 1
- **External services**: Ollama must be running with both `nomic-embed-text` (embeddings) and `llama3.2:3b` (generation) available
- **No breaking changes** — `ingest.py` and `config.py` remain unchanged except additive config fields
