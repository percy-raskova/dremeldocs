#!/usr/bin/env python3
"""
Update documentation files with metrics from metrics.json.

This script reads metrics.json and updates documentation files (README.md,
CLAUDE.md, copilot-instructions.md) by replacing template variables with
actual values, ensuring consistency across all documentation.

Template Variable Format:
  {{metric.path.to.value}} - will be replaced with the value from metrics.json
  
Example:
  {{content.total_markdown_files}} -> 559
  {{themes.marxism.markdown_files}} -> 308
"""

import json
import re
from pathlib import Path
from typing import Dict, Any


def load_metrics() -> Dict[str, Any]:
    """Load metrics from metrics.json."""
    metrics_file = Path("data/metrics.json")
    if not metrics_file.exists():
        raise FileNotFoundError(
            "metrics.json not found. Run 'python scripts/extract_metrics.py' first."
        )
    
    with open(metrics_file) as f:
        return json.load(f)


def get_metric_value(metrics: Dict[str, Any], path: str) -> Any:
    """Get a value from metrics using dot notation path."""
    parts = path.split(".")
    value = metrics
    
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            raise KeyError(f"Metric path not found: {path}")
    
    return value


def substitute_metrics(content: str, metrics: Dict[str, Any]) -> tuple[str, int]:
    """
    Replace template variables in content with actual metric values.
    
    Returns:
        (updated_content, substitution_count)
    """
    pattern = r'\{\{([a-zA-Z0-9._]+)\}\}'
    substitutions = 0
    
    def replace_func(match):
        nonlocal substitutions
        path = match.group(1)
        try:
            value = get_metric_value(metrics, path)
            substitutions += 1
            
            # Format numbers with commas if they're integers >= 1000
            if isinstance(value, int) and value >= 1000:
                return f"{value:,}"
            return str(value)
        except KeyError:
            # Return original if metric not found
            return match.group(0)
    
    updated_content = re.sub(pattern, replace_func, content)
    return updated_content, substitutions


def update_file(file_path: Path, metrics: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    Update a documentation file with metrics.
    
    Returns:
        Dictionary with update statistics
    """
    if not file_path.exists():
        return {"status": "skipped", "reason": "file not found"}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    updated_content, substitutions = substitute_metrics(original_content, metrics)
    
    if substitutions == 0:
        return {"status": "unchanged", "substitutions": 0}
    
    if not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        return {"status": "updated", "substitutions": substitutions}
    else:
        return {"status": "would_update", "substitutions": substitutions}


def main():
    """Main function to update all documentation files."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update documentation files with metrics from metrics.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Specific files to update (default: README.md, CLAUDE.md, .github/copilot-instructions.md)"
    )
    args = parser.parse_args()
    
    # Load metrics
    try:
        metrics = load_metrics()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    
    # Default files to update
    if args.files:
        files_to_update = [Path(f) for f in args.files]
    else:
        files_to_update = [
            Path("README.md"),
            Path("CLAUDE.md"),
            Path(".github/copilot-instructions.md"),
        ]
    
    print("=" * 70)
    print("DOCUMENTATION METRICS UPDATE")
    print("=" * 70)
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")
    
    # Update each file
    results = {}
    for file_path in files_to_update:
        result = update_file(file_path, metrics, dry_run=args.dry_run)
        results[str(file_path)] = result
        
        status_symbol = {
            "updated": "✅",
            "would_update": "📝",
            "unchanged": "⚪",
            "skipped": "⏭️ "
        }.get(result["status"], "❓")
        
        print(f"{status_symbol} {file_path}")
        if result["status"] in ["updated", "would_update"]:
            print(f"   {result['substitutions']} substitution(s)")
        elif result["status"] == "skipped":
            print(f"   Reason: {result.get('reason', 'unknown')}")
    
    print("\n" + "=" * 70)
    
    # Summary
    updated = sum(1 for r in results.values() if r["status"] == "updated")
    would_update = sum(1 for r in results.values() if r["status"] == "would_update")
    unchanged = sum(1 for r in results.values() if r["status"] == "unchanged")
    skipped = sum(1 for r in results.values() if r["status"] == "skipped")
    
    print("\nSummary:")
    if args.dry_run:
        print(f"  Would update: {would_update}")
    else:
        print(f"  Updated: {updated}")
    print(f"  Unchanged: {unchanged}")
    print(f"  Skipped: {skipped}")
    
    print("\nℹ️  To use template variables in your markdown files:")
    print("   {{content.total_markdown_files}} -> 559")
    print("   {{themes.marxism.name}} -> Marxism & Historical Materialism")
    print("   {{themes.marxism.markdown_files}} -> 308")
    print("   {{source_data.total_tweets_processed}} -> 21,723")
    
    return 0


if __name__ == "__main__":
    exit(main())
