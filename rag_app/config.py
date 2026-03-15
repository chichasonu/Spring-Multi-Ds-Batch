"""Configuration module for the RAG application."""

import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


# Determine which LLM provider to use based on available API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

if GOOGLE_API_KEY:
    LLM_PROVIDER = LLMProvider.GEMINI
elif OPENAI_API_KEY:
    LLM_PROVIDER = LLMProvider.OPENAI
else:
    raise ValueError(
        "No API key found. Please set either GOOGLE_API_KEY or OPENAI_API_KEY "
        "in your environment or .env file."
    )

# ChromaDB settings
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "intent_utterances")

# Data file path
DATA_FILE_PATH = os.getenv(
    "DATA_FILE_PATH",
    os.path.join(os.path.dirname(__file__), "data", "intents.json"),
)

# Default top-k results
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "1"))

# Hybrid search weights: [BM25_weight, vector_weight]
BM25_WEIGHT = float(os.getenv("BM25_WEIGHT", "0.4"))
VECTOR_WEIGHT = float(os.getenv("VECTOR_WEIGHT", "0.6"))

# FastAPI settings
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))
