# Deterministic Processing Pipeline - Google ADK + A2A + OpenAI

A deterministic document processing pipeline built with **Google Agent Development Kit (ADK)**, the **Agent-to-Agent (A2A)** protocol, and **OpenAI** models.

## Overview

This project demonstrates how to build **deterministic, predictable AI workflows** using Google ADK's Workflow Agents. Unlike LLM-routed systems where execution order varies per run, this pipeline guarantees the same processing steps execute in the same order every time.

### Architecture

```
SequentialAgent (document_processing_pipeline)
│
├── Step 1: Content Extractor (LlmAgent)
│       Extracts key content, word stats, keywords
│
├── Step 2: ParallelAgent (parallel_analysis)
│       ├── Sentiment Analyzer (LlmAgent)  ─┐
│       ├── Entity Extractor (LlmAgent)     ├── Run concurrently
│       └── Topic Classifier (LlmAgent)    ─┘
│
└── Step 3: Report Generator (LlmAgent)
        Combines all analyses into final report

LoopAgent (quality_refinement_loop)
│
├── Draft Writer (LlmAgent)
└── Quality Critic (LlmAgent)
        Iterates until quality score ≥ 8/10 (max 3 iterations)
```

### Key Concepts

| Pattern | ADK Agent | Purpose |
|---------|-----------|---------|
| **Sequential** | `SequentialAgent` | Guaranteed execution order: A → B → C |
| **Parallel** | `ParallelAgent` | Concurrent independent tasks: A \| B \| C |
| **Loop** | `LoopAgent` | Iterative refinement until quality threshold |
| **A2A Protocol** | `to_a2a()` | Expose pipeline as inter-agent service |

### Why Deterministic?

| Dimension | LLM Routing | Workflow Agents (This Project) |
|-----------|-------------|-------------------------------|
| Predictability | Low (varies per run) | **High (guaranteed order)** |
| Testability | Hard (many paths) | **Easy (one path)** |
| Performance | Slower (LLM reasons at each step) | **Faster (no intermediate decisions)** |
| Debugging | Hard | **Easy (follows prescribed order)** |

## Tech Stack

- **Google ADK** (`google-adk[a2a]`) - Agent framework with workflow orchestration
- **A2A Protocol** - Agent-to-Agent communication standard
- **OpenAI GPT-4o-mini** - LLM model (via LiteLLM integration)
- **Python 3.12+** - Runtime

## Project Structure

```
adk-a2a-deterministic-processing/
├── agents/
│   ├── __init__.py              # Package init
│   ├── tools.py                 # Custom tool functions (word count, keywords, readability)
│   ├── processing_agents.py     # Individual LlmAgent definitions
│   └── workflow.py              # Workflow compositions (Sequential, Parallel, Loop)
├── main.py                      # Direct local runner (no A2A)
├── a2a_server.py                # A2A protocol server
├── a2a_client.py                # A2A protocol client/consumer
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

## Setup

### 1. Install Dependencies

```bash
cd adk-a2a-deterministic-processing
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Or export directly:
export OPENAI_API_KEY="your-openai-api-key"
```

## Usage

### Option 1: Direct Local Execution

Run the pipeline directly without A2A protocol (simplest way to test):

```bash
python main.py
```

This will:
1. Process a sample tech article through the full Sequential + Parallel pipeline
2. Run the LoopAgent quality refinement demo
3. Print all results to the console

### Option 2: A2A Protocol (Server + Client)

**Terminal 1** - Start the A2A server:

```bash
python a2a_server.py
```

The server starts on `http://localhost:8000` with:
- Agent Card at `/.well-known/agent.json`
- JSON-RPC endpoint for task submission
- SSE streaming for real-time progress

**Terminal 2** - Run the A2A client:

```bash
python a2a_client.py
```

The client will:
1. Discover the agent's capabilities via the Agent Card
2. Send a document for processing via JSON-RPC
3. Demonstrate SSE streaming for real-time updates
4. Display the final processed report

## How It Works

### Deterministic Pipeline (SequentialAgent)

The `SequentialAgent` guarantees execution order. Each sub-agent completes before the next begins:

```python
document_processing_pipeline = SequentialAgent(
    name="document_processing_pipeline",
    sub_agents=[content_extractor, parallel_analysis, report_generator],
)
```

### Concurrent Analysis (ParallelAgent)

The `ParallelAgent` runs independent analyses simultaneously for better performance:

```python
parallel_analysis = ParallelAgent(
    name="parallel_analysis",
    sub_agents=[sentiment_analyzer, entity_extractor, topic_classifier],
)
```

### Iterative Refinement (LoopAgent)

The `LoopAgent` repeats a write-critique cycle until quality is sufficient:

```python
quality_refinement_loop = LoopAgent(
    name="quality_refinement_loop",
    sub_agents=[draft_writer, quality_critic],
    max_iterations=3,
)
```

### A2A Protocol Exposure

One function call wraps the entire pipeline into an A2A-compliant server:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

a2a_app = to_a2a(agent=document_processing_pipeline, host="0.0.0.0", port=8000)
```

### OpenAI Model Integration

All agents use OpenAI models via ADK's LiteLLM integration:

```python
from google.adk.models.lite_llm import LiteLlm

OPENAI_MODEL = LiteLlm(model="openai/gpt-4o-mini")

content_extractor = LlmAgent(
    name="content_extractor",
    model=OPENAI_MODEL,
    instruction="...",
    tools=[extract_word_count, extract_keywords],
)
```

## Custom Tools

The pipeline includes several custom tools that agents can invoke:

| Tool | Description |
|------|-------------|
| `extract_word_count` | Counts words, sentences, paragraphs |
| `extract_keywords` | Frequency-based keyword extraction |
| `calculate_readability_score` | Flesch reading ease score |
| `generate_processing_metadata` | Pipeline metadata (timestamp, version) |
| `format_analysis_report` | Structures all analyses into a report |

## References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol Specification](https://a2a-protocol.org/)
- [A2A Python SDK](https://github.com/google-a2a/a2a-python)
- [ADK Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/)
- [LiteLLM + ADK Tutorial](https://docs.litellm.ai/docs/tutorials/google_adk)
