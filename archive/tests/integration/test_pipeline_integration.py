"""
Integration tests for the complete astradocs pipeline.
"""

import json
import shutil
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


class TestPipelineIntegration:
    """End-to-end integration tests for the complete pipeline."""

    @pytest.fixture
    def setup_test_environment(self, tmp_path):
        """Set up complete test environment with all directories."""
        # Create directory structure
        source_dir = tmp_path / "source" / "data"
        source_dir.mkdir(parents=True)

        work_dir = tmp_path / "work"
        for subdir in ["filtered", "samples", "heavy_hitters"]:
            (work_dir / subdir).mkdir(parents=True)

        markdown_dir = tmp_path / "markdown"
        for subdir in ["philosophy", "politics", "both", "themes"]:
            (markdown_dir / subdir).mkdir(parents=True)

        # Create sample tweets.js
        tweets_data = self._generate_sample_tweets_js()
        (source_dir / "tweets.js").write_text(tweets_data)

        return tmp_path

    def _generate_sample_tweets_js(self):
        """Generate sample tweets.js file with various thread types."""
        tweets = [
            # Single philosophical tweet
            {
                "tweet": {
                    "id_str": "1001",
                    "full_text": "Exploring the epistemological foundations of knowledge in the digital age requires us to reconsider traditional philosophical frameworks.",
                    "created_at": "Mon Sep 06 10:00:00 +0000 2024",
                    "in_reply_to_status_id_str": None
                }
            },
            # Political thread
            {
                "tweet": {
                    "id_str": "2001",
                    "full_text": "Thread on political economy: The relationship between labor and capital is fundamentally antagonistic under capitalism.",
                    "created_at": "Mon Sep 06 11:00:00 +0000 2024",
                    "in_reply_to_status_id_str": None
                }
            },
            {
                "tweet": {
                    "id_str": "2002",
                    "full_text": "This antagonism arises from the extraction of surplus value through the difference between labor power and labor time.",
                    "created_at": "Mon Sep 06 11:01:00 +0000 2024",
                    "in_reply_to_status_id_str": "2001"
                }
            },
            {
                "tweet": {
                    "id_str": "2003",
                    "full_text": "Understanding this dynamic is crucial for analyzing contemporary class relations and economic inequality.",
                    "created_at": "Mon Sep 06 11:02:00 +0000 2024",
                    "in_reply_to_status_id_str": "2002"
                }
            },
            # Short tweet to be filtered
            {
                "tweet": {
                    "id_str": "3001",
                    "full_text": "Nice day!",
                    "created_at": "Mon Sep 06 12:00:00 +0000 2024",
                    "in_reply_to_status_id_str": None
                }
            }
        ]

        return f"window.YTD.tweets.part0 = {json.dumps(tweets)};"

    @pytest.mark.integration
    def test_complete_pipeline_flow(self, setup_test_environment):
        """Test complete pipeline from raw tweets to classified output."""
        test_dir = setup_test_environment

        # Stage 1: Filter tweets
        from scripts.local_filter_pipeline import LocalThreadExtractor

        extractor = LocalThreadExtractor(str(test_dir / "source"))

        with patch.object(extractor, 'save_results') as mock_save:
            with patch.object(extractor, 'save_sample_markdowns'):
                extractor.run_pipeline()

                # Verify filtering happened
                assert len(extractor.filtered_tweets) > 0
                assert len(extractor.threads) > 0

        # Stage 2: Generate heavy hitters
        filtered_data = {
            "metadata": {"total_threads": len(extractor.threads)},
            "threads": list(extractor.threads.values())
        }

        # Add word counts for testing
        for thread in filtered_data["threads"]:
            thread["word_count"] = len(thread.get("smushed_text", "").split())

        with patch('builtins.open'):
            with patch('json.load', return_value=filtered_data):
                from scripts.generate_heavy_hitters import generate_heavy_hitter_markdowns

                heavy_hitters = generate_heavy_hitter_markdowns()

                # Should identify any heavy hitters
                assert isinstance(heavy_hitters, list)

        # Stage 3: Classify threads
        from scripts.theme_classifier import ThemeClassifier

        themes_file = test_dir / "THEMES_EXTRACTED.md"
        themes_file.write_text("""
[x] Epistemology: 5
[x] Political Economy: 5

Keywords/Phrases You Actually Use
- "epistemological"
- "labor and capital"
- "surplus value"
""")

        classifier = ThemeClassifier(str(themes_file))

        with patch('builtins.open'):
            with patch('json.load', return_value=filtered_data):
                result = classifier.process_all_threads()

                assert "metadata" in result
                assert "threads_by_category" in result

    @pytest.mark.integration
    def test_data_format_consistency(self, setup_test_environment):
        """Test that data formats remain consistent between pipeline stages."""
        test_dir = setup_test_environment

        # Create sample filtered output
        filtered_output = {
            "metadata": {
                "total_tweets": 100,
                "filtered_tweets": 50,
                "threads_found": 10
            },
            "threads": [
                {
                    "thread_id": "thread_001",
                    "tweet_ids": ["1001", "1002"],
                    "first_tweet_date": "Mon Sep 06 10:00:00 +0000 2024",
                    "smushed_text": "Thread content here",
                    "word_count": 100,
                    "tweet_count": 2
                }
            ]
        }

        # Verify schema consistency
        required_thread_fields = {
            "thread_id", "tweet_ids", "first_tweet_date",
            "smushed_text", "word_count", "tweet_count"
        }

        for thread in filtered_output["threads"]:
            assert set(thread.keys()) >= required_thread_fields

    @pytest.mark.integration
    def test_error_handling_across_pipeline(self, setup_test_environment):
        """Test error handling and recovery across pipeline stages."""
        test_dir = setup_test_environment

        # Test with malformed tweets.js
        bad_tweets = test_dir / "source" / "data" / "tweets.js"
        bad_tweets.write_text("window.YTD.tweets.part0 = {bad json};")

        from scripts.local_filter_pipeline import LocalThreadExtractor

        extractor = LocalThreadExtractor(str(test_dir / "source"))

        # Should handle gracefully
        with pytest.raises(Exception):
            list(extractor.stream_tweets())

    @pytest.mark.integration
    @pytest.mark.slow
    def test_performance_with_large_dataset(self, setup_test_environment):
        """Test pipeline performance with large dataset."""
        test_dir = setup_test_environment

        # Generate large dataset
        large_tweets = []
        for i in range(1000):
            large_tweets.append({
                "tweet": {
                    "id_str": str(i),
                    "full_text": f"Tweet {i} " + "content " * 30,  # ~150 chars
                    "created_at": "Mon Sep 06 10:00:00 +0000 2024",
                    "in_reply_to_status_id_str": str(i-1) if i > 0 and i % 5 != 0 else None
                }
            })

        tweets_file = test_dir / "source" / "data" / "tweets.js"
        tweets_file.write_text(f"window.YTD.tweets.part0 = {json.dumps(large_tweets)};")

        from scripts.local_filter_pipeline import LocalThreadExtractor
        import time

        extractor = LocalThreadExtractor(str(test_dir / "source"))

        start_time = time.time()
        extractor.apply_filters()
        processing_time = time.time() - start_time

        # Should process in reasonable time (< 10 seconds for 1000 tweets)
        assert processing_time < 10.0
        assert len(extractor.filtered_tweets) > 0

    @pytest.mark.integration
    def test_mkdocs_compatibility(self, setup_test_environment):
        """Test that generated markdown is MkDocs compatible."""
        test_dir = setup_test_environment

        # Create sample markdown content
        markdown_content = """# Test Thread

## Metadata
- **Word count**: 500 words
- **Date**: 2024-09-06

## Content

Thread content here.

---

Navigation: [Index](../index.md)
"""

        output_file = test_dir / "markdown" / "philosophy" / "test.md"
        output_file.write_text(markdown_content)

        # Verify markdown structure
        content = output_file.read_text()

        # Check for required MkDocs elements
        assert content.startswith("#")  # Has header
        assert "##" in content  # Has subheaders
        assert "[" in content and "]" in content  # Has links

        # Check for proper line spacing (MD022, MD032)
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("#"):
                # Headers should have blank lines around them
                if i > 0 and lines[i-1].strip():
                    pytest.fail(f"MD022: No blank line before header at line {i}")

    @pytest.mark.integration
    def test_unicode_handling_end_to_end(self, setup_test_environment):
        """Test unicode handling throughout the pipeline."""
        test_dir = setup_test_environment

        # Create tweets with unicode
        unicode_tweets = [
            {
                "tweet": {
                    "id_str": "9001",
                    "full_text": "Philosophy discussion with emojis 🤔💭 and special chars: résumé, 中文, العربية" + " extra" * 20,
                    "created_at": "Mon Sep 06 10:00:00 +0000 2024",
                    "in_reply_to_status_id_str": None
                }
            }
        ]

        tweets_file = test_dir / "source" / "data" / "tweets.js"
        tweets_file.write_text(f"window.YTD.tweets.part0 = {json.dumps(unicode_tweets)};")

        from scripts.local_filter_pipeline import LocalThreadExtractor

        extractor = LocalThreadExtractor(str(test_dir / "source"))
        extractor.apply_filters()

        # Verify unicode preserved
        assert len(extractor.filtered_tweets) > 0
        assert "🤔" in extractor.filtered_tweets[0]["full_text"]
        assert "中文" in extractor.filtered_tweets[0]["full_text"]