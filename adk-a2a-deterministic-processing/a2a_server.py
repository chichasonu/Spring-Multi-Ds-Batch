"""
A2A Server - Exposes the deterministic processing pipeline via A2A protocol.

This server wraps the ADK document processing pipeline as an A2A-compliant
server with Agent Card, JSON-RPC endpoints, and SSE streaming.

Usage:
    export OPENAI_API_KEY="your-key"
    python a2a_server.py
"""

import os
import sys

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm

from agents.workflow import document_processing_pipeline, quality_refinement_loop

# Load environment variables
load_dotenv()


def create_a2a_app():
    """Create and return the A2A application wrapping the processing pipeline.

    The to_a2a() function from Google ADK wraps the agent into a full
    A2A-compliant server with:
    - Agent Card (auto-generated from agent name/description)
    - JSON-RPC endpoints for task submission
    - SSE streaming for real-time progress updates

    Returns:
        The A2A application (ASGI app).
    """
    # Wrap the deterministic pipeline as an A2A server
    a2a_app = to_a2a(
        agent=document_processing_pipeline,
        host="0.0.0.0",
        port=8000,
    )
    return a2a_app


def main() -> None:
    """Start the A2A server."""
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is required.")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("  A2A Server - Deterministic Document Processing Pipeline")
    print("  Protocol: Agent-to-Agent (A2A)")
    print("  Framework: Google ADK")
    print("  Model: OpenAI GPT-4o-mini via LiteLLM")
    print("=" * 70)
    print("\nStarting A2A server on http://0.0.0.0:8000")
    print("Agent Card available at: http://localhost:8000/.well-known/agent.json")
    print("\nPress Ctrl+C to stop the server.\n")

    # to_a2a() starts the server automatically when called with host/port
    # For manual control, we can also get the app and run with uvicorn:
    import uvicorn

    a2a_app = to_a2a(
        agent=document_processing_pipeline,
        host="0.0.0.0",
        port=8000,
    )

    # If to_a2a returns an ASGI app, run it with uvicorn
    if a2a_app is not None:
        uvicorn.run(a2a_app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
