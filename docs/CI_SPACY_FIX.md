# CI SpaCy Model Installation Fix

## Problem Diagnosis

### Root Cause
The GitHub Actions workflow was failing with "No SpaCy model found" error because:

1. **Installation mismatch**: SpaCy model was installed with `uv pip install --system` (system-wide)
2. **Execution context**: Scripts were run with `uv run python`, which creates a **virtual environment** (.venv)
3. **Result**: The system-installed SpaCy model was not accessible to the virtual environment

### Error Log Analysis
```
⚠️  No SpaCy model found. Please install one with:
    # For MAXIMUM VOCABULARY (recommended):
    uv pip install https://github.com/explosion/...
```

This error appeared when running `vocabulary_builder.py` via `uv run python`, confirming the virtual environment couldn't find the system-installed model.

## Solution Implemented

### Key Changes to `.github/workflows/deploy.yml`

1. **Removed `--system` flag**: Install dependencies in virtual environment
   ```yaml
   # Before: uv pip install --system -e .
   # After:  uv sync --frozen
   ```

2. **Install SpaCy model in venv**: Use same installation context
   ```yaml
   # Before: uv pip install --system https://...
   # After:  uv pip install https://...  (no --system flag)
   ```

3. **Added UV cache**: Speed up dependency installation
   ```yaml
   - name: Install uv
     uses: astral-sh/setup-uv@v3
     with:
       version: "latest"
       enable-cache: true  # NEW
   ```

4. **Added SpaCy model cache**: Avoid re-downloading 480MB model
   ```yaml
   - name: Cache SpaCy model
     id: cache-spacy
     uses: actions/cache@v4
     with:
       path: ~/.cache/spacy
       key: spacy-model-en_core_web_lg-3.8.0-${{ runner.os }}
   ```

### Complete Installation Flow
```bash
# 1. Install project dependencies in virtual environment
uv sync --frozen

# 2. Install SpaCy model in the SAME virtual environment
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl

# 3. Run scripts using the virtual environment
uv run python scripts/vocabulary_builder.py
uv run python scripts/theme_classifier.py
uv run python scripts/generate_themed_markdown.py
```

## Benefits

### Performance Improvements
- **UV cache**: Faster dependency installation on subsequent runs
- **SpaCy model cache**: Avoid re-downloading 480MB model (~30-60 second savings)
- **Frozen lockfile**: Consistent, reproducible builds

### Reliability Improvements
- **Consistent environment**: Virtual environment used for both installation and execution
- **No system pollution**: All dependencies isolated to project virtual environment
- **Lockfile-based**: Uses `uv.lock` for exact dependency versions

## Testing

### Verification Steps
1. Push changes to trigger GitHub Actions workflow
2. Check "Install dependencies" step completes successfully
3. Verify "Generate markdown" step can import SpaCy model
4. Confirm subsequent runs use cached SpaCy model

### Expected Results
- ✅ First run: Downloads and caches SpaCy model (~480MB)
- ✅ Subsequent runs: Uses cached model (instant)
- ✅ Scripts successfully import and use `en_core_web_lg` model
- ✅ No "No SpaCy model found" errors

## Technical Context

### UV Virtual Environment Behavior
When you run `uv run python script.py`:
1. UV creates/activates a virtual environment at `.venv/`
2. Installs dependencies from `pyproject.toml` (via `uv.lock`)
3. Runs the script within that virtual environment

**Key insight**: `--system` packages are NOT accessible from this virtual environment.

### Why `uv sync` Instead of `uv pip install -e .`
- `uv sync`: Installs from lockfile (`uv.lock`) for reproducibility
- `--frozen`: Fails if lockfile is out of sync with `pyproject.toml`
- Ensures CI uses exact same versions as local development

### SpaCy Model Installation
The SpaCy model is a 480MB wheel file that must be:
1. Downloaded from GitHub releases (not PyPI)
2. Installed in the SAME Python environment as SpaCy library
3. Available to the `spacy` package at runtime

## Alternative Approaches Considered

### ❌ Option 1: Continue using `--system`
**Problem**: Would require changing all `uv run python` to `python3` (system Python), losing virtual environment benefits

### ❌ Option 2: Manual virtual environment activation
**Problem**: Adds complexity, requires `source .venv/bin/activate` in shell scripts

### ✅ Option 3: Align installation and execution contexts (chosen)
**Benefits**:
- Simple and consistent
- Leverages UV's built-in virtual environment management
- Enables caching for faster builds
- Matches local development workflow

## Future Improvements

### Potential Optimizations
1. **Pre-built Docker image**: Include SpaCy model in base image
2. **Artifact caching**: Cache entire `.venv` directory
3. **Conditional installation**: Skip SpaCy model if classification not needed

### Monitoring
- Track workflow duration to verify caching benefits
- Monitor cache hit rates for UV and SpaCy model
- Check for any dependency conflicts with lockfile approach

---

**Author**: Claude Code (DevOps Architect persona)
**Date**: 2025-10-08
**Workflow**: `.github/workflows/deploy.yml`
**Related**: `install_spacy_model.sh`, `pyproject.toml`, `uv.lock`
