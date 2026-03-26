# document-ingestion

### Requirement: Supported format parsing
The system SHALL parse documents in PDF, EPUB, TXT, and MD formats from a source directory. PDF files SHALL be parsed using pymupdf, EPUB files using ebooklib, and TXT/MD files via plain UTF-8 read.

#### Scenario: PDF file is parsed
- **WHEN** a `.pdf` file is present in the source directory
- **THEN** the system extracts its full text content using pymupdf without raising an error

#### Scenario: EPUB file is parsed
- **WHEN** a `.epub` file is present in the source directory
- **THEN** the system extracts text from all document items using ebooklib

#### Scenario: TXT or MD file is parsed
- **WHEN** a `.txt` or `.md` file is present in the source directory
- **THEN** the system reads its content as plain UTF-8 text

#### Scenario: Unsupported file type is skipped
- **WHEN** a file with an unsupported extension is in the source directory
- **THEN** the system logs a warning and skips the file without failing

### Requirement: Text cleaning
The system SHALL clean extracted text to remove page numbers, repeated headers/footers, and common OCR artifacts before chunking.

#### Scenario: Page number lines are removed
- **WHEN** extracted text contains standalone numeric lines (e.g., `\n42\n`)
- **THEN** the cleaned text does not contain those standalone numeric lines

#### Scenario: Excessive whitespace is normalized
- **WHEN** extracted text contains multiple consecutive blank lines or trailing spaces
- **THEN** the cleaned text collapses them to single newlines

### Requirement: Chunking
The system SHALL split cleaned text into chunks using `RecursiveCharacterTextSplitter` with chunk size and overlap read from config.

#### Scenario: Text is chunked with configured size and overlap
- **WHEN** a document is cleaned and split
- **THEN** each chunk does not exceed `CHUNK_SIZE` characters and consecutive chunks share `CHUNK_OVERLAP` characters of context

#### Scenario: Short document produces at least one chunk
- **WHEN** a document's cleaned text is shorter than `CHUNK_SIZE`
- **THEN** the system produces exactly one chunk containing the full text

### Requirement: MD5-based deduplication
The system SHALL compute an MD5 hash of each source file's content and skip files whose hash is already recorded in `source_registry.json`.

#### Scenario: Already-ingested file is skipped
- **WHEN** a file's MD5 hash matches an entry in `source_registry.json`
- **THEN** the system logs that the file is already ingested and does not re-embed or re-store it

#### Scenario: New file is processed and registered
- **WHEN** a file's MD5 hash is not present in `source_registry.json`
- **THEN** the system processes the file and writes its path and hash to `source_registry.json` upon successful ingestion

#### Scenario: Modified file is re-ingested
- **WHEN** a file exists in `source_registry.json` by path but its content hash has changed
- **THEN** the system re-ingests the file and updates the registry entry

### Requirement: Embedding and ChromaDB storage
The system SHALL embed each chunk using `nomic-embed-text` via Ollama and persist vectors in a local file-based ChromaDB collection.

#### Scenario: Chunks are embedded and stored
- **WHEN** a document is successfully chunked
- **THEN** all chunks are embedded via Ollama and upserted into the ChromaDB collection at the configured path

#### Scenario: ChromaDB collection is queryable after ingestion
- **WHEN** ingestion completes for at least one document
- **THEN** a similarity search against the ChromaDB collection returns relevant results for a query related to the ingested content

### Requirement: Config-driven behaviour
The system SHALL read all tuneable parameters from environment variables via `config.py` using pydantic-settings. No values SHALL be hardcoded in the pipeline code.

#### Scenario: Chunk size and overlap are configurable
- **WHEN** `CHUNK_SIZE` and `CHUNK_OVERLAP` are set in `.env`
- **THEN** the splitter uses those values without any code change

#### Scenario: Missing required config raises a clear error
- **WHEN** a required env variable (e.g., `OLLAMA_BASE_URL`) is absent
- **THEN** the system raises a pydantic `ValidationError` at startup before processing any files

### Requirement: CLI entry point
The system SHALL provide `ingest.py` as a runnable entry point accepting a `--source` argument pointing to the directory of documents to ingest.

#### Scenario: Successful single-file ingestion
- **WHEN** `python ingest.py --source sources/` is run with one TXT file in `sources/`
- **THEN** the file is parsed, cleaned, chunked, embedded, and stored without error, and `source_registry.json` is updated

#### Scenario: Re-run skips already-ingested files
- **WHEN** `python ingest.py --source sources/` is run a second time with no new files
- **THEN** no files are re-embedded and the process exits cleanly with a log indicating all files were already ingested
