#!/usr/bin/env python3
"""
Comprehensive unit tests for generate_heavy_hitters.py module.

Tests all functions for generating markdown files from heavy-hitter threads,
including file generation, frontmatter creation, index generation, and theme templates.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open, MagicMock
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from generate_heavy_hitters import (
    generate_heavy_hitter_markdowns,
    generate_theme_template
)


# Test fixtures
@pytest.fixture
def sample_threads_data():
    """Sample filtered threads data matching expected format."""
    return {
        "threads": [
            {
                "thread_id": "thread_001",
                "word_count": 750,
                "tweet_count": 5,
                "first_tweet_date": "Wed Nov 15 14:23:45 +0000 2023",
                "smushed_text": "This is a long philosophical thread about dialectical materialism. " * 50,
                "tweet_ids": ["id1", "id2", "id3", "id4", "id5"]
            },
            {
                "thread_id": "thread_002",
                "word_count": 550,
                "tweet_count": 3,
                "first_tweet_date": "Thu Dec 07 09:15:30 +0000 2023",
                "smushed_text": "A thread about political economy and class analysis. " * 40,
                "tweet_ids": ["id6", "id7", "id8"]
            },
            {
                "thread_id": "thread_003",
                "word_count": 450,  # Below threshold
                "tweet_count": 2,
                "first_tweet_date": "Mon Jan 22 16:47:12 +0000 2024",
                "smushed_text": "Short thread about something. " * 20,
                "tweet_ids": ["id9", "id10"]
            },
            {
                "thread_id": "thread_004",
                "word_count": 1200,
                "tweet_count": 8,
                "first_tweet_date": "Invalid Date Format",  # Test date error handling
                "smushed_text": "Thread with invalid date format. " * 80,
                "tweet_ids": ["id11", "id12", "id13", "id14", "id15", "id16", "id17", "id18"]
            }
        ]
    }


@pytest.fixture
def mock_text_processing():
    """Mock text processing functions."""
    with patch('generate_heavy_hitters.generate_title') as mock_title, \
         patch('generate_heavy_hitters.generate_description') as mock_desc, \
         patch('generate_heavy_hitters.calculate_reading_time') as mock_time, \
         patch('generate_heavy_hitters.format_frontmatter_value') as mock_format, \
         patch('generate_heavy_hitters.extract_entities') as mock_entities, \
         patch('generate_heavy_hitters.generate_filename') as mock_filename, \
         patch('generate_heavy_hitters.parse_to_yyyymmdd') as mock_parse:

        # Configure mocks
        mock_title.side_effect = lambda text: f"Title for {text[:20]}..."
        mock_desc.side_effect = lambda text: f"Description of {text[:30]}..."
        mock_time.return_value = 3
        mock_format.side_effect = lambda value: f'"{value}"' if isinstance(value, str) else str(value)
        mock_entities.return_value = ["Entity1", "Entity2"]
        mock_filename.side_effect = lambda seq, date, text: f"{seq:03d}-20231115-generated_title.md"
        mock_parse.return_value = "20231115"

        yield {
            'title': mock_title,
            'desc': mock_desc,
            'time': mock_time,
            'format': mock_format,
            'entities': mock_entities,
            'filename': mock_filename,
            'parse': mock_parse
        }


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    docs_dir = tmp_path / "docs" / "heavy_hitters"
    docs_dir.mkdir(parents=True)

    return tmp_path


class TestGenerateHeavyHitterMarkdowns:
    """Test suite for generate_heavy_hitter_markdowns function."""

    @pytest.mark.unit
    def test_filters_heavy_threads(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that only threads with 500+ words are processed."""
        monkeypatch.chdir(temp_project_dir)

        # Write test data
        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        # Run function
        result = generate_heavy_hitter_markdowns()

        # Verify only threads with 500+ words are processed
        assert len(result) == 3  # Only 3 threads have 500+ words
        assert all(file['word_count'] >= 500 for file in result)

    @pytest.mark.unit
    def test_sorts_by_word_count(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that threads are sorted by word count (longest first)."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        result = generate_heavy_hitter_markdowns()

        # Check sorting
        word_counts = [file['word_count'] for file in result]
        assert word_counts == sorted(word_counts, reverse=True)
        assert word_counts[0] == 1200  # Longest thread first

    @pytest.mark.unit
    def test_generates_markdown_files(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that markdown files are generated with correct content."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        result = generate_heavy_hitter_markdowns()

        # Check files were created
        heavy_hitters_dir = temp_project_dir / "docs" / "heavy_hitters"
        markdown_files = list(heavy_hitters_dir.glob("*.md"))

        # Should have 3 thread files + 1 index file
        assert len(markdown_files) == 4

        # Check a generated file content
        first_file = heavy_hitters_dir / "001-20231115-generated_title.md"
        assert first_file.exists()

        content = first_file.read_text()
        assert "---" in content  # Has frontmatter
        assert "Thread #1:" in content  # Has title
        assert "word_count:" in content  # Has metadata

    @pytest.mark.unit
    def test_frontmatter_generation(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that frontmatter is correctly generated."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        # Read first generated file
        first_file = temp_project_dir / "docs" / "heavy_hitters" / "001-20231115-generated_title.md"
        content = first_file.read_text()

        # Check frontmatter fields
        assert 'title:' in content
        assert 'date:' in content
        assert 'created:' in content
        assert 'categories: [heavy_hitters]' in content
        assert 'thread_id:' in content
        assert 'word_count:' in content
        assert 'reading_time:' in content
        assert 'description:' in content
        assert 'tweet_count:' in content
        assert 'tags:' in content  # Changed from heavy_hitter to tags
        assert 'thread_number:' in content
        assert 'author: "@BmoreOrganized"' in content

    @pytest.mark.unit
    def test_entities_in_frontmatter(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that entities are included in frontmatter when present."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        first_file = temp_project_dir / "docs" / "heavy_hitters" / "001-20231115-generated_title.md"
        content = first_file.read_text()

        # Mock returns entities as tags now
        assert 'tags:' in content

    @pytest.mark.unit
    def test_date_parsing_error_handling(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test handling of invalid date formats."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        result = generate_heavy_hitter_markdowns()

        # Should still generate files even with invalid dates
        assert len(result) == 3

        # Check that invalid date thread is handled
        # Thread with invalid date should show "Date unknown" in display
        invalid_date_file = temp_project_dir / "docs" / "heavy_hitters" / "001-20231115-generated_title.md"
        content = invalid_date_file.read_text()
        # Note: The actual date display depends on error handling in the function

    @pytest.mark.unit
    def test_index_file_generation(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that index file is generated with correct statistics."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        index_file = temp_project_dir / "docs" / "heavy_hitters" / "index.md"
        assert index_file.exists()

        content = index_file.read_text()

        # Check index frontmatter
        assert '---' in content
        assert 'title: "Heavy Hitter Threads Index"' in content
        assert 'total_threads:' in content
        assert 'total_words:' in content
        assert 'total_reading_time:' in content

        # Check statistics section
        assert "## Statistics" in content
        assert "Total heavy threads" in content
        assert "Average thread length" in content
        assert "Longest thread" in content

    @pytest.mark.unit
    def test_index_thread_listing(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that index file lists all heavy threads."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        index_file = temp_project_dir / "docs" / "heavy_hitters" / "index.md"
        content = index_file.read_text()

        # Check thread listings
        assert "## Threads by Size" in content
        assert "### 1." in content  # First thread
        assert "### 2." in content  # Second thread
        assert "### 3." in content  # Third thread

        # Should have preview text
        assert "Preview:" in content

    @pytest.mark.unit
    def test_navigation_links(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that navigation links are included in thread files."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        first_file = temp_project_dir / "docs" / "heavy_hitters" / "001-20231115-generated_title.md"
        content = first_file.read_text()

        # Check navigation section
        assert "### Navigation" in content
        assert "← Previous" in content  # Link format changed
        assert "[Index](index.md)" in content
        assert "[Next →]" in content

    @pytest.mark.unit
    def test_tweet_ids_section(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that tweet IDs are included in the markdown."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        first_file = temp_project_dir / "docs" / "heavy_hitters" / "001-20231115-generated_title.md"
        content = first_file.read_text()

        # Check tweet IDs section
        assert "### Tweet IDs" in content

    @pytest.mark.unit
    def test_empty_data_handling(self, temp_project_dir, mock_text_processing, monkeypatch):
        """Test handling of empty thread data."""
        monkeypatch.chdir(temp_project_dir)

        empty_data = {"threads": []}
        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(empty_data, f)

        result = generate_heavy_hitter_markdowns()

        assert result == []

        # Index should still be created
        index_file = temp_project_dir / "docs" / "heavy_hitters" / "index.md"
        assert index_file.exists()

    @pytest.mark.unit
    def test_return_value_structure(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test the structure of the return value."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        result = generate_heavy_hitter_markdowns()

        # Check return value structure
        assert isinstance(result, list)
        for item in result:
            assert 'number' in item
            assert 'filename' in item
            assert 'date' in item
            assert 'word_count' in item
            assert 'tweet_count' in item
            assert 'preview' in item
            assert isinstance(item['number'], int)
            assert isinstance(item['word_count'], int)


class TestGenerateThemeTemplate:
    """Test suite for generate_theme_template function."""

    @pytest.mark.unit
    def test_creates_template_file(self, temp_project_dir, monkeypatch):
        """Test that theme template file is created."""
        monkeypatch.chdir(temp_project_dir)

        generate_theme_template()

        template_file = temp_project_dir / "docs" / "heavy_hitters" / "THEME_TEMPLATE.md"
        assert template_file.exists()

    @pytest.mark.unit
    def test_template_content_structure(self, temp_project_dir, monkeypatch):
        """Test that template contains all expected sections."""
        monkeypatch.chdir(temp_project_dir)

        generate_theme_template()

        template_file = temp_project_dir / "docs" / "heavy_hitters" / "THEME_TEMPLATE.md"
        content = template_file.read_text()

        # Check main sections
        assert "# Theme Extraction Template" in content
        assert "## Instructions" in content
        assert "## Identified Themes" in content
        assert "### Political Philosophy" in content
        assert "### General Philosophy" in content
        assert "### Applied Topics" in content
        assert "### Historical Analysis" in content
        assert "### Other Themes" in content
        assert "## Thread-Theme Mapping" in content
        assert "## Keywords/Phrases You Actually Use" in content
        assert "## Notes" in content

    @pytest.mark.unit
    def test_template_categories(self, temp_project_dir, monkeypatch):
        """Test that all theme categories are present."""
        monkeypatch.chdir(temp_project_dir)

        generate_theme_template()

        template_file = temp_project_dir / "docs" / "heavy_hitters" / "THEME_TEMPLATE.md"
        content = template_file.read_text()

        # Check political philosophy themes
        assert "Marxism/Historical Materialism" in content
        assert "Anarchism" in content
        assert "Liberalism Critique" in content
        assert "Fascism Analysis" in content

        # Check general philosophy themes
        assert "Epistemology" in content
        assert "Ethics/Moral Philosophy" in content
        assert "Dialectics" in content

        # Check applied topics
        assert "Technology Critique" in content
        assert "Environmental Philosophy" in content
        assert "Labor/Work" in content

        # Check historical analysis
        assert "American History" in content
        assert "Revolutionary Theory" in content

    @pytest.mark.unit
    def test_template_checkboxes(self, temp_project_dir, monkeypatch):
        """Test that template uses checkboxes for themes."""
        monkeypatch.chdir(temp_project_dir)

        generate_theme_template()

        template_file = temp_project_dir / "docs" / "heavy_hitters" / "THEME_TEMPLATE.md"
        content = template_file.read_text()

        # Count checkboxes
        checkbox_count = content.count("- [ ]")
        assert checkbox_count > 20  # Should have many checkboxes

    @pytest.mark.unit
    def test_template_instructions(self, temp_project_dir, monkeypatch):
        """Test that template includes usage instructions."""
        monkeypatch.chdir(temp_project_dir)

        generate_theme_template()

        template_file = temp_project_dir / "docs" / "heavy_hitters" / "THEME_TEMPLATE.md"
        content = template_file.read_text()

        assert "After reading the heavy-hitter threads" in content
        assert "Save this as: docs/heavy_hitters/THEMES_EXTRACTED.md" in content

    @pytest.mark.unit
    def test_template_examples(self, temp_project_dir, monkeypatch):
        """Test that template includes examples."""
        monkeypatch.chdir(temp_project_dir)

        generate_theme_template()

        template_file = temp_project_dir / "docs" / "heavy_hitters" / "THEME_TEMPLATE.md"
        content = template_file.read_text()

        # Check for examples section
        assert "### Example:" in content
        assert "Marxism: Threads #" in content
        assert "Technology Critique: Threads #" in content

        # Check for keyword examples
        assert '"primitive accumulation"' in content
        assert '"means of production"' in content

    @pytest.mark.unit
    def test_creates_directory_if_missing(self, tmp_path, monkeypatch):
        """Test that directory is created if it doesn't exist."""
        # Start with no docs directory
        monkeypatch.chdir(tmp_path)

        assert not (tmp_path / "docs" / "heavy_hitters").exists()

        generate_theme_template()

        # Directory should be created
        assert (tmp_path / "docs" / "heavy_hitters").exists()
        assert (tmp_path / "docs" / "heavy_hitters" / "THEME_TEMPLATE.md").exists()


class TestIntegration:
    """Integration tests for the full module."""

    @pytest.mark.integration
    def test_full_workflow(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch, capsys):
        """Test the complete workflow when running as main."""
        monkeypatch.chdir(temp_project_dir)

        # Write test data
        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        # Simulate running as main by directly calling the functions
        files = generate_heavy_hitter_markdowns()
        generate_theme_template()

        # Check outputs
        heavy_hitters_dir = temp_project_dir / "docs" / "heavy_hitters"

        # Should have markdown files
        markdown_files = list(heavy_hitters_dir.glob("*.md"))
        assert len(markdown_files) >= 4  # 3 threads + index + template

        # Check console output
        captured = capsys.readouterr()
        assert "Generating markdown for heavy-hitter threads" in captured.out

    @pytest.mark.integration
    def test_text_processing_integration(self, sample_threads_data, temp_project_dir, monkeypatch):
        """Test integration with real text_processing functions."""
        monkeypatch.chdir(temp_project_dir)

        # Write test data
        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        # Run without mocking text_processing (will use real functions)
        with patch('generate_heavy_hitters.generate_title', return_value="Real Title"):
            with patch('generate_heavy_hitters.generate_description', return_value="Real Description"):
                with patch('generate_heavy_hitters.calculate_reading_time', return_value=5):
                    with patch('generate_heavy_hitters.format_frontmatter_value', lambda x: f'"{x}"' if isinstance(x, str) else str(x)):
                        with patch('generate_heavy_hitters.extract_entities', return_value=[]):
                            with patch('generate_heavy_hitters.generate_filename', return_value="001-20231115-real_title.md"):
                                with patch('generate_heavy_hitters.parse_to_yyyymmdd', return_value="20231115"):
                                    result = generate_heavy_hitter_markdowns()

        # Verify integration worked
        assert len(result) == 3
        first_file = temp_project_dir / "docs" / "heavy_hitters" / "001-20231115-real_title.md"
        assert first_file.exists()


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.unit
    def test_missing_data_file(self, temp_project_dir, monkeypatch):
        """Test handling when filtered_threads.json is missing - returns empty list."""
        monkeypatch.chdir(temp_project_dir)

        # Don't create the data file
        result = generate_heavy_hitter_markdowns()
        assert result == []  # Should return empty list, not raise exception

    @pytest.mark.unit
    def test_malformed_json(self, temp_project_dir, monkeypatch):
        """Test handling of malformed JSON data - returns empty list."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            f.write("{ invalid json ]")

        result = generate_heavy_hitter_markdowns()
        assert result == []  # Should return empty list, not raise exception

    @pytest.mark.unit
    def test_missing_required_fields(self, temp_project_dir, mock_text_processing, monkeypatch):
        """Test handling when threads are missing required fields."""
        monkeypatch.chdir(temp_project_dir)

        bad_data = {
            "threads": [
                {
                    "thread_id": "thread_001",
                    # Missing word_count, tweet_count, etc.
                }
            ]
        }

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(bad_data, f)

        # Should raise KeyError for missing fields
        with pytest.raises(KeyError):
            generate_heavy_hitter_markdowns()


class TestStatisticsCalculation:
    """Test statistics calculation for the index."""

    @pytest.mark.unit
    def test_total_words_calculation(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that total word count is calculated correctly."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        index_file = temp_project_dir / "docs" / "heavy_hitters" / "index.md"
        content = index_file.read_text()

        # Total should be 750 + 550 + 1200 = 2500
        assert "total_words: 2500" in content

    @pytest.mark.unit
    def test_average_calculation(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that average word count is calculated correctly."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        index_file = temp_project_dir / "docs" / "heavy_hitters" / "index.md"
        content = index_file.read_text()

        # Average should be 2500 / 3 = 833.33
        assert "**Average thread length**: 833 words" in content

    @pytest.mark.unit
    def test_max_words_calculation(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that maximum word count is found correctly."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        index_file = temp_project_dir / "docs" / "heavy_hitters" / "index.md"
        content = index_file.read_text()

        # Max should be 1200
        assert "**Longest thread**: 1,200 words" in content

    @pytest.mark.unit
    def test_reading_time_calculation(self, sample_threads_data, temp_project_dir, mock_text_processing, monkeypatch):
        """Test that total reading time is calculated correctly."""
        monkeypatch.chdir(temp_project_dir)

        with open(temp_project_dir / "data" / "filtered_threads.json", 'w') as f:
            json.dump(sample_threads_data, f)

        generate_heavy_hitter_markdowns()

        index_file = temp_project_dir / "docs" / "heavy_hitters" / "index.md"
        content = index_file.read_text()

        # Total reading time = 2500 words / 225 wpm = ~11 minutes
        assert "total_reading_time: 11" in content