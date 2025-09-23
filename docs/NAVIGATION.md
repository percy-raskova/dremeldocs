# DremelDocs Navigation Guide

## 📍 Where to Find What

### For Users

#### Getting Started
1. **Project Overview**: [`README.md`](../README.md)
2. **Quick Start**: [`docs/workflow.md`](workflow.md)
3. **Setup Guide**: [`docs/setup.md`](setup.md)

#### Content Review
1. **Heavy Hitters Index**: [`docs/heavy_hitters/index.md`](heavy_hitters/index.md)
2. **Theme Template**: [`docs/heavy_hitters/THEME_TEMPLATE.md`](heavy_hitters/THEME_TEMPLATE.md)
3. **Individual Threads**: `docs/heavy_hitters/001-*.md` through `059-*.md`

#### Website Preview
1. **Homepage Design**: [`markdown/index.md`](../markdown/index.md)
2. **AI Ethics Page**: [`markdown/about/ai-ethics.md`](../markdown/about/ai-ethics.md)
3. **Custom Styles**: [`markdown/stylesheets/extra.css`](../markdown/stylesheets/extra.css)

---

### For Developers

#### Core Scripts
1. **Main Pipeline**: [`scripts/local_filter_pipeline.py`](../scripts/local_filter_pipeline.py)
2. **Heavy Hitter Generator**: [`scripts/generate_heavy_hitters.py`](../scripts/generate_heavy_hitters.py)
3. **Theme Classifier**: [`scripts/theme_classifier.py`](../scripts/theme_classifier.py)
4. **Text Processing**: [`scripts/text_processing.py`](../scripts/text_processing.py)

#### Documentation
1. **Architecture**: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
2. **API Reference**: [`docs/API.md`](API.md)
3. **Testing Guide**: [`docs/testing.md`](testing.md)
4. **Project Status**: [`docs/STATUS.md`](STATUS.md)

#### Testing
1. **Test Suite**: [`tests/`](../tests/)
2. **Unit Tests**: [`tests/unit/`](../tests/unit/)
3. **Integration Tests**: [`tests/integration/`](../tests/integration/)
4. **Test Fixtures**: [`tests/fixtures/`](../tests/fixtures/)

---

### For Claude Code

#### Project Knowledge
1. **Instructions**: [`CLAUDE.md`](../CLAUDE.md)
2. **Knowledge Base**: `.serena/memories/PROJECT_KNOWLEDGE_BASE`
3. **Technical Learnings**: `.serena/memories/technical_learnings_spacy_uv`

#### Session History
1. **Development Timeline**: `.notes/session_history/`
2. **Cleanup Summary**: `.notes/CLEANUP_SUMMARY.md`
3. **Memory Best Practices**: `.notes/SERENA_MEMORY_BEST_PRACTICES.md`

---

## 🗺️ Project Map

```
Entry Points
├── README.md ─────────────────► Project overview
├── PROJECT_INDEX.md ──────────► Complete navigation (you are here)
└── docs/INDEX.md ─────────────► Documentation hub

Processing Flow
├── twitter-archives/ ─────────► Source data
├── scripts/ ──────────────────► Processing pipeline
├── data/ ─────────────────────► Working directory
├── docs/heavy_hitters/ ───────► Manual review
└── markdown/ ─────────────────► Final website

Documentation
├── docs/ ─────────────────────► Technical docs
├── .notes/ ───────────────────► Historical records
└── .serena/memories/ ─────────► Project knowledge

Testing
├── tests/unit/ ───────────────► Component tests
├── tests/integration/ ────────► End-to-end tests
└── tests/fixtures/ ───────────► Test data
```

---

## 🚦 Task Flow Navigation

### Current Task: Theme Extraction
1. Navigate to: `docs/heavy_hitters/`
2. Review files: `001-*.md` through `059-*.md`
3. Edit: `THEME_TEMPLATE.md`
4. Save as: `THEMES_EXTRACTED.md`

### Next Steps
1. Run: `scripts/theme_classifier.py`
2. Check: `data/classified_threads.json`
3. Generate: Final markdown files
4. Preview: `mkdocs serve`

---

## 🔍 Quick Search Patterns

### Find Specific Content
```bash
# Find all heavy hitters
ls docs/heavy_hitters/*.md

# Search for specific topic
grep -r "capitalism" docs/heavy_hitters/

# Find test files
find tests -name "*.py"

# Locate configuration
find . -name "*.yaml" -o -name "*.yml"
```

### Navigate by Purpose
- **Configuration**: Look in root (`pyproject.toml`, `mkdocs.yml`)
- **Source Code**: Check `scripts/` directory
- **Documentation**: Browse `docs/` directory
- **Generated Content**: Find in `docs/heavy_hitters/`
- **Website Files**: See `markdown/` directory

---

## 📊 File Relationships

### Dependencies
```
local_filter_pipeline.py
    ├── reads: twitter-archives/data/tweets.js
    └── writes: data/filtered_threads.json

generate_heavy_hitters.py
    ├── reads: data/filtered_threads.json
    ├── uses: text_processing.py
    └── writes: docs/heavy_hitters/*.md

theme_classifier.py
    ├── reads: THEMES_EXTRACTED.md
    ├── reads: data/filtered_threads.json
    └── writes: data/classified_threads.json
```

### Test Coverage
```
test_text_processing.py ──────► text_processing.py
test_generate_heavy_hitters.py ► generate_heavy_hitters.py
test_filter_pipeline.py ──────► local_filter_pipeline.py
test_end_to_end.py ───────────► Full pipeline
```

---

## 🎯 Purpose-Based Navigation

### "I want to..."

#### Review the philosophical content
→ Go to `docs/heavy_hitters/` and browse the markdown files

#### Run the processing pipeline
→ Execute scripts in order: `local_filter_pipeline.py` → `generate_heavy_hitters.py`

#### Understand the architecture
→ Read `docs/ARCHITECTURE.md`

#### Run tests
→ Execute `uv run pytest tests/`

#### Check project status
→ See `docs/STATUS.md`

#### Preview the website
→ Run `mkdocs serve` and open http://localhost:8000

#### Find configuration files
→ Check root directory for `pyproject.toml`, `mkdocs.yml`

#### See what's been done
→ Review `.notes/session_history/consolidated_sessions.md`

---

## 📚 Reference Links

### External Resources
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material Theme](https://squidfunk.github.io/mkdocs-material/)
- [SpaCy Docs](https://spacy.io/)
- [uv Package Manager](https://github.com/astral-sh/uv)

### Internal Cross-References
- Architecture details: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- API documentation: [`API.md`](API.md)
- Testing framework: [`testing.md`](testing.md)
- Development workflow: [`workflow.md`](workflow.md)

---

*Navigation Guide v1.0 | Updated: 2025-01-23*