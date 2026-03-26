# rag-chain

### Requirement: Retrieval from ChromaDB
The system SHALL load the existing ChromaDB collection using the same embedding model and collection name as the ingestion pipeline, and use it as the retriever for all queries.

#### Scenario: Collection loads successfully
- **WHEN** `chat.py` initialises
- **THEN** the ChromaDB collection at `CHROMA_PATH` is opened with `nomic-embed-text` embeddings without error

#### Scenario: Empty collection warning
- **WHEN** `chat.py` initialises and the collection contains zero documents
- **THEN** the system logs a warning that no documents are indexed and the user should run ingestion first

### Requirement: Configurable top-k retrieval
The system SHALL retrieve the top-k most relevant chunks for each query, where k is read from config.

#### Scenario: Retrieval uses configured k
- **WHEN** `RETRIEVAL_K=5` is set in `.env`
- **THEN** each query retrieves exactly 5 chunks from ChromaDB

#### Scenario: k is configurable without code change
- **WHEN** `RETRIEVAL_K` is changed in `.env` and the process is restarted
- **THEN** the new k value is used for retrieval

### Requirement: Follow-up question condensing
The system SHALL rewrite follow-up questions using conversation history into standalone questions before retrieval, so that pronouns and implicit references resolve correctly.

#### Scenario: Follow-up resolves correctly
- **WHEN** the user asks "what happened next?" after a prior exchange about a historical event
- **THEN** the condense step produces a standalone question that includes the subject of the prior exchange before retrieval is performed

#### Scenario: First question is passed through unchanged
- **WHEN** there is no prior conversation history
- **THEN** the user's question is used directly for retrieval without a condense call

### Requirement: Context-grounded answer generation
The system SHALL generate answers using only the retrieved chunks. If the answer cannot be found in the retrieved context, the system SHALL respond with a clear "I don't know" message rather than fabricating an answer.

#### Scenario: In-context question is answered
- **WHEN** the user asks a question whose answer is present in the ingested documents
- **THEN** the system returns a factual answer derived from the retrieved chunks

#### Scenario: Out-of-context question returns "I don't know"
- **WHEN** the user asks a question whose answer is not present in any ingested document
- **THEN** the system responds with a message indicating it cannot find the answer in the available sources, without guessing

### Requirement: Source attribution
The system SHALL include source references with every answer, showing the filename and a brief excerpt from each retrieved chunk used.

#### Scenario: Sources are listed with answer
- **WHEN** the system returns an answer
- **THEN** the response includes at least one source reference showing the originating filename

#### Scenario: Sources reflect actual retrieved chunks
- **WHEN** a specific document was the basis for an answer
- **THEN** that document's filename appears in the source list

### Requirement: Session conversation memory
The system SHALL maintain conversation history within a session so that follow-up questions have access to prior exchanges. Memory SHALL reset when the process restarts.

#### Scenario: Follow-up uses prior context
- **WHEN** the user asks a follow-up question referencing a prior answer in the same session
- **THEN** the response is coherent with the prior exchange

#### Scenario: Memory resets on restart
- **WHEN** the process is restarted and a follow-up question is asked without prior context
- **THEN** the system treats it as a new first question with no history

### Requirement: CLI interaction loop
The system SHALL provide a REPL-style command-line interface in `chat.py` that accepts user input, runs the RAG chain, and prints the answer with sources. Typing `exit` or `quit` SHALL terminate the session.

#### Scenario: Question produces answer and sources
- **WHEN** the user types a question at the CLI prompt and presses Enter
- **THEN** the system prints the answer followed by the source references

#### Scenario: Session exits cleanly
- **WHEN** the user types `exit` or `quit`
- **THEN** the process terminates without error
