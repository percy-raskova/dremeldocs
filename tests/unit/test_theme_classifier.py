#!/usr/bin/env python3
"""
Unit tests for theme_classifier.py following Test-Driven Development principles.
Tests the ThemeClassifier class and all its methods for theme-based classification.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from theme_classifier import ThemeClassifier


class TestThemeClassifierInit:
    """Test ThemeClassifier initialization."""

    def test_init_with_default_themes_file(self):
        """Test initialization with default themes file path."""
        classifier = ThemeClassifier()

        assert classifier.themes_file == Path("docs/heavy_hitters/THEMES_EXTRACTED.md")
        assert classifier.themes == {}
        assert classifier.keywords == {}
        assert classifier.thread_theme_map == {}

    def test_init_with_custom_themes_file(self):
        """Test initialization with custom themes file path."""
        custom_path = "custom/themes.md"
        classifier = ThemeClassifier(themes_file=custom_path)

        assert classifier.themes_file == Path(custom_path)
        assert isinstance(classifier.themes, dict)
        assert isinstance(classifier.keywords, dict)
        assert isinstance(classifier.thread_theme_map, dict)

    def test_init_data_structures(self):
        """Test that all data structures are properly initialized."""
        classifier = ThemeClassifier()

        # Verify types
        assert isinstance(classifier.themes_file, Path)
        assert isinstance(classifier.themes, dict)
        assert isinstance(classifier.keywords, dict)
        assert isinstance(classifier.thread_theme_map, dict)

        # Verify empty at start
        assert len(classifier.themes) == 0
        assert len(classifier.keywords) == 0
        assert len(classifier.thread_theme_map) == 0


class TestLoadHumanThemes:
    """Test loading human-extracted themes from file."""

    def test_load_missing_themes_file(self, capsys):
        """Test loading when themes file doesn't exist."""
        classifier = ThemeClassifier(themes_file="nonexistent.md")

        result = classifier.load_human_themes()

        assert result is False
        captured = capsys.readouterr()
        assert "❌ Theme file not found" in captured.out
        assert "THEMES_EXTRACTED.md" in captured.out

    def test_load_valid_themes_file(self, tmp_path):
        """Test loading valid themes file."""
        themes_file = tmp_path / "themes.md"
        themes_content = """
        # Themes Extracted

        ## Identified Themes
        [x] Marxism: 10
        [x] Dialectics: 5
        [ ] Unchecked: 0

        ## Keywords/Phrases You Actually Use
        - "class struggle"
        - "dialectical materialism"

        ## Thread-Theme Mapping
        - Marxism: Threads #3, #7, #15
        - Dialectics: Threads #1, #2
        """
        themes_file.write_text(themes_content)

        classifier = ThemeClassifier(themes_file=str(themes_file))
        result = classifier.load_human_themes()

        assert result is True
        assert "Marxism" in classifier.themes
        assert classifier.themes["Marxism"] == 10
        assert "Dialectics" in classifier.themes
        assert classifier.themes["Dialectics"] == 5

    def test_load_empty_themes_file(self, tmp_path):
        """Test loading empty themes file."""
        themes_file = tmp_path / "empty.md"
        themes_file.write_text("")

        classifier = ThemeClassifier(themes_file=str(themes_file))
        result = classifier.load_human_themes()

        assert result is True  # Should load but find no themes
        assert len(classifier.themes) == 0
        assert len(classifier.keywords) == 0

    @patch("builtins.open", side_effect=PermissionError("Access denied"))
    def test_load_permission_error(self, mock_file, tmp_path):
        """Test handling permission error when loading themes file."""
        themes_file = tmp_path / "protected.md"
        themes_file.write_text("content")

        classifier = ThemeClassifier(themes_file=str(themes_file))

        with pytest.raises(PermissionError):
            classifier.load_human_themes()


class TestParseThemeSections:
    """Test parsing theme sections from content."""

    def test_parse_basic_themes(self):
        """Test parsing basic theme patterns."""
        content = """
        [x] Political Economy: 15
        [x] Cultural Criticism: 8
        [x] Imperialism: 12
        [ ] Not checked: 0
        """

        classifier = ThemeClassifier()
        classifier._parse_theme_sections(content)

        assert "Political Economy" in classifier.themes
        assert classifier.themes["Political Economy"] == 15
        assert "Cultural Criticism" in classifier.themes
        assert classifier.themes["Cultural Criticism"] == 8
        assert "Not checked" not in classifier.themes

    def test_parse_themes_without_weights(self):
        """Test parsing themes without explicit weights - the regex requires a colon."""
        # Test with proper format but no weights
        content = """
        [x] Philosophy:
        [x] Politics:
        [x] Science:
        """

        classifier = ThemeClassifier()
        classifier._parse_theme_sections(content)

        # Since no number follows the colon, these get default weight of 1
        assert "Philosophy" in classifier.themes
        assert classifier.themes["Philosophy"] == 1
        assert "Politics" in classifier.themes
        assert classifier.themes["Politics"] == 1
        assert "Science" in classifier.themes
        assert classifier.themes["Science"] == 1

    def test_parse_themes_with_special_characters(self):
        """Test parsing themes with special characters."""
        content = """
        [x] Marxism/Leninism: 10
        [x] Post-modernism: 5
        [x] COVID-19 Politics: 8
        """

        classifier = ThemeClassifier()
        classifier._parse_theme_sections(content)

        assert "Marxism/Leninism" in classifier.themes
        assert "Post-modernism" in classifier.themes
        assert "COVID-19 Politics" in classifier.themes

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        classifier = ThemeClassifier()
        classifier._parse_theme_sections("")

        assert len(classifier.themes) == 0


class TestParseKeywords:
    """Test parsing keywords from content."""

    def test_parse_basic_keywords(self):
        """Test parsing basic keyword list."""
        content = """
        ## Keywords/Phrases You Actually Use
        - "class struggle"
        - "dialectical materialism"
        - "means of production"

        ## Another Section
        """

        classifier = ThemeClassifier()
        classifier._parse_keywords(content)

        assert "class struggle" in classifier.keywords.values()
        assert "dialectical materialism" in classifier.keywords.values()
        assert "means of production" in classifier.keywords.values()

    def test_parse_keywords_with_bullets(self):
        """Test parsing keywords with different bullet styles."""
        content = """
        Keywords/Phrases You Actually Use

        * "imperialism"
        - "colonialism"
        • "capitalism"
        """

        classifier = ThemeClassifier()
        classifier._parse_keywords(content)

        assert "imperialism" in classifier.keywords.values()
        assert "colonialism" in classifier.keywords.values()

    def test_parse_keywords_case_insensitive(self):
        """Test that keywords are stored lowercase for matching."""
        content = """
        Keywords/Phrases You Actually Use
        - "Class Struggle"
        - "REVOLUTION"
        """

        classifier = ThemeClassifier()
        classifier._parse_keywords(content)

        assert "class struggle" in classifier.keywords
        assert "revolution" in classifier.keywords

    def test_parse_no_keywords_section(self):
        """Test when no keywords section exists."""
        content = """
        ## Some Other Section
        Content here
        """

        classifier = ThemeClassifier()
        classifier._parse_keywords(content)

        assert len(classifier.keywords) == 0


class TestParseThreadMappings:
    """Test parsing thread-theme mappings."""

    def test_parse_basic_mappings(self):
        """Test parsing basic thread mappings."""
        content = """
        ## Thread-Theme Mapping

        Marxism: Threads #3, #7, #15
        Dialectics: Thread #1
        Imperialism: Threads #10, #20, #30
        """

        classifier = ThemeClassifier()
        classifier._parse_thread_mappings(content)

        assert "Marxism" in classifier.thread_theme_map
        assert classifier.thread_theme_map["Marxism"] == [3, 7, 15]
        assert "Dialectics" in classifier.thread_theme_map
        assert classifier.thread_theme_map["Dialectics"] == [1]

    def test_parse_mappings_various_formats(self):
        """Test parsing mappings with various formats."""
        content = """
        Thread-Theme Mapping

        Philosophy: Threads #1, #2, #3
        Politics: Thread #5
        Science: Threads #8, #9
        """

        classifier = ThemeClassifier()
        classifier._parse_thread_mappings(content)

        assert classifier.thread_theme_map["Philosophy"] == [1, 2, 3]
        assert classifier.thread_theme_map["Politics"] == [5]
        assert classifier.thread_theme_map["Science"] == [8, 9]

    def test_parse_mappings_with_ranges(self):
        """Test parsing when thread numbers are listed as ranges."""
        content = """
        Thread-Theme Mapping
        - Theme1: Threads #1, #2, #3, #4, #5
        """

        classifier = ThemeClassifier()
        classifier._parse_thread_mappings(content)

        assert classifier.thread_theme_map["Theme1"] == [1, 2, 3, 4, 5]

    def test_parse_no_mappings_section(self):
        """Test when no mappings section exists."""
        content = """
        ## Different Section
        No mappings here
        """

        classifier = ThemeClassifier()
        classifier._parse_thread_mappings(content)

        assert len(classifier.thread_theme_map) == 0


class TestClassifyThread:
    """Test thread classification logic."""

    def test_classify_thread_with_keywords(self):
        """Test classifying thread containing keywords."""
        classifier = ThemeClassifier()
        classifier.keywords = {
            "class struggle": "class struggle",
            "revolution": "revolution",
        }
        classifier.themes = {"Marxism": 10}

        thread = {
            "smushed_text": "This is about class struggle and revolution in society",
            "thread_id": "test_001",
            "word_count": 10,
        }

        themes, confidence = classifier.classify_thread(thread)

        assert confidence > 0
        assert isinstance(themes, list)

    def test_classify_thread_no_matches(self):
        """Test classifying thread with no keyword matches."""
        classifier = ThemeClassifier()
        classifier.keywords = {"specific": "specific"}
        classifier.themes = {"Unrelated": 1}

        thread = {
            "smushed_text": "Random text about nothing in particular",
            "thread_id": "test_002",
            "word_count": 7,
        }

        themes, confidence = classifier.classify_thread(thread)

        assert len(themes) == 0 or confidence < 0.3

    def test_classify_thread_case_insensitive(self):
        """Test that classification is case insensitive."""
        classifier = ThemeClassifier()
        classifier.keywords = {"marxism": "marxism"}

        thread = {
            "smushed_text": "MARXISM and Marxism and marxism",
            "thread_id": "test_003",
            "word_count": 5,
        }

        themes, confidence = classifier.classify_thread(thread)

        assert confidence > 0

    def test_classify_empty_thread(self):
        """Test classifying empty thread text."""
        classifier = ThemeClassifier()
        classifier.keywords = {"keyword": "keyword"}

        thread = {"smushed_text": "", "thread_id": "test_004", "word_count": 0}

        themes, confidence = classifier.classify_thread(thread)

        assert len(themes) == 0
        assert confidence == 0


class TestCalculateThemeScore:
    """Test theme score calculation."""

    def test_calculate_basic_score(self):
        """Test basic theme score calculation."""
        classifier = ThemeClassifier()
        classifier.keywords = {"revolution": "revolution", "class": "class"}

        text = "revolution and class struggle"
        score = classifier._calculate_theme_score(text, "Marxism")

        assert score > 0
        assert score <= 1.0

    def test_calculate_score_no_matches(self):
        """Test score when no keywords match."""
        classifier = ThemeClassifier()
        classifier.keywords = {"unrelated": "unrelated"}

        text = "completely different content"
        score = classifier._calculate_theme_score(text, "Theme")

        assert score == 0.0

    def test_calculate_score_max_cap(self):
        """Test that score is capped at 1.0."""
        classifier = ThemeClassifier()
        classifier.keywords = {f"word{i}": f"word{i}" for i in range(20)}

        text = " ".join([f"word{i}" for i in range(20)])
        score = classifier._calculate_theme_score(text, "Theme")

        assert score == 1.0

    def test_calculate_score_partial_matches(self):
        """Test score with partial keyword matches."""
        classifier = ThemeClassifier()
        classifier.keywords = {
            "dialectical": "dialectical",
            "materialism": "materialism",
            "historical": "historical",
        }

        text = "dialectical approach to understanding"
        score = classifier._calculate_theme_score(text, "Philosophy")

        assert 0 < score < 0.5


class TestCategorizeThread:
    """Test thread categorization logic."""

    def test_categorize_philosophical(self):
        """Test categorizing philosophical threads."""
        classifier = ThemeClassifier()
        themes = ["epistemology", "dialectics"]

        category = classifier._categorize_thread(themes)

        assert category == "philosophical"

    def test_categorize_political(self):
        """Test categorizing political threads."""
        classifier = ThemeClassifier()
        themes = ["marxism", "imperialism"]

        category = classifier._categorize_thread(themes)

        assert category == "political"

    def test_categorize_both(self):
        """Test categorizing threads with both types."""
        classifier = ThemeClassifier()
        themes = ["dialectics", "marxism", "ethics", "fascism"]

        category = classifier._categorize_thread(themes)

        assert category == "both"

    def test_categorize_uncertain(self):
        """Test categorizing uncertain threads."""
        classifier = ThemeClassifier()
        themes = ["unknown_theme", "random_topic"]

        category = classifier._categorize_thread(themes)

        assert category == "uncertain"

    def test_categorize_empty(self):
        """Test categorizing thread with no themes."""
        classifier = ThemeClassifier()
        themes = []

        category = classifier._categorize_thread(themes)

        assert category == "other"

    def test_categorize_case_insensitive(self):
        """Test that categorization is case insensitive."""
        classifier = ThemeClassifier()
        themes = ["MARXISM", "Anarchism", "FASCISM"]

        category = classifier._categorize_thread(themes)

        assert category == "political"


class TestProcessAllThreads:
    """Test processing all threads functionality."""

    def test_process_missing_data_file(self, tmp_path, capsys):
        """Test processing when data file doesn't exist."""
        classifier = ThemeClassifier()

        with patch("pathlib.Path.exists", return_value=False):
            result = classifier.process_all_threads()

        assert result is None
        captured = capsys.readouterr()
        assert "Required data file not found" in captured.out

    def test_process_invalid_json(self, tmp_path, capsys):
        """Test processing with invalid JSON file."""
        data_file = tmp_path / "data" / "filtered_threads.json"
        data_file.parent.mkdir(parents=True)
        data_file.write_text("{invalid json}")

        classifier = ThemeClassifier()

        with patch("pathlib.Path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data="{invalid json}")
        ):
            result = classifier.process_all_threads()

        assert result is None
        captured = capsys.readouterr()
        assert "Invalid JSON" in captured.out

    def test_process_valid_threads(self, tmp_path):
        """Test processing valid thread data."""
        # Create test data
        test_data = {
            "threads": [
                {
                    "thread_id": "001",
                    "smushed_text": "Discussion about marxism and class struggle",
                    "word_count": 7,
                    "tweet_count": 2,
                    "first_tweet_date": "2024-01-01",
                    "tweets": [],
                },
                {
                    "thread_id": "002",
                    "smushed_text": "Thoughts on epistemology and knowledge",
                    "word_count": 5,
                    "tweet_count": 1,
                    "first_tweet_date": "2024-01-02",
                    "tweets": [],
                },
            ]
        }

        data_file = tmp_path / "data" / "filtered_threads.json"
        data_file.parent.mkdir(parents=True)
        data_file.write_text(json.dumps(test_data))

        output_file = tmp_path / "data" / "classified_threads.json"

        classifier = ThemeClassifier()
        classifier.keywords = {"marxism": "marxism", "epistemology": "epistemology"}
        classifier.themes = {"Marxism": 10, "Philosophy": 5}

        with patch(
            "pathlib.Path",
            side_effect=lambda x: data_file if "filtered" in str(x) else output_file,
        ), patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            with patch("json.dump"):
                result = classifier.process_all_threads()

        assert result is not None
        assert "metadata" in result
        assert "threads_by_category" in result

    def test_process_progress_output(self, tmp_path, capsys):
        """Test that progress is reported during processing."""
        # Create test data with 150 threads to trigger progress output
        threads = [
            {
                "thread_id": f"thread_{i:04d}",
                "smushed_text": f"Thread content {i}",
                "word_count": 10,
                "tweet_count": 1,
                "first_tweet_date": "2024-01-01",
                "tweets": [],
            }
            for i in range(150)
        ]

        test_data = {"threads": threads}

        classifier = ThemeClassifier()

        with patch("pathlib.Path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=json.dumps(test_data))
        ), patch("json.dump"):
            classifier.process_all_threads()

        captured = capsys.readouterr()
        assert "Processed 100/" in captured.out

    def test_process_categorization_counts(self, tmp_path):
        """Test that threads are properly categorized and counted."""
        test_data = {
            "threads": [
                {
                    "thread_id": "001",
                    "smushed_text": "philosophy",
                    "word_count": 1,
                    "tweet_count": 1,
                    "first_tweet_date": "2024-01-01",
                    "tweets": [],
                },
                {
                    "thread_id": "002",
                    "smushed_text": "politics",
                    "word_count": 1,
                    "tweet_count": 1,
                    "first_tweet_date": "2024-01-02",
                    "tweets": [],
                },
                {
                    "thread_id": "003",
                    "smushed_text": "random",
                    "word_count": 1,
                    "tweet_count": 1,
                    "first_tweet_date": "2024-01-03",
                    "tweets": [],
                },
            ]
        }

        classifier = ThemeClassifier()

        with patch("pathlib.Path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=json.dumps(test_data))
        ), patch("json.dump") as mock_dump:
            result = classifier.process_all_threads()

        assert result is not None
        assert len(result["threads_by_category"]) == 5  # All categories present


class TestGenerateFinalMarkdown:
    """Test markdown generation functionality."""

    def test_generate_markdown_basic(self, tmp_path):
        """Test basic markdown generation."""
        # Setup test data
        test_threads = {
            "threads_by_category": {
                "philosophical": [
                    {
                        "thread_id": "001",
                        "smushed_text": "Philosophical discussion about existence",
                        "themes": ["epistemology"],
                        "confidence": 0.8,
                        "word_count": 5,
                        "tweet_count": 1,
                        "first_tweet_date": "2024-01-01T12:00:00Z",
                    }
                ]
            }
        }

        classifier = ThemeClassifier()

        # Create a mock that returns the JSON data on first call, then acts as file writer
        read_count = [0]

        def open_side_effect(*args, **kwargs):
            read_count[0] += 1
            if read_count[0] == 1:
                # First call is reading the JSON
                return mock_open(read_data=json.dumps(test_threads))(*args, **kwargs)
            else:
                # Subsequent calls are writing markdown
                return mock_open()(*args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect) as mock_file, patch(
            "pathlib.Path.mkdir"
        ):
            classifier.generate_final_markdown("philosophical", limit=1)

            # Verify files were opened (1 read + at least 1 write)
            assert mock_file.call_count >= 2

    def test_generate_markdown_with_limit(self, tmp_path):
        """Test markdown generation with limit."""
        test_threads = {
            "threads_by_category": {
                "political": [
                    {
                        "thread_id": f"00{i}",
                        "smushed_text": f"Thread {i}",
                        "word_count": 10,
                        "tweet_count": 1,
                        "first_tweet_date": "2024-01-01T00:00:00Z",
                    }
                    for i in range(10)
                ]
            }
        }

        classifier = ThemeClassifier()
        file_count = [0]

        def count_writes(*args, **kwargs):
            file_count[0] += 1
            if file_count[0] == 1:
                # First call is reading
                return mock_open(read_data=json.dumps(test_threads))(*args, **kwargs)
            else:
                # Subsequent calls are writing
                return mock_open()(*args, **kwargs)

        with patch("builtins.open", side_effect=count_writes), patch(
            "pathlib.Path.mkdir"
        ):
            classifier.generate_final_markdown("political", limit=5)

            # Should have 1 read + 5 writes = 6 total
            assert file_count[0] == 6

    def test_generate_markdown_frontmatter(self, tmp_path):
        """Test that frontmatter is correctly formatted."""
        test_thread = {
            "thread_id": "001",
            "smushed_text": "Test content for frontmatter generation",
            "themes": ["theme1", "theme2"],
            "confidence": 0.75,
            "word_count": 7,
            "tweet_count": 2,
            "first_tweet_date": "2024-01-15T10:30:00Z",
        }

        test_data = {"threads_by_category": {"both": [test_thread]}}

        classifier = ThemeClassifier()
        written_content = []
        call_count = [0]

        def mock_open_handler(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call is reading
                return mock_open(read_data=json.dumps(test_data))(*args, **kwargs)
            else:
                # Second call is writing
                mock_file = MagicMock()
                mock_file.write = lambda content: written_content.append(content)
                mock_file.__enter__ = lambda self: mock_file
                mock_file.__exit__ = lambda self, *args: None
                return mock_file

        with patch("builtins.open", side_effect=mock_open_handler), patch(
            "pathlib.Path.mkdir"
        ):
            classifier.generate_final_markdown("both", limit=1)

        # Verify frontmatter structure
        full_content = "".join(written_content)
        assert "---" in full_content
        assert "title:" in full_content
        assert "date:" in full_content
        assert "categories:" in full_content
        assert "word_count: 7" in full_content

    def test_generate_markdown_invalid_date(self, tmp_path, capsys):
        """Test handling invalid date formats."""
        test_thread = {
            "thread_id": "001",
            "smushed_text": "Content",
            "word_count": 1,
            "tweet_count": 1,
            "first_tweet_date": "invalid-date",
        }

        test_data = {"threads_by_category": {"other": [test_thread]}}

        classifier = ThemeClassifier()

        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))), patch(
            "pathlib.Path.mkdir"
        ):
            classifier.generate_final_markdown("other", limit=1)

        captured = capsys.readouterr()
        assert "Warning: Could not parse date" in captured.out

    def test_generate_markdown_empty_category(self, tmp_path, capsys):
        """Test generating markdown for empty category."""
        test_data = {"threads_by_category": {"philosophical": []}}

        classifier = ThemeClassifier()

        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))), patch(
            "pathlib.Path.mkdir"
        ):
            classifier.generate_final_markdown("philosophical")

        captured = capsys.readouterr()
        assert "Generated 0 markdown files" in captured.out


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_full_classification_workflow(self, tmp_path):
        """Test complete workflow from loading themes to generating markdown."""
        # Create themes file
        themes_file = tmp_path / "themes.md"
        themes_content = """
        [x] Marxism: 10
        [x] Philosophy: 5

        Keywords/Phrases You Actually Use
        - "class struggle"
        - "dialectics"

        Thread-Theme Mapping
        - Marxism: Threads #1, #2
        """
        themes_file.write_text(themes_content)

        # Create data file
        data_file = tmp_path / "data" / "filtered_threads.json"
        data_file.parent.mkdir(parents=True)
        test_data = {
            "threads": [
                {
                    "thread_id": "001",
                    "smushed_text": "Discussion about class struggle and dialectics",
                    "word_count": 7,
                    "tweet_count": 2,
                    "first_tweet_date": "2024-01-01T00:00:00Z",
                    "tweets": [],
                }
            ]
        }
        data_file.write_text(json.dumps(test_data))

        # Run workflow
        classifier = ThemeClassifier(themes_file=str(themes_file))

        # Load themes
        assert classifier.load_human_themes() is True
        assert len(classifier.themes) > 0
        assert len(classifier.keywords) > 0

        # Process threads
        output_file = tmp_path / "data" / "classified_threads.json"

        # Mock the file operations more precisely
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))), patch(
            "pathlib.Path.exists", return_value=True
        ), patch("json.dump"):
            result = classifier.process_all_threads()

        assert result is not None
        assert result["metadata"]["total_threads"] == 1

    def test_error_recovery_workflow(self, tmp_path, capsys):
        """Test that workflow handles errors gracefully."""
        classifier = ThemeClassifier(themes_file="nonexistent.md")

        # Try to load missing themes
        assert classifier.load_human_themes() is False

        # Try to process without themes
        with patch("pathlib.Path.exists", return_value=False):
            result = classifier.process_all_threads()

        assert result is None

        captured = capsys.readouterr()
        assert "Theme file not found" in captured.out
        assert "Required data file not found" in captured.out


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_in_content(self):
        """Test handling Unicode in thread content."""
        classifier = ThemeClassifier()
        classifier.keywords = {"émoji": "émoji"}

        thread = {
            "smushed_text": "Text with émoji 🎉 and special chars",
            "word_count": 7,
            "thread_id": "unicode_test",
        }

        themes, confidence = classifier.classify_thread(thread)
        assert confidence > 0

    def test_very_long_thread(self):
        """Test handling very long thread content."""
        classifier = ThemeClassifier()
        classifier.keywords = {"keyword": "keyword"}

        long_text = "keyword " * 10000  # Very long text
        thread = {
            "smushed_text": long_text,
            "word_count": 10000,
            "thread_id": "long_test",
        }

        themes, confidence = classifier.classify_thread(thread)
        assert confidence <= 1.0  # Should still be capped

    def test_malformed_theme_data(self):
        """Test handling malformed theme data."""
        content = """
        [x] Theme with: colon: 10
        [x] Theme with [brackets]: 5
        [x] : 3
        """

        classifier = ThemeClassifier()
        classifier._parse_theme_sections(content)

        # Should handle gracefully without crashing
        assert isinstance(classifier.themes, dict)

    def test_circular_theme_references(self):
        """Test handling circular references in theme mappings."""
        classifier = ThemeClassifier()
        classifier.thread_theme_map = {
            "Theme1": [1, 2, 3],
            "Theme2": [2, 3, 4],
            "Theme3": [1, 4],
        }

        # Should not cause infinite loops
        thread = {"thread_id": "002", "smushed_text": "test", "word_count": 1}
        themes, confidence = classifier.classify_thread(thread)

        assert isinstance(themes, list)

    def test_empty_markdown_generation(self, tmp_path):
        """Test generating markdown with minimal data."""
        test_data = {
            "threads_by_category": {
                "other": [
                    {
                        "thread_id": "",
                        "smushed_text": "",
                        "word_count": 0,
                        "tweet_count": 0,
                        "first_tweet_date": "",
                    }
                ]
            }
        }

        classifier = ThemeClassifier()

        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))), patch(
            "pathlib.Path.mkdir"
        ):
            # Should not crash
            classifier.generate_final_markdown("other", limit=1)


class TestPerformance:
    """Test performance with large datasets."""

    def test_large_thread_count(self):
        """Test processing large number of threads."""
        classifier = ThemeClassifier()
        classifier.keywords = {"test": "test"}

        # Create 1000 threads
        threads = [
            {
                "thread_id": f"thread_{i:04d}",
                "smushed_text": f"Content {i} with test keyword",
                "word_count": 5,
                "tweet_count": 1,
                "first_tweet_date": "2024-01-01",
                "tweets": [],
            }
            for i in range(1000)
        ]

        test_data = {"threads": threads}

        with patch("pathlib.Path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=json.dumps(test_data))
        ), patch("json.dump"):
            result = classifier.process_all_threads()

        assert result is not None
        assert result["metadata"]["total_threads"] == 1000

    def test_many_themes_and_keywords(self):
        """Test with many themes and keywords."""
        classifier = ThemeClassifier()

        # Create 100 themes and 500 keywords
        classifier.themes = {f"Theme_{i}": i for i in range(100)}
        classifier.keywords = {f"keyword_{i}": f"keyword_{i}" for i in range(500)}

        thread = {
            "smushed_text": " ".join([f"keyword_{i}" for i in range(50)]),
            "word_count": 50,
            "thread_id": "test",
        }

        themes, confidence = classifier.classify_thread(thread)

        assert confidence <= 1.0
        assert isinstance(themes, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
