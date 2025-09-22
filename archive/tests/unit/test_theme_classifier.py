"""
Unit tests for theme_classifier.py
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from scripts.theme_classifier import ThemeClassifier


class TestThemeClassifier:
    """Test suite for ThemeClassifier class."""

    @pytest.fixture
    def classifier(self, tmp_path):
        """Create ThemeClassifier instance."""
        themes_file = tmp_path / "THEMES_EXTRACTED.md"
        themes_file.write_text("# Test Themes")
        return ThemeClassifier(str(themes_file))

    @pytest.fixture
    def sample_theme_content(self):
        """Sample THEMES_EXTRACTED.md content."""
        return """# Theme Extraction Results

## Identified Themes

### Political Philosophy
[x] Marxism: 10
[x] Anarchism: 5
[x] Liberalism Critique: 3

### General Philosophy
[x] Epistemology: 7
[x] Ethics: 4
[x] Dialectics: 8

## Keywords/Phrases You Actually Use
- "class struggle"
- "means of production"
- "epistemological framework"
- "moral imperative"

## Thread-Theme Mapping
- Marxism: Threads #3, #7, #15
- Epistemology: Threads #1, #4, #9
"""

    def test_initialization(self, classifier, tmp_path):
        """Test classifier initialization."""
        assert classifier.themes_file == tmp_path / "THEMES_EXTRACTED.md"
        assert isinstance(classifier.themes, dict)
        assert isinstance(classifier.keywords, dict)
        assert isinstance(classifier.thread_theme_map, dict)

    def test_load_human_themes_success(self, classifier, sample_theme_content):
        """Test loading themes from file."""
        with patch('builtins.open', mock_open(read_data=sample_theme_content)):
            result = classifier.load_human_themes()

            assert result is True
            assert len(classifier.themes) > 0

    def test_load_human_themes_missing_file(self, tmp_path):
        """Test handling of missing themes file."""
        classifier = ThemeClassifier(str(tmp_path / "nonexistent.md"))

        result = classifier.load_human_themes()

        assert result is False

    def test_parse_theme_sections(self, classifier, sample_theme_content):
        """Test parsing theme sections from markdown."""
        classifier._parse_theme_sections(sample_theme_content)

        assert "Marxism" in classifier.themes
        assert classifier.themes["Marxism"] == 10
        assert "Epistemology" in classifier.themes
        assert classifier.themes["Epistemology"] == 7

    def test_parse_keywords(self, classifier, sample_theme_content):
        """Test parsing keywords from content."""
        classifier._parse_keywords(sample_theme_content)

        assert "class struggle" in classifier.keywords
        assert "means of production" in classifier.keywords
        assert "epistemological framework" in classifier.keywords

    def test_parse_thread_mappings(self, classifier, sample_theme_content):
        """Test parsing thread-theme mappings."""
        classifier._parse_thread_mappings(sample_theme_content)

        assert "Marxism" in classifier.thread_theme_map
        assert 3 in classifier.thread_theme_map["Marxism"]
        assert 7 in classifier.thread_theme_map["Marxism"]
        assert 15 in classifier.thread_theme_map["Marxism"]

    def test_classify_thread_with_themes(self, classifier):
        """Test classifying a thread with matching themes."""
        classifier.themes = {"Marxism": 10, "Epistemology": 5}
        classifier.keywords = {
            "class": "class",
            "capital": "capital",
            "knowledge": "knowledge"
        }

        thread = {
            "smushed_text": "This thread discusses class struggle and capital accumulation in modern society, examining knowledge production."
        }

        themes, confidence = classifier.classify_thread(thread)

        assert len(themes) > 0
        assert confidence > 0.0
        assert confidence <= 1.0

    def test_classify_thread_no_themes(self, classifier):
        """Test classifying a thread with no matching themes."""
        classifier.themes = {"Marxism": 10}
        classifier.keywords = {"revolution": "revolution"}

        thread = {
            "smushed_text": "This is about cooking and recipes."
        }

        themes, confidence = classifier.classify_thread(thread)

        assert len(themes) == 0 or confidence < 0.3

    def test_calculate_theme_score(self, classifier):
        """Test theme score calculation."""
        text = "class struggle means of production capital labor"
        classifier.keywords = {
            "Marxism": ["class", "production", "capital", "labor"]
        }

        score = classifier._calculate_theme_score(text, "Marxism")

        assert score > 0
        assert score <= 1.0

    def test_categorize_thread_philosophical(self, classifier):
        """Test categorization as philosophical."""
        themes = ["epistemology", "ontology", "ethics"]

        category = classifier._categorize_thread(themes)

        assert category == "philosophical"

    def test_categorize_thread_political(self, classifier):
        """Test categorization as political."""
        themes = ["marxism", "anarchism", "imperialism"]

        category = classifier._categorize_thread(themes)

        assert category == "political"

    def test_categorize_thread_both(self, classifier):
        """Test categorization as both philosophical and political."""
        themes = ["marxism", "epistemology", "dialectics"]

        category = classifier._categorize_thread(themes)

        assert category == "both"

    def test_categorize_thread_uncertain(self, classifier):
        """Test categorization as uncertain."""
        themes = ["random_theme", "unknown_topic"]

        category = classifier._categorize_thread(themes)

        assert category in ["uncertain", "other"]

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_process_all_threads(self, mock_dump, mock_load, mock_file, classifier):
        """Test processing all threads with classification."""
        mock_load.return_value = {
            "threads": [
                {
                    "thread_id": "001",
                    "smushed_text": "Discussion of class and capital",
                    "word_count": 100,
                    "tweet_count": 1,
                    "first_tweet_date": "2024-01-01"
                }
            ]
        }

        classifier.themes = {"Marxism": 10}
        classifier.keywords = {"class": "class"}

        result = classifier.process_all_threads()

        assert "metadata" in result
        assert "threads_by_category" in result
        assert result["metadata"]["total_threads"] == 1

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_generate_final_markdown(self, mock_mkdir, mock_file, classifier):
        """Test markdown generation for classified threads."""
        mock_data = {
            "threads_by_category": {
                "philosophical": [
                    {
                        "thread_id": "001",
                        "themes": ["epistemology"],
                        "confidence": 0.8,
                        "word_count": 500,
                        "tweet_count": 5,
                        "first_tweet_date": "2024-01-01",
                        "smushed_text": "Philosophical content"
                    }
                ]
            }
        }

        with patch('json.load', return_value=mock_data):
            classifier.generate_final_markdown("philosophical", limit=1)

            # Should create markdown file
            assert mock_file.call_count > 0

    def test_confidence_calculation(self, classifier):
        """Test confidence score calculation."""
        classifier.keywords = {
            "test1": "test1",
            "test2": "test2"
        }

        thread = {
            "smushed_text": "test1 test2 test1 test1"
        }

        themes, confidence = classifier.classify_thread(thread)

        assert 0.0 <= confidence <= 1.0

    @pytest.mark.parametrize("themes,expected_category", [
        ([], "other"),
        (["unknown"], "uncertain"),
        (["epistemology"], "philosophical"),
        (["marxism"], "political"),
        (["epistemology", "marxism"], "both")
    ])
    def test_categorization_scenarios(self, classifier, themes, expected_category):
        """Test various categorization scenarios."""
        category = classifier._categorize_thread(themes)

        assert category == expected_category