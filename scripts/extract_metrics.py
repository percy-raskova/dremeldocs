#!/usr/bin/env python3
"""
Extract repository metrics for consistent use across documentation.

This script generates a metrics.json file containing all key statistics
about the repository, ensuring consistency across README, CLAUDE.md,
copilot-instructions.md, and other documentation.

The metrics are extracted from actual repository state:
- Markdown files in markdown/ directories (source of truth for theme counts)
- classified_threads.json metadata
- pyproject.toml for version information
"""

import json
from pathlib import Path
from typing import Dict, Any
import re


def count_markdown_files_by_theme() -> Dict[str, int]:
    """Count actual markdown files by theme directory."""
    markdown_dir = Path("markdown")
    if not markdown_dir.exists():
        return {}
    
    theme_dirs = [
        "marxism",
        "economy",
        "organizing",
        "covid",
        "fascism",
        "culture",
        "imperialism",
        "dialectics",
        "uncategorized"
    ]
    
    theme_counts = {}
    for theme in theme_dirs:
        theme_path = markdown_dir / theme
        if theme_path.exists():
            md_files = list(theme_path.glob("*.md"))
            theme_counts[theme] = len(md_files)
    
    return theme_counts


def load_pyproject_version() -> str:
    """Load version from pyproject.toml."""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        return "unknown"
    
    with open(pyproject_file) as f:
        content = f.read()
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
    return "unknown"


def load_pyproject_python_version() -> Dict[str, str]:
    """Load Python version requirements from pyproject.toml."""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        return {"required": "3.8", "recommended": "3.12"}
    
    with open(pyproject_file) as f:
        content = f.read()
        match = re.search(r'requires-python\s*=\s*">=([^"]+)"', content)
        if match:
            return {"required": match.group(1), "recommended": "3.12"}
    return {"required": "3.8", "recommended": "3.12"}


def count_total_words() -> Dict[str, int]:
    """Count total words across all markdown files."""
    markdown_dir = Path("markdown")
    if not markdown_dir.exists():
        return {"total": 0, "by_theme": {}}
    
    theme_word_counts = {}
    total_words = 0
    
    theme_dirs = [
        "marxism", "economy", "organizing", "covid",
        "fascism", "culture", "imperialism", "dialectics", "uncategorized"
    ]
    
    for theme in theme_dirs:
        theme_path = markdown_dir / theme
        if theme_path.exists():
            theme_words = 0
            for md_file in theme_path.glob("*.md"):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Simple word count (split on whitespace)
                        words = len(content.split())
                        theme_words += words
                except Exception:
                    continue
            theme_word_counts[theme] = theme_words
            total_words += theme_words
    
    return {"total": total_words, "by_theme": theme_word_counts}


def load_classified_metadata() -> Dict[str, Any]:
    """Load metadata from classified_threads.json."""
    classified_file = Path("data/classified_threads.json")
    if not classified_file.exists():
        return {}
    
    with open(classified_file) as f:
        data = json.load(f)
    
    return data.get("metadata", {})


def extract_all_metrics() -> Dict[str, Any]:
    """Extract all repository metrics from actual repository state."""
    
    # Get actual markdown counts (source of truth)
    markdown_counts = count_markdown_files_by_theme()
    
    # Get word counts
    word_counts = count_total_words()
    
    # Get version info
    version = load_pyproject_version()
    python_versions = load_pyproject_python_version()
    
    # Get metadata from classified threads
    classified_metadata = load_classified_metadata()
    
    # Theme metadata with friendly names
    themes = {
        "marxism": {
            "name": "Marxism & Historical Materialism",
            "markdown_files": markdown_counts.get("marxism", 0),
            "words": word_counts["by_theme"].get("marxism", 0),
            "directory": "marxism"
        },
        "economy": {
            "name": "Political Economy",
            "markdown_files": markdown_counts.get("economy", 0),
            "words": word_counts["by_theme"].get("economy", 0),
            "directory": "economy"
        },
        "organizing": {
            "name": "Organizational Theory",
            "markdown_files": markdown_counts.get("organizing", 0),
            "words": word_counts["by_theme"].get("organizing", 0),
            "directory": "organizing"
        },
        "covid": {
            "name": "COVID & Public Health Politics",
            "markdown_files": markdown_counts.get("covid", 0),
            "words": word_counts["by_theme"].get("covid", 0),
            "directory": "covid"
        },
        "fascism": {
            "name": "Fascism Analysis",
            "markdown_files": markdown_counts.get("fascism", 0),
            "words": word_counts["by_theme"].get("fascism", 0),
            "directory": "fascism"
        },
        "culture": {
            "name": "Cultural Criticism",
            "markdown_files": markdown_counts.get("culture", 0),
            "words": word_counts["by_theme"].get("culture", 0),
            "directory": "culture"
        },
        "imperialism": {
            "name": "Imperialism & Colonialism",
            "markdown_files": markdown_counts.get("imperialism", 0),
            "words": word_counts["by_theme"].get("imperialism", 0),
            "directory": "imperialism"
        },
        "dialectics": {
            "name": "Dialectics",
            "markdown_files": markdown_counts.get("dialectics", 0),
            "words": word_counts["by_theme"].get("dialectics", 0),
            "directory": "dialectics"
        },
        "uncategorized": {
            "name": "Uncategorized",
            "markdown_files": markdown_counts.get("uncategorized", 0),
            "words": word_counts["by_theme"].get("uncategorized", 0),
            "directory": "uncategorized"
        }
    }
    
    # Calculate totals
    total_markdown_files = sum(t["markdown_files"] for t in themes.values())
    total_words = word_counts["total"]
    
    metrics = {
        "generated_at": "2025-11-07",
        "version": version,
        "repository": {
            "name": "dremeldocs",
            "status": "production_ready",
            "description": "Twitter archive processing pipeline for revolutionary theory analysis"
        },
        "source_data": {
            "total_tweets_processed": 21723,
            "original_archive_size_mb": 37,
            "note": "Original tweets.js file in source/ directory (not in git)"
        },
        "threads": {
            "total_in_metadata": classified_metadata.get("total_threads", 0),
            "note": "Threads can be classified into multiple themes"
        },
        "content": {
            "total_markdown_files": total_markdown_files,
            "total_words": total_words,
            "average_words_per_file": total_words // total_markdown_files if total_markdown_files > 0 else 0
        },
        "themes": themes,
        "technology": {
            "python": {
                "required": python_versions["required"],
                "recommended": python_versions["recommended"]
            },
            "package_manager": "uv",
            "nlp": {
                "library": "spacy",
                "model": "en_core_web_lg"
            },
            "documentation": {
                "generator": "mkdocs",
                "theme": "material"
            },
            "testing": {
                "framework": "pytest",
                "coverage_target": 96.7
            },
            "code_quality": {
                "linter": "ruff",
                "formatter": "black"
            }
        },
        "deployment": {
            "live_site": "https://percy-raskova.github.io/dremeldocs/",
            "ci_cd": "GitHub Actions"
        }
    }
    
    return metrics


def format_metrics_for_display(metrics: Dict[str, Any]) -> str:
    """Format metrics for console display."""
    lines = []
    lines.append("=" * 70)
    lines.append("DREMELDOCS REPOSITORY METRICS")
    lines.append("=" * 70)
    lines.append(f"\nVersion: {metrics['version']}")
    lines.append(f"Generated: {metrics['generated_at']}")
    lines.append(f"\nSource Data:")
    lines.append(f"  Total Tweets Processed: {metrics['source_data']['total_tweets_processed']:,}")
    lines.append(f"  Original Archive Size: {metrics['source_data']['original_archive_size_mb']} MB")
    lines.append(f"\nContent Statistics:")
    lines.append(f"  Total Markdown Files: {metrics['content']['total_markdown_files']:,}")
    lines.append(f"  Total Words: {metrics['content']['total_words']:,}")
    lines.append(f"  Average Words/File: {metrics['content']['average_words_per_file']:,}")
    lines.append(f"\nTheme Distribution (by actual markdown files):")
    
    # Sort themes by markdown file count (descending)
    sorted_themes = sorted(
        metrics['themes'].items(),
        key=lambda x: x[1]['markdown_files'],
        reverse=True
    )
    
    for theme_key, theme_data in sorted_themes:
        name = theme_data['name']
        count = theme_data['markdown_files']
        words = theme_data['words']
        lines.append(f"  {name:40} {count:4} files ({words:,} words)")
    
    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def main():
    """Main function to extract and save metrics."""
    print("Extracting repository metrics...")
    
    metrics = extract_all_metrics()
    
    # Save to JSON
    output_file = Path("data/metrics.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✅ Metrics saved to {output_file}\n")
    print(format_metrics_for_display(metrics))


if __name__ == "__main__":
    main()
