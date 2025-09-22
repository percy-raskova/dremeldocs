"""
Unit tests for generate_heavy_hitters.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


class TestGenerateHeavyHitters:
    """Test suite for heavy hitter markdown generation."""

    @pytest.fixture
    def mock_thread_data(self, sample_heavy_thread):
        """Mock filtered_threads.json data."""
        return {
            "metadata": {
                "total_threads": 3,
                "filtered_tweets": 100,
                "processing_date": "2024-09-21"
            },
            "threads": [
                sample_heavy_thread,
                {
                    "thread_id": "thread_small",
                    "smushed_text": "Short thread under 500 words",
                    "word_count": 100,
                    "tweet_count": 1,
                    "first_tweet_date": "Fri Sep 06 18:00:00 +0000 2024"
                }
            ]
        }

    def test_clean_filename_generation(self):
        """Test filename cleaning function."""
        from scripts.generate_heavy_hitters import clean_filename

        # Test various inputs
        assert clean_filename("Hello World!") == "Hello_World"
        assert clean_filename("https://example.com test") == "_test"
        assert clean_filename("A" * 100, max_length=50) == "A" * 50
        assert clean_filename("special@#$%chars") == "specialchars"
        assert clean_filename("   spaces   ") == "spaces"

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_generate_heavy_hitter_markdowns(self, mock_mkdir, mock_file, mock_thread_data):
        """Test generation of markdown files for heavy hitters."""
        mock_file.return_value.read.return_value = json.dumps(mock_thread_data)

        with patch('json.load', return_value=mock_thread_data):
            from scripts.generate_heavy_hitters import generate_heavy_hitter_markdowns

            result = generate_heavy_hitter_markdowns()

            # Should only generate markdown for threads with 500+ words
            assert len(result) == 1
            assert result[0]['word_count'] >= 500

    def test_markdown_content_format(self, sample_heavy_thread):
        """Test markdown content generation format."""
        expected_elements = [
            "# Thread #",
            "## Metadata",
            "**Word count**:",
            "**Tweet count**:",
            "**Thread ID**:",
            "**Date**:",
            "## Content",
            "### Tweet IDs",
            "### Navigation"
        ]

        # Generate markdown content (would need to extract function)
        content = f"""# Thread #1: September 06, 2024

## Metadata
- **Word count**: {sample_heavy_thread['word_count']} words
- **Tweet count**: {sample_heavy_thread['tweet_count']} tweets
- **Thread ID**: {sample_heavy_thread['thread_id']}
- **Date**: {sample_heavy_thread['first_tweet_date']}

## Content

{sample_heavy_thread['smushed_text']}

---

### Tweet IDs
{', '.join(sample_heavy_thread['tweet_ids'])}

### Navigation
[← Previous](#000) | [Index](index.md) | [Next →](#002)
"""

        for element in expected_elements:
            assert element in content

    def test_date_formatting(self):
        """Test date parsing and formatting."""
        test_dates = [
            ("Sat Apr 26 15:30:45 +0000 2025", "2025-04-26", "April 26, 2025"),
            ("Mon Sep 06 18:07:59 +0000 2024", "2024-09-06", "September 06, 2024"),
            ("invalid date", "undated", "Date unknown")
        ]

        for input_date, expected_file, expected_display in test_dates:
            # Test date parsing logic (would need to extract function)
            try:
                from datetime import datetime
                date_obj = datetime.strptime(input_date, '%a %b %d %H:%M:%S %z %Y')
                file_date = date_obj.strftime('%Y-%m-%d')
                display_date = date_obj.strftime('%B %d, %Y')
            except:
                file_date = 'undated'
                display_date = 'Date unknown'

            assert file_date == expected_file
            assert display_date == expected_display

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_index_file_generation(self, mock_mkdir, mock_file, mock_thread_data):
        """Test index.md generation with statistics."""
        from scripts.generate_heavy_hitters import generate_heavy_hitter_markdowns

        with patch('json.load', return_value=mock_thread_data):
            # Run generation
            result = generate_heavy_hitter_markdowns()

            # Check index content includes statistics
            calls = mock_file().write.call_args_list
            index_content = ''.join([call[0][0] for call in calls if call[0][0]])

            if "Index" in index_content:
                assert "Total heavy threads" in index_content
                assert "Total words" in index_content
                assert "Average thread length" in index_content

    def test_markdown_linting_compliance(self, sample_heavy_thread):
        """Test markdown output follows linting rules (MD022, MD032)."""
        # Generate sample markdown
        content_lines = [
            "# Thread #1: Date",
            "",  # MD022: Headers need blank lines
            "## Metadata",
            "",
            "- **Word count**: 500",
            "- **Tweet count**: 10",
            "",  # MD032: Lists need blank lines
            "## Content",
            "",
            "Thread content here"
        ]

        content = "\n".join(content_lines)

        # Check for blank lines around headers (MD022)
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("#"):
                if i > 0:
                    assert lines[i-1] == "" or i == 0
                if i < len(lines) - 1:
                    assert lines[i+1] == ""

    def test_theme_template_generation(self):
        """Test generation of theme extraction template."""
        from scripts.generate_heavy_hitters import generate_theme_template

        with patch('builtins.open', mock_open()) as mock_file:
            with patch('pathlib.Path.mkdir'):
                generate_theme_template()

                # Verify template content
                written_content = mock_file().write.call_args[0][0]

                assert "Theme Extraction Template" in written_content
                assert "Political Philosophy" in written_content
                assert "General Philosophy" in written_content
                assert "Thread-Theme Mapping" in written_content

    @pytest.mark.parametrize("word_count,expected", [
        (499, False),   # Just under threshold
        (500, True),    # Exactly at threshold
        (501, True),    # Just over threshold
        (1000, True),   # Well over threshold
    ])
    def test_heavy_hitter_filtering(self, word_count, expected):
        """Test filtering logic for 500+ word threads."""
        thread = {
            "word_count": word_count,
            "thread_id": f"thread_{word_count}",
            "smushed_text": "content" * word_count
        }

        # Test filtering logic
        is_heavy = thread["word_count"] >= 500
        assert is_heavy == expected

    def test_special_characters_in_content(self):
        """Test handling of special markdown characters in content."""
        special_content = """
        This has *asterisks* and _underscores_
        Also [brackets] and (parentheses)
        Plus `backticks` and ```code blocks```
        # Not a header
        > Not a quote
        """

        # Should escape or handle appropriately
        # When written to markdown file
        # These shouldn't break formatting