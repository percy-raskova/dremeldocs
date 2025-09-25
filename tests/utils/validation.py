"""
Validation utilities for testing the Twitter archive processing pipeline.
"""

import re
from typing import Any, Dict, List, Optional

import yaml


def validate_filename_format(filename: str) -> bool:
    """
    Validate that filename follows the format: {3-digit}-{YYYYMMDD}-{brief_title}.md

    Args:
        filename: Filename to validate

    Returns:
        bool: True if filename matches expected format
    """
    pattern = r"^\d{3}-\d{8}-[a-zA-Z0-9_]+\.md$"
    return bool(re.match(pattern, filename))


def validate_frontmatter_structure(frontmatter: Dict[str, Any]) -> List[str]:
    """
    Validate that frontmatter contains all required fields with correct types.

    Args:
        frontmatter: Parsed YAML frontmatter dictionary

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    required_fields = {
        "title": str,
        "date": dict,
        "categories": list,
        "thread_id": str,
        "word_count": int,
        "reading_time": int,
        "description": str,
        "tweet_count": int,
        "heavy_hitter": bool,
        "thread_number": int,
        "author": str,
    }

    # Check required fields exist and have correct types
    for field, expected_type in required_fields.items():
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(frontmatter[field], expected_type):
            errors.append(
                f"Field '{field}' should be {expected_type.__name__}, got {type(frontmatter[field]).__name__}"
            )

    # Validate date structure
    if "date" in frontmatter and isinstance(frontmatter["date"], dict):
        if "created" not in frontmatter["date"]:
            errors.append("Date field missing 'created' key")
        else:
            # Validate date format YYYY-MM-DD
            date_pattern = r"^\d{4}-\d{2}-\d{2}$"
            if not re.match(date_pattern, str(frontmatter["date"]["created"])):
                errors.append("Date 'created' field must be in YYYY-MM-DD format")

    # Validate categories contains heavy_hitters
    if "categories" in frontmatter and isinstance(frontmatter["categories"], list):
        if "heavy_hitters" not in frontmatter["categories"]:
            errors.append("Categories must include 'heavy_hitters'")

    # Validate reading_time is positive
    if "reading_time" in frontmatter and isinstance(frontmatter["reading_time"], int):
        if frontmatter["reading_time"] <= 0:
            errors.append("Reading time must be positive")

    # Validate word_count is positive
    if "word_count" in frontmatter and isinstance(frontmatter["word_count"], int):
        if frontmatter["word_count"] <= 0:
            errors.append("Word count must be positive")

    return errors


def validate_yaml_syntax(yaml_content: str) -> Optional[str]:
    """
    Validate that YAML content is syntactically correct.

    Args:
        yaml_content: YAML content as string

    Returns:
        Error message if invalid, None if valid
    """
    try:
        yaml.safe_load(yaml_content)
        return None
    except yaml.YAMLError as e:
        return f"YAML syntax error: {e!s}"


def validate_markdown_structure(content: str) -> List[str]:
    """
    Validate that markdown content has expected structure.

    Args:
        content: Full markdown content including frontmatter

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    lines = content.split("\n")

    # Check for frontmatter boundaries
    if not lines[0].strip() == "---":
        errors.append("Content must start with frontmatter delimiter '---'")
        return errors

    # Find end of frontmatter
    frontmatter_end = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end is None:
        errors.append("Frontmatter must end with '---' delimiter")
        return errors

    # Extract and validate frontmatter
    frontmatter_content = "\n".join(lines[1:frontmatter_end])
    yaml_error = validate_yaml_syntax(frontmatter_content)
    if yaml_error:
        errors.append(f"Frontmatter YAML error: {yaml_error}")
        return errors

    try:
        frontmatter_data = yaml.safe_load(frontmatter_content)
        frontmatter_errors = validate_frontmatter_structure(frontmatter_data)
        errors.extend(frontmatter_errors)
    except Exception as e:
        errors.append(f"Error parsing frontmatter: {e!s}")

    # Check for main content
    content_lines = lines[frontmatter_end + 1 :]
    content_text = "\n".join(content_lines).strip()

    if not content_text:
        errors.append("Content must have body text after frontmatter")

    # Check for thread title (should start with # Thread #N:)
    title_found = False
    for line in content_lines:
        if line.strip().startswith("# Thread #"):
            title_found = True
            break

    if not title_found:
        errors.append(
            "Content should contain a thread title starting with '# Thread #'"
        )

    return errors


def validate_reading_time_calculation(text: str, calculated_time: int) -> bool:
    """
    Validate that reading time calculation is reasonable.

    Args:
        text: Source text
        calculated_time: Calculated reading time in minutes

    Returns:
        bool: True if calculation seems reasonable
    """
    words = len(text.split())
    # Standard reading speed is 200-250 words per minute
    # We'll allow a range of 150-300 wpm to be flexible
    min_time = max(1, words // 300)  # Fast reading
    max_time = max(1, (words + 149) // 150)  # Slow reading

    return min_time <= calculated_time <= max_time


def validate_smushed_text_quality(smushed_text: str) -> List[str]:
    """
    Validate that smushed text appears to be properly processed.

    Args:
        smushed_text: Combined text from multiple tweets

    Returns:
        List of quality issues found
    """
    issues = []

    # Check for common artifacts that should be cleaned
    if "@" in smushed_text and smushed_text.count("@") > 2:
        issues.append("Text contains many @ mentions - may not be properly cleaned")

    if "#" in smushed_text and smushed_text.count("#") > 5:
        issues.append("Text contains many hashtags - may not be properly cleaned")

    if "http" in smushed_text.lower():
        issues.append("Text contains URLs - should be cleaned")

    # Check for reasonable sentence structure
    sentences = smushed_text.split(".")
    if len(sentences) < 3 and len(smushed_text) > 200:
        issues.append("Long text with very few sentences - may have processing issues")

    # Check for excessive whitespace
    if "  " in smushed_text:
        issues.append("Text contains multiple consecutive spaces")

    # Check for common formatting artifacts
    if smushed_text.count("\n") > len(smushed_text) // 100:
        issues.append("Text contains many newlines - may not be properly smushed")

    return issues


def extract_frontmatter_from_content(content: str) -> Optional[Dict[str, Any]]:
    """
    Extract and parse frontmatter from markdown content.

    Args:
        content: Full markdown content

    Returns:
        Parsed frontmatter dictionary or None if extraction fails
    """
    lines = content.split("\n")

    if not lines[0].strip() == "---":
        return None

    # Find end of frontmatter
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_content = "\n".join(lines[1:i])
            try:
                return yaml.safe_load(frontmatter_content)
            except yaml.YAMLError:
                return None

    return None


def validate_thread_id_format(thread_id: str) -> bool:
    """
    Validate thread ID format.

    Args:
        thread_id: Thread identifier to validate

    Returns:
        bool: True if format is valid
    """
    # Allow various formats: thread_123, thread_abc_123, etc.
    pattern = r"^thread_[a-zA-Z0-9_]+$"
    return bool(re.match(pattern, thread_id))


def validate_tweet_ids_format(tweet_ids: List[str]) -> List[str]:
    """
    Validate tweet ID formats.

    Args:
        tweet_ids: List of tweet IDs to validate

    Returns:
        List of invalid tweet IDs
    """
    invalid_ids = []
    # Twitter tweet IDs are numeric strings, typically 18-19 digits
    pattern = r"^\d{15,20}$"

    for tweet_id in tweet_ids:
        if not re.match(pattern, tweet_id):
            invalid_ids.append(tweet_id)

    return invalid_ids
