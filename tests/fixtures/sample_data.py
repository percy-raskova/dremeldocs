"""
Test fixtures containing sample Twitter archive data for testing the processing pipeline.
"""

import json
from datetime import datetime
from typing import Dict, List, Any

# Sample thread data for testing
SAMPLE_THREAD_DATA = {
    "thread_id": "thread_test_001",
    "word_count": 756,
    "tweet_count": 18,
    "first_tweet_date": "Wed Nov 15 14:23:45 +0000 2023",
    "smushed_text": """The fundamental misunderstanding of dialectical materialism stems from treating it as a rigid formula rather than a dynamic analytical framework. Many people approach Marx's method as if it were a mechanical process where you input social conditions and output predetermined revolutionary outcomes. This mechanistic interpretation completely misses the point of dialectical thinking. Dialectical materialism isn't about applying fixed rules to social phenomena. It's about understanding how contradictions within systems create the conditions for their own transformation. The dialectical process is inherently dynamic - it's about movement, change, and the resolution of contradictions through struggle. When we examine capitalism through this lens, we're not looking for simple cause-and-effect relationships. We're analyzing how the internal contradictions of the capitalist system - particularly the contradiction between social production and private appropriation - create instabilities that point toward different forms of economic organization. The genius of Marx's approach is that it doesn't impose external solutions on social problems. Instead, it reveals how solutions emerge from within the contradictions themselves. This is why Marx could identify the proletariat as the revolutionary class - not because of moral superiority, but because of their structural position within capitalist relations. The working class embodies the fundamental contradiction of capitalism: they create all value but are systematically excluded from controlling the means of production or the products of their labor.""",
    "tweet_ids": [
        "1724780432156789123",
        "1724780434158901234",
        "1724780436160123456",
        "1724780438162234567",
        "1724780440164345678",
        "1724780442166456789",
        "1724780444168567890",
        "1724780446170678901",
        "1724780448172789012",
        "1724780450174890123",
        "1724780452176901234",
        "1724780454179012345",
        "1724780456181123456",
        "1724780458183234567",
        "1724780460185345678",
        "1724780462187456789",
        "1724780464189567890",
        "1724780466191678901"
    ]
}

# Sample thread with shorter content for boundary testing
SAMPLE_SHORT_THREAD_DATA = {
    "thread_id": "thread_test_002",
    "word_count": 45,
    "tweet_count": 3,
    "first_tweet_date": "Thu Dec 07 09:15:30 +0000 2023",
    "smushed_text": "This is a short thread for testing edge cases. It contains minimal content across just a few tweets. Testing boundaries is important.",
    "tweet_ids": [
        "1733058932123456789",
        "1733058934125567890",
        "1733058936127678901"
    ]
}

# Sample thread with special characters and formatting challenges
SAMPLE_COMPLEX_THREAD_DATA = {
    "thread_id": "thread_test_003",
    "word_count": 523,
    "tweet_count": 12,
    "first_tweet_date": "Mon Jan 22 16:47:12 +0000 2024",
    "smushed_text": """Palestine: A Case Study in "Settler Colonialism" & Imperial Logic. The Israeli state's relationship to Palestinian territory exemplifies what scholars call "settler colonialism" - a distinct form of colonialism where the colonizing population seeks to permanently replace the indigenous population rather than simply exploit their labor. This isn't just academic terminology; it's a framework that helps us understand the systematic nature of Palestinian dispossession. Unlike traditional colonialism (which extracts wealth while maintaining indigenous populations as a labor force), settler colonialism aims for what Patrick Wolfe called "the elimination of the native." This elimination can take many forms: physical removal, cultural destruction, legal erasure, or demographic replacement. In Palestine, we see all of these strategies deployed systematically since 1948. The key insight is that settler colonialism isn't an event - it's an ongoing structure. Every settlement expansion, every home demolition, every restriction on Palestinian movement serves the same fundamental goal: making Palestinian presence impossible while normalizing Israeli control. Understanding this helps explain why "peace processes" that don't address the structural relationship between Israelis and Palestinians consistently fail. You can't resolve a colonial relationship through negotiations that assume equal standing between colonizer and colonized.""",
    "tweet_ids": [
        "1749472832987654321",
        "1749472834989765432",
        "1749472836991876543",
        "1749472838993987654",
        "1749472840996098765",
        "1749472842998209876",
        "1749472845000320987",
        "1749472847002431098",
        "1749472849004542109",
        "1749472851006653210",
        "1749472853008764321",
        "1749472855010875432"
    ]
}

# Sample filtered threads data (simulating output from local_filter_pipeline.py)
SAMPLE_FILTERED_THREADS = {
    "metadata": {
        "total_tweets": 21723,
        "filtered_threads": 3,
        "filter_criteria": {
            "min_word_count": 40,
            "min_tweet_count": 3
        },
        "extracted_at": "2025-09-22T10:00:00Z"
    },
    "threads": [
        SAMPLE_THREAD_DATA,
        SAMPLE_SHORT_THREAD_DATA,
        SAMPLE_COMPLEX_THREAD_DATA
    ]
}

# Expected frontmatter for the main sample thread
EXPECTED_FRONTMATTER = {
    "title": "The fundamental misunderstanding of dialectical materialism",
    "date": {
        "created": "2023-11-15"
    },
    "categories": ["heavy_hitters"],
    "thread_id": "thread_test_001",
    "word_count": 756,
    "reading_time": 4,
    "description": "An analysis of dialectical materialism as a dynamic analytical framework rather than rigid formula, examining contradictions within capitalist systems.",
    "tweet_count": 18,
    "heavy_hitter": True,
    "thread_number": 1,
    "author": "@BmoreOrganized"
}

# Test cases for date parsing
DATE_PARSING_CASES = [
    ("Wed Nov 15 14:23:45 +0000 2023", "20231115"),
    ("Thu Dec 07 09:15:30 +0000 2023", "20231207"),
    ("Mon Jan 22 16:47:12 +0000 2024", "20240122"),
    ("Sat Apr 26 15:30:45 +0000 2025", "20250426"),
    ("Fri Sep 06 18:07:59 +0000 2024", "20240906")
]

# Test cases for filename generation
FILENAME_GENERATION_CASES = [
    (1, "Wed Nov 15 14:23:45 +0000 2023", "The fundamental misunderstanding of dialectical materialism", "001-20231115-The_fundamental_misunderstanding_of_dialectical.md"),
    (59, "Fri Sep 06 18:07:59 +0000 2024", "I have been asked by multiple comrades to comment", "059-20240906-I_have_been_asked_by_multiple_comrades_to_comment.md"),
    (100, "Mon Jan 22 16:47:12 +0000 2024", "Palestine: A Case Study in Settler Colonialism", "100-20240122-Palestine_A_Case_Study_in_Settler_Colonialism.md")
]

# Test cases for text processing edge cases
TEXT_PROCESSING_EDGE_CASES = [
    ("", ""),  # Empty text
    ("Single word.", "Single word"),  # Single word
    ("A very long title that exceeds the maximum length limit and should be truncated properly at word boundaries", "A very long title that exceeds the maximum length"),  # Long title
    ("Text with @mentions and #hashtags and URLs https://example.com", "Text with mentions and hashtags and URLs"),  # Social media artifacts
    ("Text with\nnewlines\nand\ttabs", "Text with newlines and tabs"),  # Whitespace normalization
    ("Text with LOTS of CAPS and exclamation points!!!", "Text with LOTS of CAPS and exclamation points"),  # Aggressive formatting
]

# Test cases for YAML frontmatter escaping
YAML_ESCAPING_CASES = [
    ('Simple title', '"Simple title"'),
    ('Title with "quotes"', "\"Title with 'quotes'\""),  # Now replaces inner double quotes with single
    ("Title with 'apostrophes'", "\"Title with 'apostrophes'\""),
    ('Title with: colons', '"Title with: colons"'),
    ('Title with [brackets]', '"Title with [brackets]"'),
    ('Title with {braces}', '"Title with {braces}"'),
    ('Title with | pipes', '"Title with | pipes"'),
    ('Title with > symbols', '"Title with > symbols"'),
]

def get_sample_thread(thread_id: str = "thread_test_001") -> Dict[str, Any]:
    """Get a sample thread by ID for testing."""
    thread_map = {
        "thread_test_001": SAMPLE_THREAD_DATA,
        "thread_test_002": SAMPLE_SHORT_THREAD_DATA,
        "thread_test_003": SAMPLE_COMPLEX_THREAD_DATA
    }
    return thread_map.get(thread_id, SAMPLE_THREAD_DATA)

def get_sample_filtered_data() -> Dict[str, Any]:
    """Get sample filtered threads data."""
    return SAMPLE_FILTERED_THREADS.copy()

def create_mock_twitter_data(num_threads: int = 3) -> List[Dict[str, Any]]:
    """Create mock Twitter data for testing pipeline integration."""
    threads = []
    base_date = datetime(2023, 11, 15)

    for i in range(num_threads):
        # Vary the date safely by adding days
        from datetime import timedelta
        date_obj = base_date + timedelta(days=i)
        date_str = date_obj.strftime("%a %b %d %H:%M:%S +0000 %Y")

        thread = {
            "thread_id": f"thread_test_{i+1:03d}",
            "word_count": 500 + (i * 100),  # Ensure all are heavy hitters
            "tweet_count": 10 + (i * 5),
            "first_tweet_date": date_str,
            "smushed_text": f"This is test thread number {i+1}. " * (50 + i * 10),  # Variable length
            "tweet_ids": [f"1724780{j:06d}{i:03d}" for j in range(10 + i * 5)]
        }
        threads.append(thread)

    return threads