"""
Comprehensive integration tests for local_filter_pipeline.py

This test suite provides full coverage for the LocalThreadExtractor class,
testing the complete Twitter archive processing pipeline from raw data
to filtered threads with proper error handling and edge cases.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from local_filter_pipeline import LocalThreadExtractor


class TestArchiveValidation:
    """Tests for archive structure validation."""

    def test_valid_archive_structure(self, tmp_path):
        """Test validation passes with correct archive structure."""
        # Setup valid archive
        archive_path = self._create_valid_archive(tmp_path)

        # Should not raise
        extractor = LocalThreadExtractor(archive_path)
        assert extractor.archive_path == archive_path
        assert extractor.tweets_file.exists()

    def test_missing_archive_directory(self):
        """Test handling of non-existent archive directory."""
        with pytest.raises(ValueError, match="Archive directory does not exist"):
            LocalThreadExtractor(Path("/non/existent/path"))

    def test_archive_path_is_file(self, tmp_path):
        """Test handling when archive path is a file, not directory."""
        file_path = tmp_path / "not_a_directory.txt"
        file_path.write_text("content")

        with pytest.raises(ValueError, match="Archive path is not a directory"):
            LocalThreadExtractor(file_path)

    def test_missing_data_directory(self, tmp_path):
        """Test handling of missing data directory."""
        archive_path = tmp_path / "archive"
        archive_path.mkdir()
        (archive_path / "Your archive.html").write_text("<html></html>")

        with pytest.raises(ValueError, match="Invalid archive structure"):
            LocalThreadExtractor(archive_path)

    def test_missing_tweets_file(self, tmp_path):
        """Test handling of missing tweets.js file."""
        archive_path = tmp_path / "archive"
        (archive_path / "data").mkdir(parents=True)
        (archive_path / "Your archive.html").write_text("<html></html>")

        with pytest.raises(ValueError, match="Invalid archive structure"):
            LocalThreadExtractor(archive_path)

    def test_empty_tweets_file(self, tmp_path):
        """Test handling of empty tweets.js file."""
        archive_path = self._create_valid_archive(tmp_path, tweets_content="")

        with pytest.raises(ValueError, match="tweets.js file is empty"):
            LocalThreadExtractor(archive_path)

    def test_invalid_tweets_format(self, tmp_path):
        """Test handling of invalid tweets.js format."""
        archive_path = self._create_valid_archive(
            tmp_path, tweets_content="invalid javascript content"
        )

        with pytest.raises(
            ValueError, match="does not appear to be a valid Twitter archive"
        ):
            LocalThreadExtractor(archive_path)

    def test_corrupted_tweets_file(self, tmp_path):
        """Test handling of corrupted/binary tweets file."""
        archive_path = tmp_path / "archive"
        (archive_path / "data").mkdir(parents=True)
        (archive_path / "Your archive.html").write_text("<html></html>")

        # Write binary content
        tweets_file = archive_path / "data" / "tweets.js"
        tweets_file.write_bytes(b"\x00\x01\x02\x03\x04")

        with pytest.raises(ValueError, match="appears to be corrupted"):
            LocalThreadExtractor(archive_path)

    def _create_valid_archive(self, tmp_path, tweets_content=None):
        """Helper to create a valid archive structure."""
        archive_path = tmp_path / "archive"
        data_dir = archive_path / "data"
        data_dir.mkdir(parents=True)

        # Create required files
        (archive_path / "Your archive.html").write_text("<html></html>")

        if tweets_content is None:
            tweets_content = "window.YTD.tweets.part0 = []"

        if tweets_content:  # Only write if not empty string
            (data_dir / "tweets.js").write_text(tweets_content)
        else:
            (data_dir / "tweets.js").touch()  # Create empty file

        return archive_path


class TestTweetStreaming:
    """Tests for tweet streaming functionality."""

    def test_stream_simple_tweets(self, tmp_path):
        """Test streaming basic tweets without nesting."""
        tweets_data = [
            {"id_str": "1", "full_text": "First tweet"},
            {"id_str": "2", "full_text": "Second tweet"},
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        tweets = list(extractor.stream_tweets())
        assert len(tweets) == 2
        assert tweets[0]["id_str"] == "1"
        assert tweets[1]["full_text"] == "Second tweet"

    def test_stream_nested_tweets(self, tmp_path):
        """Test streaming tweets with nested structure."""
        tweets_data = [
            {"tweet": {"id_str": "1", "full_text": "Nested tweet 1"}},
            {"tweet": {"id_str": "2", "full_text": "Nested tweet 2"}},
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        tweets = list(extractor.stream_tweets())
        assert len(tweets) == 2
        assert tweets[0]["id_str"] == "1"
        assert tweets[1]["full_text"] == "Nested tweet 2"

    def test_stream_large_dataset(self, tmp_path):
        """Test streaming performance with large dataset."""
        # Generate 5000 tweets
        tweets_data = [
            {"id_str": str(i), "full_text": f"Tweet number {i}"} for i in range(5000)
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        tweets = list(extractor.stream_tweets())
        assert len(tweets) == 5000
        assert tweets[0]["id_str"] == "0"
        assert tweets[4999]["id_str"] == "4999"

    def test_stream_malformed_json(self, tmp_path):
        """Test handling of malformed JSON in tweets file."""
        archive_path = tmp_path / "archive"
        data_dir = archive_path / "data"
        data_dir.mkdir(parents=True)
        (archive_path / "Your archive.html").write_text("<html></html>")

        # Create malformed JSON
        tweets_file = data_dir / "tweets.js"
        tweets_file.write_text('window.YTD.tweets.part0 = [{"broken": ]')

        extractor = LocalThreadExtractor(archive_path)

        # Should raise during streaming
        with pytest.raises(Exception):  # ijson will raise a parse error
            list(extractor.stream_tweets())

    def _create_archive_with_tweets(self, tmp_path, tweets_data):
        """Helper to create archive with specific tweet data."""
        archive_path = tmp_path / "archive"
        data_dir = archive_path / "data"
        data_dir.mkdir(parents=True)
        (archive_path / "Your archive.html").write_text("<html></html>")

        # Create tweets.js with data
        tweets_json = json.dumps(tweets_data)
        tweets_content = f"window.YTD.tweets.part0 = {tweets_json}"
        (data_dir / "tweets.js").write_text(tweets_content)

        return archive_path


class TestFilteringLogic:
    """Tests for two-stage filtering logic."""

    def test_stage1_filter_length(self, tmp_path):
        """Test Stage 1: Length filter (>100 chars)."""
        tweets_data = [
            {"id_str": "1", "full_text": "Short"},  # <100 chars
            {"id_str": "2", "full_text": "a" * 101},  # >100 chars
            {"id_str": "3", "full_text": "b" * 50},  # <100 chars
            {"id_str": "4", "full_text": "c" * 200},  # >100 chars
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        # Test individual filter
        assert not extractor.apply_stage1_filter(tweets_data[0])
        assert extractor.apply_stage1_filter(tweets_data[1])
        assert not extractor.apply_stage1_filter(tweets_data[2])
        assert extractor.apply_stage1_filter(tweets_data[3])

    def test_stage2_filter_threads(self, tmp_path):
        """Test Stage 2: Thread detection (replies)."""
        tweets_data = [
            {"id_str": "1", "full_text": "a" * 101},  # No reply, no replies to it
            {
                "id_str": "2",
                "full_text": "b" * 101,
                "in_reply_to_status_id_str": "1",
            },  # Reply
            {
                "id_str": "3",
                "full_text": "c" * 101,
                "in_reply_to_status_id_str": None,
            },  # Not a reply
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        # Process tweets to build reply map
        extractor.process_tweets()

        # Check filtered results
        filtered_ids = {t["id_str"] for t in extractor.filtered_tweets}
        assert "1" in filtered_ids  # Has replies
        assert "2" in filtered_ids  # Is a reply
        assert "3" not in filtered_ids  # Neither

    def test_full_filtering_pipeline(self, tmp_path):
        """Test complete two-stage filtering process."""
        tweets_data = [
            # Thread 1: Root with replies
            {"id_str": "1", "full_text": "a" * 150},
            {"id_str": "2", "full_text": "b" * 120, "in_reply_to_status_id_str": "1"},
            {"id_str": "3", "full_text": "c" * 110, "in_reply_to_status_id_str": "2"},
            # Thread 2: Partial thread
            {"id_str": "4", "full_text": "d" * 200, "in_reply_to_status_id_str": "999"},
            {"id_str": "5", "full_text": "e" * 180, "in_reply_to_status_id_str": "4"},
            # Non-thread tweets
            {"id_str": "6", "full_text": "Short tweet"},  # Too short
            {"id_str": "7", "full_text": "f" * 150},  # Long but no thread
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        extractor.process_tweets()

        # Verify results
        assert len(extractor.filtered_tweets) == 5  # 1,2,3,4,5
        filtered_ids = {t["id_str"] for t in extractor.filtered_tweets}
        assert filtered_ids == {"1", "2", "3", "4", "5"}

    def _create_archive_with_tweets(self, tmp_path, tweets_data):
        """Helper to create archive with specific tweet data."""
        archive_path = tmp_path / "archive"
        data_dir = archive_path / "data"
        data_dir.mkdir(parents=True)
        (archive_path / "Your archive.html").write_text("<html></html>")

        tweets_json = json.dumps(tweets_data)
        tweets_content = f"window.YTD.tweets.part0 = {tweets_json}"
        (data_dir / "tweets.js").write_text(tweets_content)

        return archive_path


class TestThreadReconstruction:
    """Tests for thread reconstruction logic."""

    def test_reconstruct_simple_thread(self, tmp_path):
        """Test reconstructing a simple linear thread."""
        tweets_data = [
            {"id_str": "1", "full_text": "a" * 150},
            {"id_str": "2", "full_text": "b" * 150, "in_reply_to_status_id_str": "1"},
            {"id_str": "3", "full_text": "c" * 150, "in_reply_to_status_id_str": "2"},
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        extractor.process_tweets()
        extractor.reconstruct_threads()

        assert len(extractor.threads) == 1
        thread = extractor.threads[0]
        assert len(thread) == 3
        assert [t["id_str"] for t in thread] == ["1", "2", "3"]

    def test_reconstruct_branching_thread(self, tmp_path):
        """Test reconstructing thread with multiple branches."""
        tweets_data = [
            {"id_str": "1", "full_text": "Root" + "a" * 150},
            {
                "id_str": "2",
                "full_text": "Branch1" + "b" * 150,
                "in_reply_to_status_id_str": "1",
            },
            {
                "id_str": "3",
                "full_text": "Branch2" + "c" * 150,
                "in_reply_to_status_id_str": "1",
            },
            {
                "id_str": "4",
                "full_text": "Reply" + "d" * 150,
                "in_reply_to_status_id_str": "2",
            },
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        extractor.process_tweets()
        extractor.reconstruct_threads()

        # Should create one thread with all connected tweets
        assert len(extractor.threads) == 1
        thread = extractor.threads[0]
        assert len(thread) == 4

    def test_reconstruct_partial_thread(self, tmp_path):
        """Test reconstructing thread missing root tweet."""
        tweets_data = [
            # Missing root with id "999"
            {
                "id_str": "1000",
                "full_text": "a" * 150,
                "in_reply_to_status_id_str": "999",
            },
            {
                "id_str": "1001",
                "full_text": "b" * 150,
                "in_reply_to_status_id_str": "1000",
            },
            {
                "id_str": "1002",
                "full_text": "c" * 150,
                "in_reply_to_status_id_str": "1001",
            },
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        extractor.process_tweets()
        extractor.reconstruct_threads()

        assert len(extractor.threads) == 1
        thread = extractor.threads[0]
        assert len(thread) == 3
        assert thread[0]["id_str"] == "1000"  # Starts from available root

    def test_minimum_thread_size(self, tmp_path):
        """Test that threads need at least 2 tweets."""
        tweets_data = [
            {"id_str": "1", "full_text": "a" * 150},  # Single tweet, no replies
            {
                "id_str": "2",
                "full_text": "b" * 150,
                "in_reply_to_status_id_str": "999",
            },  # Single reply
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        extractor.process_tweets()
        extractor.reconstruct_threads()

        assert len(extractor.threads) == 0  # No valid threads

    def test_thread_sorting_by_date(self, tmp_path):
        """Test threads are sorted by date (most recent first)."""
        tweets_data = [
            {"id_str": "1", "full_text": "a" * 150, "created_at": "2024-01-01"},
            {"id_str": "2", "full_text": "b" * 150, "in_reply_to_status_id_str": "1"},
            {"id_str": "3", "full_text": "c" * 150, "created_at": "2024-02-01"},
            {"id_str": "4", "full_text": "d" * 150, "in_reply_to_status_id_str": "3"},
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        extractor.process_tweets()
        extractor.reconstruct_threads()

        assert len(extractor.threads) == 2
        # Most recent thread first
        assert extractor.threads[0][0]["created_at"] == "2024-02-01"
        assert extractor.threads[1][0]["created_at"] == "2024-01-01"

    def _create_archive_with_tweets(self, tmp_path, tweets_data):
        """Helper to create archive with specific tweet data."""
        archive_path = tmp_path / "archive"
        data_dir = archive_path / "data"
        data_dir.mkdir(parents=True)
        (archive_path / "Your archive.html").write_text("<html></html>")

        tweets_json = json.dumps(tweets_data)
        tweets_content = f"window.YTD.tweets.part0 = {tweets_json}"
        (data_dir / "tweets.js").write_text(tweets_content)

        return archive_path


class TestJsonOutput:
    """Tests for JSON output generation."""

    def test_generate_json_structure(self, tmp_path):
        """Test JSON output has correct structure."""
        tweets_data = [
            {"id_str": "1", "full_text": "First tweet " + "a" * 150},
            {
                "id_str": "2",
                "full_text": "Reply tweet " + "b" * 150,
                "in_reply_to_status_id_str": "1",
            },
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        extractor.process_tweets()
        extractor.reconstruct_threads()
        output = extractor.generate_json_output()

        # Check metadata
        assert "metadata" in output
        assert output["metadata"]["total_original_tweets"] == 21723
        assert output["metadata"]["filtered_tweets"] == 2
        assert output["metadata"]["threads_found"] == 1
        assert "processing_date" in output["metadata"]
        assert output["metadata"]["filter_stages"] == ["length>100", "thread_detection"]

        # Check threads
        assert "threads" in output
        assert len(output["threads"]) == 1

        thread = output["threads"][0]
        assert "thread_id" in thread
        assert thread["tweet_count"] == 2
        assert "first_tweet_date" in thread
        assert "smushed_text" in thread
        assert "word_count" in thread
        assert thread["tweet_ids"] == ["1", "2"]
        assert "individual_tweets" in thread

    def test_json_file_creation(self, tmp_path):
        """Test JSON file is saved correctly."""
        tweets_data = [
            {"id_str": "1", "full_text": "a" * 150},
            {"id_str": "2", "full_text": "b" * 150, "in_reply_to_status_id_str": "1"},
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)

        # Change working directory to tmp_path for file creation
        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            extractor = LocalThreadExtractor(archive_path)
            extractor.process_tweets()
            extractor.reconstruct_threads()
            extractor.generate_json_output()

            # Check file was created
            json_file = Path("data/filtered_threads.json")
            assert json_file.exists()

            # Verify content
            with open(json_file) as f:
                data = json.load(f)
                assert data["metadata"]["threads_found"] == 1
        finally:
            os.chdir(original_cwd)

    def test_smushed_text_generation(self, tmp_path):
        """Test smushed_text combines all tweet texts."""
        tweets_data = [
            {"id_str": "1", "full_text": "First part of thread"},
            {
                "id_str": "2",
                "full_text": "Second part of thread",
                "in_reply_to_status_id_str": "1",
            },
            {
                "id_str": "3",
                "full_text": "Third part of thread",
                "in_reply_to_status_id_str": "2",
            },
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)
        extractor = LocalThreadExtractor(archive_path)

        extractor.process_tweets()
        extractor.reconstruct_threads()
        output = extractor.generate_json_output()

        thread = output["threads"][0]
        expected_text = (
            "First part of thread Second part of thread Third part of thread"
        )
        assert thread["smushed_text"] == expected_text
        assert thread["word_count"] == len(expected_text.split())

    def _create_archive_with_tweets(self, tmp_path, tweets_data):
        """Helper to create archive with specific tweet data."""
        archive_path = tmp_path / "archive"
        data_dir = archive_path / "data"
        data_dir.mkdir(parents=True)
        (archive_path / "Your archive.html").write_text("<html></html>")

        tweets_json = json.dumps(tweets_data)
        tweets_content = f"window.YTD.tweets.part0 = {tweets_json}"
        (data_dir / "tweets.js").write_text(tweets_content)

        return archive_path


class TestSampleMarkdownGeneration:
    """Tests for sample markdown generation."""

    def test_generate_sample_markdowns(self, tmp_path):
        """Test sample markdown files are generated."""
        tweets_data = [
            {
                "id_str": "1",
                "full_text": "Long thread " + "a" * 200,
                "created_at": "Mon Jan 15 10:30:00 +0000 2024",
            },
            {
                "id_str": "2",
                "full_text": "Reply " + "b" * 200,
                "in_reply_to_status_id_str": "1",
            },
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)

        # Change working directory
        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            extractor = LocalThreadExtractor(archive_path)
            extractor.process_tweets()
            extractor.reconstruct_threads()
            extractor.generate_sample_markdown(sample_count=1)

            # Check markdown directory created
            md_dir = Path("data/sample_threads")
            assert md_dir.exists()

            # Check markdown file created
            md_files = list(md_dir.glob("*.md"))
            assert len(md_files) == 1

            # Verify content structure
            content = md_files[0].read_text()
            assert "# Thread from" in content
            assert "Tweets in thread: 2" in content
            assert "Total words:" in content
            assert "Thread IDs: 1, 2" in content
        finally:
            os.chdir(original_cwd)

    def test_markdown_filename_generation(self, tmp_path):
        """Test markdown filenames are generated correctly."""
        tweets_data = [
            {
                "id_str": "1",
                "full_text": "Test thread about @user and #hashtag! More content...",
                "created_at": "Mon Jan 15 10:30:00 +0000 2024",
            },
            {"id_str": "2", "full_text": "b" * 150, "in_reply_to_status_id_str": "1"},
        ]

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)

        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            extractor = LocalThreadExtractor(archive_path)
            extractor.process_tweets()
            extractor.reconstruct_threads()
            extractor.generate_sample_markdown(sample_count=1)

            md_dir = Path("data/sample_threads")
            md_files = list(md_dir.glob("*.md"))

            # Filename should be date_cleaned_text.md
            filename = md_files[0].name
            assert filename.startswith("Mon Jan 15")
            assert "Test_thread_about_user_and" in filename
            assert filename.endswith(".md")
        finally:
            os.chdir(original_cwd)

    def _create_archive_with_tweets(self, tmp_path, tweets_data):
        """Helper to create archive with specific tweet data."""
        archive_path = tmp_path / "archive"
        data_dir = archive_path / "data"
        data_dir.mkdir(parents=True)
        (archive_path / "Your archive.html").write_text("<html></html>")

        tweets_json = json.dumps(tweets_data)
        tweets_content = f"window.YTD.tweets.part0 = {tweets_json}"
        (data_dir / "tweets.js").write_text(tweets_content)

        return archive_path


class TestFullPipeline:
    """End-to-end tests for complete pipeline."""

    def test_run_pipeline_complete(self, tmp_path):
        """Test complete pipeline execution."""
        # Create realistic dataset
        tweets_data = self._create_realistic_dataset()
        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)

        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            extractor = LocalThreadExtractor(archive_path)
            output = extractor.run_pipeline()

            # Verify all outputs
            assert output["metadata"]["threads_found"] > 0
            assert Path("data/filtered_threads.json").exists()
            assert Path("data/sample_threads").exists()

            # Check sample files
            sample_files = list(Path("data/sample_threads").glob("*.md"))
            assert len(sample_files) <= 5  # Default sample count
        finally:
            os.chdir(original_cwd)

    def test_pipeline_statistics(self, tmp_path):
        """Test pipeline generates correct statistics."""
        tweets_data = self._create_realistic_dataset()
        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)

        extractor = LocalThreadExtractor(archive_path)
        extractor.run_pipeline()

        # Verify statistics calculations
        total_tweets = sum(len(thread) for thread in extractor.threads)
        assert len(extractor.filtered_tweets) >= total_tweets

        if extractor.threads:
            avg_length = sum(len(t) for t in extractor.threads) / len(extractor.threads)
            max_length = max(len(t) for t in extractor.threads)
            assert avg_length > 0
            assert max_length >= 2

    def test_pipeline_performance(self, tmp_path):
        """Test pipeline handles large datasets efficiently."""
        import time

        # Create large dataset (1000 tweets)
        tweets_data = []
        for i in range(1000):
            tweet = {
                "id_str": str(i),
                "full_text": f"Tweet {i} " + "x" * 150,
                "created_at": f"2024-01-{(i % 28) + 1:02d}",
            }
            if i > 0 and i % 3 == 0:  # Every 3rd tweet is a reply
                tweet["in_reply_to_status_id_str"] = str(i - 1)
            tweets_data.append(tweet)

        archive_path = self._create_archive_with_tweets(tmp_path, tweets_data)

        start_time = time.time()
        extractor = LocalThreadExtractor(archive_path)
        extractor.run_pipeline()
        elapsed = time.time() - start_time

        # Should process 1000 tweets in reasonable time
        assert elapsed < 10  # 10 seconds max
        assert len(extractor.filtered_tweets) > 0
        assert len(extractor.threads) > 0

    def _create_realistic_dataset(self):
        """Create a realistic test dataset."""
        return [
            # Thread 1: Philosophy discussion
            {
                "id_str": "100",
                "full_text": "Discussing Kant's categorical imperative and its implications for modern ethics. This is a complex topic that requires careful consideration of multiple perspectives.",
                "created_at": "Mon Jan 01 10:00:00 +0000 2024",
            },
            {
                "id_str": "101",
                "full_text": "The universalizability principle suggests that moral actions must be applicable to all rational beings. This creates interesting challenges in pluralistic societies.",
                "in_reply_to_status_id_str": "100",
                "created_at": "Mon Jan 01 10:05:00 +0000 2024",
            },
            {
                "id_str": "102",
                "full_text": "Critics argue that the categorical imperative is too rigid and doesn't account for contextual nuances. Virtue ethics offers a more flexible framework.",
                "in_reply_to_status_id_str": "101",
                "created_at": "Mon Jan 01 10:10:00 +0000 2024",
            },
            # Thread 2: Technology critique
            {
                "id_str": "200",
                "full_text": "The attention economy is fundamentally reshaping human cognition. We're optimizing for engagement metrics rather than human flourishing or genuine connection.",
                "created_at": "Tue Jan 02 14:00:00 +0000 2024",
            },
            {
                "id_str": "201",
                "full_text": "Platform algorithms create filter bubbles that reinforce existing beliefs. This polarization threatens democratic discourse and shared understanding.",
                "in_reply_to_status_id_str": "200",
                "created_at": "Tue Jan 02 14:15:00 +0000 2024",
            },
            # Non-thread tweets
            {
                "id_str": "300",
                "full_text": "Short tweet",
                "created_at": "Wed Jan 03 09:00:00 +0000 2024",
            },
            {
                "id_str": "301",
                "full_text": "Another standalone tweet that's long enough but not part of any thread structure",
                "created_at": "Wed Jan 03 09:30:00 +0000 2024",
            },
        ]

    def _create_archive_with_tweets(self, tmp_path, tweets_data):
        """Helper to create archive with specific tweet data."""
        archive_path = tmp_path / "archive"
        data_dir = archive_path / "data"
        data_dir.mkdir(parents=True)
        (archive_path / "Your archive.html").write_text("<html></html>")

        tweets_json = json.dumps(tweets_data)
        tweets_content = f"window.YTD.tweets.part0 = {tweets_json}"
        (data_dir / "tweets.js").write_text(tweets_content)

        return archive_path


# Run configuration for pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
