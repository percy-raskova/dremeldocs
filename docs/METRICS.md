# Documentation Metrics System

## Overview

The DremelDocs repository uses a centralized metrics system to ensure consistency across all documentation files. This eliminates discrepancies between README.md, CLAUDE.md, copilot-instructions.md, and other documentation.

## Problem Solved

Previously, documentation files contained hardcoded statistics that could become out of sync:
- README showed different thread counts than CLAUDE.md
- Theme distributions varied across files
- No single source of truth for repository metrics

## Solution

A two-script system that:
1. **Extracts metrics** from the actual repository state
2. **Substitutes template variables** in documentation files

### Single Source of Truth

All metrics are stored in `data/metrics.json`, generated from:
- Actual markdown files in `markdown/` directories
- Thread metadata in `data/classified_threads.json`
- Version information from `pyproject.toml`
- Word counts across all content

## Usage

### Extract Latest Metrics

```bash
# Using make
make metrics

# Or directly
python scripts/extract_metrics.py
```

This generates `data/metrics.json` with current repository statistics.

### Update Documentation

```bash
# Preview changes (dry-run)
make metrics-check

# Update all documentation
make metrics-update

# Or update specific files
python scripts/update_docs_metrics.py --files README.md CLAUDE.md
```

### Check Current Metrics

```bash
# View formatted metrics display
python scripts/extract_metrics.py

# View raw JSON
cat data/metrics.json | jq
```

## Template Variable Format

In any markdown file, use double curly braces to reference metrics:

```markdown
This repository contains {{content.total_markdown_files}} markdown files
across {{themes.marxism.markdown_files}} Marxism threads.
```

After running `make metrics-update`, this becomes:

```markdown
This repository contains 559 markdown files
across 308 Marxism threads.
```

## Available Metrics

### Top-Level Metrics

```
{{version}}                              # 0.8.1
{{generated_at}}                         # 2025-11-07
```

### Repository Information

```
{{repository.name}}                      # dremeldocs
{{repository.status}}                    # production_ready
{{repository.description}}               # Twitter archive processing pipeline...
```

### Source Data

```
{{source_data.total_tweets_processed}}   # 21,723
{{source_data.original_archive_size_mb}} # 37
```

### Content Statistics

```
{{content.total_markdown_files}}         # 559
{{content.total_words}}                  # 187,886
{{content.average_words_per_file}}       # 336
```

### Theme Metrics

Each theme has:
- `name` - Full display name
- `markdown_files` - Number of markdown files
- `words` - Total word count
- `directory` - Directory name

```
{{themes.marxism.name}}                  # Marxism & Historical Materialism
{{themes.marxism.markdown_files}}        # 308
{{themes.marxism.words}}                 # 118,446

{{themes.economy.name}}                  # Political Economy
{{themes.economy.markdown_files}}        # 45

{{themes.covid.name}}                    # COVID & Public Health Politics
{{themes.covid.markdown_files}}          # 50
```

Available theme keys:
- `marxism` - Marxism & Historical Materialism
- `economy` - Political Economy
- `organizing` - Organizational Theory
- `covid` - COVID & Public Health Politics
- `fascism` - Fascism Analysis
- `culture` - Cultural Criticism
- `imperialism` - Imperialism & Colonialism
- `dialectics` - Dialectics
- `uncategorized` - Uncategorized

### Technology Stack

```
{{technology.python.required}}           # 3.8
{{technology.python.recommended}}        # 3.12
{{technology.package_manager}}           # uv
{{technology.nlp.library}}               # spacy
{{technology.nlp.model}}                 # en_core_web_lg
{{technology.testing.framework}}         # pytest
{{technology.testing.coverage_target}}   # 96.7
```

### Deployment

```
{{deployment.live_site}}                 # https://percy-raskova.github.io/dremeldocs/
{{deployment.ci_cd}}                     # GitHub Actions
```

## How It Works

### 1. Extract Metrics (`extract_metrics.py`)

```python
# Counts actual markdown files per theme
markdown_dir = Path("markdown")
for theme in ["marxism", "economy", ...]:
    count = len(list((markdown_dir / theme).glob("*.md")))

# Counts words in all markdown content
for md_file in all_markdown_files:
    words += len(md_file.read_text().split())

# Reads version from pyproject.toml
version = extract_from_toml('version = "0.8.1"')
```

**Output**: `data/metrics.json` with all statistics

### 2. Substitute Variables (`update_docs_metrics.py`)

```python
# Find template variables: {{path.to.metric}}
pattern = r'\{\{([a-zA-Z0-9._]+)\}\}'

# Replace with actual values from metrics.json
"{{content.total_markdown_files}}" → "559"
"{{themes.marxism.name}}" → "Marxism & Historical Materialism"
```

**Output**: Updated markdown files with current metrics

## Workflow

### For Regular Updates

1. Make changes to content (add markdown files, modify code)
2. Extract metrics: `make metrics`
3. Update docs: `make metrics-update`
4. Commit both code changes and updated documentation

### For Adding New Metrics

1. Modify `extract_metrics.py` to collect new metric
2. Run `make metrics` to regenerate `metrics.json`
3. Use new metric in templates: `{{new.metric.path}}`
4. Run `make metrics-update`
5. Document the new metric in this file

### For New Documentation Files

1. Create markdown file with template variables
2. Add file path to `update_docs_metrics.py` defaults (if standard doc)
3. Or update manually: `python scripts/update_docs_metrics.py --files newfile.md`

## Examples

### Example: Adding Thread Count to README

**Before**:
```markdown
This repository contains 585 threads on Marxism.
```

**After** (using template):
```markdown
This repository contains {{themes.marxism.markdown_files}} threads on Marxism.
```

**After** running `make metrics-update`:
```markdown
This repository contains 308 threads on Marxism.
```

### Example: Theme Distribution Table

```markdown
| Theme | Files | Words |
|-------|-------|-------|
| {{themes.marxism.name}} | {{themes.marxism.markdown_files}} | {{themes.marxism.words}} |
| {{themes.economy.name}} | {{themes.economy.markdown_files}} | {{themes.economy.words}} |
```

Becomes:
```markdown
| Theme | Files | Words |
|-------|-------|-------|
| Marxism & Historical Materialism | 308 | 118,446 |
| Political Economy | 45 | 14,742 |
```

## Current Statistics

Run `python scripts/extract_metrics.py` to see current statistics, which include:

- **Total Tweets Processed**: 21,723
- **Total Markdown Files**: 559
- **Total Words**: 187,886
- **Average Words/File**: 336
- **Theme Distribution**: 9 themes with detailed breakdown

## Benefits

✅ **Consistency**: All documentation uses the same numbers
✅ **Accuracy**: Metrics extracted from actual repository state
✅ **Automation**: Single command updates everything
✅ **Maintainability**: Easy to add new metrics
✅ **Transparency**: Clear source of truth in version control
✅ **Validation**: Easy to verify numbers are current

## Implementation Notes

### Number Formatting

- Integers ≥ 1000 are formatted with commas: `21,723`
- Smaller numbers are plain: `308`
- Strings and floats are unchanged

### File Selection

Default files updated:
- `README.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`

Custom files can be specified with `--files` argument.

### Error Handling

- Missing metrics paths return original template
- Missing files are skipped with warning
- Dry-run mode available for safety

## Makefile Targets

```bash
make metrics         # Extract metrics to data/metrics.json
make metrics-update  # Update all documentation files
make metrics-check   # Preview updates (dry-run)
```

## Scripts

### `scripts/extract_metrics.py`

Extracts metrics from repository state:
- Counts markdown files per theme
- Counts words in all content
- Reads version from pyproject.toml
- Generates data/metrics.json

**Usage**: `python scripts/extract_metrics.py`

### `scripts/update_docs_metrics.py`

Substitutes template variables in documentation:
- Finds `{{metric.path}}` patterns
- Replaces with values from metrics.json
- Supports dry-run mode
- Can target specific files

**Usage**: 
```bash
python scripts/update_docs_metrics.py              # Update defaults
python scripts/update_docs_metrics.py --dry-run    # Preview
python scripts/update_docs_metrics.py --files FILE # Update specific
```

## Future Enhancements

Potential improvements:
- [ ] Add CI check to verify metrics are current
- [ ] Include vocabulary term counts
- [ ] Add test coverage percentage from pytest
- [ ] Track metrics over time for trends
- [ ] Generate metrics changelog
- [ ] Add more granular word statistics

## Contributing

When adding content:
1. Update content (add markdown, modify code)
2. Run `make metrics` to extract new numbers
3. Run `make metrics-update` to update docs
4. Commit changes including updated metrics.json

When modifying metrics:
1. Update `extract_metrics.py`
2. Regenerate `metrics.json`
3. Update this documentation
4. Update template variables in docs as needed

---

*Last updated: 2025-11-07*
*Part of the DremelDocs documentation consistency system*
