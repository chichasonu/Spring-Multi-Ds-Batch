"""Vector store module for loading data and building ChromaDB + BM25 indexes."""

import json
from typing import Optional

from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

from rag_app.config import (
    LLM_PROVIDER,
    LLMProvider,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    DATA_FILE_PATH,
    BM25_WEIGHT,
    VECTOR_WEIGHT,
)


def _get_embedding_function():
    """Return the appropriate embedding function based on the configured provider."""
    if LLM_PROVIDER == LLMProvider.OPENAI:
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model="text-embedding-3-small")
    else:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")


def load_intent_data(file_path: Optional[str] = None) -> list[Document]:
    """Load intent-utterance data from a JSON file and return as LangChain Documents."""
    path = file_path or DATA_FILE_PATH
    with open(path, "r") as f:
        data = json.load(f)

    documents = []
    for item in data:
        intent = item["intent"]
        for utterance in item["utterances"]:
            doc = Document(
                page_content=utterance,
                metadata={"intent": intent},
            )
            documents.append(doc)
    return documents


def build_chroma_vector_store(documents: list[Document]) -> Chroma:
    """Build and persist a ChromaDB vector store from documents."""
    embedding_fn = _get_embedding_function()
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_fn,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION_NAME,
    )
    return vector_store


def get_chroma_vector_store() -> Chroma:
    """Load an existing ChromaDB vector store from disk."""
    embedding_fn = _get_embedding_function()
    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding_fn,
        collection_name=CHROMA_COLLECTION_NAME,
    )
    return vector_store


def build_hybrid_retriever(
    documents: list[Document],
    vector_store: Chroma,
    top_k: int = 1,
) -> EnsembleRetriever:
    """Build a hybrid retriever combining BM25 and vector search."""
    bm25_retriever = BM25Retriever.from_documents(documents, k=top_k)

    vector_retriever = vector_store.as_retriever(
        search_kwargs={"k": top_k},
    )

    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[BM25_WEIGHT, VECTOR_WEIGHT],
    )

    return ensemble_retriever
