#!/usr/bin/env python3
"""
Generate markdown organized by specific themes instead of broad categories
Uses the NLP-extracted themes for meaningful organization
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

try:
    from . import security_utils
except ImportError:
    # Support direct imports when not run as package
    import security_utils

# Theme name to directory mapping (short, clean names)
THEME_DIR_MAPPING = {
    "marxism_historical materialism": "marxism",
    "marxism_historical_materialism": "marxism",
    "political economy": "economy",
    "political_economy": "economy",
    "organizational theory": "organizing",
    "organizational_theory": "organizing",
    "covid_public health politics": "covid",
    "covid_public_health_politics": "covid",
    "fascism analysis": "fascism",
    "fascism_analysis": "fascism",
    "cultural criticism": "culture",
    "cultural_criticism": "culture",
    "imperialism_colonialism": "imperialism",
    "dialectics": "dialectics",
    "uncategorized": "uncategorized"
}

def get_clean_dir_name(theme: str) -> str:
    """Get the clean, short directory name for a theme"""
    return THEME_DIR_MAPPING.get(theme, theme.replace(" ", "_").lower())


def organize_by_themes() -> Dict[str, List[Any]]:
    """Reorganize threads by their specific themes"""

    with security_utils.safe_open("data/classified_threads.json") as f:
        data = json.load(f)

    # Create new organization by specific themes
    threads_by_theme = defaultdict(list)

    # Collect all threads from all categories
    all_threads = []
    for category_threads in data["threads_by_category"].values():
        all_threads.extend(category_threads)

    # Reorganize by actual themes
    for thread in all_threads:
        themes = thread.get("themes", [])

        if themes:
            # Primary theme is first or most relevant
            primary_theme = themes[0] if themes else "uncategorized"
            threads_by_theme[primary_theme].append(thread)
        else:
            threads_by_theme["uncategorized"].append(thread)

    return dict(threads_by_theme)


def generate_theme_markdown(theme: str, threads: List[Dict], output_dir: Path):
    """Generate markdown files for a specific theme"""

    output_dir.mkdir(parents=True, exist_ok=True)

    # Import text utilities
    import sys

    scripts_dir = Path(__file__).parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    from text_utilities import (
        calculate_reading_time,
        format_frontmatter_value,
        generate_description,
        generate_filename,
        generate_title,
    )

    for i, thread in enumerate(threads):
        filename = generate_filename(
            i + 1, thread["first_tweet_date"], thread["smushed_text"]
        )

        title = generate_title(thread["smushed_text"])
        description = generate_description(thread["smushed_text"])
        reading_time = calculate_reading_time(thread["smushed_text"])

        # Build frontmatter with tags
        frontmatter_lines = [
            "---",
            f"title: {format_frontmatter_value(title)}",
            f"date: {thread['first_tweet_date'][:10] if thread['first_tweet_date'] else '2025-01-01'}",
            f"description: {format_frontmatter_value(description)}",
            f"thread_id: {thread['thread_id']}",
            f"word_count: {thread['word_count']}",
            f"reading_time: {reading_time}",
            f"primary_theme: {theme}",
        ]

        # Add all themes as tags
        if thread.get("themes"):
            frontmatter_lines.append(
                f"tags: {format_frontmatter_value(thread['themes'])}"
            )

        frontmatter_lines.extend(["---", "", f"# {title}", "", thread["smushed_text"]])

        filepath = output_dir / filename
        with security_utils.safe_open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(frontmatter_lines))


def generate_theme_index(theme: str, thread_count: int, output_dir: Path):
    """Generate index page for each theme"""

    theme_display = theme.replace("_", " ").title()
    clean_theme = get_clean_dir_name(theme)

    index_content = f"""---
title: {theme_display}
---

# {theme_display}

This section contains **{thread_count} threads** related to {theme_display.lower()}.

<!-- material/tags {{ include: [{theme}] }} -->

## Recent Threads

<!-- Threads will be auto-populated by tags plugin -->
"""

    index_file = output_dir / "index.md"
    with security_utils.safe_open(index_file, "w", encoding="utf-8") as f:
        f.write(index_content)


def update_mkdocs_nav(themes_data: Dict[str, List]):
    """Generate navigation structure for mkdocs.yml"""


    # Sort themes by thread count
    sorted_themes = sorted(themes_data.items(), key=lambda x: len(x[1]), reverse=True)

    print("\n📚 Generated Navigation Structure:")
    print("nav:")
    print("  - Home: index.md")

    # Main themes section
    themes_nav = []
    for theme, threads in sorted_themes[:10]:  # Top 10 themes
        theme_display = theme.replace("_", " ").title()
        clean_dir = get_clean_dir_name(theme)
        themes_nav.append({theme_display: f"{clean_dir}/index.md"})
        print(f"  - {theme_display}: {clean_dir}/index.md  # ({len(threads)} threads)")

    print("  - Themes:")
    for item in themes_nav:
        for k, v in item.items():
            print(f"    - {k}: {v}")

    print("\n💡 Add this navigation to your mkdocs.yml!")


def main():
    """Generate markdown organized by specific themes"""

    print("🎯 Reorganizing threads by specific themes...")

    # Reorganize by themes
    threads_by_theme = organize_by_themes()

    print("\n📊 Theme Distribution:")
    for theme, threads in sorted(
        threads_by_theme.items(), key=lambda x: len(x[1]), reverse=True
    ):
        print(f"  {theme}: {len(threads)} threads")

    # Generate markdown for each theme
    base_dir = Path("markdown")

    for theme, threads in threads_by_theme.items():
        if threads:  # Only create directories for themes with content
            clean_dir = get_clean_dir_name(theme)
            theme_dir = base_dir / clean_dir
            print(f"\n📝 Generating {theme} -> {clean_dir} ({len(threads)} threads)...")

            generate_theme_markdown(theme, threads, theme_dir)
            generate_theme_index(theme, len(threads), theme_dir)

    # Update navigation
    update_mkdocs_nav(threads_by_theme)

    print(f"\n✅ Generated themed markdown in {base_dir}/")
    print("📌 Remember to:")
    print("  1. Update mkdocs.yml with the new navigation")
    print("  2. Enable the tags plugin if not already enabled")
    print("  3. Run 'uv run mkdocs serve' to preview")


if __name__ == "__main__":
    main()
