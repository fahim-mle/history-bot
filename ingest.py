"""
history-bot ingestion pipeline.

Usage:
    python ingest.py --source sources/
"""

import argparse
import hashlib
import json
import logging
import re
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path

import fitz  # pymupdf
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from config import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".epub"}


# ---------------------------------------------------------------------------
# Parsers (task 2.1–2.4)
# ---------------------------------------------------------------------------

def parse_txt(path: Path) -> str:
    """Read plain UTF-8 text for .txt and .md files."""
    return path.read_text(encoding="utf-8")


def parse_pdf(path: Path) -> str:
    """Extract all text from a PDF using pymupdf."""
    doc = fitz.open(str(path))
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)


def parse_epub(path: Path) -> str:
    """Extract text from all document items in an EPUB, stripping HTML."""
    book = epub.read_epub(str(path))
    parts: list[str] = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        parts.append(soup.get_text(separator="\n"))
    return "\n".join(parts)


def parse_document(path: Path) -> str | None:
    """Route to the correct parser by file extension. Returns None for unsupported types."""
    ext = path.suffix.lower()
    if ext in (".txt", ".md"):
        return parse_txt(path)
    if ext == ".pdf":
        return parse_pdf(path)
    if ext == ".epub":
        return parse_epub(path)
    log.warning("Skipping unsupported file type: %s", path)
    return None


# ---------------------------------------------------------------------------
# Cleaning (task 3.1)
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Strip standalone page-number lines, collapse multiple blank lines,
    and strip trailing whitespace from each line.
    """
    # Remove lines that are only digits (page numbers)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.splitlines()]
    # Collapse runs of blank lines to a single blank line
    cleaned: list[str] = []
    prev_blank = False
    for line in lines:
        is_blank = line == ""
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank
    return "\n".join(cleaned).strip()


# ---------------------------------------------------------------------------
# Chunking (task 4.1)
# ---------------------------------------------------------------------------

def chunk_text(text: str) -> list[str]:
    """Split text using RecursiveCharacterTextSplitter with config values."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_text(text)


# ---------------------------------------------------------------------------
# Deduplication registry (tasks 5.1–5.4)
# ---------------------------------------------------------------------------

def load_registry(path: str) -> dict:
    """Load source_registry.json; return empty dict if absent."""
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _registry_hash(entry) -> str:
    """Extract hash from either old string format or new dict format."""
    if isinstance(entry, dict):
        return entry.get("hash", "")
    return entry  # legacy: bare hash string


def save_registry(registry: dict[str, str], path: str) -> None:
    """Write registry atomically to avoid partial writes."""
    p = Path(path)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=p.parent, delete=False, suffix=".tmp"
    ) as tmp:
        json.dump(registry, tmp, indent=2)
        tmp_path = tmp.name
    os.replace(tmp_path, p)


def compute_md5(path: Path) -> str:
    """Return the hex MD5 hash of a file's content."""
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Embedding and storage (tasks 6.1–6.2)
# ---------------------------------------------------------------------------

def get_vector_store() -> Chroma:
    """Initialise OllamaEmbeddings and return a persistent Chroma client."""
    embeddings = OllamaEmbeddings(
        model=settings.embed_model,
        base_url=settings.ollama_base_url,
    )
    return Chroma(
        collection_name="history",
        embedding_function=embeddings,
        persist_directory=settings.chroma_path,
    )


def store_chunks(chunks: list[str], source_path: str, vector_store: Chroma) -> None:
    """Upsert chunks into ChromaDB with source metadata."""
    metadatas = [{"source": source_path} for _ in chunks]
    vector_store.add_texts(texts=chunks, metadatas=metadatas)


# ---------------------------------------------------------------------------
# Per-file orchestration (task 7.1)
# ---------------------------------------------------------------------------

def ingest_file(
    path: Path,
    registry: dict,
    vector_store: Chroma,
) -> str:
    """Parse → clean → chunk → store → update registry for a single file.

    Returns a status string: 'ingested', 'skipped', 'no_chunks', or 'unsupported'.
    """
    key = str(path)
    current_hash = compute_md5(path)

    # Tasks 1.2 & 1.3 — handle both old (str) and new (dict) registry shapes
    existing = registry.get(key)
    if existing is not None and _registry_hash(existing) == current_hash:
        log.info("Already ingested (skipping): %s", path)
        return "skipped"

    if existing is not None:
        log.info("File changed, re-ingesting: %s", path)
    else:
        log.info("Ingesting new file: %s", path)

    raw = parse_document(path)
    if raw is None:
        return "unsupported"

    cleaned = clean_text(raw)
    chunks = chunk_text(cleaned)
    if not chunks:
        log.warning("No chunks produced for %s — skipping.", path)
        return "no_chunks"

    log.info("  %d chunks → ChromaDB", len(chunks))
    store_chunks(chunks, key, vector_store)

    # Task 1.1 — write new dict shape with ingested_at timestamp
    registry[key] = {
        "hash": current_hash,
        "ingested_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
    }
    return "ingested"


# ---------------------------------------------------------------------------
# Entry point (tasks 7.2–7.3)
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into ChromaDB.")
    parser.add_argument(
        "--source",
        default=settings.source_dir,
        help="Directory of source documents (default: %(default)s)",
    )
    args = parser.parse_args()

    source_dir = Path(args.source)
    if not source_dir.is_dir():
        log.error("Source directory does not exist: %s", source_dir)
        raise SystemExit(1)

    registry = load_registry(settings.registry_path)

    # Warn if ChromaDB has data but registry is missing (check before init creates the file)
    chroma_db_file = Path(settings.chroma_path) / "chroma.sqlite3"
    if chroma_db_file.exists() and not Path(settings.registry_path).exists():
        log.warning(
            "ChromaDB at '%s' contains data but source_registry.json is missing. "
            "Re-running will create duplicate chunks.",
            settings.chroma_path,
        )

    vector_store = get_vector_store()

    files = [
        f for f in source_dir.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        log.info("No supported files found in %s", source_dir)
        return

    for file_path in sorted(files):
        ingest_file(file_path, registry, vector_store)

    save_registry(registry, settings.registry_path)
    log.info("Done. Registry saved to %s", settings.registry_path)


if __name__ == "__main__":
    main()
