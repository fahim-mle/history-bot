## Why

Adding books to history-bot currently requires a terminal, which breaks the self-contained app experience built in phase 3. The admin panel removes that dependency by exposing file upload, ingestion status, and manual sync directly in the Streamlit UI.

## What Changes

- **BREAKING (structure)**: `app.py` is replaced by Streamlit's multipage convention — `app.py` becomes the entry point shell, existing chat UI moves to `pages/1_Chat.py`, new admin panel lives at `pages/2_Admin.py`
- New `pages/1_Chat.py` — exact content of the current `app.py` chat UI, no behaviour change
- New `pages/2_Admin.py` — three sections: file uploader, ingested sources table, manual sync button
- File uploader accepts PDF, EPUB, TXT, MD; saves uploads to `sources/` then runs the ingestion pipeline in-process
- Ingested sources table reads `source_registry.json` and displays filename, extension, and ingestion timestamp
- Manual sync button re-runs ingestion on `sources/` to pick up any files added outside the UI
- `app.py` entry point shell sets page config and serves as the multipage root

## Capabilities

### New Capabilities

- `admin-panel`: Browser-based ingestion management — upload files, view ingested sources table, and trigger manual sync without touching the terminal

### Modified Capabilities

## Impact

- **New files**: `pages/1_Chat.py`, `pages/2_Admin.py`
- **Modified files**: `app.py` (gutted to entry-point shell only)
- **No changes** to `ingest.py`, `chat.py`, `config.py`
- **source_registry.json** must include an `ingested_at` timestamp field per entry — `ingest.py` updated to write it
- **No new dependencies** — `streamlit`, `ingest.py` imports already available
