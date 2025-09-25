# Configuration Management Quick Start Guide

## Overview

This guide helps you implement the new configuration management system for DremelDocs, following MkDocs Material best practices.

## Immediate Benefits

1. **No more hardcoded paths** - All paths in `config/pipeline.yml`
2. **Environment switching** - Easy dev/staging/prod configuration
3. **Cleaner scripts** - Configuration separated from code
4. **MkDocs Material compliance** - Following official best practices
5. **Duplicate prevention** - Built into pipeline configuration

## Quick Implementation (10 minutes)

### Step 1: Create Environment File

  ```bash
  # Create .env file for local settings

  ```

### Step 2: Update Scripts to Use Configuration

Add to your Python scripts:

```python
import yaml
from pathlib import Path

# Load pipeline configuration
config_path = Path(__file__).parent.parent / "config" / "pipeline.yml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Use configuration instead of hardcoded paths
input_file = config['stages']['filtering']['input']
output_file = config['stages']['filtering']['output']
```

### Step 3: Test New Configuration

```bash
# Test that scripts still work with configuration
uv run python scripts/theme_classifier.py --clear-only

# Verify site still builds
mkdocs serve
```

## Full Implementation Plan

### Phase 1: Basic Setup (Today)
- [x] Config directory structure created
- [x] `pipeline.yml` configuration file created
- [ ] Update `theme_classifier.py` to use config
- [ ] Test pipeline with configuration

### Phase 2: Script Updates (This Week)
- [ ] Update `local_filter_pipeline.py` to use config
- [ ] Update `generate_heavy_hitters.py` to use config
- [ ] Create `ConfigLoader` class for all scripts
- [ ] Remove hardcoded paths

### Phase 3: Environment Setup (Next Week)
⬜ Create dev/staging/prod configurations
⬜ Setup environment switching
⬜ Add CI/CD configuration
⬜ Document deployment process

## Configuration Files Created

1. **`config/CONFIGURATION_ARCHITECTURE.md`** - Complete specification (35KB)
2. **`config/pipeline.yml`** - Pipeline configuration
3. **`config/QUICK_START.md`** - This guide

## Next Steps

1. Review `CONFIGURATION_ARCHITECTURE.md` for full details
2. Update one script to test configuration approach
3. Gradually migrate all scripts to use configuration
4. Add environment-specific settings as needed

## Key Configuration Patterns

### Loading Configuration in Python

```python
import yaml

def load_config(config_name="pipeline"):
    """Load configuration file."""
    config_path = Path(__file__).parent.parent / "config" / f"{config_name}.yml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# Use in script
config = load_config("pipeline")
output_dir = config["stages"]["heavy_hitters"]["output"]
```

### Environment Variables in YAML

```yaml
# Use !ENV pattern in config files
site_url: !ENV [SITE_URL, "http://localhost:8000"]
debug: !ENV [DEBUG, false]
```

### Clearing Markdown (Already Implemented)

Your `theme_classifier.py` already has the clearing feature:

```bash
# Clear only
uv run python scripts/theme_classifier.py --clear-only

# Clear and regenerate
uv run python scripts/theme_classifier.py

# Skip clearing
uv run python scripts/theme_classifier.py --no-clear
```

## MkDocs Material Best Practices Applied

1. **Plugin Order**: Search plugin first
2. **Environment Variables**: Using !ENV pattern
3. **Meta Plugin**: Support for .meta.yml files
4. **Feature Flags**: Standard Material features
5. **Cache Management**: .cache/ directory structure
6. **Privacy Plugin**: Self-hosting assets

## Support

- Full specification: `config/CONFIGURATION_ARCHITECTURE.md`
- MkDocs Material docs: https://squidfunk.github.io/mkdocs-material/
- Configuration issues: Check paths are relative to project root
- Environment issues: Verify .env file is loaded
