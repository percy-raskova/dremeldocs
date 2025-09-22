# Setup Instructions

## Prerequisites

- Python 3.8+
- uv (Python package manager)
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd astradocs
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Install MkDocs (for final site generation):
```bash
uv pip install mkdocs mkdocs-material
```

## Directory Structure

```
astradocs/
├── source/          # Twitter archive data (read-only)
├── scripts/         # Processing scripts
├── data/            # Generated JSON outputs
├── docs/            # Project documentation
├── markdown/        # MkDocs source (final content)
└── site/           # MkDocs HTML output
```

## Quick Start

1. Ensure your Twitter archive is in `source/`
2. Run the processing pipeline: `python scripts/local_filter_pipeline.py`
3. Generate heavy hitters: `python scripts/generate_heavy_hitters.py`
4. Review threads in `docs/heavy_hitters/`
5. Extract themes and save as `THEMES_EXTRACTED.md`
6. Run classifier: `python scripts/theme_classifier.py`
7. Build site: `mkdocs build`