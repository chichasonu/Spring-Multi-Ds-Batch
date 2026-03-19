"""
A2A Client - Consumes the deterministic processing pipeline via A2A protocol.

This client connects to the A2A server, discovers the agent's capabilities
through the Agent Card, and sends documents for processing.

Usage:
    # First, start the A2A server in another terminal:
    #   python a2a_server.py

    # Then run the client:
    python a2a_client.py
"""

import asyncio
import json
import sys

import httpx


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
A2A_SERVER_URL = "http://localhost:8000"
AGENT_CARD_PATH = "/.well-known/agent.json"


# ---------------------------------------------------------------------------
# Sample document for testing
# ---------------------------------------------------------------------------
SAMPLE_DOCUMENT = """
The European Union's Artificial Intelligence Act, which came into force on
August 1, 2024, represents the world's most comprehensive regulatory framework
for AI systems. The legislation introduces a risk-based classification system
that categorizes AI applications into four tiers: unacceptable risk, high risk,
limited risk, and minimal risk.

Under the new law, AI systems used for social scoring by governments and
real-time biometric surveillance in public spaces are banned outright.
High-risk applications, including those used in healthcare, education, and
law enforcement, must meet strict requirements for transparency, data quality,
human oversight, and cybersecurity.

EU Commissioner Thierry Breton stated that "the AI Act ensures that Europeans
can trust AI technology while allowing innovation to flourish." The regulation
includes fines of up to 35 million euros or 7% of global annual revenue for
non-compliance.

Tech companies including Meta, Google, and Microsoft have expressed mixed
reactions. While supporting the principle of AI safety, industry leaders warn
that excessive regulation could drive AI innovation outside Europe. The
European AI Office, established in Brussels, will oversee enforcement with a
team of 140 specialists.

Small and medium enterprises (SMEs) will receive a two-year grace period
for compliance, along with access to regulatory sandboxes for testing new
AI applications. The European Commission has allocated 1 billion euros to
support AI development that aligns with the new regulatory framework.
"""


async def discover_agent(client: httpx.AsyncClient) -> dict:
    """Discover the remote agent's capabilities via the Agent Card.

    The Agent Card is a JSON document served at /.well-known/agent.json
    that describes the agent's name, description, skills, and endpoints.

    Args:
        client: The HTTP client to use for the request.

    Returns:
        The Agent Card as a dictionary.
    """
    print("\n[1] Discovering agent capabilities...")
    response = await client.get(f"{A2A_SERVER_URL}{AGENT_CARD_PATH}")

    if response.status_code == 200:
        agent_card = response.json()
        print(f"    Agent Name: {agent_card.get('name', 'Unknown')}")
        print(f"    Description: {agent_card.get('description', 'N/A')}")
        skills = agent_card.get("skills", [])
        if skills:
            print(f"    Skills: {len(skills)} available")
            for skill in skills:
                print(f"      - {skill.get('name', 'unnamed')}: {skill.get('description', '')}")
        return agent_card
    else:
        print(f"    Failed to discover agent: HTTP {response.status_code}")
        return {}


async def send_task(client: httpx.AsyncClient, document: str) -> dict:
    """Send a document processing task to the A2A server via JSON-RPC.

    A2A uses JSON-RPC 2.0 for task communication. The client sends a
    'tasks/send' request with the document as a message.

    Args:
        client: The HTTP client to use for the request.
        document: The document text to process.

    Returns:
        The task result as a dictionary.
    """
    print("\n[2] Sending document processing task via A2A JSON-RPC...")

    # A2A JSON-RPC request format
    jsonrpc_request = {
        "jsonrpc": "2.0",
        "id": "task-001",
        "method": "tasks/send",
        "params": {
            "id": "task-001",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": f"Process this document through the deterministic pipeline:\n\n{document}",
                    }
                ],
            },
        },
    }

    print(f"    Request method: {jsonrpc_request['method']}")
    print(f"    Document length: {len(document)} characters")

    response = await client.post(
        A2A_SERVER_URL,
        json=jsonrpc_request,
        timeout=120.0,
    )

    if response.status_code == 200:
        result = response.json()
        print("    Task submitted successfully!")
        return result
    else:
        print(f"    Task failed: HTTP {response.status_code}")
        print(f"    Response: {response.text[:500]}")
        return {"error": f"HTTP {response.status_code}"}


async def send_task_streaming(client: httpx.AsyncClient, document: str) -> None:
    """Send a task with SSE streaming to receive real-time progress updates.

    A2A supports Server-Sent Events (SSE) for streaming task progress.
    The client receives incremental updates as the pipeline processes.

    Args:
        client: The HTTP client to use for the request.
        document: The document text to process.
    """
    print("\n[3] Sending task with SSE streaming for real-time updates...")

    jsonrpc_request = {
        "jsonrpc": "2.0",
        "id": "task-002",
        "method": "tasks/sendSubscribe",
        "params": {
            "id": "task-002",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": f"Process this document:\n\n{document}",
                    }
                ],
            },
        },
    }

    print("    Streaming task progress...")
    try:
        async with client.stream(
            "POST",
            A2A_SERVER_URL,
            json=jsonrpc_request,
            timeout=120.0,
        ) as response:
            if response.status_code != 200:
                print(f"    Streaming failed: HTTP {response.status_code}")
                return

            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data:
                        try:
                            event = json.loads(data)
                            status = event.get("result", {}).get("status", {})
                            state = status.get("state", "unknown")
                            message = status.get("message", {})
                            print(f"    [{state}] {json.dumps(message)[:200]}")
                        except json.JSONDecodeError:
                            print(f"    [raw] {data[:200]}")
    except httpx.ReadTimeout:
        print("    Streaming timed out (this is normal for long-running tasks)")
    except Exception as e:
        print(f"    Streaming error: {e}")


async def main() -> None:
    """Main client entry point demonstrating A2A protocol interaction."""
    print("\n" + "=" * 70)
    print("  A2A Client - Document Processing Consumer")
    print("  Connecting to A2A server at:", A2A_SERVER_URL)
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        # Step 1: Discover the agent
        try:
            agent_card = await discover_agent(client)
        except httpx.ConnectError:
            print(f"\n    ERROR: Cannot connect to A2A server at {A2A_SERVER_URL}")
            print("    Make sure the A2A server is running: python a2a_server.py")
            sys.exit(1)

        if not agent_card:
            print("\n    WARNING: Could not discover agent, proceeding anyway...")

        # Step 2: Send a task (standard request/response)
        result = await send_task(client, SAMPLE_DOCUMENT)

        # Display result
        print("\n[Result] Task Response:")
        print("-" * 50)
        if "result" in result:
            task_result = result["result"]
            artifacts = task_result.get("artifacts", [])
            if artifacts:
                for artifact in artifacts:
                    parts = artifact.get("parts", [])
                    for part in parts:
                        if "text" in part:
                            print(part["text"])
            else:
                status = task_result.get("status", {})
                message = status.get("message", {})
                parts = message.get("parts", [])
                for part in parts:
                    if "text" in part:
                        print(part["text"])
                if not parts:
                    print(json.dumps(task_result, indent=2)[:2000])
        elif "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(json.dumps(result, indent=2)[:2000])

        # Step 3: Demonstrate streaming (optional)
        print("\n" + "-" * 50)
        await send_task_streaming(client, SAMPLE_DOCUMENT)

    print("\n" + "=" * 70)
    print("  A2A Client completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
