#!/usr/bin/env python3
"""
Markdown generation module for theme classification
Handles generating markdown files with frontmatter and clearing existing content
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

try:
    from . import security_utils
    from .text_utilities import (
        calculate_reading_time,
        extract_entities,
        format_frontmatter_value,
        generate_description,
        generate_filename,
        generate_title,
    )
except ImportError:
    # Support direct imports when not run as package
    import security_utils
    from text_utilities import (
        calculate_reading_time,
        extract_entities,
        format_frontmatter_value,
        generate_description,
        generate_filename,
        generate_title,
    )


class MarkdownGenerator:
    """Handles markdown file generation and management"""

    def clear_all_markdown(self) -> int:
        """Clear all existing markdown files from all category directories.

        This prevents duplicates when regenerating content.
        Preserves directory structure but removes all .md files.
        """
        markdown_dir = Path("markdown")
        total_removed = 0

        # List of directories that may contain generated content
        theme_dirs = [
            "both",
            "philosophical",
            "political",
            "uncertain",
            "other",
            "philosophy",
            "politics",  # Old structure
            "marxism_historical materialism",
            "political economy",
            "dialectics",
            "imperialism_colonialism",
            "organizational theory",
            "fascism analysis",
            "cultural criticism",
            "covid_public health politics",
            "intersectional",
        ]

        print("\n🗑️  Clearing existing markdown files to prevent duplicates...")

        for dir_name in theme_dirs:
            dir_path = markdown_dir / dir_name
            if dir_path.exists():
                md_files = list(dir_path.glob("*.md"))
                if md_files:
                    print(f"  - Removing {len(md_files)} files from {dir_name}/")
                    for file in md_files:
                        file.unlink()
                    total_removed += len(md_files)

        # Don't remove index.md and other root-level files
        print(f"  ✅ Removed {total_removed} markdown files total")
        print("  ℹ️  Preserved index.md and other configuration files")
        return total_removed

    def generate_final_markdown(
        self,
        category: str = "both",
        limit: Optional[int] = None,
        clear_existing: bool = True,
    ) -> None:
        """Generate markdown files for classified threads with proper frontmatter.

        Args:
            category: Thread category to generate
            limit: Maximum number of threads to generate
            clear_existing: Whether to clear existing markdown files before generation
        """
        print(f"\n📝 Generating markdown for '{category}' threads with frontmatter...")

        with security_utils.safe_open("data/classified_threads.json", encoding="utf-8") as f:
            data = json.load(f)

        threads = data["threads_by_category"].get(category, [])

        if limit:
            threads = threads[:limit]

        output_dir = Path(f"markdown/{category}")

        # Clear existing markdown files if requested
        if clear_existing and output_dir.exists():
            existing_files = list(output_dir.glob("*.md"))
            if existing_files:
                print(
                    f"  🗑️  Clearing {len(existing_files)} existing markdown files in {output_dir}"
                )
                for file in existing_files:
                    file.unlink()

        output_dir.mkdir(parents=True, exist_ok=True)

        for i, thread in enumerate(threads):
            # Generate clean filename using standardized format
            filename = generate_filename(
                i + 1, thread["first_tweet_date"], thread["smushed_text"]
            )

            # Generate title and description using SpaCy-enhanced functions
            title = generate_title(thread["smushed_text"])
            description = generate_description(thread["smushed_text"])
            reading_time = calculate_reading_time(
                thread["smushed_text"]
            )  # Now uses actual text for accurate count

            # Extract entities for potential tags
            entities = extract_entities(thread["smushed_text"])

            # Format date properly - handle Twitter's date format
            try:
                # Twitter format: "Wed Oct 26 12:50:18 +0000 2022"
                created_date = datetime.strptime(
                    thread["first_tweet_date"], "%a %b %d %H:%M:%S %z %Y"
                )
                date_str = created_date.strftime("%Y-%m-%d")
            except Exception as e:
                print(
                    f"Warning: Could not parse date '{thread['first_tweet_date']}': {e}"
                )
                date_str = "2025-01-01"  # Default date if parsing fails

            # Build frontmatter
            frontmatter_lines = [
                "---",
                f"title: {format_frontmatter_value(title)}",
                "date:",
                f"  created: {date_str}",
                f"categories: {format_frontmatter_value([category])}",
                f"thread_id: {format_frontmatter_value(thread['thread_id'])}",
                f"word_count: {thread['word_count']}",
                f"reading_time: {reading_time}",
                f"description: {format_frontmatter_value(description)}",
            ]

            # Add themes as tags if available
            if thread.get("themes"):
                frontmatter_lines.append(
                    f"tags: {format_frontmatter_value(thread['themes'])}"
                )

            # Add extracted entities as additional metadata
            if entities:
                frontmatter_lines.append(
                    f"entities: {format_frontmatter_value(entities)}"
                )

            # Add confidence score as custom metadata
            if thread.get("confidence"):
                frontmatter_lines.append(
                    f"confidence_score: {thread['confidence']:.2f}"
                )

            frontmatter_lines.append(f"tweet_count: {thread['tweet_count']}")
            frontmatter_lines.append('author: "@BmoreOrganized"')
            frontmatter_lines.append("---")
            frontmatter_lines.append("")  # Empty line after frontmatter

            # Create main content
            content_lines = [
                f"# {title}",
                "",
                thread["smushed_text"],
                "",
                "---",
                "",
                f"*Thread ID: {thread['thread_id']}*",
            ]

            # Combine frontmatter and content
            full_content = "\n".join(frontmatter_lines) + "\n".join(content_lines)

            filepath = output_dir / filename
            with security_utils.safe_open(filepath, "w", encoding="utf-8") as f:
                f.write(full_content)

        print(
            f"✅ Generated {len(threads)} markdown files with frontmatter in {output_dir}"
        )