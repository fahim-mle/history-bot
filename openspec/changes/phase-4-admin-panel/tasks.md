## 1. Registry Schema Update

- [x] 1.1 Update `ingest_file()` in `ingest.py` to write `{"hash": md5, "ingested_at": datetime.utcnow().isoformat()}` instead of a bare hash string
- [x] 1.2 Update `ingest_file()` registry lookup to read both old (string) and new (dict) formats — treat a string value as `{"hash": value, "ingested_at": "unknown"}`
- [x] 1.3 Update `compute_md5` call sites in `ingest_file()` to extract hash from the new dict shape when comparing

## 2. Multipage Structure

- [x] 2.1 Create `pages/` directory
- [x] 2.2 Copy current `app.py` content to `pages/1_Chat.py` unchanged
- [x] 2.3 Strip `app.py` to a minimal shell: keep only `st.set_page_config(page_title="History Bot", layout="centered")`

## 3. Admin Panel — File Upload

- [x] 3.1 In `pages/2_Admin.py`, add `st.set_page_config(page_title="Admin — History Bot", layout="centered")` and page header
- [x] 3.2 Add `st.file_uploader` accepting `["pdf", "epub", "txt", "md"]`, `accept_multiple_files=True`
- [x] 3.3 On upload: write each file's bytes to `sources/<filename>` using `pathlib`
- [x] 3.4 For each saved file: call `ingest_file(path, registry, vector_store)` inside `st.spinner(f"Ingesting {filename}…")` and collect result messages
- [x] 3.5 Load registry and vector store once before the loop; save registry after all files are processed
- [x] 3.6 Display per-file success/skip messages after ingestion completes

## 4. Admin Panel — Sources Table

- [x] 4.1 Implement `load_sources_table()` — reads `source_registry.json`, returns a list of dicts with keys `filename`, `type`, `ingested_at`; returns empty list if file absent
- [x] 4.2 Render table with `st.dataframe(df, use_container_width=True)` below an "Ingested Sources" subheader
- [x] 4.3 Show "No sources ingested yet." message when the table is empty

## 5. Admin Panel — Manual Sync

- [x] 5.1 Add "Sync sources/" button; on click, iterate all supported files in `sources/`, call `ingest_file()` for each, save registry, report how many were new vs skipped

## 6. Verification

- [ ] 6.1 Run `streamlit run app.py` — confirm sidebar shows "Chat" and "Admin" pages, chat UI works as before
- [ ] 6.2 Upload a PDF or EPUB via the Admin page — confirm file appears in `sources/`, is ingested into ChromaDB, and shows in the sources table
- [ ] 6.3 Upload the same file again — confirm "already ingested" message, no re-embedding
- [ ] 6.4 Manually place a file in `sources/` and click "Sync sources/" — confirm it is ingested and appears in the table
- [ ] 6.5 Check `source_registry.json` — confirm new entries have `hash` and `ingested_at` fields; confirm old entries (if any) still load without error
