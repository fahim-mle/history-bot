## Context

history-bot is a local RAG application for querying a personal history document collection. Currently there is no ingestion pipeline — documents sit in a `sources/` directory and cannot be queried. This design covers the one-time and incremental ingestion flow: read files → clean text → chunk → embed → store in ChromaDB. All external calls go through Ollama running locally; there is no cloud dependency.

## Goals / Non-Goals

**Goals:**
- Process PDF, EPUB, TXT, and MD files from a local directory
- Produce clean, consistently-sized chunks suitable for semantic search (700 tokens, 100 overlap)
- Persist embeddings in a local file-based ChromaDB collection
- Skip files already present in `source_registry.json` to make re-runs safe and fast
- Keep all tuneable values (chunk size, overlap, model names, paths) in `.env` via `config.py`

**Non-Goals:**
- Web scraping or remote document fetching
- Streamlit or any UI
- MongoDB or any database other than ChromaDB
- Conversation memory or retrieval at this phase
- Parallel/async ingestion

## Decisions

### D1: Single-file entry point (`ingest.py`) over a package structure

A single script with clearly separated functions (parse → clean → chunk → embed → store) is sufficient for this phase and avoids premature abstraction. A package layout can be introduced when retrieval and UI are added.

*Alternatives considered*: A `src/ingestion/` package with separate modules. Rejected because the added indirection provides no value before the retrieval layer exists.

### D2: `source_registry.json` for deduplication (MD5 hash keyed by file path)

A flat JSON file is human-readable, requires no extra dependencies, and survives process restarts. The MD5 hash of the file content (not just the path) means a changed file will be re-ingested automatically.

*Alternatives considered*: SQLite for richer metadata. Rejected because it adds a dependency and the query patterns here are trivial (key lookup only).

### D3: pydantic-settings for config, single `.env` file

All tuneable parameters (chunk size, overlap, source dir, ChromaDB path, Ollama base URL, model names) live in `.env`. `config.py` exposes a single `Settings` singleton. No hardcoded values anywhere in the pipeline.

*Alternatives considered*: `python-dotenv` + manual `os.getenv` calls. Rejected because pydantic-settings gives type validation and IDE completion for free.

### D4: LangChain `RecursiveCharacterTextSplitter` for chunking

Splits on paragraph → sentence → word boundaries in order, preserving semantic coherence. Standard choice for RAG pipelines.

*Alternatives considered*: Fixed-size token splitting. Rejected because it cuts mid-sentence, degrading retrieval quality.

### D5: ChromaDB with `OllamaEmbeddings` via LangChain

LangChain's `Chroma` wrapper handles collection creation, upsert, and persistence. `OllamaEmbeddings` points at the local Ollama server. No API keys required.

*Alternatives considered*: Direct `chromadb` client without LangChain. Rejected because LangChain's abstraction makes switching embedding models or vector stores trivial later.

## Risks / Trade-offs

- **Large PDFs with heavy OCR artifacts** → Mitigation: regex-based cleaning removes common patterns (page numbers `\d+`, repeated header/footer lines). Imperfect but sufficient for well-formatted history books.
- **EPUB files with unusual structure** → Mitigation: `ebooklib` covers standard EPUB2/3; edge cases (DRM, exotic metadata) will surface at runtime. Out-of-scope files should be converted to TXT manually.
- **Ollama not running** → Mitigation: the embedding step will raise a clear connection error. Document in README that Ollama must be running with `nomic-embed-text` pulled before ingestion.
- **source_registry.json drift** → If the file is deleted, all documents will be re-ingested (duplicate chunks). Mitigation: warn if ChromaDB collection is non-empty and registry is missing.
- **Chunk size / overlap tuning** → 700/100 is a reasonable default for long-form history text; may need adjustment. Values are `.env`-configurable so no code change required.
