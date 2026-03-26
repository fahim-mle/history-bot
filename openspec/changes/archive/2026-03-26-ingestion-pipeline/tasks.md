## 1. Project Setup

- [x] 1.1 Create `pyproject.toml` with uv-compatible project metadata and all dependencies: `pymupdf`, `ebooklib`, `langchain`, `langchain-community`, `langchain-chroma`, `chromadb`, `pydantic-settings`, `ollama`
- [x] 1.2 Create `.env.example` documenting all required env vars (`CHUNK_SIZE`, `CHUNK_OVERLAP`, `SOURCE_DIR`, `CHROMA_PATH`, `OLLAMA_BASE_URL`, `EMBED_MODEL`, `REGISTRY_PATH`)
- [x] 1.3 Create `config.py` using pydantic-settings `BaseSettings` to load and validate all env vars from `.env`
- [x] 1.4 Create `sources/`, `vector_store/`, and `raw_sources/` directories (with `.gitkeep` so they are tracked)
- [x] 1.5 Add `.gitignore` entries for `.env`, `vector_store/`, and `source_registry.json`

## 2. Document Parsers

- [x] 2.1 Implement `parse_txt(path)` — plain UTF-8 read for `.txt` and `.md` files
- [x] 2.2 Implement `parse_pdf(path)` — extract text from all pages using pymupdf (`fitz`)
- [x] 2.3 Implement `parse_epub(path)` — extract text from all document items using ebooklib, stripping HTML tags
- [x] 2.4 Implement `parse_document(path)` — dispatcher that routes to the correct parser by extension; logs warning and returns `None` for unsupported types

## 3. Text Cleaning

- [x] 3.1 Implement `clean_text(text)` — strip standalone numeric lines (page numbers), collapse multiple blank lines to one, strip trailing whitespace per line

## 4. Chunking

- [x] 4.1 Implement `chunk_text(text)` — use `RecursiveCharacterTextSplitter` with `chunk_size` and `chunk_overlap` from config; return list of strings

## 5. Deduplication Registry

- [x] 5.1 Implement `load_registry(path)` — read `source_registry.json`; return empty dict if file does not exist
- [x] 5.2 Implement `save_registry(registry, path)` — write registry dict to `source_registry.json` atomically
- [x] 5.3 Implement `compute_md5(path)` — return hex MD5 hash of file content
- [x] 5.4 Add registry lookup in ingestion flow: skip file if path exists in registry AND hash matches; update entry if hash has changed

## 6. Embedding and ChromaDB Storage

- [x] 6.1 Implement `get_vector_store()` — initialise `OllamaEmbeddings` with `EMBED_MODEL` and `OLLAMA_BASE_URL` from config; return `Chroma` client pointed at `CHROMA_PATH`
- [x] 6.2 Implement `store_chunks(chunks, source_path, vector_store)` — upsert chunks into ChromaDB with `source` metadata

## 7. Entry Point

- [x] 7.1 Implement `ingest_file(path, registry, vector_store)` — orchestrates parse → clean → chunk → store → update registry for a single file
- [x] 7.2 Implement `main()` with `argparse` accepting `--source` directory; iterate all supported files and call `ingest_file`; warn if ChromaDB is non-empty but registry is missing
- [x] 7.3 Add `if __name__ == "__main__": main()` guard to `ingest.py`

## 8. Verification

- [x] 8.1 Place one small `.txt` file in `sources/` and run `python ingest.py --source sources/` — confirm no errors and `source_registry.json` is created
- [x] 8.2 Open a Python REPL, load the ChromaDB collection, and run a similarity search — confirm relevant chunks are returned
- [x] 8.3 Re-run `python ingest.py --source sources/` — confirm the file is skipped and logs indicate it was already ingested
