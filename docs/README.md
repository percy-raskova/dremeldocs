# DremelDocs Documentation Hub

## 📚 Available Documentation

### [PROJECT_INDEX.md](PROJECT_INDEX.md)
**Comprehensive Project Documentation**
- Project overview and statistics
- System architecture diagrams
- Technology stack details
- Testing framework documentation
- Development workflow guides
- Performance characteristics

### [PIPELINE_REFERENCE.md](PIPELINE_REFERENCE.md)
**Detailed Pipeline Documentation**
- Stage-by-stage processing guide
- Data flow specifications
- Configuration options
- Error handling strategies
- Performance optimization tips
- Troubleshooting solutions

### [QUICK_START.md](QUICK_START.md)
**Getting Started Guide**
- Installation instructions
- Basic usage commands
- Common operations
- Customization options
- Debugging tips

### [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
**Technical API Reference**
- Core module documentation
- Class and method signatures
- Data format specifications
- Extension points
- Integration examples
- Testing utilities

## 🎯 Quick Navigation

### For New Users
1. Start with [QUICK_START.md](QUICK_START.md)
2. Run the pipeline with `uv run python run_pipeline.py`
3. View results at http://localhost:8000

### For Developers
1. Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. Understand the [PIPELINE_REFERENCE.md](PIPELINE_REFERENCE.md)
3. Explore extension points and plugin architecture

### For Contributors
1. Read [PROJECT_INDEX.md](PROJECT_INDEX.md) for architecture
2. Check testing framework documentation
3. Follow development workflow guidelines

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Threads Processed** | 1,363 |
| **Original Tweets** | 21,723 |
| **Word Count** | ~200,000 |
| **Themes** | 8 categories |
| **Processing Time** | ~2 minutes |
| **Test Coverage** | 98% |

## 🛠️ Key Components

### Data Pipeline
1. **LocalThreadExtractor** - Extract threads from Twitter archive
2. **ThemeClassifier** - Classify by revolutionary themes
3. **VocabularyBuilder** - Extract domain vocabulary
4. **Markdown Generator** - Create MkDocs content

### Output Structure
```
data/
├── filtered_threads.json    # 1,363 threads
├── classified_threads.json  # Themed content
└── vocabularies/*.yaml      # Classification patterns

markdown/
├── [theme_directories]/     # Organized by theme
├── themes/                  # Theme overviews
└── index.md                # Home page
```

## 🚀 Common Tasks

### Run Complete Pipeline
```bash
uv run python run_pipeline.py
```

### View Documentation
```bash
uv run mkdocs serve
```

### Run Tests
```bash
uv run pytest tests/
```

### Clean and Rebuild
```bash
rm -rf data/*.json markdown/* site/
uv run python run_pipeline.py
```

## 📝 Documentation Updates

These documents were generated on **2025-09-25** for DremelDocs version **0.8.1**.

To regenerate documentation:
```bash
/sc:index . --type docs --format md
```

## 🔗 Related Resources

### Project Files
- Main configuration: `mkdocs.yml`
- Dependencies: `pyproject.toml`
- Pipeline scripts: `scripts/`
- Test suite: `tests/`

### External Links
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material Theme](https://squidfunk.github.io/mkdocs-material/)
- [SpaCy NLP](https://spacy.io/)

---

*Documentation Hub for DremelDocs Archive System*
*A revolutionary theory knowledge base preservation project*