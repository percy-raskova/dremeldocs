"""
Shared pytest fixtures and configuration for astradocs tests.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def sample_tweet() -> Dict[str, Any]:
    """Single sample tweet for testing."""
    return {
        "tweet": {
            "id_str": "1234567890",
            "full_text": "This is a sample philosophical tweet about epistemology and the nature of knowledge in modern society.",
            "created_at": "Mon Sep 06 18:07:59 +0000 2024",
            "in_reply_to_status_id_str": None,
            "entities": {
                "urls": [],
                "hashtags": [],
                "user_mentions": []
            }
        }
    }


@pytest.fixture
def sample_thread_tweets() -> List[Dict[str, Any]]:
    """Sample thread of connected tweets."""
    return [
        {
            "tweet": {
                "id_str": "1000000001",
                "full_text": "Thread about political economy and class analysis. This is part 1/5 discussing the relationship between labor and capital.",
                "created_at": "Fri Sep 06 18:00:00 +0000 2024",
                "in_reply_to_status_id_str": None,
            }
        },
        {
            "tweet": {
                "id_str": "1000000002",
                "full_text": "Part 2/5: The extraction of surplus value happens through the difference between labor power and labor time.",
                "created_at": "Fri Sep 06 18:01:00 +0000 2024",
                "in_reply_to_status_id_str": "1000000001",
            }
        },
        {
            "tweet": {
                "id_str": "1000000003",
                "full_text": "Part 3/5: This creates a fundamental antagonism between the interests of workers and capital owners.",
                "created_at": "Fri Sep 06 18:02:00 +0000 2024",
                "in_reply_to_status_id_str": "1000000002",
            }
        },
    ]


@pytest.fixture
def sample_heavy_thread() -> Dict[str, Any]:
    """Sample thread data with 500+ words for heavy hitter testing."""
    long_text = " ".join([
        f"Sentence {i} discussing philosophical concepts, political theory, and social analysis."
        for i in range(75)  # ~750 words
    ])

    return {
        "thread_id": "thread_1000",
        "tweet_ids": ["1000000001", "1000000002", "1000000003"],
        "first_tweet_date": "Fri Sep 06 18:00:00 +0000 2024",
        "smushed_text": long_text,
        "word_count": len(long_text.split()),
        "tweet_count": 3
    }


@pytest.fixture
def sample_filtered_data() -> Dict[str, Any]:
    """Sample output from local_filter_pipeline."""
    return {
        "metadata": {
            "total_tweets": 21723,
            "filtered_tweets": 10396,
            "threads_found": 1363,
            "processing_date": "2024-09-21"
        },
        "threads": [
            {
                "thread_id": "thread_0001",
                "tweet_ids": ["1234567890"],
                "first_tweet_date": "Mon Sep 06 18:07:59 +0000 2024",
                "smushed_text": "A philosophical thread about consciousness.",
                "word_count": 150,
                "tweet_count": 1
            },
            {
                "thread_id": "thread_0002",
                "tweet_ids": ["1000000001", "1000000002"],
                "first_tweet_date": "Fri Sep 06 18:00:00 +0000 2024",
                "smushed_text": "Political analysis of current events and their historical context.",
                "word_count": 600,
                "tweet_count": 2
            }
        ]
    }


@pytest.fixture
def sample_themes() -> Dict[str, Any]:
    """Sample theme extraction data."""
    return {
        "philosophical": {
            "epistemology": ["knowledge", "truth", "belief"],
            "ontology": ["being", "existence", "reality"],
            "ethics": ["moral", "ought", "virtue"]
        },
        "political": {
            "marxism": ["class", "capital", "labor", "surplus value"],
            "anarchism": ["hierarchy", "autonomy", "mutual aid"],
            "liberalism": ["individual", "rights", "democracy"]
        }
    }


@pytest.fixture
def temp_source_dir(tmp_path: Path) -> Path:
    """Create temporary source directory with mock Twitter data."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    data_dir = source_dir / "data"
    data_dir.mkdir()

    # Create mock tweets.js file
    tweets_file = data_dir / "tweets.js"
    tweets_data = """window.YTD.tweets.part0 = [
        {
            "tweet": {
                "id_str": "1234567890",
                "full_text": "Test tweet content that is definitely longer than one hundred characters to pass our filtering requirements.",
                "created_at": "Mon Sep 06 18:07:59 +0000 2024"
            }
        }
    ];"""
    tweets_file.write_text(tweets_data)

    return source_dir


@pytest.fixture
def temp_work_dir(tmp_path: Path) -> Path:
    """Create temporary work directory for outputs."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()

    for subdir in ["filtered", "samples", "heavy_hitters"]:
        (work_dir / subdir).mkdir()

    return work_dir


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent test results."""
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2024, 9, 21, 12, 0, 0)
        mock_dt.strptime = datetime.strptime
        yield mock_dt


@pytest.fixture
def mock_file_operations():
    """Mock file I/O operations."""
    with patch('builtins.open', create=True) as mock_open:
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.mkdir'):
                yield mock_open