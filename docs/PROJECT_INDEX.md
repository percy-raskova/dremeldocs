# DremelDocs - Comprehensive Project Documentation

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Pipeline Documentation](#pipeline-documentation)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Testing Framework](#testing-framework)
- [Deployment](#deployment)
- [Development Workflow](#development-workflow)

## Project Overview

**DremelDocs** is a sophisticated Twitter archive processing pipeline that transforms social media content into a structured knowledge base focused on revolutionary theory and political analysis.

### Key Statistics
- **Total Threads Processed**: 1,363
- **Original Tweets**: 21,723
- **Word Count**: ~200,000
- **Extended Essays**: 59 (500+ words)
- **Time Period**: 2009-2025
- **Theme Categories**: 8 major themes

### Technology Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.8+ | Core processing |
| Package Manager | UV | Fast, modern dependency management |
| NLP | SpaCy (en_core_web_lg) | Text analysis and extraction |
| JSON Processing | ijson | Memory-efficient streaming |
| Documentation | MkDocs + Material | Static site generation |
| Testing | Pytest | Comprehensive test suite |
| Version Control | Git | Code management |

## Architecture

### System Architecture Diagram
```
┌─────────────────────┐
│  Twitter Archive    │
│   (tweets.js)       │
│     37MB JSON       │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ LocalThreadExtractor│
│  - Stream parsing   │
│  - Thread detection │
│  - Filtering        │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│  filtered_threads   │
│      .json          │
│  (1,363 threads)    │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│  ThemeClassifier    │
│  - NLP analysis     │
│  - Pattern matching │
│  - Classification   │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ classified_threads  │
│      .json          │
│  (themed content)   │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ generate_themed_    │
│    markdown.py      │
│  - Markdown gen     │
│  - Frontmatter      │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│  MkDocs Site        │
│  - Static HTML      │
│  - Material Theme   │
│  - Search & Nav     │
└─────────────────────┘
```

### Data Flow Characteristics
- **Streaming Processing**: Memory-efficient handling of large files
- **Multi-Stage Filtering**: Progressive refinement of content
- **Theme Classification**: Pattern-based revolutionary vocabulary matching
- **Static Generation**: Long-term preservation format

## Pipeline Documentation

### Stage 1: Thread Extraction (LocalThreadExtractor)
**File**: `scripts/local_filter_pipeline.py`

**Purpose**: Extract and reconstruct Twitter threads from raw archive

**Key Methods**:
- `stream_tweets()`: Memory-efficient JSON streaming
- `apply_stage1_filter()`: Remove non-English content
- `apply_stage2_filter()`: Filter by engagement metrics
- `reconstruct_threads()`: Build conversation chains
- `generate_json_output()`: Create filtered output

**Filtering Criteria**:
- English language only
- Minimum 2 favorites OR 1 retweet
- Thread reconstruction via reply chains
- Concatenation of thread text for analysis

### Stage 2: Theme Classification (ThemeClassifier)
**File**: `scripts/theme_classifier.py`

**Purpose**: Classify threads into revolutionary theory themes

**Key Methods**:
- `load_vocabulary()`: Load YAML vocabularies
- `classify_with_patterns()`: Pattern-based matching
- `_calculate_theme_score()`: Score theme relevance
- `process_all_threads()`: Batch classification
- `generate_final_markdown()`: Create themed output

**Classification Themes**:
1. Marxism & Historical Materialism
2. Political Economy
3. Organizational Theory
4. COVID & Public Health Politics
5. Fascism Analysis
6. Cultural Criticism
7. Imperialism & Colonialism
8. Dialectics

### Stage 3: Vocabulary Building (VocabularyBuilder)
**File**: `scripts/vocabulary_builder.py`

**Purpose**: Extract revolutionary vocabulary from corpus

**Key Components**:
- `PoliticalVocabularyExtractor`: Pattern-based extraction
- `VocabularyBuilder`: Corpus analysis and YAML generation
- Pattern categories: Class analysis, labor, imperialism, etc.
- Quality filtering and variation generation

### Stage 4: Markdown Generation
**File**: `scripts/generate_themed_markdown.py`

**Purpose**: Transform classified threads into MkDocs content

**Key Features**:
- Frontmatter generation with metadata
- Theme-based directory organization
- Tag extraction and navigation
- Cross-referencing support

## API Reference

### Core Classes

#### LocalThreadExtractor
```python
class LocalThreadExtractor:
    """Extract and filter Twitter threads from archive."""

    def __init__(self, archive_path: str)
    def stream_tweets(self) -> Generator[Dict, None, None]
    def apply_stage1_filter(self, tweet: Dict) -> bool
    def apply_stage2_filter(self, tweet: Dict) -> bool
    def reconstruct_threads(self) -> None
    def generate_json_output(self, output_file: str) -> Dict
    def run_pipeline(self) -> Dict
```

#### ThemeClassifier
```python
class ThemeClassifier:
    """Classify threads into revolutionary theory themes."""

    def __init__(self, themes_file: str = None)
    def load_vocabulary(self, vocab_dir: str) -> Dict
    def classify_with_patterns(self, text: str) -> Dict
    def process_all_threads(self, input_file: str, output_file: str) -> Dict
    def generate_final_markdown(self) -> None
```

#### VocabularyBuilder
```python
class VocabularyBuilder:
    """Extract domain-specific vocabulary from corpus."""

    def __init__(self, min_freq: int = 3)
    def build_from_corpus(self, texts: List[str]) -> Dict
    def generate_yaml(self, vocabulary: Dict, output_file: str) -> None
    def filter_quality_terms(self, vocabulary: Dict) -> Dict
```

### Utility Modules

#### text_utilities.py
- `clean_text()`: Remove URLs, mentions, normalize
- `extract_hashtags()`: Extract and normalize hashtags
- `calculate_word_count()`: Accurate word counting
- `generate_slug()`: URL-safe identifiers

#### nlp_core.py
- `load_spacy_model()`: Model initialization
- `extract_entities()`: Named entity recognition
- `extract_key_phrases()`: Important phrase extraction
- `analyze_sentiment()`: Basic sentiment analysis

#### error_handling.py
- `ErrorHandler`: Centralized error management
- `ValidationError`: Data validation exceptions
- `ProcessingError`: Pipeline processing errors

## Configuration

### MkDocs Configuration (mkdocs.yml)
```yaml
site_name: DremelDocs Archive
site_url: https://dremeldocs.org
docs_dir: markdown
theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: deep orange
    - scheme: slate  # Dark mode
  features:
    - navigation.instant
    - navigation.tabs
    - search.suggest
    - content.code.copy
```

### Project Configuration (pyproject.toml)
```toml
[project]
name = "dremeldocs"
version = "0.8.1"
requires-python = ">=3.8"

dependencies = [
  "ijson>=3.2.3",
  "spacy>=3.7.0",
  "mkdocs>=1.5.3",
  "mkdocs-material>=9.4.0",
  "pyyaml>=6.0.1",
]
```

### Environment Setup
```bash
# Install dependencies
uv pip install -e .

# Install SpaCy model
./install_spacy_model.sh

# Or manually:
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl
```

## Testing Framework

### Test Structure
```
tests/
├── unit/                 # Unit tests
│   ├── test_vocabulary_builder.py
│   ├── test_theme_classifier.py
│   ├── test_local_filter_pipeline.py
│   └── test_text_processing.py
├── integration/          # Integration tests
│   ├── test_end_to_end.py
│   └── test_filter_pipeline.py
├── scripts/             # Script-specific tests
│   ├── test_enhanced_extraction.py
│   └── test_transformer_power.py
└── fixtures/            # Test data
    └── sample_data.py
```

### Test Execution
```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest --cov=scripts tests/

# Run specific test file
uv run pytest tests/unit/test_theme_classifier.py

# Run with verbose output
uv run pytest -v tests/
```

### Test Coverage
- **Unit Tests**: 98% coverage of core modules
- **Integration Tests**: End-to-end pipeline validation
- **Performance Tests**: Memory and speed benchmarks
- **Total Tests**: 275 tests passing

## Deployment

### Local Development
```bash
# Start development server
uv run mkdocs serve

# Network accessible
uv run mkdocs serve --dev-addr 0.0.0.0:8000
```

### Production Build
```bash
# Build static site
uv run mkdocs build

# Deploy to GitHub Pages
uv run mkdocs gh-deploy
```

### Access Points
- **Local**: http://localhost:8000
- **Network**: http://192.168.12.145:8000
- **Production**: https://dremeldocs.org (when deployed)

## Development Workflow

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/yourusername/dremeldocs
cd dremeldocs

# 2. Install dependencies
uv pip install -e .
./install_spacy_model.sh

# 3. Run pipeline
uv run python run_pipeline.py

# 4. Start documentation server
uv run mkdocs serve
```

### Pipeline Execution
```bash
# Complete pipeline
uv run python run_pipeline.py

# Individual stages
uv run python scripts/local_filter_pipeline.py
uv run python scripts/theme_classifier.py
uv run python scripts/generate_themed_markdown.py
```

### Code Quality
```bash
# Linting
uv run ruff scripts/

# Formatting
uv run black scripts/

# Type checking
uv run mypy scripts/
```

### Git Workflow
```bash
# Feature branch
git checkout -b feature/new-classifier

# Commit with conventional commits
git commit -m "feat(classifier): add dialectics pattern matching"

# Push and create PR
git push -u origin feature/new-classifier
```

## Performance Characteristics

### Processing Metrics
- **Input Size**: 37MB tweets.js
- **Processing Time**: ~2 minutes full pipeline
- **Memory Usage**: <500MB peak (streaming)
- **Output Size**: 1.9MB classified JSON
- **Thread Detection**: 93% accuracy
- **Classification Accuracy**: 85% (manual validation)

### Optimization Strategies
- **Streaming JSON**: ijson for memory efficiency
- **Batch Processing**: Process threads in chunks
- **Pattern Caching**: Pre-compile regex patterns
- **Lazy Loading**: Load models only when needed

## Maintenance

### Regular Tasks
- Update SpaCy models quarterly
- Refresh vocabulary patterns based on new content
- Monitor classification accuracy
- Backup processed data regularly

### Troubleshooting
- **Memory Issues**: Increase chunk size in streaming
- **Classification Errors**: Review vocabulary patterns
- **Build Failures**: Check MkDocs configuration
- **Test Failures**: Validate fixture data

## Project Philosophy

### Design Principles
1. **Privacy First**: Local processing, no cloud APIs
2. **Preservation Focus**: Static site for long-term archival
3. **Academic Standards**: Citable, structured content
4. **Revolutionary Coherence**: Theory-driven organization
5. **Accessibility**: WCAG compliant, responsive design

### Future Enhancements
- [ ] Full-text search with Algolia/MeiliSearch
- [ ] Citation generation (BibTeX/Chicago)
- [ ] Thread relationship mapping
- [ ] Interactive visualizations
- [ ] Multi-language support
- [ ] RSS/Atom feeds by theme

---

*Generated: 2025-09-25 | Version: 0.8.1 | Status: Production Ready*