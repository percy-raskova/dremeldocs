# AstraDocs Project Index 📚

Complete navigation and reference for the AstraDocs Twitter archive processing pipeline.

## 🗺️ Navigation Map

### Quick Links
- [README](../README.md) - Project overview and quick start
- [Current Status](#current-status) - Where we are now
- [Pipeline Workflow](#pipeline-workflow) - Processing stages
- [Scripts Reference](#scripts-reference) - Tool documentation
- [Project Structure](#project-structure) - Directory organization

## 📊 Current Status

### ✅ Completed
- [x] Project refactoring - Clean MkDocs-friendly structure
- [x] Dependency optimization - Removed 75% of dependencies
- [x] Local filtering pipeline - 21,723 → 1,363 threads
- [x] Heavy hitter generation - 59 threads (500+ words)
- [x] Documentation structure - Comprehensive docs

### 🔄 In Progress
- [ ] **Theme extraction** - Manual review of heavy hitters (USER ACTION REQUIRED)

### ⏳ Pending
- [ ] Thread classification - Apply themes to all 1,363 threads
- [ ] Markdown generation - Create final content structure
- [ ] MkDocs deployment - Build and deploy static site

## 🔄 Pipeline Workflow

### Stage 1: Local Filtering
**Script**: [`scripts/local_filter_pipeline.py`](../scripts/local_filter_pipeline.py)
- **Input**: `source/data/tweets.js` (37MB, 21,723 tweets)
- **Process**: Stream processing with ijson, 2-stage filtering
- **Output**: `data/filtered_threads.json` (1,363 threads)
- **Time**: ~2 minutes

### Stage 2: Heavy Hitter Extraction
**Script**: [`scripts/generate_heavy_hitters.py`](../scripts/generate_heavy_hitters.py)
- **Input**: `data/filtered_threads.json`
- **Filter**: Threads with 500+ words
- **Output**: `docs/heavy_hitters/` (59 markdown files)
- **Purpose**: Identify substantial content for theme extraction

### Stage 3: Theme Extraction (Manual)
**Process**: Human review
- **Input**: Read `docs/heavy_hitters/*.md`
- **Template**: `docs/heavy_hitters/THEME_TEMPLATE.md`
- **Output**: `THEMES_EXTRACTED.md`
- **Time**: 1-2 hours of reading

### Stage 4: Classification
**Script**: [`scripts/theme_classifier.py`](../scripts/theme_classifier.py)
- **Input**: `THEMES_EXTRACTED.md` + `data/filtered_threads.json`
- **Process**: Apply themes to all threads
- **Output**: `data/classified_threads.json`
- **Categories**: philosophy, politics, both, [custom themes]

### Stage 5: Markdown Generation
**Process**: Generate final content
- **Input**: `data/classified_threads.json`
- **Output**: `markdown/` directory structure
- **Organization**: By theme and category

### Stage 6: Site Building
**Tool**: MkDocs
- **Config**: `mkdocs.yml`
- **Source**: `markdown/` directory
- **Output**: `site/` (HTML)
- **Commands**: `mkdocs serve`, `mkdocs build`

## 📂 Project Structure

### Core Directories

#### `source/` - Raw Data
- Twitter archive export
- 83 JavaScript files
- Main file: `data/tweets.js` (37MB)

#### `scripts/` - Processing Pipeline
- `local_filter_pipeline.py` - Main filtering logic
- `generate_heavy_hitters.py` - Extract long threads
- `theme_classifier.py` - Apply categorization

#### `data/` - Working Data
- `filtered_threads.json` - 1,363 processed threads
- `sample_threads/` - Sample markdown outputs
- `classified_threads.json` - After classification

#### `docs/` - Project Documentation
- `heavy_hitters/` - Threads for review
- `pipeline/` - Original design docs
- `workflow.md` - Process guide
- `setup.md` - Installation guide

#### `markdown/` - MkDocs Content
- `philosophy/` - Philosophical threads
- `politics/` - Political threads
- `both/` - Mixed content
- `themes/` - Custom theme organization

#### `archive/` - Historical Files
- `legacy/` - Old scripts
- `reports/` - Analysis documents
- `pipeline-docs/` - Original planning

## 📜 Scripts Reference

### `local_filter_pipeline.py`
```python
# Main filtering pipeline
extractor = LocalThreadExtractor("source")
extractor.run_pipeline()
```
- **Classes**: `LocalThreadExtractor`, `TwitterArchiveExtractor`
- **Methods**: `stream_tweets()`, `extract_threads()`, `filter_threads()`
- **Key Features**: ijson streaming, thread reconstruction, 2-stage filtering

### `generate_heavy_hitters.py`
```python
# Extract threads with 500+ words
# Generates markdown files for manual review
```
- **Functions**: `load_threads()`, `generate_markdown()`, `create_index()`
- **Output Format**: Individual markdown files with metadata

### `theme_classifier.py`
```python
# Apply themes to all threads
classifier = ThemeClassifier("THEMES_EXTRACTED.md")
classifier.classify_all_threads()
```
- **Classes**: `ThemeClassifier`
- **Methods**: `load_themes()`, `classify_thread()`, `generate_markdown()`

## 🔧 Configuration Files

### `pyproject.toml`
- Project metadata and dependencies
- Optional dependency groups: `[dev]`, `[logging]`, `[extras]`
- Minimal core dependencies (8 packages)

### `mkdocs.yml`
- MkDocs configuration
- Material theme settings
- Navigation structure
- Plugin configuration

### `requirements.txt`
- Core dependencies only
- Synchronized with pyproject.toml
- Use for basic installation

## 📈 Metrics & Stats

### Processing Metrics
- **Input Size**: 37MB (tweets.js)
- **Total Tweets**: 21,723
- **Filtered Threads**: 1,363 (6.3% retention)
- **Heavy Hitters**: 59 (4.3% of threads)
- **Total Words**: ~200,000 in heavy hitters

### Performance
- **Memory Usage**: <100MB (streaming)
- **Processing Time**: ~2 minutes
- **Cost Savings**: $108 (API) → $0 (local)

### Content Distribution
- Philosophy: TBD after classification
- Politics: TBD after classification
- Both: TBD after classification
- Other themes: TBD after extraction

## 🔗 Related Documentation

### Internal Docs
- [Architecture](ARCHITECTURE.md) - Technical design details
- [API Reference](API.md) - Detailed script documentation
- [Status](STATUS.md) - Current project state
- [Workflow](workflow.md) - Step-by-step guide

### External Resources
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [ijson Documentation](https://github.com/ICRAR/ijson)

## 🎯 Next Actions

1. **USER ACTION REQUIRED**: Review heavy hitter threads in `docs/heavy_hitters/`
2. Extract themes and save as `THEMES_EXTRACTED.md`
3. Run `python scripts/theme_classifier.py`
4. Generate final markdown structure
5. Configure and deploy MkDocs site

---

*Last updated: September 2025*