# Processing Workflow

## Overview

Transform 21,723 tweets into a curated collection of philosophical and political threads.

## Stage 1: Local Filtering

**Script**: `scripts/local_filter_pipeline.py`

- Streams through 37MB tweets.js file using ijson
- Applies 2-stage filter:
  1. Length filter: >100 characters
  2. Thread detection: Reply chains
- Outputs: `data/filtered_threads.json`
- Result: 21,723 tweets → 1,363 threads

## Stage 2: Heavy Hitter Generation

**Script**: `scripts/generate_heavy_hitters.py`

- Filters for threads with 500+ words
- Generates markdown files for manual review
- Outputs: `docs/heavy_hitters/` (59 files)
- Total: 42,774 words of philosophical/political content

## Stage 3: Manual Theme Extraction

**Process**: Human review

1. Read through heavy hitter threads
2. Identify recurring themes and patterns
3. Fill out `THEME_TEMPLATE.md`
4. Save as `THEMES_EXTRACTED.md`

## Stage 4: Classification

**Script**: `scripts/theme_classifier.py`

- Loads human-extracted themes
- Classifies all 1,363 threads
- Organizes by theme (philosophy, politics, both, etc.)
- Outputs: `data/classified_threads.json`

## Stage 5: Markdown Generation

- Generate final markdown files
- Organize into `markdown/` directory
- Structure by themes

## Stage 6: Site Building

```bash
mkdocs serve  # Preview locally
mkdocs build  # Generate HTML in site/
```

## Cost Savings

- Original approach: $108 in API costs
- Local-first approach: $0
- Human-in-the-loop: Better quality through personal knowledge