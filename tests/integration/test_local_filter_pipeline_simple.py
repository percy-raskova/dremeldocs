"""
Simple integration tests for local_filter_pipeline.py

Focused on testing the core functionality that actually matters
for the DremelDocs hobbyist project.
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from local_filter_pipeline import LocalThreadExtractor


class TestCoreFilteringPipeline:
    """Test the essential pipeline functionality."""

    def test_valid_archive_loads_successfully(self, tmp_path):
        """Test that a valid Twitter archive structure loads without errors."""
        # Create minimal valid archive
        archive = tmp_path / "archive"
        (archive / "data").mkdir(parents=True)
        (archive / "data" / "tweets.js").write_text('window.YTD.tweets.part0 = []')
        (archive / "Your archive.html").write_text("<html></html>")

        # Should initialize without errors
        extractor = LocalThreadExtractor(archive)
        assert extractor.tweets_file.exists()

    def test_filters_tweets_by_length(self, tmp_path):
        """Test that short tweets are filtered out (must be >100 chars)."""
        archive = self._create_test_archive(tmp_path, [
            {"id_str": "1", "full_text": "Short tweet"},  # Too short
            {"id_str": "2", "full_text": "a" * 101}  # Long enough
        ])

        extractor = LocalThreadExtractor(archive)
        extractor.process_tweets()

        # Only the long tweet should pass
        assert len(extractor.tweets_by_id) == 1
        assert "2" in extractor.tweets_by_id

    def test_identifies_threads(self, tmp_path):
        """Test that reply chains are identified as threads."""
        archive = self._create_test_archive(tmp_path, [
            {"id_str": "1", "full_text": "First tweet " + "x" * 100},
            {"id_str": "2", "full_text": "Reply tweet " + "x" * 100,
             "in_reply_to_status_id_str": "1"},
            {"id_str": "3", "full_text": "Another reply " + "x" * 100,
             "in_reply_to_status_id_str": "2"}
        ])

        extractor = LocalThreadExtractor(archive)
        extractor.process_tweets()
        extractor.reconstruct_threads()

        # Should find one thread with 3 tweets
        assert len(extractor.threads) == 1
        assert len(extractor.threads[0]) == 3

    def test_generates_json_output(self, tmp_path):
        """Test that JSON output is generated with correct structure."""
        archive = self._create_test_archive(tmp_path, [
            {"id_str": "1", "full_text": "Thread start " + "x" * 100},
            {"id_str": "2", "full_text": "Thread reply " + "x" * 100,
             "in_reply_to_status_id_str": "1"}
        ])

        extractor = LocalThreadExtractor(archive)
        extractor.process_tweets()
        extractor.reconstruct_threads()
        output = extractor.generate_json_output()

        # Check basic structure
        assert "metadata" in output
        assert "threads" in output
        assert len(output["threads"]) == 1
        assert output["threads"][0]["tweet_count"] == 2
        assert output["threads"][0]["tweet_ids"] == ["1", "2"]

    def test_handles_missing_archive_gracefully(self):
        """Test that missing archive directory raises clear error."""
        with pytest.raises(ValueError, match="Archive directory does not exist"):
            LocalThreadExtractor(Path("/does/not/exist"))

    def test_handles_empty_tweets_file(self, tmp_path):
        """Test that empty tweets.js file is detected."""
        archive = tmp_path / "archive"
        (archive / "data").mkdir(parents=True)
        (archive / "data" / "tweets.js").touch()  # Empty file
        (archive / "Your archive.html").write_text("<html></html>")

        with pytest.raises(ValueError, match="tweets.js file is empty"):
            LocalThreadExtractor(archive)

    def _create_test_archive(self, tmp_path, tweets_data):
        """Helper to quickly create a test archive."""
        archive = tmp_path / "archive"
        (archive / "data").mkdir(parents=True)
        (archive / "Your archive.html").write_text("<html></html>")

        tweets_json = json.dumps(tweets_data)
        tweets_js = f'window.YTD.tweets.part0 = {tweets_json}'
        (archive / "data" / "tweets.js").write_text(tweets_js)

        return archive


class TestRealWorldScenarios:
    """Test with realistic data patterns we expect to see."""

    def test_philosophy_thread_extraction(self, tmp_path):
        """Test extraction of a typical philosophy discussion thread."""
        archive = self._create_test_archive(tmp_path, [
            {
                "id_str": "1",
                "full_text": "Discussing the implications of historical materialism on modern political economy. The base-superstructure relationship remains relevant.",
                "created_at": "Mon Jan 15 10:00:00 +0000 2024"
            },
            {
                "id_str": "2",
                "full_text": "The material conditions of production fundamentally shape social relations and ideology, not the reverse as idealists claim.",
                "in_reply_to_status_id_str": "1",
                "created_at": "Mon Jan 15 10:05:00 +0000 2024"
            },
            {
                "id_str": "3",
                "full_text": "This framework helps explain why technological changes drive social transformations, from feudalism to capitalism and beyond.",
                "in_reply_to_status_id_str": "2",
                "created_at": "Mon Jan 15 10:10:00 +0000 2024"
            }
        ])

        extractor = LocalThreadExtractor(archive)
        extractor.run_pipeline()

        # Should extract the philosophy thread
        assert len(extractor.threads) == 1
        thread = extractor.threads[0]
        assert len(thread) == 3

        # Check smushed text contains key terms
        output = extractor.generate_json_output()
        smushed = output["threads"][0]["smushed_text"]
        assert "historical materialism" in smushed
        assert "base-superstructure" in smushed

    def test_filters_out_noise(self, tmp_path):
        """Test that short tweets and non-threads are filtered out."""
        archive = self._create_test_archive(tmp_path, [
            # Good thread
            {"id_str": "1", "full_text": "Long thoughtful tweet about philosophy " + "x" * 80},
            {"id_str": "2", "full_text": "Continuing the discussion " + "x" * 100,
             "in_reply_to_status_id_str": "1"},

            # Noise to filter out
            {"id_str": "3", "full_text": "RT @someone: check this out"},  # Too short
            {"id_str": "4", "full_text": "lol"},  # Too short
            {"id_str": "5", "full_text": "Random long tweet with no replies " + "x" * 100},  # No thread
        ])

        extractor = LocalThreadExtractor(archive)
        extractor.run_pipeline()

        # Should only extract the one good thread
        assert len(extractor.threads) == 1
        assert len(extractor.threads[0]) == 2
        assert extractor.threads[0][0]["id_str"] == "1"

    def _create_test_archive(self, tmp_path, tweets_data):
        """Helper to create test archive."""
        archive = tmp_path / "archive"
        (archive / "data").mkdir(parents=True)
        (archive / "Your archive.html").write_text("<html></html>")

        tweets_json = json.dumps(tweets_data)
        tweets_js = f'window.YTD.tweets.part0 = {tweets_json}'
        (archive / "data" / "tweets.js").write_text(tweets_js)

        return archive


if __name__ == "__main__":
    pytest.main([__file__, "-v"])