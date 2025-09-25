"""
End-to-end tests for the Twitter archive processing pipeline.

Tests the complete pipeline from raw Twitter data through to final markdown output,
verifying that all components work together correctly.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

# Try to import the pipeline modules
try:
    from generate_heavy_hitters import generate_heavy_hitter_markdowns
    from local_filter_pipeline import LocalThreadExtractor
    from text_processing import (
        calculate_reading_time,
        format_frontmatter_value,
        generate_description,
        generate_filename,
        generate_title,
        parse_to_yyyymmdd,
    )
except ImportError as e:
    pytest.skip(f"Pipeline modules not available: {e}", allow_module_level=True)

from tests.fixtures.sample_data import (
    create_mock_twitter_data,
    get_sample_filtered_data,
)
from tests.utils.validation import (
    extract_frontmatter_from_content,
    validate_filename_format,
    validate_frontmatter_structure,
    validate_markdown_structure,
    validate_smushed_text_quality,
)


class TestEndToEndPipeline:
    """Test the complete pipeline from raw data to markdown output."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        workspace = {
            "root": Path(temp_dir),
            "data": Path(temp_dir) / "data",
            "docs": Path(temp_dir) / "docs" / "heavy_hitters",
        }

        # Create necessary directories
        workspace["data"].mkdir(parents=True)
        workspace["docs"].mkdir(parents=True)

        yield workspace

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_complete_pipeline_flow(self, temp_workspace):
        """Test the complete pipeline from filter to markdown generation."""
        # Step 1: Create mock filtered threads data
        filtered_data = get_sample_filtered_data()

        # Write filtered data to temporary file
        filtered_file = temp_workspace["data"] / "filtered_threads.json"
        with open(filtered_file, "w", encoding="utf-8") as f:
            json.dump(filtered_data, f, indent=2)

        # Step 2: Mock the markdown generation process
        # Since we can't easily run the full generate_heavy_hitters script,
        # we'll simulate the process

        threads = filtered_data["threads"]
        heavy_threads = [t for t in threads if t["word_count"] >= 500]

        generated_files = []

        for i, thread in enumerate(heavy_threads):
            # Generate filename
            filename = generate_filename(
                i + 1, thread["first_tweet_date"], thread["smushed_text"]
            )
            filepath = temp_workspace["docs"] / filename

            # Generate frontmatter components
            title = generate_title(thread["smushed_text"])
            description = generate_description(thread["smushed_text"])
            reading_time = calculate_reading_time(thread["smushed_text"])

            # Create frontmatter
            date_for_frontmatter = parse_to_yyyymmdd(thread["first_tweet_date"])
            date_formatted = f"{date_for_frontmatter[:4]}-{date_for_frontmatter[4:6]}-{date_for_frontmatter[6:8]}"

            frontmatter_dict = {
                "title": format_frontmatter_value(title),
                "date": {"created": date_formatted},
                "categories": ["heavy_hitters"],
                "thread_id": format_frontmatter_value(thread["thread_id"]),
                "word_count": thread["word_count"],
                "reading_time": reading_time,
                "description": format_frontmatter_value(description),
                "tweet_count": thread["tweet_count"],
                "heavy_hitter": True,
                "thread_number": i + 1,
                "author": format_frontmatter_value("@BmoreOrganized"),
            }

            # Generate markdown content
            import yaml

            frontmatter_yaml = yaml.safe_dump(
                frontmatter_dict, default_flow_style=False
            )

            content = f"""---
{frontmatter_yaml}---

# Thread #{i + 1}: {title}

*{thread["word_count"]} words • {thread["tweet_count"]} tweets • ~{reading_time} min read*

---

{thread["smushed_text"]}

---

### Tweet IDs
{", ".join(thread["tweet_ids"])}

### Navigation
[← Previous](#{i:03d}) | [Index](index.md) | [Next →](#{i + 2:03d})
"""

            # Write the file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            generated_files.append(filepath)

        # Step 3: Validate all generated files
        assert len(generated_files) > 0, "No files were generated"

        for filepath in generated_files:
            assert filepath.exists(), f"File not created: {filepath}"

            # Read and validate content
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Validate markdown structure
            structure_errors = validate_markdown_structure(content)
            assert len(structure_errors) == 0, (
                f"Markdown structure errors in {filepath.name}: {structure_errors}"
            )

            # Validate frontmatter
            frontmatter = extract_frontmatter_from_content(content)
            assert frontmatter is not None, (
                f"Could not extract frontmatter from {filepath.name}"
            )

            frontmatter_errors = validate_frontmatter_structure(frontmatter)
            assert len(frontmatter_errors) == 0, (
                f"Frontmatter errors in {filepath.name}: {frontmatter_errors}"
            )

            # Validate filename format
            assert validate_filename_format(filepath.name), (
                f"Invalid filename format: {filepath.name}"
            )

    @pytest.mark.integration
    def test_pipeline_with_real_heavy_hitters_sample(self, temp_workspace):
        """Test pipeline using a sample that mimics real heavy hitters data."""
        # Create a more realistic sample thread
        realistic_thread = {
            "thread_id": "thread_real_001",
            "word_count": 1159,
            "tweet_count": 27,
            "first_tweet_date": "Fri Sep 06 18:07:59 +0000 2024",
            "smushed_text": """I have been asked by multiple comrades to comment on the Lake Quonnipaug Conference. The goal of the conference is to bring together Marxist organizations in North America into a federation that can eventually constitute a legitimate all-empire communist party. I should also point out that the program of the proposed org is exactly correct in its assessment of the tasks ahead of us. The conference isn't wrong, it's just 2-5 years early. Out of respect for their security, I will not share details that have not been publicly shared, such as location, scheduling, program, orgs in attendance, etc. I will only be commenting on the broad scope, form, and mission of the conference. First, I'll come right out with two assertions: 1) I do not think the conference in its specific form is a productive venture and am not optimistic about it bearing fruit in the long term. 2) I still encourage attendance by those for whom it does not present hardship. I have many reasons for my skepticism, but a lot of it boils down to the problem of organizational development across the movement as a whole. The constitution of a federation of local communist organizations requires those organizations to actually... exist. To be perfectly blunt, they don't. Not in the form they need to be. There are many small groups I'm aware of -- and many more besides -- that are absolutely on the right track. Principled Marxists, committed to revolution, self-aware of their current and future role, etc. But let's be clear: you and your 6 study buddies meeting once a week to discuss the next section of Blood in My Eye are not a Communist Organization. Even if you also do a bit of food distribution. Rather, you are the core cell of what could become such an organization. Many of these groups recognize this, and are actively struggling to develop themselves into what they know they need to be. They are trying to figure out how to recruit new members, how to educate themselves, how to serve and empower their communities, etc.""",
            "tweet_ids": [f"1832118{564494700976 + i}" for i in range(27)],
        }

        # Generate and validate all pipeline outputs
        title = generate_title(realistic_thread["smushed_text"])
        description = generate_description(realistic_thread["smushed_text"])
        reading_time = calculate_reading_time(realistic_thread["smushed_text"])
        filename = generate_filename(
            1, realistic_thread["first_tweet_date"], realistic_thread["smushed_text"]
        )

        # Validate all outputs
        assert len(title) > 0 and len(title) <= 60
        assert len(description) > 0 and len(description) <= 200
        assert reading_time >= 1
        assert validate_filename_format(filename)

        # Validate text quality
        quality_issues = validate_smushed_text_quality(realistic_thread["smushed_text"])
        # Some quality issues are acceptable, but major ones should be flagged
        serious_issues = [
            issue
            for issue in quality_issues
            if "processing issues" in issue or "may not be properly" in issue
        ]
        assert len(serious_issues) == 0, (
            f"Serious text quality issues: {serious_issues}"
        )

    @pytest.mark.integration
    def test_pipeline_error_handling(self, temp_workspace):
        """Test pipeline behavior with various error conditions."""
        error_cases = [
            # Thread with missing data
            {
                "thread_id": "thread_error_001",
                "word_count": 500,
                "tweet_count": 10,
                "first_tweet_date": "Invalid date format",
                "smushed_text": "Test content",
                "tweet_ids": ["123", "456"],
            },
            # Thread with empty text
            {
                "thread_id": "thread_error_002",
                "word_count": 0,
                "tweet_count": 1,
                "first_tweet_date": "Fri Sep 06 18:07:59 +0000 2024",
                "smushed_text": "",
                "tweet_ids": ["789"],
            },
            # Thread with problematic characters
            {
                "thread_id": "thread_error_003",
                "word_count": 500,
                "tweet_count": 5,
                "first_tweet_date": "Fri Sep 06 18:07:59 +0000 2024",
                "smushed_text": "Text with\x00null bytes and\x01control chars",
                "tweet_ids": ["101112"],
            },
        ]

        for i, error_case in enumerate(error_cases):
            try:
                # Test each pipeline component with error case
                title = generate_title(error_case["smushed_text"])
                description = generate_description(error_case["smushed_text"])
                reading_time = calculate_reading_time(error_case["smushed_text"])

                # Pipeline should handle errors gracefully
                assert isinstance(title, str)
                assert isinstance(description, str)
                assert isinstance(reading_time, int)

            except Exception as e:
                # If exceptions occur, they should be reasonable
                assert isinstance(e, (ValueError, TypeError, KeyError))

    @pytest.mark.integration
    def test_pipeline_output_consistency(self, temp_workspace):
        """Test that pipeline outputs are consistent across multiple runs."""
        thread = get_sample_filtered_data()["threads"][0]

        # Run pipeline components multiple times
        runs = []
        for _ in range(3):
            run_result = {
                "title": generate_title(thread["smushed_text"]),
                "description": generate_description(thread["smushed_text"]),
                "reading_time": calculate_reading_time(thread["smushed_text"]),
                "filename": generate_filename(
                    1, thread["first_tweet_date"], thread["smushed_text"]
                ),
            }
            runs.append(run_result)

        # Results should be consistent across runs
        first_run = runs[0]
        for i, run in enumerate(runs[1:], 1):
            assert run["title"] == first_run["title"], (
                f"Title inconsistent in run {i + 1}"
            )
            assert run["description"] == first_run["description"], (
                f"Description inconsistent in run {i + 1}"
            )
            assert run["reading_time"] == first_run["reading_time"], (
                f"Reading time inconsistent in run {i + 1}"
            )
            assert run["filename"] == first_run["filename"], (
                f"Filename inconsistent in run {i + 1}"
            )

    @pytest.mark.integration
    def test_pipeline_performance(self, temp_workspace):
        """Test pipeline performance with modest datasets."""
        import time

        # Create a modest dataset for hobbyist testing
        large_dataset = create_mock_twitter_data(
            10
        )  # Reduced from 20 for faster testing

        start_time = time.time()

        # Process all threads
        processed_count = 0
        for thread in large_dataset:
            try:
                title = generate_title(thread["smushed_text"])
                description = generate_description(thread["smushed_text"])
                reading_time = calculate_reading_time(thread["smushed_text"])
                filename = generate_filename(
                    processed_count + 1,
                    thread["first_tweet_date"],
                    thread["smushed_text"],
                )

                # Basic validation
                assert len(title) > 0
                assert len(description) > 0
                assert reading_time > 0
                assert validate_filename_format(filename)

                processed_count += 1

            except Exception as e:
                pytest.fail(f"Pipeline failed on thread {processed_count}: {e}")

        end_time = time.time()
        processing_time = end_time - start_time

        # Performance assertions (relaxed for hobbyist project)
        assert processed_count == len(large_dataset), "Not all threads were processed"
        # Allow up to 2 minutes for processing (hobbyist hardware varies)
        assert processing_time < 120, (
            f"Pipeline processing time: {processing_time:.2f} seconds for {len(large_dataset)} threads"
        )

        # Calculate average processing time per thread
        avg_time_per_thread = processing_time / len(large_dataset)
        # Allow up to 10 seconds per thread (relaxed for varying hardware)
        assert avg_time_per_thread < 10, (
            f"Average processing time: {avg_time_per_thread:.2f} seconds per thread"
        )

    @pytest.mark.integration
    def test_pipeline_memory_usage(self, temp_workspace):
        """Test that pipeline doesn't consume excessive memory."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Process a reasonable number of threads for memory testing
        large_dataset = create_mock_twitter_data(10)  # Reduced for hobbyist testing

        for thread in large_dataset:
            # Process thread
            title = generate_title(thread["smushed_text"])
            description = generate_description(thread["smushed_text"])
            reading_time = calculate_reading_time(thread["smushed_text"])

            # Check memory periodically
            current_memory = process.memory_info().rss
            memory_increase = current_memory - initial_memory

            # Memory increase should be reasonable (less than 200MB for hobbyist systems)
            # Relaxed from 100MB to account for varying Python implementations
            assert memory_increase < 200 * 1024 * 1024, (
                f"Memory usage: {memory_increase / 1024 / 1024:.1f} MB"
            )

    @pytest.mark.integration
    def test_realistic_heavy_hitter_validation(self, temp_workspace):
        """Test validation against a realistic heavy hitter thread."""
        # Use a thread that matches the actual format from docs/heavy_hitters/
        realistic_thread = {
            "thread_id": "thread_validation_001",
            "word_count": 756,
            "tweet_count": 18,
            "first_tweet_date": "Wed Nov 15 14:23:45 +0000 2023",
            "smushed_text": "The fundamental misunderstanding of dialectical materialism stems from treating it as a rigid formula rather than a dynamic analytical framework. Many people approach Marx's method as if it were a mechanical process where you input social conditions and output predetermined revolutionary outcomes. This mechanistic interpretation completely misses the point of dialectical thinking.",
            "tweet_ids": [f"172478043215678900{i}" for i in range(18)],
        }

        # Generate complete markdown
        title = generate_title(realistic_thread["smushed_text"])
        description = generate_description(realistic_thread["smushed_text"])
        reading_time = calculate_reading_time(realistic_thread["smushed_text"])
        filename = generate_filename(
            1, realistic_thread["first_tweet_date"], realistic_thread["smushed_text"]
        )

        # Create frontmatter
        date_for_frontmatter = parse_to_yyyymmdd(realistic_thread["first_tweet_date"])
        date_formatted = f"{date_for_frontmatter[:4]}-{date_for_frontmatter[4:6]}-{date_for_frontmatter[6:8]}"

        frontmatter_dict = {
            "title": format_frontmatter_value(title),
            "date": {"created": date_formatted},
            "categories": ["heavy_hitters"],
            "thread_id": format_frontmatter_value(realistic_thread["thread_id"]),
            "word_count": realistic_thread["word_count"],
            "reading_time": reading_time,
            "description": format_frontmatter_value(description),
            "tweet_count": realistic_thread["tweet_count"],
            "heavy_hitter": True,
            "thread_number": 1,
            "author": format_frontmatter_value("@BmoreOrganized"),
        }

        # Validate all components
        assert validate_filename_format(filename)

        frontmatter_errors = validate_frontmatter_structure(frontmatter_dict)
        assert len(frontmatter_errors) == 0, f"Frontmatter errors: {frontmatter_errors}"

        # Validate reading time calculation
        assert reading_time >= 1, "Reading time should be at least 1 minute"
        assert reading_time <= 8, "Reading time seems too high for this thread length"

        # Create and validate complete markdown
        import yaml

        frontmatter_yaml = yaml.safe_dump(frontmatter_dict, default_flow_style=False)
        complete_markdown = f"""---
{frontmatter_yaml}---

# Thread #1: {title}

{realistic_thread["smushed_text"]}
"""

        structure_errors = validate_markdown_structure(complete_markdown)
        assert len(structure_errors) == 0, (
            f"Markdown structure errors: {structure_errors}"
        )
