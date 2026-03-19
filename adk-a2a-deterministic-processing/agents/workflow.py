"""
Deterministic workflow compositions using ADK Workflow Agents.

This module composes the individual LLM agents into deterministic pipelines
using SequentialAgent, ParallelAgent, and LoopAgent. The execution order
is guaranteed regardless of LLM behavior.

Pipeline Architecture:
    SequentialAgent (document_processing_pipeline)
    |
    |-- Step 1: content_extractor (LlmAgent)
    |       Extracts key content, statistics, keywords
    |
    |-- Step 2: ParallelAgent (parallel_analysis)
    |       |-- sentiment_analyzer (LlmAgent)
    |       |-- entity_extractor (LlmAgent)
    |       |-- topic_classifier (LlmAgent)
    |
    |-- Step 3: report_generator (LlmAgent)
    |       Combines all analyses into final report
    |
    LoopAgent (quality_refinement_loop)
    |
    |-- Iteration: draft_writer -> quality_critic
    |       Repeats until quality threshold met (max 3 iterations)
"""

from google.adk.agents import LoopAgent, ParallelAgent, SequentialAgent

from agents.processing_agents import (
    content_extractor,
    draft_writer,
    entity_extractor,
    quality_critic,
    report_generator,
    sentiment_analyzer,
    topic_classifier,
)


# ===========================================================================
# Parallel Analysis Stage
# ===========================================================================
# These three agents run concurrently since they are independent of each other.
# Each analyzes the document from a different perspective simultaneously.
parallel_analysis = ParallelAgent(
    name="parallel_analysis",
    description=(
        "Runs sentiment analysis, entity extraction, and topic classification "
        "concurrently for maximum efficiency."
    ),
    sub_agents=[sentiment_analyzer, entity_extractor, topic_classifier],
)


# ===========================================================================
# Main Document Processing Pipeline (Sequential)
# ===========================================================================
# Guarantees execution order: Extract -> Analyze (parallel) -> Report
# This is deterministic: the same input always follows the same path.
document_processing_pipeline = SequentialAgent(
    name="document_processing_pipeline",
    description=(
        "A deterministic document processing pipeline that extracts content, "
        "performs parallel analysis (sentiment, entities, topics), and generates "
        "a comprehensive report. Execution order is guaranteed."
    ),
    sub_agents=[content_extractor, parallel_analysis, report_generator],
)


# ===========================================================================
# Quality Refinement Loop
# ===========================================================================
# Iteratively improves a draft until quality threshold is met.
# The draft_writer produces output, the quality_critic evaluates it.
# Loop continues until critic approves or max_iterations is reached.
quality_refinement_loop = LoopAgent(
    name="quality_refinement_loop",
    description=(
        "Iteratively refines a document summary through a write-critique cycle. "
        "The draft writer produces a summary, the critic evaluates quality. "
        "Loop continues until quality score >= 8/10 or max 3 iterations."
    ),
    sub_agents=[draft_writer, quality_critic],
    max_iterations=3,
)
