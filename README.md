# History Bot

A local RAG (Retrieval-Augmented Generation) chatbot specialised in history documents. Ask questions about your history books and primary sources — the bot retrieves relevant passages and answers like a historian, citing its sources.

Runs entirely on your machine using [Ollama](https://ollama.com) for LLM inference and [ChromaDB](https://www.trychroma.com) for vector storage. No API keys or internet connection required after setup.

## How it works

1. **Ingest** — PDF, EPUB, TXT, and MD files are parsed, cleaned, chunked, and embedded into a local ChromaDB vector store.
2. **Chat** — Questions are answered using a conversational RAG chain: relevant chunks are retrieved and passed to the LLM alongside the question and chat history.
3. **UI** — A Streamlit multipage app provides a chat interface and an admin panel for uploading and managing source documents.

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (package manager)
- [Ollama](https://ollama.com) with the following models pulled:

```bash
ollama pull qwen3.5:latest        # LLM
ollama pull nomic-embed-text      # embeddings
```

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/fahim-mle/history-bot.git
cd history-bot

# 2. Install dependencies
uv sync

# 3. Configure environment (optional — defaults work out of the box)
cp .env.example .env   # edit if needed
```

### Environment variables

All settings have sensible defaults. Override via `.env` or environment:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LLM_MODEL` | `qwen3.5:latest` | Ollama model for chat |
| `EMBED_MODEL` | `nomic-embed-text` | Ollama model for embeddings |
| `SOURCE_DIR` | `sources/` | Directory scanned for source files |
| `CHROMA_PATH` | `vector_store/` | ChromaDB persistence directory |
| `REGISTRY_PATH` | `source_registry.json` | Ingestion registry file |
| `RETRIEVAL_K` | `5` | Number of chunks retrieved per query |

## Running the app

```bash
uv run streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

The app has two pages:

- **Chat** — ask questions about your ingested documents.
- **Admin** — upload new source files, view ingested sources, and manually sync the `sources/` directory.

## Ingesting documents via CLI

You can also ingest documents directly from the command line:

```bash
# Place files in sources/ then run:
uv run python ingest.py
```

Supported formats: `.pdf`, `.epub`, `.txt`, `.md`

The ingestion registry (`source_registry.json`) tracks which files have been ingested. Re-running `ingest.py` skips unchanged files and re-ingests only modified ones.

## Project structure

```
history-bot/
├── app.py              # Streamlit entrypoint
├── pages/
│   ├── 1_Chat.py       # Chat UI
│   └── 2_Admin.py      # Admin panel (upload, sync, sources table)
├── chat.py             # RAG chain and CLI loop
├── ingest.py           # Document parsing, chunking, and ingestion
├── config.py           # Settings (pydantic-settings)
├── sources/            # Source documents (gitignored)
├── vector_store/       # ChromaDB data (gitignored)
└── source_registry.json
```

## License

See [LICENSE](LICENSE).
