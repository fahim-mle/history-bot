## ADDED Requirements

### Requirement: Multipage app structure
The system SHALL use Streamlit's multipage convention with `app.py` as the entry shell, the chat UI at `pages/1_Chat.py`, and the admin panel at `pages/2_Admin.py`. Navigation between pages SHALL appear in the Streamlit sidebar automatically.

#### Scenario: Chat page accessible via sidebar
- **WHEN** the user opens the app
- **THEN** the sidebar shows "Chat" and "Admin" navigation entries and the chat UI is the default page

#### Scenario: Admin page accessible via sidebar
- **WHEN** the user clicks "Admin" in the sidebar
- **THEN** the admin panel page is displayed without reloading the browser

#### Scenario: Chat UI behaviour unchanged
- **WHEN** the user navigates to the Chat page
- **THEN** all phase-3 chat behaviours (session memory, sources expander, clear button) work identically to before

### Requirement: File upload and ingestion
The system SHALL provide a file uploader accepting PDF, EPUB, TXT, and MD files. Uploaded files SHALL be saved to the `sources/` directory and immediately ingested into ChromaDB using the existing ingestion pipeline.

#### Scenario: Uploaded file is saved and ingested
- **WHEN** the user uploads a supported file via the admin panel
- **THEN** the file is written to `sources/`, ingested via the pipeline, and a success message is shown

#### Scenario: Already-ingested file is skipped
- **WHEN** the user uploads a file that is already in `source_registry.json` with the same hash
- **THEN** the system reports the file was already ingested and does not re-embed it

#### Scenario: Unsupported file type is rejected
- **WHEN** the user uploads a file with an unsupported extension
- **THEN** the uploader does not accept the file (enforced via `type` parameter)

### Requirement: Ingested sources table
The system SHALL display a table of all ingested sources read from `source_registry.json`, showing the filename, file type, and ingestion timestamp for each entry.

#### Scenario: Table reflects current registry
- **WHEN** the admin page loads
- **THEN** every entry in `source_registry.json` is shown as a row in the table

#### Scenario: Table updates after upload
- **WHEN** a file is successfully uploaded and ingested
- **THEN** the sources table on next render includes the new entry

#### Scenario: Empty state shown when no files ingested
- **WHEN** `source_registry.json` does not exist or is empty
- **THEN** the table section shows a message indicating no sources have been ingested yet

### Requirement: Manual sync
The system SHALL provide a "Sync sources/" button that re-runs the ingestion pipeline on the `sources/` directory, picking up any files added outside the UI.

#### Scenario: Sync ingests new files
- **WHEN** a file has been manually placed in `sources/` and the user clicks "Sync sources/"
- **THEN** the file is ingested and added to `source_registry.json`

#### Scenario: Sync skips already-ingested files
- **WHEN** all files in `sources/` are already in `source_registry.json` with matching hashes
- **THEN** no files are re-embedded and a message confirms everything is up to date

### Requirement: Ingestion timestamp in registry
The system SHALL record an ISO-format `ingested_at` timestamp alongside the file hash in `source_registry.json` for each ingested file. The registry SHALL remain readable for entries written by earlier versions (hash-only string values).

#### Scenario: New ingestion writes timestamp
- **WHEN** a file is ingested for the first time
- **THEN** `source_registry.json` contains `{"hash": "...", "ingested_at": "YYYY-MM-DDTHH:MM:SS"}` for that file

#### Scenario: Old registry entries are readable
- **WHEN** `source_registry.json` contains entries in the old string-only format
- **THEN** the system reads them without error, treating the string as the hash and `ingested_at` as "unknown"
