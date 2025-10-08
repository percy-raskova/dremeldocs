# DremelDocs Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- UV package manager
- 1GB free disk space
- Git (for version control)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/percy-raskova/dremeldocs
cd dremeldocs
```

### 2. Install Dependencies
```bash
# Install Python dependencies
uv pip install -e .

# Install SpaCy language model
./install_spacy_model.sh
```

### 3. Prepare Your Twitter Archive
Place your Twitter archive file at:
```
source/data/tweets.js
```

## Running the Pipeline

### Option 1: One-Command Execution (Recommended)
```bash
uv run python run_pipeline.py
```

This will:
1. Extract threads from your archive
2. Classify them by theme
3. Generate markdown documentation
4. Provide a summary report

### Option 2: Manual Stage Execution
```bash
# Stage 1: Extract threads
uv run python scripts/local_filter_pipeline.py

# Stage 2: Classify themes
uv run python scripts/theme_classifier.py

# Stage 3: Generate markdown
uv run python scripts/generate_themed_markdown.py
```

## Viewing Your Documentation

### Start the Documentation Server
```bash
# Local access only
uv run mkdocs serve

# Network accessible (view from phone/tablet)
uv run mkdocs serve --dev-addr 0.0.0.0:8000
```

### Access Points
- **Local**: http://localhost:8000
- **Network**: http://[your-ip]:8000

## What to Expect

### Processing Time
- Small archive (<10MB): ~30 seconds
- Medium archive (10-50MB): ~2 minutes
- Large archive (>50MB): ~5 minutes

### Output Structure
```
data/
├── filtered_threads.json     # Extracted threads
├── classified_threads.json    # Themed content
└── vocabularies/*.yaml       # Classification patterns

markdown/
├── index.md                  # Home page
├── themes/                   # Theme overview
├── [theme_name]/            # Themed content
│   ├── index.md
│   └── thread_*.md
└── tags.md                  # Tag navigation
```

## Common Commands

### View Statistics
```bash
# Check thread count
jq length data/filtered_threads.json

# View theme distribution
uv run python -c "import json; print(json.load(open('data/classified_threads.json'))['statistics'])"
```

### Rebuild Specific Components
```bash
# Regenerate markdown only
uv run python scripts/generate_themed_markdown.py

# Reclassify with updated vocabulary
uv run python scripts/theme_classifier.py --force

# Clean and rebuild everything
rm -rf data/*.json markdown/* site/
uv run python run_pipeline.py
```

### Testing
```bash
# Run all tests
uv run pytest tests/

# Quick validation
uv run pytest tests/integration/test_end_to_end.py
```

## Customization

### Adjust Classification Themes
Edit vocabularies in `data/vocabularies/`:
```yaml
# Example: marxism_communism.yaml
theme: marxism_historical_materialism
keywords:
  - class struggle
  - dialectical materialism
  # Add your terms here
```

### Modify Site Appearance
Edit `mkdocs.yml`:
```yaml
theme:
  palette:
    primary: indigo    # Change primary color
    accent: deep orange # Change accent color
```

### Change Filtering Criteria
Edit `scripts/local_filter_pipeline.py`:
```python
# Line ~140: Adjust engagement threshold
if tweet.get('favorite_count', 0) >= 2:  # Change minimum favorites
```

## Troubleshooting

### Issue: "SpaCy model not found"
```bash
# Reinstall the model
./install_spacy_model.sh
```

### Issue: "Memory Error"
```bash
# Process in smaller chunks
export CHUNK_SIZE=500
uv run python scripts/local_filter_pipeline.py
```

### Issue: "MkDocs build error"
```bash
# Reinstall MkDocs
uv pip install --force-reinstall mkdocs mkdocs-material
```

### Issue: "No threads found"
Check your archive structure:
```bash
# Verify tweets.js format
head -20 source/data/tweets.js
```

## Getting Help

### Check Documentation
- Project Index: `claudedocs/PROJECT_INDEX.md`
- Pipeline Reference: `claudedocs/PIPELINE_REFERENCE.md`
- Testing Guide: `tests/TESTING_GUIDE.md`

### Debug Mode
```bash
# Run with debug output
LOG_LEVEL=DEBUG uv run python run_pipeline.py
```

### Validate Installation
```bash
# Check all dependencies
uv pip list | grep -E "spacy|mkdocs|ijson"

# Verify SpaCy model
uv run python -c "import spacy; nlp = spacy.load('en_core_web_lg'); print('✓ SpaCy ready')"
```

## Next Steps

1. **Explore the Generated Site**: Browse your processed content
2. **Customize Themes**: Adjust classification patterns in vocabularies
3. **Deploy Online**: Use `mkdocs gh-deploy` for GitHub Pages
4. **Add Custom Pages**: Create additional markdown content
5. **Contribute**: Submit improvements via pull requests

## Performance Tips

- **Use UV**: Always prefix commands with `uv run` for proper environment
- **Close Other Apps**: Free up memory during processing
- **Check Disk Space**: Ensure 500MB free for processing
- **Network Serve**: Use `0.0.0.0:8000` to access from other devices

---

*Quick Start Guide v0.8.1 | Generated: 2025-09-25*