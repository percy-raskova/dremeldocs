"""
Unit tests for frontmatter generation functionality.

Tests the YAML frontmatter generation used in the markdown output files,
including proper field inclusion, YAML syntax validation, and special character escaping.
"""

import pytest
import yaml
import sys
from pathlib import Path
from datetime import datetime

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from text_processing import (
    format_frontmatter_value,
    parse_to_yyyymmdd,
    generate_title,
    generate_description,
    calculate_reading_time
)

from tests.fixtures.sample_data import (
    SAMPLE_THREAD_DATA,
    SAMPLE_SHORT_THREAD_DATA,
    SAMPLE_COMPLEX_THREAD_DATA,
    EXPECTED_FRONTMATTER,
    YAML_ESCAPING_CASES
)

from tests.utils.validation import (
    validate_frontmatter_structure,
    validate_yaml_syntax,
    extract_frontmatter_from_content
)


class TestFrontmatterGeneration:
    """Test frontmatter generation for markdown files."""

    @pytest.mark.unit
    def test_generate_complete_frontmatter(self):
        """Test generation of complete frontmatter for a thread."""
        thread = SAMPLE_THREAD_DATA
        thread_number = 1

        # Generate all frontmatter components
        title = generate_title(thread["smushed_text"])
        description = generate_description(thread["smushed_text"])
        reading_time = calculate_reading_time(thread["smushed_text"])

        # Get date in YYYY-MM-DD format for frontmatter
        date_for_frontmatter = parse_to_yyyymmdd(thread["first_tweet_date"])
        date_formatted = f"{date_for_frontmatter[:4]}-{date_for_frontmatter[4:6]}-{date_for_frontmatter[6:8]}"

        # Build frontmatter dictionary
        frontmatter_dict = {
            'title': title,
            'date': {
                'created': date_formatted
            },
            'categories': ['heavy_hitters'],
            'thread_id': thread["thread_id"],
            'word_count': thread["word_count"],
            'reading_time': reading_time,
            'description': description,
            'tweet_count': thread["tweet_count"],
            'heavy_hitter': True,
            'thread_number': thread_number,
            'author': "@BmoreOrganized"
        }

        # Validate frontmatter structure
        errors = validate_frontmatter_structure(frontmatter_dict)
        assert len(errors) == 0, f"Frontmatter validation errors: {errors}"

        # Test YAML serialization
        yaml_content = yaml.safe_dump(frontmatter_dict, default_flow_style=False)
        yaml_error = validate_yaml_syntax(yaml_content)
        assert yaml_error is None, f"YAML syntax error: {yaml_error}"

    @pytest.mark.unit
    def test_frontmatter_field_types(self):
        """Test that frontmatter fields have correct types."""
        thread = SAMPLE_THREAD_DATA

        # Generate frontmatter components and verify types
        title = generate_title(thread["smushed_text"])
        assert isinstance(title, str)

        description = generate_description(thread["smushed_text"])
        assert isinstance(description, str)

        reading_time = calculate_reading_time(thread["smushed_text"])
        assert isinstance(reading_time, int)

        # Test date formatting
        date_formatted = parse_to_yyyymmdd(thread["first_tweet_date"])
        assert isinstance(date_formatted, str)
        assert len(date_formatted) == 8  # YYYYMMDD format

        # Test word count and tweet count
        assert isinstance(thread["word_count"], int)
        assert isinstance(thread["tweet_count"], int)

    @pytest.mark.unit
    def test_frontmatter_required_fields(self):
        """Test that all required frontmatter fields are present."""
        expected_fields = {
            'title', 'date', 'categories', 'thread_id', 'word_count',
            'reading_time', 'description', 'tweet_count', 'heavy_hitter',
            'thread_number', 'author'
        }

        # Use the expected frontmatter from fixtures
        frontmatter = EXPECTED_FRONTMATTER.copy()

        # Check all required fields are present
        for field in expected_fields:
            assert field in frontmatter, f"Missing required field: {field}"

    @pytest.mark.unit
    def test_frontmatter_date_structure(self):
        """Test that date field has correct nested structure."""
        thread = SAMPLE_THREAD_DATA

        # Generate date structure
        date_yyyymmdd = parse_to_yyyymmdd(thread["first_tweet_date"])
        date_formatted = f"{date_yyyymmdd[:4]}-{date_yyyymmdd[4:6]}-{date_yyyymmdd[6:8]}"

        date_structure = {
            'created': date_formatted
        }

        # Validate date structure
        assert isinstance(date_structure, dict)
        assert 'created' in date_structure
        assert isinstance(date_structure['created'], str)

        # Validate date format (YYYY-MM-DD)
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        assert re.match(date_pattern, date_structure['created'])

        # Validate date is parseable
        try:
            datetime.strptime(date_structure['created'], '%Y-%m-%d')
        except ValueError:
            pytest.fail(f"Invalid date format: {date_structure['created']}")

    @pytest.mark.unit
    def test_frontmatter_categories_structure(self):
        """Test that categories field is properly structured."""
        categories = ['heavy_hitters']

        assert isinstance(categories, list)
        assert len(categories) >= 1
        assert 'heavy_hitters' in categories

        # All categories should be strings
        for category in categories:
            assert isinstance(category, str)
            assert len(category) > 0

    @pytest.mark.unit
    def test_frontmatter_yaml_escaping(self):
        """Test YAML special character escaping in frontmatter values."""
        # Test cases with special characters that need escaping
        test_cases = [
            'Title with "quotes" needs escaping',
            "Title with 'apostrophes' might need escaping",
            'Title with: colons needs escaping',
            'Title with [brackets] needs escaping',
            'Title with {braces} needs escaping',
            'Title with | pipe needs escaping',
            'Title with > greater than',
            'Title with & ampersand',
            'Title with % percent'
        ]

        for test_title in test_cases:
            escaped_title = format_frontmatter_value(test_title)

            # Create minimal frontmatter with escaped title
            frontmatter = {
                'title': escaped_title,
                'description': format_frontmatter_value(f"Description for {test_title}")
            }

            # Test that it serializes to valid YAML
            try:
                yaml_content = yaml.safe_dump(frontmatter)
                # Parse it back to ensure it's valid
                parsed_back = yaml.safe_load(yaml_content)
                assert isinstance(parsed_back, dict)
            except yaml.YAMLError as e:
                pytest.fail(f"YAML escaping failed for '{test_title}': {e}")

    @pytest.mark.unit
    @pytest.mark.parametrize("input_value,expected_output", YAML_ESCAPING_CASES)
    def test_format_frontmatter_value_escaping(self, input_value, expected_output):
        """Test format_frontmatter_value function with various inputs."""
        result = format_frontmatter_value(input_value)
        assert result == expected_output

    @pytest.mark.unit
    def test_frontmatter_boolean_values(self):
        """Test that boolean values are properly handled in frontmatter."""
        frontmatter = {
            'heavy_hitter': True,
            'processed': False
        }

        # Test YAML serialization of booleans
        yaml_content = yaml.safe_dump(frontmatter)
        parsed_back = yaml.safe_load(yaml_content)

        assert parsed_back['heavy_hitter'] is True
        assert parsed_back['processed'] is False

    @pytest.mark.unit
    def test_frontmatter_integer_values(self):
        """Test that integer values are properly handled in frontmatter."""
        frontmatter = {
            'word_count': 756,
            'reading_time': 4,
            'tweet_count': 18,
            'thread_number': 1
        }

        # Test YAML serialization of integers
        yaml_content = yaml.safe_dump(frontmatter)
        parsed_back = yaml.safe_load(yaml_content)

        for key, value in frontmatter.items():
            assert parsed_back[key] == value
            assert isinstance(parsed_back[key], int)

    @pytest.mark.unit
    def test_frontmatter_with_entities(self):
        """Test frontmatter generation when entities are present."""
        # Test with entity data (if extract_entities function is available)
        entities = ["Marx", "capitalism", "proletariat"]

        frontmatter = {
            'title': 'Test title',
            'entities': format_frontmatter_value(entities)
        }

        # Test YAML serialization
        yaml_content = yaml.safe_dump(frontmatter)
        yaml_error = validate_yaml_syntax(yaml_content)
        assert yaml_error is None

    @pytest.mark.unit
    def test_frontmatter_markdown_integration(self):
        """Test frontmatter integration in complete markdown content."""
        # Create a complete markdown file content with frontmatter
        thread = SAMPLE_THREAD_DATA

        # Generate frontmatter components
        title = generate_title(thread["smushed_text"])
        description = generate_description(thread["smushed_text"])
        reading_time = calculate_reading_time(thread["smushed_text"])

        # Build frontmatter
        frontmatter_dict = {
            'title': format_frontmatter_value(title),
            'date': {
                'created': '2023-11-15'
            },
            'categories': ['heavy_hitters'],
            'thread_id': format_frontmatter_value(thread["thread_id"]),
            'word_count': thread["word_count"],
            'reading_time': reading_time,
            'description': format_frontmatter_value(description),
            'tweet_count': thread["tweet_count"],
            'heavy_hitter': True,
            'thread_number': 1,
            'author': format_frontmatter_value("@BmoreOrganized")
        }

        # Create complete markdown content
        frontmatter_yaml = yaml.safe_dump(frontmatter_dict, default_flow_style=False)
        markdown_content = f"""---
{frontmatter_yaml}---

# Thread #1: {title}

{thread["smushed_text"]}
"""

        # Test that frontmatter can be extracted back
        extracted_frontmatter = extract_frontmatter_from_content(markdown_content)
        assert extracted_frontmatter is not None

        # Validate extracted frontmatter
        errors = validate_frontmatter_structure(extracted_frontmatter)
        assert len(errors) == 0, f"Extracted frontmatter validation errors: {errors}"


class TestFrontmatterVariations:
    """Test frontmatter generation with different thread types."""

    @pytest.mark.unit
    def test_short_thread_frontmatter(self):
        """Test frontmatter generation for short threads."""
        thread = SAMPLE_SHORT_THREAD_DATA

        title = generate_title(thread["smushed_text"])
        description = generate_description(thread["smushed_text"])
        reading_time = calculate_reading_time(thread["smushed_text"])

        frontmatter_dict = {
            'title': format_frontmatter_value(title),
            'word_count': thread["word_count"],
            'reading_time': reading_time,
            'description': format_frontmatter_value(description),
            'tweet_count': thread["tweet_count"]
        }

        # Even short threads should have valid frontmatter
        assert isinstance(frontmatter_dict['title'], str)
        assert frontmatter_dict['word_count'] > 0
        assert frontmatter_dict['reading_time'] >= 1  # Minimum 1 minute
        assert isinstance(frontmatter_dict['description'], str)

    @pytest.mark.unit
    def test_complex_thread_frontmatter(self):
        """Test frontmatter generation for complex threads with special content."""
        thread = SAMPLE_COMPLEX_THREAD_DATA

        title = generate_title(thread["smushed_text"])
        description = generate_description(thread["smushed_text"])

        # Complex threads should handle special characters properly
        escaped_title = format_frontmatter_value(title)
        escaped_description = format_frontmatter_value(description)

        # Test that escaping works for complex content
        frontmatter_dict = {
            'title': escaped_title,
            'description': escaped_description
        }

        yaml_content = yaml.safe_dump(frontmatter_dict)
        yaml_error = validate_yaml_syntax(yaml_content)
        assert yaml_error is None

    @pytest.mark.unit
    def test_frontmatter_consistency_across_threads(self):
        """Test that frontmatter structure is consistent across different threads."""
        threads = [SAMPLE_THREAD_DATA, SAMPLE_SHORT_THREAD_DATA, SAMPLE_COMPLEX_THREAD_DATA]

        frontmatter_structures = []

        for i, thread in enumerate(threads):
            title = generate_title(thread["smushed_text"])
            description = generate_description(thread["smushed_text"])
            reading_time = calculate_reading_time(thread["smushed_text"])

            frontmatter_dict = {
                'title': format_frontmatter_value(title),
                'date': {'created': '2023-11-15'},
                'categories': ['heavy_hitters'],
                'thread_id': format_frontmatter_value(thread["thread_id"]),
                'word_count': thread["word_count"],
                'reading_time': reading_time,
                'description': format_frontmatter_value(description),
                'tweet_count': thread["tweet_count"],
                'heavy_hitter': True,
                'thread_number': i + 1,
                'author': format_frontmatter_value("@BmoreOrganized")
            }

            frontmatter_structures.append(set(frontmatter_dict.keys()))

            # Validate each frontmatter
            errors = validate_frontmatter_structure(frontmatter_dict)
            assert len(errors) == 0, f"Thread {i+1} frontmatter errors: {errors}"

        # All frontmatter should have the same structure (same keys)
        first_structure = frontmatter_structures[0]
        for i, structure in enumerate(frontmatter_structures[1:], 1):
            assert structure == first_structure, f"Thread {i+1} has different frontmatter structure"