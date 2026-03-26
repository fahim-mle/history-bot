## ADDED Requirements

### Requirement: Single-page chat interface
The system SHALL provide a single-page Streamlit application in `app.py` that displays a conversation between the user and the RAG chain using `st.chat_message` components.

#### Scenario: Messages render on load
- **WHEN** the user opens the app in a browser
- **THEN** all messages from the current session are displayed in order, with user messages in user bubbles and assistant replies in assistant bubbles

#### Scenario: New message appears after submit
- **WHEN** the user submits a question via `st.chat_input`
- **THEN** the user message and the assistant reply both appear in the chat without a full page reload

### Requirement: Session-persistent chain
The system SHALL initialise the RAG chain and message history exactly once per browser session, storing them in `st.session_state`, so that the chain and its memory survive Streamlit reruns.

#### Scenario: Chain initialises on first load
- **WHEN** a new browser session is started
- **THEN** the chain is built once and stored in `st.session_state`

#### Scenario: Chain is not rebuilt on subsequent interactions
- **WHEN** the user submits a second or later question in the same session
- **THEN** the same chain instance is reused with its conversation memory intact

### Requirement: Follow-up questions work correctly
The system SHALL pass each new question through the existing `ConversationalRetrievalChain` so that multi-turn conversations condense and resolve follow-up questions correctly.

#### Scenario: Follow-up resolves with context
- **WHEN** the user asks a follow-up question in the UI that references a prior answer
- **THEN** the assistant's reply is coherent with the prior exchange

### Requirement: Per-answer source expander
The system SHALL display an `st.expander` labelled with the source count below each assistant message, containing the formatted source references for that answer.

#### Scenario: Sources expander appears with answer
- **WHEN** the assistant returns an answer
- **THEN** a collapsed expander labelled "Sources (N)" appears below the assistant bubble

#### Scenario: Sources are visible on expand
- **WHEN** the user clicks the expander
- **THEN** the filenames and chunk excerpts for the retrieved documents are displayed

### Requirement: Clear conversation control
The system SHALL provide a sidebar button labelled "Clear conversation" that resets the session memory and display history, returning the chat to an empty state.

#### Scenario: Clear resets chat display
- **WHEN** the user clicks "Clear conversation"
- **THEN** the chat area is empty and no prior messages are visible

#### Scenario: Clear resets chain memory
- **WHEN** the user clicks "Clear conversation" and asks a follow-up question
- **THEN** the question is treated as a first question with no prior history

### Requirement: Loading indicator during chain call
The system SHALL display a spinner while the RAG chain is processing a query, so the user knows a response is in progress.

#### Scenario: Spinner shown during query
- **WHEN** the user submits a question
- **THEN** a loading spinner is visible until the assistant reply is ready
