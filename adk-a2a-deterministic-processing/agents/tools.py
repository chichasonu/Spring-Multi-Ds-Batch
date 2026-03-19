"""
Custom tools for the deterministic document processing pipeline.

These tools provide utility functions that agents can use during processing.
They demonstrate how ADK agents interact with tools in a deterministic workflow.
"""

import json
import re
from datetime import datetime, timezone


def extract_word_count(text: str) -> dict:
    """Counts words, sentences, and paragraphs in the given text.

    Args:
        text: The input text to analyze.

    Returns:
        A dictionary with word_count, sentence_count, and paragraph_count.
    """
    words = len(text.split())
    sentences = len(re.split(r'[.!?]+', text.strip())) - 1
    if sentences < 1:
        sentences = 1
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])
    if paragraphs < 1:
        paragraphs = 1

    return {
        "word_count": words,
        "sentence_count": sentences,
        "paragraph_count": paragraphs,
        "avg_words_per_sentence": round(words / sentences, 1),
    }


def extract_keywords(text: str) -> dict:
    """Extracts potential keywords from text using simple frequency analysis.

    Args:
        text: The input text to extract keywords from.

    Returns:
        A dictionary with the top keywords and their frequencies.
    """
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again",
        "further", "then", "once", "and", "but", "or", "nor", "not", "so",
        "yet", "both", "either", "neither", "each", "every", "all", "any",
        "few", "more", "most", "other", "some", "such", "no", "only",
        "own", "same", "than", "too", "very", "just", "because", "if",
        "when", "where", "how", "what", "which", "who", "whom", "this",
        "that", "these", "those", "i", "me", "my", "myself", "we", "our",
        "ours", "you", "your", "yours", "he", "him", "his", "she", "her",
        "hers", "it", "its", "they", "them", "their", "theirs",
    }

    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    filtered = [w for w in words if w not in stop_words]

    freq: dict[str, int] = {}
    for word in filtered:
        freq[word] = freq.get(word, 0) + 1

    top_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "keywords": [{"word": w, "frequency": f} for w, f in top_keywords],
        "total_unique_words": len(freq),
    }


def calculate_readability_score(text: str) -> dict:
    """Calculates a simplified readability score for the text.

    Args:
        text: The input text to score.

    Returns:
        A dictionary with readability metrics.
    """
    words = text.split()
    word_count = len(words)
    sentences = len(re.split(r'[.!?]+', text.strip())) - 1
    if sentences < 1:
        sentences = 1

    syllable_count = 0
    for word in words:
        word_clean = re.sub(r'[^a-zA-Z]', '', word.lower())
        if not word_clean:
            continue
        vowels = "aeiou"
        count = 0
        prev_vowel = False
        for char in word_clean:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        if word_clean.endswith('e') and count > 1:
            count -= 1
        if count < 1:
            count = 1
        syllable_count += count

    avg_sentence_length = word_count / sentences
    avg_syllables_per_word = syllable_count / max(word_count, 1)

    flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    flesch_score = max(0, min(100, round(flesch_score, 1)))

    if flesch_score >= 80:
        level = "Easy"
    elif flesch_score >= 60:
        level = "Standard"
    elif flesch_score >= 40:
        level = "Moderate"
    elif flesch_score >= 20:
        level = "Difficult"
    else:
        level = "Very Difficult"

    return {
        "flesch_reading_ease": flesch_score,
        "readability_level": level,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_syllables_per_word": round(avg_syllables_per_word, 2),
    }


def generate_processing_metadata() -> dict:
    """Generates metadata for the current processing run.

    Returns:
        A dictionary with processing metadata including timestamp and version.
    """
    return {
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "1.0.0",
        "framework": "Google ADK",
        "protocol": "A2A (Agent-to-Agent)",
        "model_provider": "OpenAI",
    }


def format_analysis_report(
    content_summary: str,
    sentiment: str,
    entities: str,
    topics: str,
) -> dict:
    """Formats all analysis results into a structured report.

    Args:
        content_summary: The content extraction summary.
        sentiment: The sentiment analysis result.
        entities: The entity extraction result.
        topics: The topic classification result.

    Returns:
        A dictionary containing the formatted report.
    """
    return {
        "report": {
            "content_summary": content_summary,
            "sentiment_analysis": sentiment,
            "entity_extraction": entities,
            "topic_classification": topics,
        },
        "metadata": generate_processing_metadata(),
    }
