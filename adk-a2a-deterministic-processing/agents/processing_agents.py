"""
Individual LLM agents for the deterministic document processing pipeline.

Each agent handles a specific processing step. They are composed into
deterministic workflows using SequentialAgent, ParallelAgent, and LoopAgent.

All agents use OpenAI models via LiteLLM integration.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from agents.tools import (
    calculate_readability_score,
    extract_keywords,
    extract_word_count,
    format_analysis_report,
    generate_processing_metadata,
)

# ---------------------------------------------------------------------------
# Model configuration - OpenAI only
# ---------------------------------------------------------------------------
OPENAI_MODEL = LiteLlm(model="openai/gpt-4o-mini")


# ===========================================================================
# Stage 1: Content Extraction Agent
# ===========================================================================
content_extractor = LlmAgent(
    name="content_extractor",
    model=OPENAI_MODEL,
    description="Extracts and summarizes the key content from a document.",
    instruction="""You are a content extraction specialist. Your job is to:

1. Read the provided document text carefully
2. Extract the main topic and thesis
3. Identify key arguments or points (up to 5)
4. Provide a concise summary (2-3 sentences)
5. Use the extract_word_count tool to get document statistics
6. Use the extract_keywords tool to identify important terms

Format your output as a structured analysis with clear sections:
- **Main Topic**: [one line]
- **Key Points**: [bulleted list]
- **Summary**: [2-3 sentences]
- **Statistics**: [from tools]
- **Keywords**: [from tools]

Be precise and factual. Do not add information not present in the source text.""",
    tools=[extract_word_count, extract_keywords],
)


# ===========================================================================
# Stage 2a: Sentiment Analysis Agent (runs in parallel)
# ===========================================================================
sentiment_analyzer = LlmAgent(
    name="sentiment_analyzer",
    model=OPENAI_MODEL,
    description="Analyzes the emotional tone and sentiment of text.",
    instruction="""You are a sentiment analysis expert. Analyze the text for:

1. **Overall Sentiment**: Positive, Negative, Neutral, or Mixed
2. **Confidence Score**: 0.0 to 1.0
3. **Emotional Tones**: List detected emotions (e.g., optimistic, concerned, urgent)
4. **Tone Shifts**: Note any changes in tone throughout the text
5. **Objectivity Score**: How objective vs subjective the text is (0.0 = fully subjective, 1.0 = fully objective)

Format your output as:
- **Overall Sentiment**: [sentiment] (confidence: [score])
- **Emotional Tones**: [list]
- **Tone Shifts**: [description or "None detected"]
- **Objectivity**: [score] - [brief explanation]

Be analytical and precise. Base your analysis only on the text provided.""",
    tools=[],
)


# ===========================================================================
# Stage 2b: Entity Extraction Agent (runs in parallel)
# ===========================================================================
entity_extractor = LlmAgent(
    name="entity_extractor",
    model=OPENAI_MODEL,
    description="Extracts named entities and important references from text.",
    instruction="""You are a named entity recognition specialist. Extract:

1. **People**: Names of individuals mentioned
2. **Organizations**: Companies, institutions, groups
3. **Locations**: Places, cities, countries
4. **Dates/Times**: Temporal references
5. **Technologies/Products**: Technical terms, product names
6. **Quantities**: Numbers, percentages, monetary values

Format your output as:
- **People**: [list or "None found"]
- **Organizations**: [list or "None found"]
- **Locations**: [list or "None found"]
- **Dates/Times**: [list or "None found"]
- **Technologies/Products**: [list or "None found"]
- **Quantities**: [list or "None found"]
- **Total Entities Found**: [count]

Only extract entities explicitly mentioned in the text.""",
    tools=[],
)


# ===========================================================================
# Stage 2c: Topic Classification Agent (runs in parallel)
# ===========================================================================
topic_classifier = LlmAgent(
    name="topic_classifier",
    model=OPENAI_MODEL,
    description="Classifies the document into relevant topic categories.",
    instruction="""You are a topic classification expert. Classify the text into:

1. **Primary Category**: The main topic area (e.g., Technology, Business, Science, Health, Politics, Education, Environment)
2. **Sub-Categories**: Up to 3 more specific sub-topics
3. **Confidence**: Your confidence in the classification (High/Medium/Low)
4. **Related Fields**: Adjacent topic areas that the text touches on
5. **Target Audience**: Who would find this text most relevant

Use the calculate_readability_score tool to assess the text complexity.

Format your output as:
- **Primary Category**: [category] (confidence: [level])
- **Sub-Categories**: [list]
- **Related Fields**: [list]
- **Target Audience**: [description]
- **Readability**: [from tool]

Be systematic and evidence-based in your classification.""",
    tools=[calculate_readability_score],
)


# ===========================================================================
# Stage 3: Report Generation Agent
# ===========================================================================
report_generator = LlmAgent(
    name="report_generator",
    model=OPENAI_MODEL,
    description="Generates a comprehensive analysis report from all processing stages.",
    instruction="""You are a report generation specialist. Your job is to:

1. Combine all the analysis results from previous processing stages
2. Use the format_analysis_report tool to structure the output
3. Use the generate_processing_metadata tool to add metadata
4. Create a cohesive, well-structured final report

The report should include:
- **Executive Summary**: 2-3 sentence overview of the document
- **Content Analysis**: Key findings from content extraction
- **Sentiment Profile**: Sentiment and emotional analysis results
- **Entity Map**: Important entities identified
- **Topic Classification**: Categories and audience
- **Processing Metadata**: Pipeline information

Synthesize the information; don't just repeat it. Draw connections between
the different analyses. Be concise but thorough.""",
    tools=[format_analysis_report, generate_processing_metadata],
)


# ===========================================================================
# Loop Agents: Iterative Quality Refinement
# ===========================================================================

draft_writer = LlmAgent(
    name="draft_writer",
    model=OPENAI_MODEL,
    description="Writes or refines a document summary draft.",
    instruction="""You are a skilled technical writer. Your job is to:

1. If this is the first iteration: Write a clear, engaging executive summary
   of the document based on all the analysis provided.
2. If feedback from the critic is available: Revise your previous draft
   incorporating the specific feedback provided.

The summary should be:
- 150-250 words
- Clear and professional
- Well-structured with proper transitions
- Factually accurate based on the source analysis

Output ONLY the draft text, nothing else.""",
    tools=[],
)

quality_critic = LlmAgent(
    name="quality_critic",
    model=OPENAI_MODEL,
    description="Evaluates draft quality and provides improvement feedback.",
    instruction="""You are a quality assurance critic. Evaluate the draft for:

1. **Clarity** (1-10): Is it easy to understand?
2. **Completeness** (1-10): Does it cover all key points?
3. **Accuracy** (1-10): Is it factually consistent with the source?
4. **Conciseness** (1-10): Is it appropriately brief without losing meaning?
5. **Overall Score** (1-10): Average of above scores

If the Overall Score is 8 or above, respond with:
"APPROVED - Quality threshold met. Overall score: [score]/10"

If below 8, provide specific, actionable feedback:
"NEEDS REVISION - Overall score: [score]/10
Feedback:
- [specific improvement 1]
- [specific improvement 2]
- [specific improvement 3]"

Be constructive but demanding. High quality is the goal.""",
    tools=[],
)
