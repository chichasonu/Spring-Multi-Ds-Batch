"""RAG chain module for intent classification from utterance queries."""

from langchain.schema import Document
from langchain_chroma import Chroma

from rag_app.config import LLM_PROVIDER, LLMProvider
from rag_app.vector_store import (
    load_intent_data,
    build_chroma_vector_store,
    build_hybrid_retriever,
)


def _get_llm():
    """Return the appropriate LLM based on the configured provider."""
    if LLM_PROVIDER == LLMProvider.OPENAI:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    else:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)


class RAGIntentClassifier:
    """Hybrid RAG-based intent classifier using BM25 + vector search."""

    def __init__(self):
        self.documents: list[Document] = []
        self.vector_store: Chroma | None = None
        self.llm = _get_llm()
        self._initialized = False

    def initialize(self) -> None:
        """Load data and build indexes."""
        self.documents = load_intent_data()
        self.vector_store = build_chroma_vector_store(self.documents)
        self._initialized = True

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def query(self, user_query: str, top_k: int = 1) -> dict:
        """
        Query the hybrid retriever and return the predicted intent.

        Args:
            user_query: The user's utterance to classify.
            top_k: Number of top documents to retrieve.

        Returns:
            A dict with the predicted intent, matched utterances, and LLM explanation.
        """
        if not self._initialized or self.vector_store is None:
            raise RuntimeError("RAGIntentClassifier not initialized. Call initialize() first.")

        retriever = build_hybrid_retriever(
            documents=self.documents,
            vector_store=self.vector_store,
            top_k=top_k,
        )

        retrieved_docs = retriever.invoke(user_query)

        # Limit to top_k results (EnsembleRetriever may return more)
        retrieved_docs = retrieved_docs[:top_k]

        # Build context from retrieved documents
        context_lines = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_lines.append(
                f"{i}. Utterance: \"{doc.page_content}\" -> Intent: \"{doc.metadata['intent']}\""
            )
        context = "\n".join(context_lines)

        # Use LLM to confirm / refine the intent prediction
        prompt = (
            f"You are an intent classifier. Given the user's query and the most similar "
            f"utterances retrieved from the database, determine the correct intent.\n\n"
            f"User Query: \"{user_query}\"\n\n"
            f"Retrieved similar utterances and their intents:\n{context}\n\n"
            f"Based on the retrieved results, what is the most likely intent for the "
            f"user's query? Return ONLY the intent name, nothing else."
        )

        llm_response = self.llm.invoke(prompt)
        predicted_intent = llm_response.content.strip()

        return {
            "query": user_query,
            "predicted_intent": predicted_intent,
            "top_k": top_k,
            "retrieved_utterances": [
                {
                    "utterance": doc.page_content,
                    "intent": doc.metadata["intent"],
                }
                for doc in retrieved_docs
            ],
        }


# Singleton instance
_classifier: RAGIntentClassifier | None = None


def get_classifier() -> RAGIntentClassifier:
    """Get or create the singleton RAGIntentClassifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = RAGIntentClassifier()
        _classifier.initialize()
    return _classifier
