#!/usr/bin/env python3
"""
Complete DremelDocs pipeline runner with safety checks.
Clears old markdown files before regeneration to prevent duplicates.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'=' * 60}")
    print(f"🚀 {description}")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception running {description}: {e}")
        return False


def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    checks = []

    # Check for source data
    source_file = Path("source/data/tweets.js")
    if source_file.exists():
        print(f"✅ Source data found: {source_file}")
        checks.append(True)
    else:
        print(f"❌ Source data not found: {source_file}")
        checks.append(False)

    # Check for scripts
    required_scripts = [
        "scripts/local_filter_pipeline.py",
        "scripts/generate_heavy_hitters.py",
        "scripts/theme_classifier.py",
    ]

    for script in required_scripts:
        if Path(script).exists():
            print(f"✅ Script found: {script}")
            checks.append(True)
        else:
            print(f"❌ Script missing: {script}")
            checks.append(False)

    return all(checks)


def backup_existing_markdown() -> None:
    """Create a backup of existing markdown files."""
    markdown_dir = Path("markdown")
    backup_dir = Path(f"backups/markdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    if markdown_dir.exists() and any(markdown_dir.glob("**/*.md")):
        print(f"\n📦 Backing up existing markdown to {backup_dir}")
        backup_dir.parent.mkdir(exist_ok=True)
        run_command(f"cp -r {markdown_dir} {backup_dir}", "Backup creation")


def main():
    """Run the complete pipeline with safety checks."""
    print("""
╔══════════════════════════════════════════════════════════╗
║     DremelDocs Complete Pipeline Runner                  ║
║     Revolutionary Theory Archive Generation              ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    if not check_prerequisites():
        print(
            "\n❌ Prerequisites check failed. Please ensure all required files are present."
        )
        sys.exit(1)

    # Ask for confirmation before clearing
    print("\n⚠️  WARNING: This will clear all existing markdown files!")
    print("A backup will be created first.")
    response = input("Continue? (y/N): ").strip().lower()

    if response != "y":
        print("❌ Pipeline cancelled by user")
        sys.exit(0)

    # Create backup
    backup_existing_markdown()

    # Pipeline stages
    stages = [
        (
            "uv run python scripts/local_filter_pipeline.py",
            "Stage 1: Extract and filter threads from Twitter archive",
        ),
        (
            "uv run python scripts/generate_heavy_hitters.py",
            "Stage 2: Generate heavy hitter documents (500+ words)",
        ),
        (
            "echo 'Manual theme extraction required' && ls docs/heavy_hitters/*.md | wc -l",
            "Stage 3: Check heavy hitters generated",
        ),
    ]

    # Run initial stages
    for cmd, description in stages:
        if not run_command(cmd, description):
            print(f"\n❌ Pipeline failed at: {description}")
            print("Please fix the issue and run again.")
            sys.exit(1)

    # Check if themes have been extracted
    themes_file = Path("docs/heavy_hitters/THEMES_EXTRACTED.md")
    if not themes_file.exists():
        print("\n" + "=" * 60)
        print("⏸️  MANUAL STEP REQUIRED")
        print("=" * 60)
        print("\n📝 Please complete manual theme extraction:")
        print("1. Review the threads in docs/heavy_hitters/")
        print("2. Fill out THEME_TEMPLATE.md with your insights")
        print("3. Save as docs/heavy_hitters/THEMES_EXTRACTED.md")
        print("4. Run this script again to continue!")
        sys.exit(0)

    # Run classification with clearing
    print("\n" + "=" * 60)
    print("🚀 Stage 4: Classify all threads and generate markdown")
    print("=" * 60)

    # This will clear existing markdown and generate new files
    if not run_command(
        "uv run python scripts/theme_classifier.py",
        "Theme classification and markdown generation",
    ):
        print("\n❌ Classification failed")
        sys.exit(1)

    # Final statistics
    print("\n" + "=" * 60)
    print("📊 PIPELINE COMPLETE - Final Statistics")
    print("=" * 60)

    # Count files
    if Path("data/filtered_threads.json").exists():
        with open("data/filtered_threads.json") as f:
            data = json.load(f)
            print(f"📚 Total threads extracted: {len(data.get('threads', []))}")

    markdown_count = len(list(Path("markdown").glob("**/*.md")))
    print(f"📝 Total markdown files generated: {markdown_count}")

    print("\n✨ Pipeline completed successfully!")
    print("\nNext steps:")
    print("1. Run 'mkdocs serve' to preview the site")
    print("2. Run 'mkdocs build' to generate static site")
    print("\n🌐 Site will be available at http://localhost:8000")


if __name__ == "__main__":
    main()
