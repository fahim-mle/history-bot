"""
history-bot RAG chat interface.

Usage:
    python chat.py
"""

import logging
import warnings

# Import langchain packages first; langchain_classic.__init__ calls
# surface_langchain_deprecation_warnings() which prepends a "default" filter.
# We add our "ignore" filter AFTER all imports so it sits at position 0 and wins.
from langchain_chroma import Chroma
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_core._api import LangChainDeprecationWarning
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings

# Suppress LangChain deprecation warnings (task 4.3).
# Must come after langchain imports so this filter is first in the chain.
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

from config import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Vector store (task 2.1)
# ---------------------------------------------------------------------------

def get_vector_store() -> Chroma:
    """Load the existing ChromaDB collection (same as ingest.py)."""
    embeddings = OllamaEmbeddings(
        model=settings.embed_model,
        base_url=settings.ollama_base_url,
    )
    return Chroma(
        collection_name="history",
        embedding_function=embeddings,
        persist_directory=settings.chroma_path,
    )


def check_collection_not_empty(vector_store: Chroma) -> None:
    """Warn if the collection has no documents (task 2.2)."""
    count = vector_store._collection.count()
    if count == 0:
        log.warning(
            "ChromaDB collection is empty — run `python ingest.py` first to index your documents."
        )
    else:
        log.info("Collection loaded: %d chunks indexed.", count)


# ---------------------------------------------------------------------------
# Prompt templates (tasks 3.1, 3.2)
# ---------------------------------------------------------------------------

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
    """Given the following conversation and a follow-up question, rephrase the \
follow-up question to be a standalone question that fully captures the intent \
without requiring the chat history.

Chat history:
{chat_history}

Follow-up question: {question}

Standalone question:"""
)

QA_PROMPT = PromptTemplate.from_template(
    """You are a historian. Use the sources below as your primary evidence.
    Synthesize across them, draw connections, and reason like a historian would.
Cite your sources. If evidence is insufficient, say so.

If the answer cannot be found in the context, respond with:
"I don't know based on the available sources."

Context:
{context}

Question: {question}

Answer:"""
)


# ---------------------------------------------------------------------------
# RAG chain (tasks 4.1, 4.2)
# ---------------------------------------------------------------------------

def build_chain(vector_store: Chroma) -> ConversationalRetrievalChain:
    """Build the ConversationalRetrievalChain with memory."""
    llm = ChatOllama(
        model=settings.llm_model,
        base_url=settings.ollama_base_url,
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
    retriever = vector_store.as_retriever(
        search_kwargs={"k": settings.retrieval_k}
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,
        verbose=False,
    )


# ---------------------------------------------------------------------------
# Source formatting (task 5.1)
# ---------------------------------------------------------------------------

def format_sources(source_docs: list) -> str:
    """Format retrieved source documents into a readable source list."""
    if not source_docs:
        return "  (no sources)"
    seen: set[str] = set()
    lines: list[str] = []
    for doc in source_docs:
        filename = doc.metadata.get("source", "unknown")
        excerpt = doc.page_content[:150].replace("\n", " ").strip()
        if filename not in seen:
            seen.add(filename)
            lines.append(f"  [{filename}]")
        lines.append(f"    …{excerpt}…")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI loop (tasks 6.1, 6.2, 6.3)
# ---------------------------------------------------------------------------

def main() -> None:
    print("history-bot — type your question, or 'exit' to quit.\n")

    vector_store = get_vector_store()
    check_collection_not_empty(vector_store)
    chain = build_chain(vector_store)

    print()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        result = chain.invoke({"question": user_input})
        answer = result.get("answer", "")
        sources = result.get("source_documents", [])

        print(f"\nBot: {answer}")
        print("\nSources:")
        print(format_sources(sources))
        print()


if __name__ == "__main__":
    main()
