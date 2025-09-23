# DremelDocs Project Knowledge Base

## Project Overview
**Type**: Twitter Archive Processing Pipeline  
**Purpose**: Transform 21,723 tweets from @BmoreOrganized into curated philosophical/political MkDocs site  
**Status**: 85% complete (blocked on manual theme extraction)  
**Stack**: Python 3.12, MkDocs Material, SpaCy, uv package manager

## Architecture

### Data Pipeline
```
twitter-archives/data/tweets.js (37MB)
    ↓ [ijson streaming]
1. Length filter (>100 chars)
    ↓ 
2. Thread detection (reply chains)
    ↓
3. 1,363 threads identified
    ↓
4. 59 heavy hitters (500+ words)
    ↓
5. Theme classification (human-guided)
    ↓
6. MkDocs static site generation
```

### Key Scripts
- `scripts/local_filter_pipeline.py` - Streaming JSON processor
- `scripts/generate_heavy_hitters.py` - Markdown generator  
- `scripts/theme_classifier.py` - Human-guided classifier
- `scripts/enhanced_tag_extractor.py` - NLP tag extraction

## Technical Specifications

### Performance
- **Input**: 37MB tweets.js (21,723 tweets)
- **Output**: 1,363 threads → 59 heavy hitters
- **Processing**: ~2 minutes, 50MB peak memory
- **Cost Savings**: $108 (avoided API calls via local filtering)

### NLP Configuration
- **Model**: spaCy en_core_web_lg (685k vocabulary)
- **Installation**: `uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl`
- **Features**: Semantic similarity, political/philosophical domain vocabulary
- **Fallback Chain**: large → transformer → medium → small

### Testing
- **Total Tests**: 119 (100% passing)
- **Coverage**: 89% on core modules
- **Test Command**: `uv run pytest tests/ --cov=scripts`

## Development Workflow

### Quick Start Commands
```bash
# Activate project
cd /home/percy/projects/dremeldocs

# Run pipeline
uv run python scripts/local_filter_pipeline.py

# Generate heavy hitters  
uv run python scripts/generate_heavy_hitters.py

# Run tests
uv run pytest tests/

# Serve website
mkdocs serve
```

### Git Workflow
- Feature branches only (never work on main)
- Conventional commits encouraged
- Pre-commit hooks for syntax and secrets
- `.gitignore` configured for Python projects

## Domain Knowledge

### Twitter Archive Structure
- 83 JavaScript files wrapping JSON data
- Key file: `tweets.js` with all tweet content
- Media in separate directories (not processed)
- Private data requiring careful handling

### Content Classification
- Philosophy keywords: dialectical, praxis, hegemony, materialism
- Politics keywords: imperialism, capitalism, socialism, organizing
- Thread detection: reply_to_status_id chains
- Heavy hitters: 500+ word threads for manual review

## Code Style Conventions
- **Python 3.12+** with type hints where beneficial
- **PEP 8** standard formatting
- **Module Structure**: parser/, classifier/, processor/, utils/
- **Error Handling**: try/except with loguru logging
- **Testing**: pytest with fixtures and integration tests

## Pending Work
1. User reviews 59 heavy hitters in `docs/heavy_hitters/`
2. User fills out `THEME_TEMPLATE.md` with themes
3. Run `theme_classifier.py` on all 1,363 threads
4. Generate final markdown collection
5. Deploy to GitHub Pages

## Lessons Learned
- **Streaming is essential** for large JSON files (ijson)
- **Local-first saves money** - filter before API calls
- **Human judgment invaluable** for philosophical content
- **uv requires special handling** for SpaCy models (no pip module)
- **Hobbyist tolerances** in tests (10s/thread, 200MB memory)