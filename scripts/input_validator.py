#!/usr/bin/env python3
"""
Input validation module for the DremelDocs pipeline.

Provides comprehensive validation for JSON data, command arguments,
and user inputs to prevent malformed data from entering the pipeline.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class InputValidator:
    """Comprehensive input validation for the DremelDocs pipeline."""

    # Valid theme names from the analysis report
    VALID_THEMES = {
        "marxism_historical_materialism",
        "political_economy",
        "organizational_theory",
        "covid_public_health_politics",
        "fascism_analysis",
        "cultural_criticism",
        "imperialism_colonialism",
        "dialectics",
        "intersectional",
        "other",
    }

    # Tweet structure validation
    # Twitter uses id_str in exports, so we accept either id or id_str
    REQUIRED_TWEET_FIELDS = ["full_text"]  # Only full_text is truly required
    OPTIONAL_TWEET_FIELDS = [
        "id", "id_str", "created_at",
        "favorite_count", "retweet_count", "user",
        "in_reply_to_status_id", "in_reply_to_user_id"
    ]

    # Thread structure validation
    REQUIRED_THREAD_FIELDS = ["thread_id", "text", "created_at"]
    OPTIONAL_THREAD_FIELDS = [
        "tweet_count", "total_favorites", "total_retweets",
        "tweets", "themes", "confidence", "tags"
    ]

    @classmethod
    def validate_tweet(cls, tweet: Dict[str, Any]) -> bool:
        """
        Validate a tweet object structure.

        Args:
            tweet: Tweet dictionary to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(tweet, dict):
            raise ValidationError(f"Tweet must be a dictionary, got {type(tweet)}")

        # Check required fields
        missing = set(cls.REQUIRED_TWEET_FIELDS) - set(tweet.keys())
        if missing:
            raise ValidationError(f"Tweet missing required fields: {missing}")

        # Validate field types - accept either id or id_str
        has_id = "id" in tweet or "id_str" in tweet
        if not has_id:
            raise ValidationError("Tweet must have either 'id' or 'id_str' field")

        # Check the ID field that exists
        if "id" in tweet and not isinstance(tweet.get("id"), (str, int)):
            raise ValidationError("Tweet id must be string or integer")
        if "id_str" in tweet and not isinstance(tweet.get("id_str"), str):
            raise ValidationError("Tweet id_str must be string")

        if not isinstance(tweet.get("full_text"), str):
            raise ValidationError("Tweet full_text must be string")

        # Validate created_at format IF present (not required for tests)
        if "created_at" in tweet:
            created_at = tweet.get("created_at")
            if not cls._validate_datetime(created_at):
                raise ValidationError(f"Invalid created_at format: {created_at}")

        # Validate numeric fields if present (Twitter exports these as strings)
        for field in ["favorite_count", "retweet_count"]:
            if field in tweet:
                value = tweet[field]
                # Try to convert string to number
                if isinstance(value, str):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        raise ValidationError(f"{field} must be numeric or numeric string")
                elif not isinstance(value, (int, float)):
                    raise ValidationError(f"{field} must be numeric")

                if value < 0:
                    raise ValidationError(f"{field} cannot be negative")

        return True

    @classmethod
    def validate_thread(cls, thread: Dict[str, Any]) -> bool:
        """
        Validate a thread object structure.

        Args:
            thread: Thread dictionary to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(thread, dict):
            raise ValidationError(f"Thread must be a dictionary, got {type(thread)}")

        # Check required fields
        missing = set(cls.REQUIRED_THREAD_FIELDS) - set(thread.keys())
        if missing:
            raise ValidationError(f"Thread missing required fields: {missing}")

        # Validate thread_id
        if not thread.get("thread_id"):
            raise ValidationError("Thread must have non-empty thread_id")

        # Validate text
        if not isinstance(thread.get("text"), str):
            raise ValidationError("Thread text must be string")

        # Validate themes if present
        if "themes" in thread:
            cls.validate_themes(thread["themes"])

        # Validate confidence if present
        if "confidence" in thread:
            confidence = thread["confidence"]
            if not isinstance(confidence, (int, float)):
                raise ValidationError("Confidence must be numeric")
            if not 0 <= confidence <= 1:
                raise ValidationError("Confidence must be between 0 and 1")

        # Validate tweet_count if present
        if "tweet_count" in thread:
            if not isinstance(thread["tweet_count"], int):
                raise ValidationError("tweet_count must be integer")
            if thread["tweet_count"] < 1:
                raise ValidationError("tweet_count must be positive")

        return True

    @classmethod
    def validate_themes(cls, themes: Union[str, List[str]]) -> bool:
        """
        Validate theme names.

        Args:
            themes: Single theme or list of themes

        Returns:
            True if valid

        Raises:
            ValidationError: If invalid themes found
        """
        if isinstance(themes, str):
            themes = [themes]

        if not isinstance(themes, list):
            raise ValidationError(f"Themes must be string or list, got {type(themes)}")

        invalid = set(themes) - cls.VALID_THEMES
        if invalid:
            raise ValidationError(
                f"Invalid themes: {invalid}. Valid themes: {cls.VALID_THEMES}"
            )

        return True

    @classmethod
    def validate_json_file(cls, file_path: Union[str, Path],
                          schema: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate and load a JSON file.

        Args:
            file_path: Path to JSON file
            schema: Optional schema type ("tweets", "threads", "classified")

        Returns:
            Loaded JSON data

        Raises:
            ValidationError: If file is invalid
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        if not file_path.suffix.lower() == ".json":
            raise ValidationError(f"File must be JSON: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in {file_path}: {e}")

        # Apply schema-specific validation
        if schema == "threads" and isinstance(data, dict):
            threads = data.get("threads", [])
            for thread in threads[:5]:  # Validate first 5 for performance
                cls.validate_thread(thread)

        return data

    @classmethod
    def validate_vocabulary_entry(cls, entry: Dict[str, Any]) -> bool:
        """
        Validate a vocabulary YAML entry.

        Args:
            entry: Vocabulary dictionary

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        required = ["theme", "keywords"]
        missing = set(required) - set(entry.keys())
        if missing:
            raise ValidationError(f"Vocabulary missing required fields: {missing}")

        # Validate theme
        if entry["theme"] not in cls.VALID_THEMES:
            raise ValidationError(f"Invalid vocabulary theme: {entry['theme']}")

        # Validate keywords
        keywords = entry.get("keywords", [])
        if not isinstance(keywords, list):
            raise ValidationError("Keywords must be a list")

        if not keywords:
            raise ValidationError("Keywords list cannot be empty")

        for keyword in keywords:
            if not isinstance(keyword, str):
                raise ValidationError(f"Keyword must be string, got: {keyword}")
            if not keyword.strip():
                raise ValidationError("Keywords cannot be empty strings")

        # Validate patterns if present
        if "patterns" in entry:
            patterns = entry["patterns"]
            if not isinstance(patterns, list):
                raise ValidationError("Patterns must be a list")

            for pattern in patterns:
                try:
                    re.compile(pattern)
                except re.error as e:
                    raise ValidationError(f"Invalid regex pattern '{pattern}': {e}")

        return True

    @classmethod
    def sanitize_text(cls, text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text input for safe processing.

        Args:
            text: Text to sanitize
            max_length: Optional maximum length

        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            text = str(text)

        # Remove null bytes and control characters
        text = text.replace('\x00', '')
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Apply length limit if specified
        if max_length and len(text) > max_length:
            text = text[:max_length]

        return text

    @classmethod
    def validate_command_args(cls, args: List[str]) -> bool:
        """
        Validate command line arguments for safety.

        Args:
            args: Command arguments

        Returns:
            True if valid

        Raises:
            ValidationError: If dangerous arguments detected
        """
        dangerous_patterns = [
            r';\s*rm\s+-rf',  # Command injection
            r'&&.*rm',        # Command chaining
            r'\|.*sh',        # Pipe to shell
            r'`.*`',          # Command substitution
            r'\$\(.*\)',      # Command substitution
            r'\.\./',         # Path traversal
        ]

        for arg in args:
            for pattern in dangerous_patterns:
                if re.search(pattern, arg, re.IGNORECASE):
                    raise ValidationError(f"Dangerous argument pattern detected: {arg}")

        return True

    @classmethod
    def _validate_datetime(cls, dt_str: str) -> bool:
        """Validate datetime string format."""
        if not dt_str:
            return False

        # Common Twitter datetime formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%a %b %d %H:%M:%S +0000 %Y",
        ]

        for fmt in formats:
            try:
                datetime.strptime(str(dt_str), fmt)
                return True
            except ValueError:
                continue

        return False


def validate_pipeline_input(input_file: Union[str, Path]) -> bool:
    """
    Validate input for the main pipeline.

    Args:
        input_file: Path to input file

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    validator = InputValidator()

    # Check if it's the Twitter archive
    if "tweets.js" in str(input_file):
        # Basic validation for Twitter archive
        input_path = Path(input_file)
        if not input_path.exists():
            raise ValidationError(f"Twitter archive not found: {input_file}")

        # Check file size (should be reasonable)
        size_mb = input_path.stat().st_size / (1024 * 1024)
        if size_mb > 1000:  # 1GB limit
            raise ValidationError(f"Archive too large: {size_mb:.1f}MB")

    else:
        # Validate as JSON
        data = validator.validate_json_file(input_file)

    return True


# Convenience exports
__all__ = [
    'ValidationError',
    'InputValidator',
    'validate_pipeline_input',
]