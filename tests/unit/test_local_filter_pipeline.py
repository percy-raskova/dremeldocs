#!/usr/bin/env python3
"""
Unit tests for local_filter_pipeline.py following TDD methodology.
Tests are designed to be comprehensive, isolated, and fast.
"""

import json

# Add scripts directory to path for imports
import sys
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from local_filter_pipeline import LocalThreadExtractor


class TestLocalThreadExtractorInit:
    """Test initialization and archive validation."""

    def test_init_valid_archive(self, tmp_path):
        """Test initialization with valid archive structure."""
        # Create valid archive structure
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()

        # Create tweets.js with valid header
        tweets_file = archive_dir / "data" / "tweets.js"
        tweets_file.write_text("window.YTD.tweets.part0 = []")

        # Create archive.html
        (archive_dir / "archive.html").write_text("<html></html>")

        # Should initialize without errors
        extractor = LocalThreadExtractor(archive_dir)
        assert extractor.archive_path == archive_dir
        assert extractor.tweets_file == tweets_file
        assert isinstance(extractor.tweets_by_id, dict)
        assert isinstance(extractor.reply_map, dict)

    def test_init_missing_archive_dir(self):
        """Test initialization with non-existent directory."""
        with pytest.raises(ValueError) as exc_info:
            LocalThreadExtractor(Path("/non/existent/path"))
        assert "Archive directory does not exist" in str(exc_info.value)

    def test_init_not_a_directory(self, tmp_path):
        """Test initialization with file instead of directory."""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("content")

        with pytest.raises(ValueError) as exc_info:
            LocalThreadExtractor(file_path)
        assert "Archive path is not a directory" in str(exc_info.value)

    def test_init_missing_data_dir(self, tmp_path):
        """Test initialization with missing data directory."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "archive.html").write_text("<html></html>")

        with pytest.raises(ValueError) as exc_info:
            LocalThreadExtractor(archive_dir)
        assert "Invalid archive structure" in str(exc_info.value)

    def test_init_missing_tweets_js(self, tmp_path):
        """Test initialization with missing tweets.js file."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "archive.html").write_text("<html></html>")

        with pytest.raises(ValueError) as exc_info:
            LocalThreadExtractor(archive_dir)
        assert "Invalid archive structure" in str(exc_info.value)

    def test_init_empty_tweets_js(self, tmp_path):
        """Test initialization with empty tweets.js file."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "data" / "tweets.js").write_text("")
        (archive_dir / "archive.html").write_text("<html></html>")

        with pytest.raises(ValueError) as exc_info:
            LocalThreadExtractor(archive_dir)
        assert "tweets.js file is empty" in str(exc_info.value)

    def test_init_invalid_tweets_js_format(self, tmp_path):
        """Test initialization with invalid tweets.js format."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "data" / "tweets.js").write_text("invalid content")
        (archive_dir / "archive.html").write_text("<html></html>")

        with pytest.raises(ValueError) as exc_info:
            LocalThreadExtractor(archive_dir)
        assert "does not appear to be a valid Twitter archive" in str(exc_info.value)

    def test_init_accepts_your_archive_html(self, tmp_path):
        """Test that 'Your archive.html' is accepted."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "data" / "tweets.js").write_text("window.YTD.tweets.part0 = []")
        (archive_dir / "Your archive.html").write_text("<html></html>")

        # Should initialize without errors
        extractor = LocalThreadExtractor(archive_dir)
        assert extractor.archive_path == archive_dir


class TestStreamTweets:
    """Test tweet streaming functionality."""

    @pytest.fixture
    def mock_tweets_data(self):
        """Sample tweets data for testing."""
        return [
            {
                "tweet": {
                    "id_str": "1",
                    "full_text": "First tweet",
                    "created_at": "2024-01-01",
                }
            },
            {
                "tweet": {
                    "id_str": "2",
                    "full_text": "Second tweet",
                    "created_at": "2024-01-02",
                }
            },
            {
                "id_str": "3",
                "full_text": "Third tweet without wrapper",
                "created_at": "2024-01-03",
            },
        ]

    def test_stream_tweets_with_wrapper(self, tmp_path, mock_tweets_data):
        """Test streaming tweets with 'tweet' wrapper."""
        archive_dir = self._setup_archive(tmp_path)

        # Create tweets.js with wrapped format
        tweets_js = "window.YTD.tweets.part0 = " + json.dumps(mock_tweets_data)
        (archive_dir / "data" / "tweets.js").write_text(tweets_js)

        extractor = LocalThreadExtractor(archive_dir)
        tweets = list(extractor.stream_tweets())

        assert len(tweets) == 3
        assert tweets[0]["id_str"] == "1"
        assert tweets[1]["id_str"] == "2"
        assert tweets[2]["id_str"] == "3"

    def test_stream_tweets_handles_large_file(self, tmp_path):
        """Test streaming handles large files efficiently."""
        archive_dir = self._setup_archive(tmp_path)

        # Create a large tweets file
        large_tweets = [
            {"tweet": {"id_str": str(i), "full_text": f"Tweet {i}"}}
            for i in range(5000)
        ]
        tweets_js = "window.YTD.tweets.part0 = " + json.dumps(large_tweets)
        (archive_dir / "data" / "tweets.js").write_bytes(tweets_js.encode())

        extractor = LocalThreadExtractor(archive_dir)
        tweet_count = 0

        # Should stream without loading all into memory
        for tweet in extractor.stream_tweets():
            tweet_count += 1
            assert "id_str" in tweet
            assert "full_text" in tweet

        assert tweet_count == 5000

    def test_stream_tweets_invalid_json_start(self, tmp_path):
        """Test error handling for invalid JSON start."""
        archive_dir = self._setup_archive(tmp_path)

        # Create tweets.js without proper JSON array
        (archive_dir / "data" / "tweets.js").write_text(
            'window.YTD.tweets.part0 = "not an array"'
        )

        extractor = LocalThreadExtractor(archive_dir)
        with pytest.raises(ValueError) as exc_info:
            list(extractor.stream_tweets())
        assert "Could not find JSON array start" in str(exc_info.value)

    def _setup_archive(self, tmp_path):
        """Helper to set up valid archive structure."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "archive.html").write_text("<html></html>")
        return archive_dir


class TestFiltering:
    """Test tweet filtering functionality."""

    def test_stage1_filter_passes_long_tweets(self):
        """Test stage 1 filter passes tweets > 100 chars."""
        extractor = Mock(spec=LocalThreadExtractor)

        tweet_long = {"full_text": "x" * 101}
        tweet_short = {"full_text": "x" * 100}
        tweet_empty = {"full_text": ""}

        assert LocalThreadExtractor.apply_stage1_filter(extractor, tweet_long) is True
        assert LocalThreadExtractor.apply_stage1_filter(extractor, tweet_short) is False
        assert LocalThreadExtractor.apply_stage1_filter(extractor, tweet_empty) is False

    def test_stage1_filter_handles_missing_text(self):
        """Test stage 1 filter handles missing full_text field."""
        extractor = Mock(spec=LocalThreadExtractor)
        tweet_no_text = {"id_str": "123"}

        assert (
            LocalThreadExtractor.apply_stage1_filter(extractor, tweet_no_text) is False
        )

    def test_stage2_filter_detects_replies(self):
        """Test stage 2 filter detects reply tweets."""
        extractor = Mock(spec=LocalThreadExtractor)

        tweet_reply = {"id_str": "2", "in_reply_to_status_id_str": "1"}
        tweet_not_reply = {"id_str": "3", "in_reply_to_status_id_str": None}

        assert LocalThreadExtractor.apply_stage2_filter(extractor, tweet_reply) is True
        assert (
            LocalThreadExtractor.apply_stage2_filter(extractor, tweet_not_reply) is True
        )  # Has id_str

    def test_process_tweets_integration(self, tmp_path):
        """Test the complete tweet processing pipeline."""
        archive_dir = self._setup_archive_with_tweets(tmp_path)

        extractor = LocalThreadExtractor(archive_dir)
        extractor.process_tweets()

        # Check that filtering worked
        assert len(extractor.filtered_tweets) > 0
        assert len(extractor.tweets_by_id) > 0

        # All filtered tweets should be > 100 chars and part of threads
        for tweet in extractor.filtered_tweets:
            assert len(tweet.get("full_text", "")) > 100

    def _setup_archive_with_tweets(self, tmp_path):
        """Helper to set up archive with sample tweets."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "archive.html").write_text("<html></html>")

        # Create sample tweets with various characteristics
        tweets = [
            {"tweet": {"id_str": "1", "full_text": "x" * 101}},  # Long, no reply
            {
                "tweet": {
                    "id_str": "2",
                    "full_text": "x" * 101,
                    "in_reply_to_status_id_str": "1",
                }
            },  # Reply
            {"tweet": {"id_str": "3", "full_text": "x" * 50}},  # Too short
            {
                "tweet": {
                    "id_str": "4",
                    "full_text": "x" * 101,
                    "in_reply_to_status_id_str": "2",
                }
            },  # Thread
        ]

        tweets_js = "window.YTD.tweets.part0 = " + json.dumps(tweets)
        (archive_dir / "data" / "tweets.js").write_text(tweets_js)

        return archive_dir


class TestThreadReconstruction:
    """Test thread reconstruction functionality."""

    def test_build_thread_from_root(self):
        """Test building a thread from root tweet."""
        extractor = Mock(spec=LocalThreadExtractor)
        extractor.tweets_by_id = {
            "1": {"id_str": "1", "full_text": "Root tweet"},
            "2": {
                "id_str": "2",
                "full_text": "Reply 1",
                "in_reply_to_status_id_str": "1",
            },
            "3": {
                "id_str": "3",
                "full_text": "Reply 2",
                "in_reply_to_status_id_str": "1",
            },
        }
        extractor.reply_map = {"1": ["2", "3"]}

        processed = set()
        thread = LocalThreadExtractor._build_thread(extractor, "1", processed)

        assert len(thread) == 3
        assert thread[0]["id_str"] == "1"
        assert "2" in processed
        assert "3" in processed

    def test_build_partial_thread(self):
        """Test building a partial thread from middle."""
        extractor = Mock(spec=LocalThreadExtractor)
        extractor.tweets_by_id = {
            "2": {
                "id_str": "2",
                "full_text": "Middle",
                "in_reply_to_status_id_str": "1",
            },
            "3": {
                "id_str": "3",
                "full_text": "Reply",
                "in_reply_to_status_id_str": "2",
            },
        }
        extractor.reply_map = {"2": ["3"]}

        processed = set()
        thread = LocalThreadExtractor._build_partial_thread(extractor, "2", processed)

        assert len(thread) == 2
        assert thread[0]["id_str"] == "2"
        assert thread[1]["id_str"] == "3"

    def test_reconstruct_threads_integration(self, tmp_path):
        """Test full thread reconstruction process."""
        archive_dir = self._setup_archive_with_thread(tmp_path)

        extractor = LocalThreadExtractor(archive_dir)
        extractor.process_tweets()
        extractor.reconstruct_threads()

        assert len(extractor.threads) > 0
        # Check threads have at least 2 tweets
        for thread in extractor.threads:
            assert len(thread) >= 2

    def test_thread_sorting_by_date(self):
        """Test that threads are sorted by date."""
        extractor = Mock(spec=LocalThreadExtractor)
        extractor.threads = [
            [{"created_at": "2024-01-03"}],
            [{"created_at": "2024-01-01"}],
            [{"created_at": "2024-01-02"}],
        ]
        extractor.tweets_by_id = {}
        extractor.reply_map = {}

        LocalThreadExtractor.reconstruct_threads(extractor)

        # Should be sorted in reverse chronological order
        dates = [t[0]["created_at"] for t in extractor.threads]
        assert dates == sorted(dates, reverse=True)

    def _setup_archive_with_thread(self, tmp_path):
        """Helper to set up archive with a thread."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "archive.html").write_text("<html></html>")

        # Create a thread
        tweets = [
            {
                "tweet": {
                    "id_str": "1",
                    "full_text": "x" * 101,
                    "created_at": "2024-01-01",
                }
            },
            {
                "tweet": {
                    "id_str": "2",
                    "full_text": "x" * 101,
                    "created_at": "2024-01-02",
                    "in_reply_to_status_id_str": "1",
                }
            },
            {
                "tweet": {
                    "id_str": "3",
                    "full_text": "x" * 101,
                    "created_at": "2024-01-03",
                    "in_reply_to_status_id_str": "2",
                }
            },
        ]

        tweets_js = "window.YTD.tweets.part0 = " + json.dumps(tweets)
        (archive_dir / "data" / "tweets.js").write_text(tweets_js)

        return archive_dir


class TestOutputGeneration:
    """Test JSON and markdown output generation."""

    def test_generate_json_output_structure(self, tmp_path):
        """Test JSON output has correct structure."""
        extractor = Mock(spec=LocalThreadExtractor)
        extractor.filtered_tweets = [{"id_str": "1"}, {"id_str": "2"}]
        extractor.threads = [
            [{"id_str": "1", "full_text": "Tweet 1", "created_at": "2024-01-01"}],
            [{"id_str": "2", "full_text": "Tweet 2", "created_at": "2024-01-02"}],
        ]

        # Create the output directory
        output_dir = tmp_path / "data"
        output_dir.mkdir()
        output_file = output_dir / "filtered_threads.json"

        # Mock Path and open to use tmp_path
        with patch("local_filter_pipeline.Path") as mock_path:
            # Make Path constructor return the actual tmp_path based object when called
            mock_path.side_effect = (
                lambda x: output_file if "filtered_threads" in x else tmp_path / x
            )

            with patch("builtins.open", mock_open()):
                output = LocalThreadExtractor.generate_json_output(extractor)

        assert "metadata" in output
        assert "threads" in output
        assert output["metadata"]["filtered_tweets"] == 2
        assert output["metadata"]["threads_found"] == 2
        assert len(output["threads"]) == 2

        # Check thread structure
        thread = output["threads"][0]
        assert "thread_id" in thread
        assert "tweet_count" in thread
        assert "smushed_text" in thread
        assert "word_count" in thread
        assert "tweet_ids" in thread

    def test_smushed_text_generation(self):
        """Test that text is properly smushed together."""
        extractor = Mock(spec=LocalThreadExtractor)
        thread = [
            {"full_text": "First part"},
            {"full_text": "Second part"},
            {"full_text": "Third part"},
        ]
        extractor.threads = [thread]
        extractor.filtered_tweets = []

        with patch("local_filter_pipeline.Path"), patch("builtins.open", mock_open()):
            output = LocalThreadExtractor.generate_json_output(extractor)

        smushed = output["threads"][0]["smushed_text"]
        assert smushed == "First part Second part Third part"

    def test_generate_sample_markdown(self, tmp_path):
        """Test markdown generation."""
        extractor = Mock(spec=LocalThreadExtractor)
        extractor.threads = [
            [
                {
                    "full_text": "Long tweet " * 20,
                    "created_at": "2024-01-01 12:00:00",
                    "id_str": "1",
                }
            ],
            [
                {
                    "full_text": "Short",
                    "created_at": "2024-01-02 13:00:00",
                    "id_str": "2",
                }
            ],
        ]

        # Create sample directory
        sample_dir = tmp_path / "data" / "sample_threads"
        sample_dir.mkdir(parents=True)

        with patch("local_filter_pipeline.Path") as mock_path:
            # Return the actual directory that exists
            mock_path.side_effect = (
                lambda x: sample_dir if "sample_threads" in x else tmp_path / x
            )

            with patch("builtins.open", mock_open()) as mock_file:
                LocalThreadExtractor.generate_sample_markdown(extractor, sample_count=2)

                # Check that files were created
                assert mock_file.call_count == 2

    def test_markdown_filename_sanitization(self):
        """Test that markdown filenames are properly sanitized."""
        extractor = Mock(spec=LocalThreadExtractor)
        thread = [
            {
                "full_text": "This has special chars!@#$%^&*()",
                "created_at": "2024-01-01 12:00:00",
                "id_str": "1",
            }
        ]
        extractor.threads = [thread]

        with patch("local_filter_pipeline.Path"), patch(
            "builtins.open", mock_open()
        ) as mock_file:
            LocalThreadExtractor.generate_sample_markdown(extractor, sample_count=1)

            # Get the filename used
            call_args = mock_file.call_args_list[0]
            filename = str(call_args[0][0])

            # Should not contain special characters
            assert "!" not in filename
            assert "@" not in filename
            assert "#" not in filename


class TestRunPipeline:
    """Test the complete pipeline execution."""

    def test_run_pipeline_complete_flow(self, tmp_path):
        """Test that run_pipeline executes all steps."""
        archive_dir = self._setup_complete_archive(tmp_path)

        extractor = LocalThreadExtractor(archive_dir)

        # Mock the output directory creation
        with patch("local_filter_pipeline.Path.mkdir"):
            output = extractor.run_pipeline()

        assert output is not None
        assert "metadata" in output
        assert output["metadata"]["filtered_tweets"] > 0
        assert output["metadata"]["threads_found"] > 0

    def test_run_pipeline_statistics(self, tmp_path):
        """Test that pipeline generates correct statistics."""
        archive_dir = self._setup_complete_archive(tmp_path)

        extractor = LocalThreadExtractor(archive_dir)

        # Create the output directory
        output_dir = tmp_path / "data"
        output_dir.mkdir(exist_ok=True)

        # Patch Path to use our tmp_path for output
        with patch("local_filter_pipeline.Path") as mock_path:
            # Configure the mock to handle different paths
            def path_side_effect(path_str):
                if "data/filtered_threads.json" in str(path_str):
                    return output_dir / "filtered_threads.json"
                elif "data/sample_threads" in str(path_str):
                    return output_dir / "sample_threads"
                else:
                    return Path(path_str)

            mock_path.side_effect = path_side_effect
            mock_path.return_value.parent.mkdir.return_value = None

            output = extractor.run_pipeline()

        # Check statistics are calculated
        assert output["metadata"]["total_original_tweets"] == 21723
        assert "processing_date" in output["metadata"]
        assert output["metadata"]["filter_stages"] == ["length>100", "thread_detection"]

    def _setup_complete_archive(self, tmp_path):
        """Helper to set up a complete archive for testing."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "archive.html").write_text("<html></html>")

        # Create a more complete set of tweets
        tweets = []
        for i in range(10):
            tweet = {
                "tweet": {
                    "id_str": str(i),
                    "full_text": f"This is tweet number {i} " + "x" * 100,
                    "created_at": f"2024-01-{i + 1:02d} 12:00:00",
                }
            }
            if i > 0 and i % 2 == 0:
                tweet["tweet"]["in_reply_to_status_id_str"] = str(i - 1)
            tweets.append(tweet)

        tweets_js = "window.YTD.tweets.part0 = " + json.dumps(tweets)
        (archive_dir / "data" / "tweets.js").write_text(tweets_js)

        return archive_dir


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_corrupted_tweets_file(self, tmp_path):
        """Test handling of corrupted tweets.js file."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "archive.html").write_text("<html></html>")

        # Create corrupted file (binary data)
        (archive_dir / "data" / "tweets.js").write_bytes(b"\x00\x01\x02\x03")

        with pytest.raises(ValueError) as exc_info:
            LocalThreadExtractor(archive_dir)
        assert "corrupted or not a text file" in str(exc_info.value)

    def test_empty_thread_handling(self):
        """Test that empty threads are not included."""
        extractor = Mock(spec=LocalThreadExtractor)
        extractor.tweets_by_id = {"1": {"id_str": "1", "full_text": "Single tweet"}}
        extractor.reply_map = {}
        extractor.threads = []
        extractor.filtered_tweets = []

        # Process should not add single tweets as threads
        processed = set()
        thread = LocalThreadExtractor._build_thread(extractor, "1", processed)
        assert len(thread) == 1  # Single tweet

        # But reconstruct_threads should filter it out
        LocalThreadExtractor.reconstruct_threads(extractor)
        # Only threads with 2+ tweets should be added

    def test_missing_fields_handling(self):
        """Test graceful handling of missing tweet fields."""
        extractor = Mock(spec=LocalThreadExtractor)

        # Tweet without id_str
        tweet_no_id = {"full_text": "x" * 101}
        # Tweet without full_text
        tweet_no_text = {"id_str": "1"}

        # Should handle gracefully
        assert LocalThreadExtractor.apply_stage2_filter(extractor, tweet_no_id) is False
        assert (
            LocalThreadExtractor.apply_stage1_filter(extractor, tweet_no_text) is False
        )


class TestPerformance:
    """Test performance-related aspects."""

    def test_memory_efficient_streaming(self, tmp_path, capsys):
        """Test that streaming prints progress for large files."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "data").mkdir()
        (archive_dir / "archive.html").write_text("<html></html>")

        # Create file with 2000 tweets to trigger progress printing
        tweets = [
            {"tweet": {"id_str": str(i), "full_text": f"Tweet {i}"}}
            for i in range(2000)
        ]
        tweets_js = "window.YTD.tweets.part0 = " + json.dumps(tweets)
        (archive_dir / "data" / "tweets.js").write_text(tweets_js)

        extractor = LocalThreadExtractor(archive_dir)
        list(extractor.stream_tweets())

        captured = capsys.readouterr()
        assert "Processed 1000 tweets" in captured.out
        assert "Processed 2000 tweets" in captured.out

    def test_large_thread_handling(self):
        """Test handling of very large threads."""
        extractor = Mock(spec=LocalThreadExtractor)

        # Create a large thread
        large_thread = []
        extractor.tweets_by_id = {}
        extractor.reply_map = {}

        for i in range(100):
            tweet = {"id_str": str(i), "full_text": f"Tweet {i}"}
            if i > 0:
                tweet["in_reply_to_status_id_str"] = str(i - 1)
                extractor.reply_map[str(i - 1)] = [str(i)]
            extractor.tweets_by_id[str(i)] = tweet
            large_thread.append(tweet)

        processed = set()
        thread = LocalThreadExtractor._build_thread(extractor, "0", processed)

        # Should handle large threads
        assert len(thread) == 100
        assert len(processed) == 100


# Test fixtures for integration testing
@pytest.fixture
def complete_archive(tmp_path):
    """Create a complete test archive."""
    archive_dir = tmp_path / "test_archive"
    archive_dir.mkdir()
    (archive_dir / "data").mkdir()
    (archive_dir / "archive.html").write_text("<html><body>Test Archive</body></html>")

    # Create realistic tweet data
    tweets = [
        {
            "tweet": {
                "id_str": "1000",
                "full_text": "This is the start of an interesting thread about Python testing. "
                * 3,
                "created_at": "Wed Nov 15 14:23:45 +0000 2023",
                "user": {"screen_name": "testuser"},
            }
        },
        {
            "tweet": {
                "id_str": "1001",
                "full_text": "Continuing the thread: Test-driven development is crucial for quality. "
                * 3,
                "created_at": "Wed Nov 15 14:25:00 +0000 2023",
                "in_reply_to_status_id_str": "1000",
                "user": {"screen_name": "testuser"},
            }
        },
        {
            "tweet": {
                "id_str": "1002",
                "full_text": "Finally, always write tests first before implementation. "
                * 3,
                "created_at": "Wed Nov 15 14:26:00 +0000 2023",
                "in_reply_to_status_id_str": "1001",
                "user": {"screen_name": "testuser"},
            }
        },
    ]

    tweets_js = "window.YTD.tweets.part0 = " + json.dumps(tweets)
    (archive_dir / "data" / "tweets.js").write_text(tweets_js)

    return archive_dir


def test_integration_complete_flow(complete_archive, tmp_path):
    """Integration test for complete pipeline flow."""
    with patch("local_filter_pipeline.Path") as mock_path:
        # Mock output paths
        mock_path.side_effect = lambda x: tmp_path / x if isinstance(x, str) else x

        extractor = LocalThreadExtractor(complete_archive)
        output = extractor.run_pipeline()

        # Verify complete flow
        assert output["metadata"]["threads_found"] > 0
        assert len(output["threads"]) > 0

        # Check first thread
        thread = output["threads"][0]
        assert thread["tweet_count"] >= 2
        assert "smushed_text" in thread
        assert thread["word_count"] > 0
