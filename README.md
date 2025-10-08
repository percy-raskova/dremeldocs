# DremelDocs

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![MkDocs](https://img.shields.io/badge/mkdocs-material-blue.svg)](https://squidfunk.github.io/mkdocs-material/)
[![Tests](https://img.shields.io/badge/tests-96.7%25-green.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive archive of 21,723 tweets organized into 1,363 thematically classified threads on revolutionary theory, extracted from Twitter/X for preservation, study, and cross-analysis.

## 📚 Overview

DremelDocs is a completed Twitter archive processing pipeline that transforms raw tweet data into a navigable, theme-based documentation site. Using advanced NLP techniques and Marxist political vocabulary extraction, the project classifies and organizes revolutionary discourse for researchers, activists, and scholars.

### Key Features

- **🔄 Automated Processing**: Complete pipeline from raw tweets.js to organized documentation
- **🏷️ Theme Classification**: 8 revolutionary theory themes using NLP and pattern matching
- **📖 Vocabulary Extraction**: 858+ revolutionary terms automatically extracted
- **🔍 Cross-Analysis**: Threads with multiple themes accessible for intersectional study
- **📱 Modern UI**: MkDocs Material theme with responsive design
- **🔒 Privacy-First**: All processing done locally, no cloud APIs required

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Total Tweets Processed** | 21,723 |
| **Threads Extracted** | 1,363 |
| **Themes Identified** | 8 + uncategorized |
| **Revolutionary Terms** | 858 |
| **Test Coverage** | 96.7% |
| **Processing Time** | ~2 minutes |

### Theme Distribution

- **Marxism & Historical Materialism**: 585 threads
- **Political Economy**: 82 threads
- **Organizational Theory**: 40 threads
- **COVID & Public Health Politics**: 140 threads
- **Fascism Analysis**: 101 threads
- **Cultural Criticism**: 39 threads
- **Imperialism & Colonialism**: 44 threads
- **Dialectics**: 11 threads
- **Uncategorized**: 321 threads

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- uv (recommended) or pip
- 100MB+ free disk space
- SpaCy English language model

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/percy-raskova/dremeldocs.git
   cd dremeldocs
   ```

2. Install dependencies with uv (recommended):
   ```bash
   uv pip install -e .
   ```

   Or with pip:
   ```bash
   pip install -e .
   ```

3. Install the SpaCy language model:
   ```bash
   ./install_spacy_model.sh
   # Or manually:
   python -m spacy download en_core_web_sm
   ```

### Quick Start

```bash
# View the documentation site
make serve
# Browse to http://localhost:8000

# Or manually:
uv run mkdocs serve
```

## 🔧 Pipeline Usage

The complete pipeline is already run with all content generated. To re-run or modify:

### Complete Pipeline

```bash
# Run entire pipeline (if starting fresh)
echo "y" | make pipeline

# Individual steps:
make extract-vocabulary   # Extract revolutionary vocabulary
make classify            # Classify threads by theme
make generate           # Generate markdown files
make serve             # Start documentation server
```

### Data Processing Only

```bash
# Generate markdown from existing classifications
python scripts/generate_themed_markdown.py

# Clean and regenerate
make clean-markdown
make generate
```

## 🏗️ Architecture

### Pipeline Components

```
1. vocabulary_builder.py
   ├── Extracts Marxist/revolutionary vocabulary
   ├── Pattern-based concept detection
   └── Outputs: data/vocabularies/*.yaml

2. theme_classifier.py
   ├── Uses vocabularies for classification
   ├── Confidence-based theme assignment
   └── Outputs: data/classified_threads.json

3. generate_themed_markdown.py
   ├── Creates markdown from classified data
   ├── Organizes by theme directories
   └── Outputs: markdown/[theme]/
```

### Directory Structure

```
dremeldocs/
├── data/
│   ├── tweets.js              # Original Twitter archive
│   ├── classified_threads.json # 1,363 classified threads
│   └── vocabularies/          # Extracted vocabularies
├── markdown/
│   ├── marxism/               # 585 threads
│   ├── economy/               # 82 threads
│   ├── organizing/            # 40 threads
│   ├── covid/                 # 140 threads
│   ├── fascism/               # 101 threads
│   ├── culture/               # 39 threads
│   ├── imperialism/           # 44 threads
│   ├── dialectics/            # 11 threads
│   └── uncategorized/         # 321 threads
├── scripts/
│   ├── vocabulary_builder.py  # Vocabulary extraction
│   ├── theme_classifier.py    # Theme classification
│   └── generate_themed_markdown.py # Markdown generation
└── tests/                     # 96.7% passing test suite
```

## 🧪 Development

### Testing

```bash
# Run all tests
uv run pytest tests/

# Run specific test suites
uv run pytest tests/unit/          # Unit tests
uv run pytest tests/integration/   # Integration tests

# Run with coverage
uv run pytest --cov=scripts tests/
```

### Code Quality

```bash
# Format code
uv run black scripts/

# Lint code
uv run ruff scripts/

# Type checking (if configured)
uv run mypy scripts/
```

### Performance

- **Processing Speed**: ~2 minutes for full pipeline
- **Memory Usage**: Efficient streaming JSON processing
- **Input Size**: 37MB tweets.js
- **Output Size**: 1.9MB classified JSON + markdown files

## 🎯 Key Concepts

### Theme Classification

The system uses pattern-based classification with Marxist political vocabulary:

```python
# Example patterns
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

### Vocabulary Extraction

Automated extraction of revolutionary terminology:
- Class analysis terms
- Historical materialism concepts
- Organizational theory vocabulary
- Anti-imperialist language
- Critical theory terms

### Cross-Analysis

Threads with multiple themes enable intersectional study:
- Primary theme classification
- Secondary theme relationships
- Cross-cutting analysis possibilities

## 📝 Documentation

### User Guides
- [Installation Guide](docs/installation.md)
- [Pipeline Documentation](docs/pipeline.md)
- [Theme Classification](docs/classification.md)

### Developer Documentation
- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api.md)
- [Testing Guide](docs/testing.md)

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- **UI/UX**: Enhance the MkDocs theme and navigation
- **Classification**: Improve theme detection patterns
- **Vocabulary**: Expand revolutionary terminology extraction
- **Performance**: Optimize processing for larger archives
- **Testing**: Increase test coverage beyond 96.7%

Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📚 Related Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [SpaCy NLP](https://spacy.io/)
- [Revolutionary Theory Resources](docs/resources.md)

## 🛠️ Troubleshooting

### Common Issues

1. **SpaCy model not found**: Run `./install_spacy_model.sh`
2. **MkDocs warnings**: Normal for auto-discovery mode, content still accessible
3. **Long processing time**: Expected for 21,723 tweets (~10 minutes)
4. **Memory issues**: Ensure 1GB+ RAM available

### Support

- [GitHub Issues](https://github.com/percy-raskova/dremeldocs/issues)
- [Documentation](https://percy-raskova.github.io/dremeldocs/)

## 🚀 Deployment

### GitHub Pages Deployment

This repository is configured for automatic deployment to GitHub Pages.

#### Automatic Deployment (Recommended)

1. **Enable GitHub Pages** in your repository settings:
   - Go to Settings → Pages
   - Source: GitHub Actions
   - Branch: Not applicable (using Actions)

2. **Push to main branch**:
   ```bash
   git add .
   git commit -m "Deploy to GitHub Pages"
   git push origin main
   ```

3. **Wait for deployment** (usually 2-3 minutes):
   - Check Actions tab for build status
   - Site will be available at: https://percy-raskova.github.io/dremeldocs/

#### Manual Deployment

If you prefer to deploy manually using MkDocs:

```bash
# Build and deploy in one command
mkdocs gh-deploy --force

# Or build first, then deploy
mkdocs build --clean
mkdocs gh-deploy --force --no-history
```

#### Local Preview

Before deploying, always test locally:

```bash
make serve
# Or
uv run mkdocs serve
# Browse to http://localhost:8000
```

### Deployment Status

[![Deploy to GitHub Pages](https://github.com/percy-raskova/dremeldocs/actions/workflows/deploy.yml/badge.svg)](https://github.com/percy-raskova/dremeldocs/actions/workflows/deploy.yml)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Twitter/X archive export feature for data preservation
- SpaCy team for excellent NLP tools
- MkDocs Material theme developers
- Revolutionary theorists whose work informed the classification system

---

*DremelDocs: Preserving revolutionary discourse for future generations*

**Last Updated**: September 2025 | **Version**: 1.0.0 | **Status**: Production Ready