## Why

history-bot needs a reliable way to ingest local source documents (PDF, EPUB, TXT, MD) into a vector store before any retrieval or Q&A can happen. Without an ingestion pipeline, the bot has no knowledge base to query against.

## What Changes

- New `ingest.py` entry point that accepts a `--source` directory and processes all supported files within it
- New `config.py` using pydantic-settings to load all configuration from `.env` (chunk size, overlap, paths, model names)
- Format-specific parsers for PDF (pymupdf), EPUB (ebooklib), and TXT/MD (plain read)
- Text cleaning step to strip page numbers, headers, and OCR artifacts
- Chunking via `RecursiveCharacterTextSplitter` (size=700, overlap=100)
- MD5-based deduplication against a `source_registry.json` file — already-ingested files are skipped on re-run
- Embedding via `nomic-embed-text` through Ollama, stored in a local file-based ChromaDB collection

## Capabilities

### New Capabilities

- `document-ingestion`: End-to-end pipeline that parses, cleans, chunks, deduplicates, embeds, and stores documents from a local source directory into ChromaDB

### Modified Capabilities

## Impact

- **New files**: `ingest.py`, `config.py`, `source_registry.json` (runtime-generated), `sources/` directory (user-populated)
- **Dependencies added**: `pymupdf`, `ebooklib`, `langchain`, `langchain-community`, `chromadb`, `pydantic-settings`, `ollama`
- **External services**: Ollama must be running locally with `nomic-embed-text` model available
- **No breaking changes** — this is a greenfield pipeline with no existing code affected
