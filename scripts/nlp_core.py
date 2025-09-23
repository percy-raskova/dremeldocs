#!/usr/bin/env python3
"""
Core NLP functionality and model loading for DremelDocs.
Handles SpaCy model initialization and configuration management.
"""

import re
import yaml
from typing import Dict, List, Any
from pathlib import Path
import spacy
from spacy.tokens import Doc

# Load SpaCy model once at module level for efficiency
# NUCLEAR FUSION MODE: Using LARGE model for MAXIMUM VOCABULARY POWER!
try:
    # First try the LARGE model for MASSIVE vocabulary and vectors
    nlp = spacy.load("en_core_web_lg")
    print("🚀💥 LARGE MODEL LOADED - MAXIMUM VOCABULARY POWER ENGAGED!")
    MODEL_TYPE = "large"
except OSError:
    try:
        # Fallback to transformer for contextual understanding
        nlp = spacy.load("en_core_web_trf")
        print("🚀 TRANSFORMER MODEL LOADED - CONTEXTUAL POWER ENGAGED!")
        MODEL_TYPE = "transformer"
    except OSError:
        try:
            # Fallback to medium if large/transformer not available
            nlp = spacy.load("en_core_web_md")
            print("💪 Medium model loaded with word vectors")
            MODEL_TYPE = "medium"
        except OSError:
            try:
                # Final fallback to small model
                nlp = spacy.load("en_core_web_sm")
                print("📦 Small model loaded - basic functionality")
                MODEL_TYPE = "small"
            except OSError:
                print("⚠️  No SpaCy model found. Please install one with:")
                print("    # For MAXIMUM VOCABULARY (recommended):")
                print("    uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl")
                print("    # Or for contextual understanding:")
                print("    uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0-py3-none-any.whl")
                import sys
                sys.exit(1)

# Keep all components enabled for full functionality


def load_nlp_config() -> Dict[str, Any]:
    """Load NLP configuration from YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "nlp_settings.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"⚠️  Configuration file not found: {config_path}")
        print("   Using fallback configuration")
        # Fallback configuration if file doesn't exist
        return {
            'tags': {
                'min_chunk_words': 2,
                'max_chunk_words': 5,
                'max_tags': 10,
                'weights': {
                    'domain_term': 2.5,
                    'named_entity': 2.0,
                    'quoted_phrase': 1.8,
                    'proper_noun': 1.5,
                    'multi_word': 1.2,
                    'length_bonus': 0.1
                },
                'domain_vocabulary': {'political_theory': [], 'philosophy': []}
            },
            'content_filters': {
                'skip_phrases': ['the people', 'the way', 'the thing'],
                'min_concept_length': 8
            },
            'patterns': {
                'quote_patterns': [r'"([^"]{10,100})"', r"'([^']{10,100})'"],
                'theory_patterns': [r"theory of \w+", r"\w+ theory"],
                'relationship_patterns': [r"\w+ is \w+", r"\w+ means \w+"]
            }
        }


# Global configuration
NLP_CONFIG = load_nlp_config()


def clean_social_text(doc: Doc) -> str:
    """
    Remove URLs, mentions, and hashtags using SpaCy token attributes.

    Args:
        doc: SpaCy Doc object

    Returns:
        Cleaned text without social media artifacts
    """
    cleaned_tokens = []

    for token in doc:
        # Skip URLs using SpaCy's built-in URL detection
        if token.like_url:
            continue

        # Skip social media mentions and hashtags
        if token.text.startswith(('@', '#')):
            continue

        # Skip standalone 'RT' (retweet indicator)
        if token.text.upper() == 'RT' and token.i == 0:
            continue

        cleaned_tokens.append(token.text)

    # Reconstruct with proper spacing
    cleaned = ' '.join(cleaned_tokens)

    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def calculate_reading_time(text: str) -> int:
    """
    Calculate reading time using SpaCy's tokenization for more accurate word count.

    Args:
        text: Text to calculate reading time for

    Returns:
        Estimated reading time in minutes
    """
    doc = nlp.make_doc(text)  # Fast tokenization only

    # Count only alphabetic tokens (exclude punctuation, symbols)
    word_count = sum(1 for token in doc if token.is_alpha)

    # Average reading speed: 225 words per minute
    return max(1, round(word_count / 225))


def process_batch(texts: List[str], batch_size: int = 100) -> List[Doc]:
    """
    Process multiple texts efficiently using SpaCy's pipe method.

    Args:
        texts: List of texts to process
        batch_size: Size of processing batches

    Returns:
        List of processed Doc objects
    """
    return list(nlp.pipe(texts, batch_size=batch_size))