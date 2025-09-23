# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

DremelDocs is a Twitter archive processing pipeline that transforms 21,723 tweets into a curated MkDocs knowledge base focused on philosophical and political content. The project is 85% complete, blocked on manual theme extraction.

## Core Commands

### Development & Testing
```bash
# Run the main pipeline (uses uv package manager)
uv run python scripts/local_filter_pipeline.py      # Extract & filter threads
uv run python scripts/generate_heavy_hitters.py     # Generate markdown for 500+ word threads
uv run python scripts/theme_classifier.py           # Classify threads (after manual theme extraction)

# Testing (requires project installation and SpaCy model)
uv pip install -e .                                # Install project first (one-time)
./install_spacy_model.sh                           # Install SpaCy model (one-time)
uv run --extra dev pytest tests/                   # Run all tests
uv run --extra dev pytest tests/unit/              # Unit tests only
uv run --extra dev pytest tests/integration/       # Integration tests only
uv run --extra dev pytest tests/ --cov=scripts     # With coverage report
uv run --extra dev pytest tests/unit/test_text_processing.py  # Single test file

# Code quality
uv run black scripts/                              # Format code
uv run ruff scripts/                               # Lint code
uv run mypy scripts/                               # Type checking

# Documentation site
mkdocs serve                                       # Preview at localhost:8000
mkdocs build                                       # Build static site in site/
```

### SpaCy Model Installation
```bash
# SpaCy models must be installed via URL with uv (not via spacy download)
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl
```

## High-Level Architecture

### Data Processing Pipeline
```
twitter-archives/data/tweets.js (37MB, 21,723 tweets)
    ↓ [local_filter_pipeline.py - ijson streaming]
data/filtered_threads.json (1,363 threads)
    ↓ [generate_heavy_hitters.py]
docs/heavy_hitters/*.md (59 files, 500+ words each)
    ↓ [MANUAL: User extracts themes → THEMES_EXTRACTED.md]
data/classified_threads.json
    ↓ [theme_classifier.py]
markdown/themes/* (Final MkDocs content)
```

### Key Architectural Decisions

1. **Streaming JSON Processing**: Uses ijson to handle 37MB files without memory overflow
2. **Two-Stage Filtering**: Length filter (>100 chars) → Thread detection (reply chains)
3. **Human-in-the-Loop Classification**: Manual theme extraction for better quality than pure AI
4. **Cost Optimization**: Local processing saves $108 in API costs

### Module Dependencies
- `text_processing.py` (1,120 lines) - Core NLP utilities used by all scripts
  - Contains: EnhancedTagExtractor, ChunkScorer, DomainVocabulary, PatternMatcher
  - Should be split into: nlp_core.py, tag_extraction.py, text_utilities.py
- `local_filter_pipeline.py` → Standalone entry point
- `generate_heavy_hitters.py` → Depends on text_processing.py
- `theme_classifier.py` → Depends on text_processing.py and user-provided themes

## Current State & Blockers

### Completed (85%)
- ✅ Pipeline infrastructure complete
- ✅ 21,723 tweets → 1,363 threads extracted
- ✅ 59 heavy hitter documents generated
- ✅ Test suite: 119 tests, 100% passing
- ✅ MkDocs theme configured

### Blocked on User Action
- ⏳ Manual review of docs/heavy_hitters/*.md
- ⏳ Fill out THEME_TEMPLATE.md → Save as THEMES_EXTRACTED.md
- ⏳ Run classification on all threads
- ⏳ Generate final markdown site

## Code Quality Notes

### Recent Improvements (Completed Refactoring)
✅ **Bare except clauses**: Fixed all bare except statements
✅ **Module splitting**: text_processing.py split into nlp_core.py, tag_extraction.py, text_utilities.py
✅ **Test file location**: Tests moved to proper tests/ directory structure
✅ **Type hints**: All functions now have complete type annotations (100% coverage)

### Testing Coverage
- Core modules: 89% coverage
- text_processing.py: 71%
- generate_heavy_hitters.py: 89%
- local_filter_pipeline.py: 21% (works in practice)

## Project-Specific Patterns

### Error Handling with uv
```python
# SpaCy model loading pattern (uv environments lack pip module)
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    print("Install with: uv pip install [URL]")
    sys.exit(1)
```

### Twitter Archive Data Structure
```javascript
// All data files follow this pattern:
window.YTD.category_name.part0 = [ /* array of data objects */ ]
```

### Thread Detection Logic
- Threads identified by reply_to_status_id chains
- Minimum 2 tweets to qualify as thread
- Heavy hitters: 500+ words total in thread

## Performance Characteristics
- Processing time: ~2 minutes for full pipeline
- Memory usage: 50MB peak (using streaming)
- Input: 37MB tweets.js → Output: 4MB filtered JSON
- Reduction rate: 96% (21,723 → 1,363 meaningful threads)