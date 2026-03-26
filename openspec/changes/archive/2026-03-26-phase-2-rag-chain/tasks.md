## 1. Config

- [x] 1.1 Add `RETRIEVAL_K` (default: 3) and `LLM_MODEL` (default: `llama3.2:3b`) to `config.py`
- [x] 1.2 Update `.env.example` with the two new keys and their defaults (note: keep RETRIEVAL_K=3 to stay within llama3.2:3b ~4k context window)

## 2. Vector Store Loader

- [x] 2.1 Implement `get_vector_store()` in `chat.py` — load existing ChromaDB collection using `OllamaEmbeddings` (same as `ingest.py`)
- [x] 2.2 Implement `check_collection_not_empty(vector_store)` — log warning if collection has zero documents

## 3. Prompt Templates

- [x] 3.1 Define `CONDENSE_QUESTION_PROMPT` — rewrites follow-up questions into standalone questions using chat history
- [x] 3.2 Define `QA_PROMPT` — strict system prompt instructing the model to answer only from context and return "I don't know based on the available sources" when context is insufficient

## 4. RAG Chain

- [x] 4.1 Implement `build_chain(vector_store)` — create `ConversationBufferMemory` with `memory_key="chat_history"` and `return_messages=True`
- [x] 4.2 Wire `ConversationalRetrievalChain.from_llm()` with `ChatOllama` (LLM_MODEL), retriever (`RETRIEVAL_K`), memory, `CONDENSE_QUESTION_PROMPT`, `QA_PROMPT`, and `return_source_documents=True`
- [x] 4.3 Suppress LangChain deprecation warnings in CLI output — filter `LangChainDeprecationWarning` via `warnings.filterwarnings` at module level so they don't clutter the interactive session

## 5. Response Formatting

- [x] 5.1 Implement `format_sources(source_docs)` — extract `metadata["source"]` filename and first 150 chars of `page_content` from each retrieved document; return a formatted string

## 6. CLI Loop

- [x] 6.1 Implement `main()` — initialise vector store, warn if empty, build chain, then run input loop
- [x] 6.2 In the loop: print prompt, read input, skip blank lines, exit on `quit`/`exit`, invoke chain, print answer then sources
- [x] 6.3 Add `if __name__ == "__main__": main()` guard

## 7. Verification (strictly in order — do not skip ahead)

- [x] 7.1 Run `python chat.py` and ask a question about the ingested content — confirm answer is returned with sources
- [x] 7.2 Ask a follow-up using a pronoun or "what happened next?" — confirm condense step resolves it and answer is coherent with prior exchange
- [x] 7.3 Only after 7.1 and 7.2 pass: ask a question about a topic not in the ingested documents — confirm response contains "I don't know"
