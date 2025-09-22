# Suggested Commands

## Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
# or with uv (if available)
uv pip install -r requirements.txt
```

## Development Commands
```bash
# Run main entry point
python main.py

# Analyze Twitter archive structure
python analyze_twitter_structure.py

# Extract tweets (when implemented)
python -m src.parser.archive_extractor /path/to/archive

# Run classification pipeline (when implemented)
python scripts/run_pipeline.py --archive twitter-archives/
```

## MkDocs Commands
```bash
# Serve documentation locally
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Testing Commands
```bash
# No test framework currently configured
# Suggested: pytest
pytest tests/         # When tests are implemented
```

## Linting and Formatting
```bash
# No linting currently configured
# Suggested tools:
ruff check .         # Fast Python linter
ruff format .        # Python formatter
mypy src/           # Type checking (if type hints added)
```

## Git Commands
```bash
# Check status
git status

# View changes  
git diff

# Create feature branch
git checkout -b feature/name

# Stage and commit
git add .
git commit -m "feat: description"

# View commit history
git log --oneline -10
```

## System Utilities
```bash
# List files
ls -la

# Find files
find . -name "*.py"

# Search in files
grep -r "pattern" src/

# Check disk usage
du -sh twitter-archives/

# Monitor memory usage during processing
watch -n 1 free -h
```

## Data Processing Pipeline (Future)
```bash
# Full pipeline execution
./scripts/run_all.sh twitter-archives/

# Step-by-step execution
python scripts/extract_tweets.py twitter-archives/
python scripts/find_threads.py
python scripts/classify_threads.py  
python scripts/generate_markdown.py
```