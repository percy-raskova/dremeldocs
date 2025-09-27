#!/usr/bin/env python3
"""
Interface definitions to break circular dependencies.

This module provides base classes and interfaces that can be imported
by multiple modules without creating circular dependencies.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

# Re-export common types to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spacy.tokens import Doc, Token, Span


class TextProcessorInterface(ABC):
    """Base interface for text processing components."""

    @abstractmethod
    def process(self, text: str) -> Any:
        """Process text and return results."""
        pass


class TagExtractorInterface(ABC):
    """Base interface for tag extraction components."""

    @abstractmethod
    def extract_tags(self, text: str) -> List[str]:
        """Extract tags from text."""
        pass

    @abstractmethod
    def extract_concept_tags(
        self, text: str, max_tags: int = 10
    ) -> List[Tuple[str, float]]:
        """Extract concept tags with scores."""
        pass


class NLPProcessorInterface(ABC):
    """Base interface for NLP processing components."""

    @abstractmethod
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        pass

    @abstractmethod
    def process_document(self, text: str) -> 'Doc':
        """Process text and return SpaCy Doc."""
        pass


# Shared configuration that was causing circular imports
MODEL_TYPE = "large"  # Will be set during model loading

NLP_CONFIG = {
    "disable": ["tok2vec", "attribute_ruler", "lemmatizer"],
    "max_length": 2_000_000,
}


# Singleton holder for NLP model to avoid multiple imports
_nlp_instance = None


def get_nlp_instance():
    """Get or create the singleton NLP instance."""
    global _nlp_instance, MODEL_TYPE
    if _nlp_instance is None:
        import spacy

        # Load SpaCy model with fallback priority
        # NUCLEAR FUSION MODE: Using LARGE model for MAXIMUM VOCABULARY POWER!
        try:
            # First try the LARGE model for MASSIVE vocabulary and vectors
            _nlp_instance = spacy.load("en_core_web_lg")
            print("🚀💥 LARGE MODEL LOADED - MAXIMUM VOCABULARY POWER ENGAGED!")
            MODEL_TYPE = "large"
        except OSError:
            try:
                # Fallback to transformer for contextual understanding
                _nlp_instance = spacy.load("en_core_web_trf")
                print("🚀 TRANSFORMER MODEL LOADED - CONTEXTUAL POWER ENGAGED!")
                MODEL_TYPE = "transformer"
            except OSError:
                try:
                    # Fallback to medium if large/transformer not available
                    _nlp_instance = spacy.load("en_core_web_md")
                    print("💪 Medium model loaded with word vectors")
                    MODEL_TYPE = "medium"
                except OSError:
                    try:
                        # Final fallback to small model
                        _nlp_instance = spacy.load("en_core_web_sm")
                        print("📦 Small model loaded - basic functionality")
                        MODEL_TYPE = "small"
                    except OSError:
                        print("⚠️  No SpaCy model found. Please install one with:")
                        print("    # For MAXIMUM VOCABULARY (recommended):")
                        print(
                            "    uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl"
                        )
                        print("    # Or for contextual understanding:")
                        print(
                            "    uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0-py3-none-any.whl"
                        )
                        import sys
                        sys.exit(1)

        # Configure the model
        _nlp_instance.max_length = NLP_CONFIG["max_length"]

    return _nlp_instance


def clean_social_text(text: str) -> str:
    """
    Clean social media text for processing.

    Moved here from nlp_core to break circular dependency.
    """
    import re

    # Handle different input types
    if hasattr(text, 'text'):  # SpaCy Doc object
        text = text.text
    elif not isinstance(text, str):
        text = str(text)

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)

    # Remove mentions but keep the context
    text = re.sub(r"@\w+", "", text)

    # Remove hashtags but keep the word
    text = re.sub(r"#(\w+)", r"\1", text)

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# Export convenience functions
__all__ = [
    'TextProcessorInterface',
    'TagExtractorInterface',
    'NLPProcessorInterface',
    'MODEL_TYPE',
    'NLP_CONFIG',
    'get_nlp_instance',
    'clean_social_text',
]