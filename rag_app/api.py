"""FastAPI service for the RAG intent classifier."""

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag_app.config import DEFAULT_TOP_K, FASTAPI_HOST, FASTAPI_PORT
from rag_app.rag_chain import get_classifier

app = FastAPI(
    title="RAG Intent Classifier API",
    description=(
        "A hybrid RAG-based intent classifier using LangChain, ChromaDB, "
        "and BM25 with Gemini Flash / OpenAI GPT."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str = Field(..., description="The user utterance to classify")
    top_k: int = Field(
        default=DEFAULT_TOP_K,
        ge=1,
        le=20,
        description="Number of top documents to retrieve (default: 1)",
    )


class RetrievedUtterance(BaseModel):
    utterance: str
    intent: str


class QueryResponse(BaseModel):
    query: str
    predicted_intent: str
    top_k: int
    retrieved_utterances: list[RetrievedUtterance]


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/classify", response_model=QueryResponse)
def classify_intent(request: QueryRequest):
    """
    Classify the intent of a user utterance using hybrid RAG search.

    The system uses a combination of BM25 (keyword) and vector similarity
    search to find the most relevant utterances, then uses an LLM to
    determine the final intent.
    """
    try:
        classifier = get_classifier()
        result = classifier.query(
            user_query=request.query,
            top_k=request.top_k,
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/classify", response_model=QueryResponse)
def classify_intent_get(
    query: str = Query(..., description="The user utterance to classify"),
    top_k: int = Query(
        default=DEFAULT_TOP_K,
        ge=1,
        le=20,
        description="Number of top documents to retrieve",
    ),
):
    """GET endpoint for intent classification."""
    try:
        classifier = get_classifier()
        result = classifier.query(user_query=query, top_k=top_k)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the FastAPI server."""
    uvicorn.run(
        "rag_app.api:app",
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
