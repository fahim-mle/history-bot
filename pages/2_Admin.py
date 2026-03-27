"""
history-bot Admin panel — file upload, sources table, manual sync.
"""

import json
from pathlib import Path

import streamlit as st

from config import settings
from ingest import (
    SUPPORTED_EXTENSIONS,
    get_vector_store,
    ingest_file,
    load_registry,
    save_registry,
)

st.set_page_config(page_title="Admin — History Bot", layout="centered")
st.title("Admin")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_sources_table() -> list[dict]:
    """Read source_registry.json; return list of dicts with filename/type/ingested_at."""
    p = Path(settings.registry_path)
    if not p.exists():
        return []
    try:
        registry = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    rows = []
    for key, entry in registry.items():
        filename = Path(key).name
        ext = Path(key).suffix.lower()
        if isinstance(entry, dict):
            ingested_at = entry.get("ingested_at", "unknown")
        else:
            ingested_at = "unknown"
        rows.append({"filename": filename, "type": ext, "ingested_at": ingested_at})
    return rows


# ---------------------------------------------------------------------------
# File Upload (tasks 3.2 – 3.6)
# ---------------------------------------------------------------------------

st.subheader("Upload files")

uploaded_files = st.file_uploader(
    "Upload PDF, EPUB, TXT, or MD files",
    type=["pdf", "epub", "txt", "md"],
    accept_multiple_files=True,
)

if uploaded_files:
    sources_dir = Path(settings.source_dir)
    sources_dir.mkdir(parents=True, exist_ok=True)

    registry = load_registry(settings.registry_path)
    vector_store = get_vector_store()

    messages: list[str] = []
    for uploaded_file in uploaded_files:
        dest = sources_dir / uploaded_file.name
        dest.write_bytes(uploaded_file.getbuffer())

        with st.spinner(f"Ingesting {uploaded_file.name}…"):
            result = ingest_file(dest, registry, vector_store)

        if result == "ingested":
            messages.append(f"✓ {uploaded_file.name} — ingested")
        elif result == "skipped":
            messages.append(f"— {uploaded_file.name} — already ingested (skipped)")
        elif result == "no_chunks":
            messages.append(f"⚠ {uploaded_file.name} — no text extracted")
        else:
            messages.append(f"✗ {uploaded_file.name} — unsupported type")

    save_registry(registry, settings.registry_path)

    for msg in messages:
        st.write(msg)


# ---------------------------------------------------------------------------
# Ingested Sources Table (tasks 4.1 – 4.3)
# ---------------------------------------------------------------------------

st.subheader("Ingested sources")

rows = load_sources_table()
if rows:
    st.dataframe(rows, use_container_width=True)
else:
    st.info("No sources ingested yet.")


# ---------------------------------------------------------------------------
# Manual Sync (task 5.1)
# ---------------------------------------------------------------------------

st.subheader("Sync sources/")

if st.button("Sync sources/"):
    sources_dir = Path(settings.source_dir)
    if not sources_dir.is_dir():
        st.warning(f"Sources directory not found: {sources_dir}")
    else:
        files = [
            f for f in sources_dir.rglob("*")
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        if not files:
            st.info("No supported files found in sources/.")
        else:
            registry = load_registry(settings.registry_path)
            vector_store = get_vector_store()
            n_ingested = 0
            n_skipped = 0
            for file_path in sorted(files):
                with st.spinner(f"Checking {file_path.name}…"):
                    result = ingest_file(file_path, registry, vector_store)
                if result == "ingested":
                    n_ingested += 1
                else:
                    n_skipped += 1
            save_registry(registry, settings.registry_path)
            st.success(
                f"Sync complete — {n_ingested} new, {n_skipped} skipped."
            )
