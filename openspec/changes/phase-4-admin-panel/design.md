## Context

Phase 3 delivered a single-page Streamlit app (`app.py`). Adding an admin panel means introducing a second page, which requires converting to Streamlit's multipage convention. The ingestion logic already exists in `ingest.py` — the admin panel is a UI wrapper around `ingest_file()`, `load_registry()`, and `save_registry()`. No new dependencies are needed.

The one data schema change: `source_registry.json` currently stores `{path: md5_hash}`. The sources table needs an ingestion timestamp, so the value becomes `{hash: str, ingested_at: str}`. `ingest.py` must write this new shape; the registry lookup logic must handle both the old and new shapes during the transition.

## Goals / Non-Goals

**Goals:**
- Convert to Streamlit multipage: `app.py` shell + `pages/1_Chat.py` + `pages/2_Admin.py`
- File uploader in admin: save to `sources/`, run ingestion, report outcome
- Sources table: read registry, show filename, type, timestamp
- Manual sync button: re-ingest `sources/` for files added outside the UI
- `ingest.py` writes `ingested_at` ISO timestamp alongside the hash

**Non-Goals:**
- Deleting or re-ingesting individual sources from the UI
- Per-file progress bar (spinner per batch is sufficient)
- Web scraper or URL ingestion
- MongoDB migration

## Decisions

### D1: Streamlit multipage via `pages/` directory

Streamlit's multipage convention requires page files in a `pages/` subdirectory, named with a numeric prefix for ordering (`1_Chat.py`, `2_Admin.py`). The `app.py` root becomes a minimal shell — it only needs `set_page_config` and optionally a landing redirect. This is the least-friction path; no router library needed.

*Alternatives considered*: Single-file with `st.sidebar.radio` for navigation. Rejected — Streamlit's native multipage gives free sidebar navigation, browser history, and bookmarkable URLs.

### D2: Run ingestion in-process via `ingest_file()`, not subprocess

`ingest.py` exports `ingest_file()`, `load_registry()`, `save_registry()`, and `get_vector_store()`. Calling these directly from the admin page avoids subprocess overhead, keeps the Streamlit spinner working naturally, and shares the same Python process (no serialisation needed).

*Alternatives considered*: `subprocess.run(["uv", "run", "python", "ingest.py", ...])`. Rejected — harder to surface errors, no spinner integration, subprocess startup latency per file.

### D3: Save uploaded files to `sources/` before ingesting

`st.file_uploader` returns in-memory `BytesIO` objects. Writing them to `sources/` first means: (a) the file is on disk with its original name for registry keying, (b) manual sync and file-upload paths are unified — both call `ingest_file(path, ...)`, (c) uploaded files persist across restarts.

*Alternatives considered*: Ingest directly from `BytesIO` without saving. Rejected — would require a separate registry key scheme and would lose the file on restart.

### D4: registry value shape change — `{hash, ingested_at}` dict

Current shape: `{"sources/foo.txt": "abc123"}`. New shape: `{"sources/foo.txt": {"hash": "abc123", "ingested_at": "2026-03-27T10:00:00"}}`. The lookup in `ingest_file()` must handle both shapes (read old as hash-only string, write new as dict). This gives a clean migration without breaking existing registries.

*Alternatives considered*: Parallel `registry_meta.json` file. Rejected — two files to keep in sync is worse than one schema change with a compatibility shim.

### D5: Sources table built from registry, not ChromaDB

The registry is the authoritative record of what has been successfully ingested. Reading it is instant (no Ollama call). ChromaDB could provide chunk counts but adds latency and complexity; not worth it for a status table.

## Risks / Trade-offs

- **Concurrent ingestion** → If user clicks "Upload" and "Sync" simultaneously, both call `ingest_file()` on the same registry dict. Mitigation: Streamlit's single-threaded rerun model makes true concurrency unlikely; document that simultaneous triggers are unsupported.
- **Large file upload latency** → A 50MB PDF uploaded via `st.file_uploader` writes to disk then ingests synchronously — could take 30–60s. Mitigation: `st.spinner` during the whole operation; acceptable for local single-user use.
- **Registry backward compatibility** → Existing registries have string values. Mitigation: shim in `load_registry()` normalises old entries to `{"hash": v, "ingested_at": "unknown"}` on read.
- **`pages/` file naming** → Streamlit uses the filename (minus prefix and underscores) as the page label in the sidebar. `1_Chat.py` → "Chat", `2_Admin.py` → "Admin". This is the desired behaviour.

## Migration Plan

1. Create `pages/` directory
2. Copy `app.py` content to `pages/1_Chat.py`; strip to shell in `app.py`
3. Update `ingest.py` to write new registry shape with `ingested_at`
4. Add backward-compat shim to `load_registry()`
5. Write `pages/2_Admin.py`
6. Verify chat page unchanged, admin panel works end-to-end
