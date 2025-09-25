# CLAUDE.md - DremelDocs AI Assistant Guide

This file provides guidance to Claude Code when working with the DremelDocs repository.

## Repository Overview

DremelDocs is a **COMPLETED** Twitter archive processing pipeline that has successfully transformed 21,723 tweets into 1,363 classified threads organized by revolutionary theory themes. The project uses automated theme classification with Marxist political vocabulary extraction.

## Current State

### ✅ Completed
- **Data Processing**: 21,723 tweets → 1,363 threads extracted
- **Theme Classification**: All threads classified into 8 themes using automated NLP
- **Vocabulary Extraction**: 858 revolutionary terms extracted and organized
- **MkDocs Configuration**: Site structure ready with Material theme

### 🔧 Final Step Required
- Run `python scripts/generate_themed_markdown.py` to create markdown files from classified data

## Core Commands

### Complete the Pipeline
```bash
# Generate markdown files from classified threads
python scripts/generate_themed_markdown.py

# Preview the site
make serve  # or: uv run mkdocs serve
```

### Development & Testing
```bash
# Install project (one-time setup)
uv pip install -e .
./install_spacy_model.sh  # Install SpaCy model

# Run tests
uv run pytest tests/        # All tests
uv run pytest tests/unit/   # Unit tests only

# Code quality
uv run ruff scripts/        # Lint
uv run black scripts/       # Format
```

## Architecture

### Classification Pipeline
```
1. vocabulary_builder.py
   → Extracts Marxist/philosophical vocabulary
   → Generates YAML vocabularies

2. theme_classifier.py
   → Uses vocabularies to classify threads
   → Outputs classified_threads.json

3. generate_themed_markdown.py
   → Creates markdown from classified data
   → Organizes by theme directories
```

### Data Files
- `data/classified_threads.json` - 1,363 threads with theme classifications
- `data/vocabularies/*.yaml` - Extracted revolutionary vocabularies
- `markdown/` - MkDocs content directory

### Theme Distribution
- marxism_historical materialism: 585 threads
- political economy: 418 threads
- organizational theory: 326 threads
- covid_public health politics: 297 threads
- fascism analysis: 246 threads
- cultural criticism: 237 threads
- imperialism_colonialism: 233 threads
- dialectics: 70 threads

## Key Scripts

### Production Scripts
- `vocabulary_builder.py` - Revolutionary vocabulary extraction
- `theme_classifier.py` - Automated theme classification
- `generate_themed_markdown.py` - Markdown generation
- `nlp_core.py` - NLP utilities
- `tag_extraction.py` - Tag extraction system
- `text_utilities.py` - Text processing utilities

### Archived (Do Not Use)
- `scripts/archived_experiments/` - Historical experiments, superseded by production code

## Project Patterns

### Vocabulary Extraction
```python
# Pattern-based Marxist concept detection
marxist_patterns = {
    "class_analysis": [
        r"\b(working|ruling|owning) class\b",
        r"\bclass (consciousness|struggle|war)\b",
    ]
}
```

### Theme Classification
```python
# Confidence-based classification
thread["themes"] = classify_with_patterns(text)
thread["confidence"] = calculate_confidence(matches)
```

## Testing

- **Test Coverage**: 98% success rate (275 tests)
- **Core Modules**: Well-tested classification and extraction
- **Integration**: End-to-end pipeline validated

## Performance

- Processing time: ~2 minutes for full classification
- Memory efficient: Streaming JSON processing
- Input: 37MB tweets.js → Output: 1.9MB classified JSON

## Important Notes

1. **No Heavy Hitters**: The "heavy hitter" concept has been removed - all threads are classified equally
2. **Fully Automated**: No manual theme extraction required - vocabulary extraction is automated
3. **Classification Complete**: All 1,363 threads already classified in `classified_threads.json`
4. **Only Markdown Generation Remains**: The final step is generating markdown files

## Quick Start for New Session

```bash
# 1. Check current state
ls data/classified_threads.json  # Should exist with 1,363 threads
ls markdown/                      # Check current content

# 2. Generate markdown (if needed)
python scripts/generate_themed_markdown.py

# 3. Start documentation server
make serve

# 4. Browse to http://localhost:8000
```

## Architecture Philosophy

This project demonstrates computational political analysis using:
- Pattern-based revolutionary vocabulary extraction
- NLP-powered theme classification
- Privacy-first local processing (no cloud APIs)
- Static site generation for long-term preservation

---

*Last updated after comprehensive cleanup and artifact removal*