# Hybrid RAG Intent Classifier

A Retrieval-Augmented Generation (RAG) application that classifies user utterances into intents using **hybrid search** (BM25 + Vector similarity).

## Architecture

- **LangChain** — orchestration framework
- **ChromaDB** — vector store for semantic search
- **BM25** — keyword-based retrieval via `rank-bm25`
- **EnsembleRetriever** — combines BM25 + vector search (hybrid RAG)
- **LLM** — Gemini Flash or OpenAI GPT for final intent prediction
- **Embeddings** — OpenAI `text-embedding-3-small` or Google `embedding-001` (no HuggingFace)
- **FastAPI** — REST API backend service
- **Streamlit** — interactive web UI

## How It Works

1. Utterance-intent pairs are loaded from `data/intents.json`
2. Utterances are indexed in both ChromaDB (vector embeddings) and a BM25 index
3. When a user submits a query:
   - **BM25** retrieves keyword-matched utterances
   - **Vector search** retrieves semantically similar utterances
   - **EnsembleRetriever** merges and re-ranks results from both
   - The **LLM** analyzes the top-k retrieved utterances and predicts the intent
4. The predicted intent and matching utterances are returned

## Setup

### 1. Install Dependencies

```bash
cd rag_app
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your API key:
- **Gemini Flash**: Set `GOOGLE_API_KEY`
- **OpenAI GPT**: Set `OPENAI_API_KEY`

### 3. Start the FastAPI Backend

```bash
python -m rag_app.api
```

The API will be available at `http://localhost:8000`.

### 4. Start the Streamlit UI

```bash
streamlit run rag_app/streamlit_app.py
```

The UI will be available at `http://localhost:8501`.

## API Endpoints

### POST /classify
Classify an utterance's intent.

**Request Body:**
```json
{
  "query": "I want to check my account balance",
  "top_k": 1
}
```

**Response:**
```json
{
  "query": "I want to check my account balance",
  "predicted_intent": "check_balance",
  "top_k": 1,
  "retrieved_utterances": [
    {
      "utterance": "What is my account balance?",
      "intent": "check_balance"
    }
  ]
}
```

### GET /classify?query=...&top_k=1
Same as POST but via query parameters.

### GET /health
Health check endpoint.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | — | Google API key for Gemini Flash |
| `OPENAI_API_KEY` | — | OpenAI API key (alternative to Gemini) |
| `DEFAULT_TOP_K` | `1` | Default number of results to retrieve |
| `BM25_WEIGHT` | `0.4` | Weight for BM25 in hybrid search |
| `VECTOR_WEIGHT` | `0.6` | Weight for vector search in hybrid search |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB persistence directory |

## Custom Data

Replace `data/intents.json` with your own utterance-intent data following this format:

```json
[
  {
    "intent": "your_intent_name",
    "utterances": [
      "example utterance 1",
      "example utterance 2"
    ]
  }
]
```
