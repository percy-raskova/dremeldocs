#!/usr/bin/env python3
"""
General text processing utilities for DremelDocs.
Provides title generation, descriptions, frontmatter formatting, and filename utilities.
"""

import re
from typing import Optional, List, Union, Any
from datetime import datetime
from dateutil import parser
from spacy.tokens import Doc, Span

# Import from our new modules
from nlp_core import nlp, clean_social_text
from tag_extraction import EnhancedTagExtractor, extract_concept_tags


def skip_common_starters(doc: Doc, min_chunk_words: int = 2) -> Optional[str]:
    """
    Skip common starting words (pronouns, articles) and find first meaningful content.

    Args:
        doc: SpaCy Doc object
        min_chunk_words: Minimum words in a meaningful chunk

    Returns:
        First meaningful phrase text, or None if not found
    """
    SKIP_WORDS = {
        # Pronouns
        'i', 'we', 'you', 'they', 'it', 'he', 'she', 'that', 'this', 'these', 'those',
        # Articles
        'the', 'a', 'an',
        # Common verbs that don't add meaning alone
        'is', 'are', 'was', 'were', 'have', 'has', 'had',
        # Other common starters
        'so', 'but', 'and', 'or', 'if', 'when', 'while',
        # Contractions (both forms)
        "that's", "it's", "there's", "here's", "what's", "who's",
        "thats", "its", "whats", "whos", "'s"
    }

    for sent in doc.sents:
        sent_text = sent.text.strip()

        # Look for quoted phrases (often important)
        if '"' in sent_text or "'" in sent_text:
            # Find quoted content
            quoted_pattern = r'["\']([^"\']+)["\']'
            matches = re.findall(quoted_pattern, sent_text)
            for match in matches:
                if len(match.split()) >= min_chunk_words:
                    return match

        # Get meaningful tokens
        tokens = [t for t in sent if not t.is_punct and not t.is_space]
        if not tokens:
            continue

        # Check if starts with skip word (including contractions)
        first_word_lower = tokens[0].text.lower()

        # If not a skip word, look for substantial content
        if first_word_lower not in SKIP_WORDS:
            # Try noun chunks first
            for chunk in sent.noun_chunks:
                chunk_text = chunk.text.strip()
                # Ensure we get complete phrases
                if len(chunk_text.split()) >= min_chunk_words and len(chunk_text) > 15:
                    return chunk_text

            # Return sentence if meaningful
            if len(sent_text) > 20 and not sent_text.lower().startswith(tuple(SKIP_WORDS)):
                return sent_text[:100]  # Cap length but keep meaningful

        # First word is skip word - find content after it
        # Look for the best noun chunk
        best_chunk = None
        best_score = 0

        for chunk in sent.noun_chunks:
            chunk_text = chunk.text.strip()
            chunk_words = chunk_text.split()

            # Score chunks
            score = len(chunk_words)
            # Boost for proper nouns
            if any(t.pos_ == 'PROPN' for t in chunk):
                score += 3
            # Boost for named entities
            if any(t.ent_type_ for t in chunk):
                score += 2

            if score > best_score and len(chunk_words) >= min_chunk_words:
                best_chunk = chunk_text
                best_score = score

        if best_chunk and len(best_chunk) > 10:
            return best_chunk

        # Try verb phrases with objects as fallback
        for token in sent:
            if token.pos_ == 'VERB' and token.dep_ == 'ROOT':
                # Get full verb phrase with modifiers and objects
                children = list(token.subtree)
                if len(children) >= min_chunk_words:
                    phrase_start = min(t.i for t in children)
                    phrase_end = max(t.i for t in children) + 1
                    phrase = doc[phrase_start:phrase_end]
                    phrase_text = ' '.join([t.text for t in phrase if not t.is_space])

                    # Clean up the phrase
                    phrase_text = phrase_text.strip()
                    # Remove leading skip words
                    for skip in SKIP_WORDS:
                        if phrase_text.lower().startswith(skip + ' '):
                            phrase_text = phrase_text[len(skip)+1:]
                            break

                    if len(phrase_text.split()) >= min_chunk_words and len(phrase_text) > 15:
                        return phrase_text

    return None


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
    Now with smart starter skipping for better titles.

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

    # Process with SpaCy (process more text for better context)
    doc = nlp(text[:2000])  # Increased from 1000 for better analysis

    # Strategy 1: Try smart starter skipping first
    meaningful_start = skip_common_starters(doc)
    if meaningful_start:
        # Clean and truncate if needed
        meaningful_start = meaningful_start.strip('.!?,;:')
        if len(meaningful_start) <= max_length:
            return meaningful_start
        # Truncate at word boundary
        return meaningful_start[:max_length].rsplit(' ', 1)[0] + '...'

    # Strategy 2: Fall back to original method with improvements
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
    description_parts: List[str] = []
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
    Extract meaningful tags from text using enhanced tag extraction.
    This function provides backward compatibility with the original interface
    but uses the new EnhancedTagExtractor for better results.

    Args:
        text: Text to extract entities from
        limit: Maximum number of entities to return

    Returns:
        List of entity/concept strings for use as tags
    """
    try:
        # Use the new enhanced extractor
        extractor = EnhancedTagExtractor()
        enhanced_tags = extractor.extract_enhanced_tags(text, max_tags=limit)

        if enhanced_tags:
            return enhanced_tags

    except Exception as e:
        # Fallback to original method if enhanced extraction fails
        print(f"⚠️  Enhanced extraction failed: {e}")
        print("Falling back to basic extraction...")

    # Fallback: Use the original basic method
    return extract_entities_basic(text, limit)


def extract_entities_basic(text: str, limit: int = 5) -> List[str]:
    """
    Original basic entity extraction method (kept as fallback).
    Extract meaningful tags from text using noun chunks and named entities.

    Args:
        text: Text to extract entities from
        limit: Maximum number of entities to return

    Returns:
        List of entity/concept strings for use as tags
    """
    # Process with full pipeline for better analysis
    doc = nlp(text[:2000])

    # Get concept tags from noun chunks (better for philosophical content)
    concept_tags = extract_concept_tags(doc, max_tags=limit * 2)  # Get extra for filtering

    # Also get traditional named entities
    traditional_entities = []
    seen = set()

    for ent in doc.ents:
        # Skip temporal/numeric entities
        if ent.label_ in ("DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"):
            continue

        # Normalize and deduplicate
        normalized = ent.text.strip().lower()
        if normalized not in seen and len(normalized) > 2:
            traditional_entities.append(ent.text.strip())
            seen.add(normalized)

    # Combine and deduplicate, preferring concept tags
    combined_tags = []
    seen_normalized = set()

    # Add concept tags first (higher priority)
    for tag in concept_tags:
        normalized = tag.lower()
        if normalized not in seen_normalized:
            combined_tags.append(tag)
            seen_normalized.add(normalized)
            if len(combined_tags) >= limit:
                return combined_tags

    # Add traditional entities if space remains
    for entity in traditional_entities:
        normalized = entity.lower()
        if normalized not in seen_normalized:
            combined_tags.append(entity)
            seen_normalized.add(normalized)
            if len(combined_tags) >= limit:
                return combined_tags

    return combined_tags


def format_frontmatter_value(value: Any) -> str:
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
        # Replace inner double quotes with single quotes for better readability
        # Then escape any remaining quotes and backslashes
        value = value.replace('"', "'")
        escaped = value.replace('\\', '\\\\')
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


def parse_to_yyyymmdd(date_str: Union[str, datetime, None]) -> str:
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
    if not date_str:
        return "20250101"  # Default

    try:
        if isinstance(date_str, datetime):
            date_obj = date_str
        else:
            # Try flexible parsing
            date_obj = parser.parse(str(date_str))

        return date_obj.strftime('%Y%m%d')
    except Exception as e:
        # Fallback to default
        print(f"Warning: Could not parse date '{date_str}': {e}")
        return "20250101"


def generate_brief_title(text: str, max_length: int = 50) -> str:
    """
    Generate a brief, filename-safe title using SpaCy NLP.

    Process:
    1. Use SpaCy-enhanced title generation
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


def generate_filename(sequence_num: int, date_str: Union[str, datetime, None], text: str, max_title_length: int = 50) -> str:
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