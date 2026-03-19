"""
Direct runner for the deterministic document processing pipeline.

This script runs the pipeline locally without A2A protocol,
useful for testing and development.

Usage:
    export OPENAI_API_KEY="your-key"
    python main.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.workflow import document_processing_pipeline, quality_refinement_loop

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Sample documents for demonstration
# ---------------------------------------------------------------------------
SAMPLE_DOCUMENTS = {
    "tech_article": """
Artificial intelligence is transforming the healthcare industry at an unprecedented pace.
In 2024, researchers at Stanford University developed a new deep learning model capable of
detecting early-stage pancreatic cancer with 97% accuracy, outperforming human radiologists
by a significant margin. The model, trained on over 500,000 CT scans from hospitals across
the United States, Europe, and Asia, uses a novel attention mechanism that focuses on subtle
tissue density variations invisible to the human eye.

Dr. Sarah Chen, lead researcher on the project, noted that "this technology could save
hundreds of thousands of lives annually by catching cancers that would otherwise go
undetected until stage 3 or 4." The research was published in Nature Medicine and has
already attracted $50 million in funding from the Bill & Melinda Gates Foundation and
the National Institutes of Health.

However, critics raise concerns about algorithmic bias. A study by MIT's AI Ethics Lab
found that similar diagnostic AI systems showed 15% lower accuracy for patients from
underrepresented ethnic groups, primarily due to training data imbalances. The FDA has
responded by proposing new guidelines requiring demographic parity testing before
approval of AI-based medical devices.

The global AI in healthcare market is projected to reach $188 billion by 2030, growing
at a compound annual growth rate of 37%. Major players including Google Health, IBM Watson
Health, and Microsoft's Project InnerEye are investing heavily in this space, while
startups like PathAI and Tempus are disrupting traditional diagnostic workflows.
""",
    "business_report": """
Tesla reported record quarterly revenue of $25.2 billion in Q3 2024, a 9% increase
year-over-year, driven primarily by strong Model Y sales in China and Europe. The company
delivered 462,890 vehicles during the quarter, exceeding analyst expectations of 450,000
units. CEO Elon Musk highlighted the upcoming launch of the Cybertruck production ramp
and the company's progress on Full Self-Driving (FSD) technology.

Operating margins improved to 11.2%, up from 7.6% in Q2, thanks to manufacturing
efficiencies at Gigafactory Texas and cost reductions in battery production. The company's
energy generation and storage segment saw a 40% revenue increase, with Megapack
deployments reaching an all-time high of 5.2 GWh.

Despite the strong results, shares fell 3% in after-hours trading as investors expressed
concern over Musk's announcement to delay the Robotaxi unveiling to Q1 2025. Analysts
at Morgan Stanley maintained their overweight rating with a price target of $310, citing
the long-term potential of Tesla's AI and energy businesses. Meanwhile, competition from
Chinese EV makers BYD and NIO continues to intensify, with BYD surpassing Tesla in global
EV sales for the second consecutive quarter.
""",
}


async def run_pipeline(document_text: str, pipeline_name: str) -> None:
    """Run the document processing pipeline on the given text.

    Args:
        document_text: The document text to process.
        pipeline_name: A name for this pipeline run.
    """
    print(f"\n{'='*80}")
    print(f"  Running: {pipeline_name}")
    print(f"{'='*80}\n")

    session_service = InMemorySessionService()
    session = session_service.create_session(
        app_name="deterministic_processing",
        user_id="user_1",
        session_id=f"session_{pipeline_name}",
    )

    runner = Runner(
        agent=document_processing_pipeline,
        app_name="deterministic_processing",
        session_service=session_service,
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=f"Process this document:\n\n{document_text}")],
    )

    print("Processing document through deterministic pipeline...")
    print("  Step 1: Content Extraction")
    print("  Step 2: Parallel Analysis (Sentiment + Entities + Topics)")
    print("  Step 3: Report Generation")
    print()

    final_response = "No response generated."
    async for event in runner.run_async(
        user_id="user_1",
        session_id=f"session_{pipeline_name}",
        new_message=user_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
            break

    print(f"--- Final Report ---\n{final_response}\n")


async def run_quality_loop(document_text: str) -> None:
    """Run the quality refinement loop on the given text.

    Args:
        document_text: The document text to refine.
    """
    print(f"\n{'='*80}")
    print("  Running: Quality Refinement Loop (LoopAgent)")
    print(f"{'='*80}\n")

    session_service = InMemorySessionService()
    session = session_service.create_session(
        app_name="quality_refinement",
        user_id="user_1",
        session_id="session_quality_loop",
    )

    runner = Runner(
        agent=quality_refinement_loop,
        app_name="quality_refinement",
        session_service=session_service,
    )

    user_message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    "Write an executive summary for this document. "
                    "Refine until quality score >= 8/10:\n\n"
                    f"{document_text}"
                )
            )
        ],
    )

    print("Running iterative refinement (max 3 iterations)...")
    print("  Each iteration: Draft Writer -> Quality Critic")
    print()

    final_response = "No response generated."
    async for event in runner.run_async(
        user_id="user_1",
        session_id="session_quality_loop",
        new_message=user_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
            break

    print(f"--- Final Refined Output ---\n{final_response}\n")


async def main() -> None:
    """Main entry point demonstrating all deterministic processing patterns."""
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is required.")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("  Google ADK + A2A: Deterministic Processing Example")
    print("  Using OpenAI models via LiteLLM")
    print("=" * 80)

    # --- Demo 1: Sequential + Parallel Pipeline ---
    print("\n[DEMO 1] Document Processing Pipeline (Sequential + Parallel)")
    print("  Architecture: Extract -> [Sentiment | Entities | Topics] -> Report")
    await run_pipeline(
        SAMPLE_DOCUMENTS["tech_article"],
        "tech_article_analysis",
    )

    # --- Demo 2: Quality Refinement Loop ---
    print("\n[DEMO 2] Quality Refinement Loop (LoopAgent)")
    print("  Architecture: Draft -> Critique -> Revise (repeat until quality >= 8/10)")
    await run_quality_loop(SAMPLE_DOCUMENTS["business_report"])

    print("\n" + "=" * 80)
    print("  All demos completed successfully!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
