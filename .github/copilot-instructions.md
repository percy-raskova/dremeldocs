# GitHub Copilot Instructions for DremelDocs

## Project Summary

DremelDocs is a **completed** Twitter archive processing pipeline that transforms 21,723 tweets into 1,363 thematically classified threads on revolutionary theory. The project uses automated NLP-based theme classification with Marxist political vocabulary extraction, generating a navigable MkDocs documentation site.

**Technology Stack:**
- Python 3.12+ with `uv` package manager
- SpaCy for NLP and text processing
- MkDocs with Material theme for documentation
- pytest for testing (96.7% coverage)
- ruff for linting, black for formatting

**Live Site:** https://percy-raskova.github.io/dremeldocs/

## Repository Status

✅ **Production Ready** - Core pipeline is complete and operational
- All 21,723 tweets processed into 1,363 classified threads
- Theme classification system fully functional
- Vocabulary extraction automated
- Documentation site deployed

## Architecture Overview

### Pipeline Components

```
1. vocabulary_builder.py
   └── Extracts Marxist/revolutionary vocabulary using pattern matching
   └── Outputs: data/vocabularies/*.yaml

2. theme_classifier.py  
   └── Classifies threads using extracted vocabularies
   └── Outputs: data/classified_threads.json (1,363 threads)

3. generate_themed_markdown.py
   └── Creates markdown files organized by theme
   └── Outputs: markdown/[theme]/
```

### Directory Structure

- `scripts/` - Production pipeline scripts
- `scripts/archived_experiments/` - Historical code, do NOT use or modify
- `data/` - Processed data files and vocabularies
- `markdown/` - Generated MkDocs content organized by theme
- `tests/` - Comprehensive test suite (unit + integration)
- `docs/` - Documentation files
- `config/` - Configuration files

### Key Data Files

- `data/classified_threads.json` - 1,363 classified threads (version controlled)
- `data/vocabularies/*.yaml` - Extracted revolutionary vocabularies
- `source/data/tweets.js` - Original Twitter archive (not in repo, gitignored)

## Build, Test, and Development Commands

### Installation & Setup

```bash
# Install project dependencies
uv pip install -e .

# Install SpaCy language model (required)
./install_spacy_model.sh
# Or manually: python -m spacy download en_core_web_lg
```

### Testing

```bash
# Run all tests (REQUIRED before submitting PR)
uv run pytest tests/

# Run with coverage report
uv run pytest tests/ --cov=scripts --cov-report=term

# Run specific test suites
uv run pytest tests/unit/          # Unit tests only
uv run pytest tests/integration/   # Integration tests only
```

**Acceptance Criteria:** All PRs must maintain or improve 96.7% test coverage.

### Code Quality

```bash
# Format code (REQUIRED - run before commit)
uv run black scripts/

# Lint code (REQUIRED - must pass)
uv run ruff scripts/

# Type checking (optional but recommended)
uv run mypy scripts/
```

**Acceptance Criteria:** All code must pass `black` formatting and `ruff` linting checks.

### Documentation

```bash
# Serve documentation locally
make serve
# Or: uv run mkdocs serve
# Browse to http://localhost:8000

# Build documentation
uv run mkdocs build --clean

# Deploy (automatic via GitHub Actions)
```

### Pipeline Commands

```bash
# Complete pipeline (if starting fresh)
make pipeline

# Individual steps
make extract-vocabulary   # Extract revolutionary vocabulary
make classify            # Classify threads by theme
make generate           # Generate markdown files
```

## Coding Standards

### Python Style

- Follow PEP 8 with black formatting (line length: 88)
- Use type hints where reasonable (not strictly enforced)
- Prefer descriptive variable names over abbreviations
- Add docstrings to all public functions and classes

### Code Organization

- Keep functions focused and single-purpose
- Extract complex logic into well-named helper functions
- Use pattern matching for theme classification (see existing patterns)
- Prefer streaming JSON processing for large files (use `ijson`)

### Testing Patterns

- Unit tests in `tests/unit/` for individual functions
- Integration tests in `tests/integration/` for pipeline components
- Use pytest fixtures for common test data
- Mock external dependencies (file I/O, SpaCy models where appropriate)

### Documentation

- Update CLAUDE.md if making architectural changes
- Keep README.md synchronized with major feature changes
- Add inline comments for complex NLP patterns or algorithms
- Document breaking changes in commit messages

## Workflow Guidelines

### Branch Strategy

- **main** - Production branch (requires PR approval, triggers deployment)
- **dev** - Development branch for integration
- **feature/** or **copilot/** - Feature/task branches

### Pull Request Process

1. Create feature branch from `dev`
2. Make changes following coding standards
3. Run tests and linting: `uv run pytest tests/ && uv run ruff scripts/ && uv run black scripts/`
4. Commit with conventional commits format: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
5. Create PR to `dev` first for testing
6. After validation, PR from `dev` to `main` triggers deployment

### Required Checks

All PRs must:
- [ ] Pass all existing tests
- [ ] Maintain or improve test coverage (≥96.7%)
- [ ] Pass ruff linting
- [ ] Pass black formatting
- [ ] Include relevant test updates if adding/changing functionality
- [ ] Reference related issue number if applicable

## Forbidden Actions

### Do NOT Modify

- **`scripts/archived_experiments/`** - Historical code, superseded by production scripts
- **`.github/workflows/deploy.yml`** - CI/CD pipeline (changes require maintainer review)
- **`data/classified_threads.json`** - Production classification data (regenerate via pipeline if needed)
- **`source/` directory** - Original archive data (gitignored, user-specific)

### Do NOT Remove

- **Existing tests** - May break functionality or pipeline
- **SpaCy model dependencies** - Required for NLP processing
- **Theme classification patterns** - Core to the analysis system

### Sensitive Areas Requiring Extra Care

- **`vocabulary_builder.py`** - Vocabulary extraction patterns (test thoroughly)
- **`theme_classifier.py`** - Classification logic (affects all 1,363 threads)
- **`mkdocs.yml`** - Site configuration (test with `mkdocs serve` before committing)
- **CI/CD workflows** - Deployment automation (coordinate with maintainers)

## Theme Classification System

### 8 Revolutionary Theory Themes

1. **Marxism & Historical Materialism** (585 threads)
2. **Political Economy** (418 threads)
3. **Organizational Theory** (326 threads)
4. **COVID & Public Health Politics** (297 threads)
5. **Fascism Analysis** (246 threads)
6. **Cultural Criticism** (237 threads)
7. **Imperialism & Colonialism** (233 threads)
8. **Dialectics** (70 threads)

### Pattern-Based Classification

Example classification pattern:
```python
marxist_patterns = {
    "class_analysis": [
        r"\b(working|ruling|owning) class\b",
        r"\bclass (consciousness|struggle|war)\b",
    ],
    "historical_materialism": [
        r"\bmaterial (conditions|reality|base)\b",
        r"\bmode of production\b",
    ]
}
```

When modifying classification:
- Test against full dataset (`data/classified_threads.json`)
- Validate pattern changes don't break existing classifications
- Run integration tests for theme classifier

## Task Scoping Best Practices

### Good Tasks for Copilot

✅ Bug fixes in specific modules
✅ Adding/updating unit tests
✅ Documentation improvements
✅ Code formatting and style fixes
✅ Adding new vocabulary patterns
✅ Refactoring individual functions
✅ Performance optimizations with clear metrics

### Tasks Requiring Human Review

⚠️ Changes to core classification algorithm
⚠️ Modifications to CI/CD pipeline
⚠️ Breaking changes to data formats
⚠️ Major architectural changes
⚠️ Changes affecting all 1,363 threads
⚠️ New external dependencies

## Communication & Clarification

### When Instructions Are Unclear

1. Comment on the issue/PR requesting clarification
2. Reference specific files/lines that need clarification
3. Propose 2-3 alternative approaches with trade-offs
4. Wait for human approval before proceeding with ambiguous changes

### Reporting Progress

- Commit messages should be clear and specific
- Reference issue numbers in commits: `fix: resolve #123`
- Use conventional commits format
- Update PR description with progress checklist

## Project-Specific Patterns

### JSON Processing

Always use streaming for large files:
```python
import ijson
with open('data/classified_threads.json', 'rb') as f:
    threads = ijson.items(f, 'item')
    for thread in threads:
        process_thread(thread)
```

### NLP Processing

Load SpaCy model once and reuse:
```python
import spacy
nlp = spacy.load("en_core_web_lg")
# Reuse nlp object for all documents
```

### File Paths

Use Path objects for cross-platform compatibility:
```python
from pathlib import Path
data_dir = Path(__file__).parent.parent / "data"
```

## Performance Considerations

- Full pipeline processes 21,723 tweets in ~2 minutes
- Use streaming JSON for memory efficiency
- SpaCy model loading is expensive (cache the nlp object)
- Markdown generation creates ~1,363 files (use batch processing)

## Troubleshooting Common Issues

### SpaCy Model Not Found
```bash
./install_spacy_model.sh
# Or: python -m spacy download en_core_web_lg
```

### MkDocs Build Warnings
- Auto-discovery mode warnings are normal
- Content remains accessible despite warnings

### Test Failures
1. Check if SpaCy model is installed
2. Verify `data/classified_threads.json` exists
3. Run tests with `-v` flag for verbose output
4. Check for file path issues (use Path objects)

## References

- [Repository README](../README.md)
- [Claude Instructions](../CLAUDE.md) - AI assistant guide
- [CI/CD Documentation](../docs/CICD_PIPELINE.md)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [SpaCy NLP](https://spacy.io/)

## Questions or Issues?

- **GitHub Issues:** https://github.com/percy-raskova/dremeldocs/issues
- **Documentation:** https://percy-raskova.github.io/dremeldocs/
- **Security Policy:** See [SECURITY.md](../SECURITY.md) for security reporting guidelines and project scope clarifications

---

*Last updated: November 2025 | For GitHub Copilot Coding Agent guidance*
