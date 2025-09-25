#!/usr/bin/env python3
"""
DremelDocs Pipeline Orchestrator
Complete pipeline from Twitter archive to MkDocs site
"""

import json
import subprocess
import sys
from pathlib import Path

import spacy

from config.loader import ConfigLoader


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n{'=' * 50}")
    print(f"{description}")
    print(f"{'=' * 50}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Success: {description}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"Failed: {description}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False


def check_prerequisites() -> bool:
    """Check if required files and tools exist"""
    print("\n🔍 Checking prerequisites...")

    # Check for source data
    if not Path("source/data/tweets.js").exists():
        print("Missing source/data/tweets.js - Twitter archive required")
        return False

    # Check for SpaCy model
    try:
        nlp = spacy.load("en_core_web_lg")
        print("SpaCy model loaded")
    except OSError:
        print("SpaCy model not found. Installing...")
        cmd = "uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl"
        if not run_command(cmd, "Installing SpaCy model"):
            return False

    return True


def main():
    """Run the complete DremelDocs pipeline"""
    print(
        """
    ╔══════════════════════════════════════════════════╗
    ║         DremelDocs Pipeline Orchestrator         ║
    ║  Twitter Archive → Filtered → Classified → Site  ║
    ╚══════════════════════════════════════════════════╝
    """
    )

    # Check prerequisites
    if not check_prerequisites():
        print("\nPrerequisites not met. Please fix issues and try again.")
        sys.exit(1)

    # Step 1: Run filter pipeline
    if not run_command(
        "uv run python scripts/local_filter_pipeline.py",
        "Step 1: Filtering Twitter archive (21,723 → ~1,363 threads)",
    ):
        print("Pipeline failed at filtering stage")
        sys.exit(1)

    # Step 2: Run theme classifier
    if not run_command(
        "uv run python scripts/theme_classifier.py",
        "Step 2: Classifying threads by themes",
    ):
        print("Pipeline failed at classification stage")
        sys.exit(1)

    # Step 3: Generate themed markdown (NEW APPROACH!)
    if not run_command(
        "uv run python scripts/generate_themed_markdown.py",
        "Step 3: Generating markdown organized by SPECIFIC THEMES (not generic categories!)",
    ):
        print("Pipeline failed at markdown generation stage")
        sys.exit(1)

    # Check results
    try:
        with open("data/classified_threads.json") as f:
            data = json.load(f)

        print("\nClassification Results:")
        print(f"  Total threads: {data['metadata']['total_threads']}")
        for category, threads in data["threads_by_category"].items():
            print(f"  {category}: {len(threads)}")
    except Exception as e:
        print(f" Could not read classification results: {e}")

    # Step 3: Build MkDocs site
    if not run_command("mkdocs build --strict", "Step 3: Building MkDocs site"):
        print(" MkDocs build failed - checking if we can still serve...")

    # Final message
    print(
        """
    ╔══════════════════════════════════════════════════╗
    ║              Pipeline Complete! 🎉               ║
    ╚══════════════════════════════════════════════════╝

    Generated files:
    📁 data/filtered_threads.json - Filtered threads
    📁 data/classified_threads.json - Classified threads
    📁 markdown/*/ - Markdown files for MkDocs
    📁 site/ - Static site (if build succeeded)

    Next steps:
    1. Review generated content in markdown/
    2. Run 'mkdocs serve' to preview locally
    3. Deploy with 'mkdocs gh-deploy' for GitHub Pages
    """
    )


def run_pipeline(env="development"):
    """Run complete pipeline with configuration."""

    # Load configuration
    loader = ConfigLoader(env=env)
    config = loader.load_pipeline_config()

    # Run each stage
    for stage_name, stage_config in config["stages"].items():
        if "script" in stage_config:
            print(f"Running {stage_name}...")

            # Set environment variables for script
            env_vars = os.environ.copy()
            env_vars["PIPELINE_CONFIG"] = json.dumps(stage_config)

            # Run script
            result = subprocess.run(
                ["python", stage_config["script"]],
                env=env_vars,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"Stage {stage_name} failed: {result.stderr}")
                return False

    return True


# Run pipeline
if __name__ == "__main__":
    import sys

    env = sys.argv[1] if len(sys.argv) > 1 else "development"
    success = run_pipeline(env)
    sys.exit(0 if success else 1)
