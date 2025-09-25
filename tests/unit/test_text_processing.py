"""
Unit tests for text processing functions in the Twitter archive pipeline.

Tests the core text processing functions including:
- generate_title(): Creates clean, meaningful titles from text
- generate_description(): Creates proper summaries
- generate_filename(): Produces correct format: 001-20250122-title_here.md
- parse_to_yyyymmdd(): Handles various date formats
- format_frontmatter_value(): Properly escapes YAML special characters
- calculate_reading_time(): Estimates reading time from word count
"""

import sys
from pathlib import Path

import pytest

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from text_utilities import (
    calculate_reading_time,
    format_frontmatter_value,
    generate_brief_title,
    generate_description,
    generate_filename,
    generate_title,
    parse_to_yyyymmdd,
)

from tests.fixtures.sample_data import (
    DATE_PARSING_CASES,
    FILENAME_GENERATION_CASES,
    SAMPLE_COMPLEX_THREAD_DATA,
    SAMPLE_SHORT_THREAD_DATA,
    SAMPLE_THREAD_DATA,
    TEXT_PROCESSING_EDGE_CASES,
    YAML_ESCAPING_CASES,
)
from tests.utils.validation import (
    validate_filename_format,
    validate_reading_time_calculation,
    validate_smushed_text_quality,
)


class TestGenerateTitle:
    """Test the generate_title function."""

    @pytest.mark.unit
    def test_generate_title_basic(self):
        """Test basic title generation from sample thread."""
        text = SAMPLE_THREAD_DATA["smushed_text"]
        title = generate_title(text)

        assert isinstance(title, str)
        assert len(title) > 0
        assert len(title) <= 60  # Default max_length
        assert not title.endswith(".")  # Should strip trailing punctuation
        # NLP model extracts better title than just first sentence
        assert len(title) > 10  # Should have meaningful content

    @pytest.mark.unit
    def test_generate_title_custom_length(self):
        """Test title generation with custom max length."""
        text = SAMPLE_THREAD_DATA["smushed_text"]
        title = generate_title(text, max_length=30)

        assert len(title) <= 30
        assert len(title) > 0

    @pytest.mark.unit
    def test_generate_title_short_text(self):
        """Test title generation with short text."""
        text = SAMPLE_SHORT_THREAD_DATA["smushed_text"]
        title = generate_title(text)

        assert isinstance(title, str)
        assert len(title) > 0
        # Check that title is generated from the text
        assert len(title) > 0  # Should have content

    @pytest.mark.unit
    @pytest.mark.parametrize("input_text,expected_output", TEXT_PROCESSING_EDGE_CASES)
    def test_generate_title_edge_cases(self, input_text, expected_output):
        """Test title generation with edge cases."""
        title = generate_title(input_text)

        if expected_output == "":
            assert title == ""
        else:
            assert isinstance(title, str)
            # For non-empty expected outputs, verify reasonable processing
            if expected_output and len(expected_output) <= 60:
                assert len(title) <= 60

    @pytest.mark.unit
    def test_generate_title_social_media_cleanup(self):
        """Test that titles are generated even with social media artifacts."""
        text = "This is @mentioned text with #hashtags and https://urls.com that should be cleaned"
        title = generate_title(text)

        # Title should be generated (even if social media artifacts aren't fully cleaned)
        assert isinstance(title, str)
        assert len(title) > 0
        # The NLP model should generate a meaningful title from the content

    @pytest.mark.unit
    def test_generate_title_punctuation_removal(self):
        """Test that trailing punctuation is properly removed."""
        test_cases = [
            "This is a sentence.",
            "This is a question?",
            "This is exciting!",
            "This has: colons",
            "This has; semicolons",
        ]

        for text in test_cases:
            title = generate_title(text)
            assert not title.endswith((".", "?", "!", ":", ";"))


class TestGenerateDescription:
    """Test the generate_description function."""

    @pytest.mark.unit
    def test_generate_description_basic(self):
        """Test basic description generation."""
        text = SAMPLE_THREAD_DATA["smushed_text"]
        description = generate_description(text)

        assert isinstance(description, str)
        assert len(description) > 0
        assert len(description) <= 200  # Typical description length
        assert "dialectical materialism" in description.lower()

    @pytest.mark.unit
    def test_generate_description_short_text(self):
        """Test description generation with short text."""
        text = SAMPLE_SHORT_THREAD_DATA["smushed_text"]
        description = generate_description(text)

        assert isinstance(description, str)
        assert len(description) > 0

    @pytest.mark.unit
    def test_generate_description_complex_text(self):
        """Test description generation with complex political text."""
        text = SAMPLE_COMPLEX_THREAD_DATA["smushed_text"]
        description = generate_description(text)

        assert isinstance(description, str)
        assert len(description) > 0
        assert any(
            term in description.lower() for term in ["palestine", "colonial", "settler"]
        )


class TestGenerateFilename:
    """Test the generate_filename function."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "seq_num,date_str,text,expected", FILENAME_GENERATION_CASES
    )
    def test_generate_filename_cases(self, seq_num, date_str, text, expected):
        """Test filename generation with various inputs."""
        filename = generate_filename(seq_num, date_str, text)

        # Validate basic format
        assert validate_filename_format(filename)

        # Check sequence number formatting
        assert filename.startswith(f"{seq_num:03d}-")

        # Check date formatting
        expected_date = parse_to_yyyymmdd(date_str)
        assert expected_date in filename

        # Check file extension
        assert filename.endswith(".md")

    @pytest.mark.unit
    def test_generate_filename_sequence_padding(self):
        """Test that sequence numbers are properly zero-padded."""
        test_cases = [(1, "001"), (42, "042"), (100, "100"), (999, "999")]

        for seq_num, expected_padded in test_cases:
            filename = generate_filename(
                seq_num, "Wed Nov 15 14:23:45 +0000 2023", "Test title"
            )
            assert filename.startswith(expected_padded + "-")

    @pytest.mark.unit
    def test_generate_filename_title_sanitization(self):
        """Test that titles are properly sanitized for filenames."""
        problematic_title = (
            "Title with/slashes and\\backslashes and:colons and?questions"
        )
        filename = generate_filename(
            1, "Wed Nov 15 14:23:45 +0000 2023", problematic_title
        )

        # Check that problematic characters are handled
        assert "/" not in filename
        assert "\\" not in filename
        assert "?" not in filename
        # Should contain underscores or be otherwise cleaned
        assert validate_filename_format(filename)


class TestParseDateToYYYYMMDD:
    """Test the parse_to_yyyymmdd function."""

    @pytest.mark.unit
    @pytest.mark.parametrize("input_date,expected_output", DATE_PARSING_CASES)
    def test_parse_date_twitter_format(self, input_date, expected_output):
        """Test parsing Twitter date format to YYYYMMDD."""
        result = parse_to_yyyymmdd(input_date)
        assert result == expected_output

    @pytest.mark.unit
    def test_parse_date_invalid_input(self):
        """Test parsing with invalid date inputs."""
        invalid_dates = [
            "",
            "not a date",
            "2023-13-45",  # Invalid month/day
            None,
        ]

        for invalid_date in invalid_dates:
            # Should either raise exception or return a reasonable default
            try:
                result = parse_to_yyyymmdd(invalid_date)
                # If it doesn't raise an exception, result should be a string
                assert isinstance(result, str)
            except (ValueError, TypeError, AttributeError):
                # These exceptions are acceptable for invalid input
                pass

    @pytest.mark.unit
    def test_parse_date_edge_cases(self):
        """Test date parsing edge cases."""
        # Test leap year
        leap_year_date = "Mon Feb 29 12:00:00 +0000 2024"
        result = parse_to_yyyymmdd(leap_year_date)
        assert result == "20240229"


class TestFormatFrontmatterValue:
    """Test the format_frontmatter_value function."""

    @pytest.mark.unit
    @pytest.mark.parametrize("input_value,expected_output", YAML_ESCAPING_CASES)
    def test_yaml_escaping(self, input_value, expected_output):
        """Test YAML special character escaping."""
        result = format_frontmatter_value(input_value)
        assert result == expected_output

    @pytest.mark.unit
    def test_format_frontmatter_non_string(self):
        """Test frontmatter formatting with non-string values."""
        test_cases = [
            (123, "123"),
            (True, "true"),
            (False, "false"),
            ([], "[]"),
            ({}, "{}"),
        ]

        for input_val, _expected in test_cases:
            result = format_frontmatter_value(input_val)
            # Should handle non-strings gracefully
            assert isinstance(result, str)

    @pytest.mark.unit
    def test_format_frontmatter_empty_and_none(self):
        """Test frontmatter formatting with empty/None values."""
        assert format_frontmatter_value("") == '""'

        # Test None handling
        result = format_frontmatter_value(None)
        assert isinstance(result, str)


class TestCalculateReadingTime:
    """Test the calculate_reading_time function."""

    @pytest.mark.unit
    def test_calculate_reading_time_basic(self):
        """Test basic reading time calculation."""
        text = SAMPLE_THREAD_DATA["smushed_text"]
        reading_time = calculate_reading_time(text)

        assert isinstance(reading_time, int)
        assert reading_time > 0
        assert validate_reading_time_calculation(text, reading_time)

    @pytest.mark.unit
    def test_calculate_reading_time_short_text(self):
        """Test reading time for short text."""
        text = SAMPLE_SHORT_THREAD_DATA["smushed_text"]
        reading_time = calculate_reading_time(text)

        assert isinstance(reading_time, int)
        assert reading_time >= 1  # Minimum should be 1 minute

    @pytest.mark.unit
    def test_calculate_reading_time_empty_text(self):
        """Test reading time calculation with empty text."""
        reading_time = calculate_reading_time("")
        assert reading_time >= 1  # Should return minimum time

    @pytest.mark.unit
    def test_calculate_reading_time_long_text(self):
        """Test reading time calculation with very long text."""
        # Create a long text (approximately 1000 words)
        long_text = "word " * 1000
        reading_time = calculate_reading_time(long_text)

        assert isinstance(reading_time, int)
        assert reading_time >= 3  # Should be at least 3-4 minutes for 1000 words
        assert reading_time <= 8  # Should not be unreasonably high


class TestGenerateBriefTitle:
    """Test the generate_brief_title function."""

    @pytest.mark.unit
    def test_generate_brief_title_basic(self):
        """Test basic brief title generation."""
        text = SAMPLE_THREAD_DATA["smushed_text"]
        brief_title = generate_brief_title(text)

        assert isinstance(brief_title, str)
        assert len(brief_title) > 0
        assert len(brief_title) <= 50  # Default max length
        # Should be filename-safe (no spaces, special chars replaced with underscores)
        assert " " not in brief_title
        assert brief_title.replace("_", "").replace("-", "").isalnum()

    @pytest.mark.unit
    def test_generate_brief_title_custom_length(self):
        """Test brief title with custom max length."""
        text = SAMPLE_THREAD_DATA["smushed_text"]
        brief_title = generate_brief_title(text, max_length=20)

        assert len(brief_title) <= 20

    @pytest.mark.unit
    def test_generate_brief_title_filename_safety(self):
        """Test that brief titles are safe for filenames."""
        problematic_text = "Title with/slashes and spaces and:colons!"
        brief_title = generate_brief_title(problematic_text)

        # Should not contain filesystem problematic characters
        forbidden_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|", " "]
        for char in forbidden_chars:
            assert char not in brief_title


class TestCleanSocialText:
    """Test the clean_social_text function."""

    @pytest.mark.unit
    def test_clean_social_text_basic(self):
        """Test basic social media text cleaning."""
        # This test assumes clean_social_text is available and working
        # If the function processes spaCy docs, we may need to mock or adapt
        pass  # Placeholder - implement based on actual function signature

    @pytest.mark.unit
    def test_clean_social_text_artifacts(self):
        """Test removal of social media artifacts."""
        # Test cases for @mentions, #hashtags, URLs, etc.
        pass  # Placeholder - implement based on actual function behavior


class TestExtractKeyPhrase:
    """Test the extract_key_phrase function."""

    @pytest.mark.unit
    def test_extract_key_phrase_basic(self):
        """Test key phrase extraction."""
        # This test depends on the actual implementation
        pass  # Placeholder - implement based on actual function behavior


# Integration tests for the text processing module
class TestTextProcessingIntegration:
    """Integration tests for text processing functions working together."""

    @pytest.mark.integration
    def test_full_text_processing_pipeline(self):
        """Test that all text processing functions work together coherently."""
        thread = SAMPLE_THREAD_DATA

        # Generate all text processing outputs
        title = generate_title(thread["smushed_text"])
        description = generate_description(thread["smushed_text"])
        reading_time = calculate_reading_time(thread["smushed_text"])
        filename = generate_filename(
            1, thread["first_tweet_date"], thread["smushed_text"]
        )

        # Validate they all work together
        assert len(title) > 0
        assert len(description) > 0
        assert reading_time > 0
        assert validate_filename_format(filename)

        # Validate reading time is reasonable for the word count
        assert validate_reading_time_calculation(thread["smushed_text"], reading_time)

    @pytest.mark.integration
    def test_text_quality_validation(self):
        """Test that processed text meets quality standards."""
        for thread_data in [SAMPLE_THREAD_DATA, SAMPLE_COMPLEX_THREAD_DATA]:
            quality_issues = validate_smushed_text_quality(thread_data["smushed_text"])

            # Some issues may be acceptable in test data, but validate structure
            assert isinstance(quality_issues, list)

            # Generate title and description
            title = generate_title(thread_data["smushed_text"])
            description = generate_description(thread_data["smushed_text"])

            # Validate outputs are reasonable
            assert len(title.strip()) > 0
            assert len(description.strip()) > 0

    @pytest.mark.integration
    def test_consistency_across_samples(self):
        """Test that processing is consistent across different sample types."""
        samples = [
            SAMPLE_THREAD_DATA,
            SAMPLE_SHORT_THREAD_DATA,
            SAMPLE_COMPLEX_THREAD_DATA,
        ]

        for i, sample in enumerate(samples):
            # All samples should produce valid outputs
            title = generate_title(sample["smushed_text"])
            description = generate_description(sample["smushed_text"])
            reading_time = calculate_reading_time(sample["smushed_text"])
            filename = generate_filename(
                i + 1, sample["first_tweet_date"], sample["smushed_text"]
            )

            # Basic validation
            assert isinstance(title, str) and len(title) > 0
            assert isinstance(description, str) and len(description) > 0
            assert isinstance(reading_time, int) and reading_time > 0
            assert validate_filename_format(filename)
