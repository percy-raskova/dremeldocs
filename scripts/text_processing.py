#!/usr/bin/env python3
"""
SpaCy-enhanced text processing utilities for generating titles and descriptions.
Provides linguistic-aware text extraction for better frontmatter generation.
"""

import re
from typing import Optional, List, Tuple
import spacy
from spacy.tokens import Doc, Span

# Load SpaCy model once at module level for efficiency
# Use small model for speed - upgrade to medium/large if needed
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("⚠️  SpaCy model not found. Please install it with:")
    print("    uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl")
    import sys
    sys.exit(1)

# Keep all components enabled for full functionality


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


def extract_key_phrase(sent: Span) -> Optional[str]:
    """
    Extract the most important phrase from a sentence using dependency parsing.

    Args:
        sent: SpaCy Span representing a sentence

    Returns:
        Key phrase if found, None otherwise
    """
    # Look for the main subject (nsubj) or root verb's object
    subject = None
    root = None

    for token in sent:
        if token.dep_ == "ROOT":
            root = token
        if token.dep_ in ("nsubj", "nsubjpass"):
            subject = token

    # If we have a subject, try to expand it to its full noun chunk
    if subject:
        for chunk in sent.noun_chunks:
            if subject in chunk:
                return chunk.text

    # Otherwise, try to find the most important noun chunk
    noun_chunks = list(sent.noun_chunks)
    if noun_chunks:
        # Prefer longer, more descriptive chunks
        noun_chunks.sort(key=lambda x: len(x.text), reverse=True)
        return noun_chunks[0].text

    return None


def generate_title(text: str, max_length: int = 60) -> str:
    """
    Generate a title using SpaCy sentence segmentation and linguistic analysis.

    Args:
        text: Raw text to generate title from
        max_length: Maximum character length for title

    Returns:
        Generated title string
    """
    if not text:
        return ""

    # Remove RT prefix if present
    if text.startswith('RT '):
        text = text[3:].lstrip()

    # Process with SpaCy
    doc = nlp(text[:1000])  # Limit processing for efficiency

    # Clean social media artifacts first
    cleaned_full = clean_social_text(doc)

    # Re-process cleaned text to get better sentence segmentation
    doc_cleaned = nlp(cleaned_full)
    sentences = list(doc_cleaned.sents)

    if not sentences:
        # Fallback if no sentences detected
        return cleaned_full[:max_length].rsplit(' ', 1)[0] + ('...' if len(cleaned_full) > max_length else '')

    first_sent = sentences[0]
    first_text = first_sent.text.strip()

    # If first sentence is short enough, use it
    if len(first_text) <= max_length:
        # Remove trailing punctuation for titles
        first_text = first_text.rstrip('.!?,;:')
        return first_text

    # Try to extract the key phrase
    key_phrase = extract_key_phrase(first_sent)
    if key_phrase and len(key_phrase) <= max_length:
        return key_phrase

    # Fallback: truncate at word boundary
    truncated = first_text[:max_length].rsplit(' ', 1)[0]

    # Remove incomplete punctuation at end
    truncated = truncated.rstrip('.!?,;:')

    return truncated + '...'


def generate_description(text: str, max_length: int = 160) -> str:
    """
    Generate a description using multiple complete sentences when possible.

    Args:
        text: Raw text to generate description from
        max_length: Maximum character length for description

    Returns:
        Generated description string
    """
    if not text:
        return ""

    # Process with SpaCy (limit for efficiency)
    doc = nlp(text[:2000])

    # Get sentences
    sentences = list(doc.sents)
    if not sentences:
        # Fallback if no sentences detected
        return text[:max_length].rsplit(' ', 1)[0] + ('...' if len(text) > max_length else '')

    # Collect complete sentences up to max_length
    description_parts = []
    char_count = 0

    for sent in sentences[:3]:  # Consider up to 3 sentences
        cleaned = clean_social_text(sent.as_doc())

        # Skip very short sentences (likely fragments)
        if len(cleaned) < 10:
            continue

        # Check if adding this sentence would exceed limit
        space_needed = 1 if description_parts else 0  # Space between sentences
        if char_count + len(cleaned) + space_needed <= max_length:
            description_parts.append(cleaned)
            char_count += len(cleaned) + space_needed
        else:
            # If we haven't added anything yet, we need to truncate the first sentence
            if not description_parts:
                truncated = cleaned[:max_length].rsplit(' ', 1)[0]
                return truncated + '...'
            break

    if description_parts:
        return ' '.join(description_parts).strip()

    # Fallback: use first sentence truncated
    first_cleaned = clean_social_text(sentences[0].as_doc())
    if len(first_cleaned) <= max_length:
        return first_cleaned

    truncated = first_cleaned[:max_length].rsplit(' ', 1)[0]
    return truncated + '...'


def extract_entities(text: str, limit: int = 5) -> List[str]:
    """
    Extract named entities from text for potential use as tags.

    Args:
        text: Text to extract entities from
        limit: Maximum number of entities to return

    Returns:
        List of entity strings
    """
    # Process with NER enabled (it's part of the default pipeline)
    doc = nlp(text[:2000])

    entities = []
    seen = set()

    for ent in doc.ents:
        # Skip certain entity types that aren't useful as tags
        if ent.label_ in ("DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"):
            continue

        # Normalize and deduplicate
        normalized = ent.text.strip().lower()
        if normalized not in seen and len(normalized) > 2:
            entities.append(ent.text.strip())
            seen.add(normalized)

            if len(entities) >= limit:
                break

    return entities


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


def format_frontmatter_value(value) -> str:
    """
    Properly format values for YAML frontmatter, escaping as needed.

    Args:
        value: Value to format (string, list, or other)

    Returns:
        Properly formatted string for YAML
    """
    if value is None:
        return '""'

    if isinstance(value, str):
        # Always quote strings for consistency and predictability
        # Escape backslashes and quotes
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'

    elif isinstance(value, list):
        if not value:
            return '[]'
        formatted_items = [format_frontmatter_value(item) for item in value]
        return '[' + ', '.join(formatted_items) + ']'

    elif isinstance(value, bool):
        return 'true' if value else 'false'

    else:
        return str(value)


# Filename generation functions for consistent naming
def parse_to_yyyymmdd(date_str) -> str:
    """
    Parse various date formats to YYYYMMDD format.

    Handles:
    - Twitter format: "Sat Apr 26 15:30:45 +0000 2025"
    - ISO format: "2025-04-26T15:30:45Z"
    - Date strings: "2025-04-26"
    - Datetime objects

    Args:
        date_str: Date string or datetime object to parse

    Returns:
        Date string in YYYYMMDD format
    """
    from datetime import datetime
    from dateutil import parser

    if not date_str:
        return "20250101"  # Default

    try:
        if isinstance(date_str, datetime):
            date_obj = date_str
        else:
            # Try flexible parsing
            date_obj = parser.parse(str(date_str))

        return date_obj.strftime('%Y%m%d')
    except:
        # Fallback to default
        return "20250101"


def generate_brief_title(text: str, max_length: int = 50) -> str:
    """
    Generate a brief, filename-safe title using SpaCy NLP.

    Process:
    1. Use SpaCy to extract meaningful title from text
    2. Convert to filename-safe format
    3. Replace spaces with underscores
    4. Ensure lowercase for consistency

    Args:
        text: Source text
        max_length: Maximum title length

    Returns:
        Filename-safe title like: "dialectical_materialism_and_praxis"
    """
    # Use SpaCy-enhanced title generation
    title = generate_title(text, max_length + 10)  # Allow extra for processing

    # Convert to filename-safe format
    safe_title = re.sub(r'[^\w\s-]', '', title)  # Keep alphanumeric, spaces, hyphens
    safe_title = safe_title.replace(' ', '_')     # Spaces to underscores
    safe_title = re.sub(r'_+', '_', safe_title)   # Collapse multiple underscores
    safe_title = safe_title.strip('_')            # Remove leading/trailing underscores

    # Ensure not empty
    if not safe_title:
        safe_title = 'untitled'

    # Truncate if needed (at word boundary)
    if len(safe_title) > max_length:
        safe_title = safe_title[:max_length].rsplit('_', 1)[0]

    return safe_title.lower()


def generate_filename(sequence_num: int, date_str, text: str, max_title_length: int = 50) -> str:
    """
    Generate standardized filename: {sequence}-{YYYYMMDD}-{title}.md

    Args:
        sequence_num: Thread sequence number (1-based, zero-padded to 3 digits)
        date_str: Date string in various formats (Twitter, ISO, etc.)
        text: Source text to generate title from
        max_title_length: Maximum length for title portion

    Returns:
        Formatted filename like: 001-20250122-dialectical_materialism.md
    """
    # Format sequence number with zero-padding
    seq = f"{sequence_num:03d}"

    # Parse and format date as YYYYMMDD
    date_formatted = parse_to_yyyymmdd(date_str)

    # Generate brief, filename-safe title
    title = generate_brief_title(text, max_title_length)

    return f"{seq}-{date_formatted}-{title}.md"


# Batch processing optimization for multiple documents
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


if __name__ == "__main__":
    # Test the functions
    test_text = """RT @someone: This is an amazing philosophical thread about dialectical materialism!
    https://t.co/abc123 Check it out. #philosophy #marxism
    The relationship between theory and praxis is fundamental to understanding revolutionary change."""

    print("Test Text:", test_text)
    print("-" * 50)
    print("Title:", generate_title(test_text))
    print("Description:", generate_description(test_text))
    print("Entities:", extract_entities(test_text))
    print("Reading Time:", calculate_reading_time(test_text), "min")

    # Test filename generation
    print("-" * 50)
    print("Filename Generation Tests:")
    test_dates = [
        "Sat Apr 26 15:30:45 +0000 2025",
        "2025-04-26T15:30:45Z",
        "2025-04-26",
        None
    ]
    for i, date in enumerate(test_dates, 1):
        filename = generate_filename(i, date, test_text)
        print(f"  Date: {date}")
        print(f"  Filename: {filename}")
        print()