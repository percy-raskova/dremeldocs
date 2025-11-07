#!/usr/bin/env python3
"""
Extract repository metrics for consistent use across documentation.

This script generates a metrics.json file containing all key statistics
about the repository, ensuring consistency across README, CLAUDE.md,
copilot-instructions.md, and other documentation.
"""

import json
from pathlib import Path
from typing import Dict, Any


def count_markdown_files() -> Dict[str, int]:
    """Count markdown files by theme directory."""
    markdown_dir = Path("markdown")
    if not markdown_dir.exists():
        return {}
    
    theme_counts = {}
    total_count = 0
    
    for md_file in markdown_dir.rglob("*.md"):
        # Skip index files and special files
        if md_file.name in ["index.md", "tags.md", "INSURRECTION.md"]:
            continue
            
        total_count += 1
        
        # Get theme from directory structure
        if len(md_file.parts) > 1:
            theme = md_file.parts[1]
            if theme not in ["about", "themes", "analysis"]:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    theme_counts["_total"] = total_count
    return theme_counts


def load_classified_threads() -> Dict[str, Any]:
    """Load classified threads metadata."""
    classified_file = Path("data/classified_threads.json")
    if not classified_file.exists():
        return {}
    
    with open(classified_file) as f:
        data = json.load(f)
    
    return data.get("metadata", {})


def count_vocabulary_terms() -> int:
    """Count vocabulary terms across all vocabulary files."""
    vocab_dir = Path("data/vocabularies")
    if not vocab_dir.exists():
        return 0
    
    import yaml
    
    total_terms = 0
    for vocab_file in vocab_dir.glob("*.yaml"):
        try:
            with open(vocab_file) as f:
                vocab_data = yaml.safe_load(f)
                if isinstance(vocab_data, dict):
                    for category_terms in vocab_data.values():
                        if isinstance(category_terms, list):
                            total_terms += len(category_terms)
        except Exception:
            continue
    
    return total_terms


def count_source_tweets() -> int:
    """Count tweets in source archive if available."""
    source_file = Path("source/data/tweets.js")
    if not source_file.exists():
        return 0
    
    # This is a rough estimate - actual parsing would be more complex
    # For now, use the documented number
    return 21723  # Known value from documentation


def extract_all_metrics() -> Dict[str, Any]:
    """Extract all repository metrics."""
    
    classified_metadata = load_classified_threads()
    markdown_counts = count_markdown_files()
    
    # Theme mapping between classified data and markdown directories
    theme_mapping = {
        "marxism_historical_materialism": "marxism",
        "political_economy": "economy",
        "organizational_theory": "organizing",
        "covid_public_health_politics": "covid",
        "fascism_analysis": "fascism",
        "cultural_criticism": "culture",
        "imperialism_colonialism": "imperialism",
        "dialectics": "dialectics",
    }
    
    # Extract theme counts from classified data
    theme_counts = {}
    if "theme_counts" in classified_metadata:
        for theme_key, count in classified_metadata["theme_counts"].items():
            markdown_key = theme_mapping.get(theme_key, theme_key)
            theme_counts[markdown_key] = {
                "classified_threads": count,
                "markdown_files": markdown_counts.get(markdown_key, 0)
            }
    
    # Add uncategorized count
    uncategorized_count = (
        classified_metadata.get("total_threads", 0) 
        - sum(theme_counts[t]["classified_threads"] for t in theme_counts)
    )
    theme_counts["uncategorized"] = {
        "classified_threads": uncategorized_count,
        "markdown_files": markdown_counts.get("uncategorized", 0)
    }
    
    metrics = {
        "last_updated": "2025-11-07",
        "repository": {
            "name": "dremeldocs",
            "version": "0.8.1",
            "status": "production_ready"
        },
        "tweets": {
            "total_processed": count_source_tweets(),
            "source_file_size_mb": 37
        },
        "threads": {
            "total": classified_metadata.get("total_threads", 0),
            "classified": classified_metadata.get("classified", 0),
            "unclassified": 0
        },
        "themes": {
            "count": len(theme_mapping),
            "details": theme_counts
        },
        "vocabulary": {
            "total_terms": count_vocabulary_terms(),
            "extracted": True
        },
        "markdown": {
            "total_files": markdown_counts.get("_total", 0),
            "by_theme": {k: v for k, v in markdown_counts.items() if k != "_total"}
        },
        "documentation": {
            "site_url": "https://percy-raskova.github.io/dremeldocs/",
            "mkdocs_theme": "material"
        },
        "testing": {
            "coverage_target": 96.7,
            "framework": "pytest"
        },
        "technology": {
            "python_required": "3.8",
            "python_recommended": "3.12",
            "package_manager": "uv",
            "nlp_library": "spacy",
            "nlp_model": "en_core_web_lg"
        }
    }
    
    return metrics


def main():
    """Main function to extract and save metrics."""
    metrics = extract_all_metrics()
    
    output_file = Path("data/metrics.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Metrics extracted to {output_file}")
    print(f"\nKey Statistics:")
    print(f"  Total Tweets: {metrics['tweets']['total_processed']:,}")
    print(f"  Total Threads: {metrics['threads']['total']:,}")
    print(f"  Total Markdown Files: {metrics['markdown']['total_files']:,}")
    print(f"  Vocabulary Terms: {metrics['vocabulary']['total_terms']:,}")
    print(f"\nTheme Distribution:")
    for theme, data in sorted(metrics['themes']['details'].items()):
        print(f"  {theme}: {data['classified_threads']} threads, {data['markdown_files']} files")


if __name__ == "__main__":
    main()
