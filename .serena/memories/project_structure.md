# Project Structure

## Current Directory Layout
```
/home/percy/projects/astradocs/
├── .serena/                        # Serena MCP project config
├── .claude/                        # Claude configuration
├── twitter-archives/               # 1.9GB Twitter data export
│   ├── Your archive.html          # Browser viewer
│   └── data/                      # JavaScript data files (not yet extracted)
├── twitter-pipeline-docs/          # Documentation (7 files)
│   ├── 00-quick-start.md
│   ├── 01-data-structure-analysis.md
│   ├── 02-extraction-pipeline.md
│   ├── 03-thread-detection-strategy.md
│   ├── 04-classification-approach.md
│   ├── 05-implementation-plan.md
│   └── 06-technical-specifications.md
├── src/                            # Python source code
│   ├── parser/                    # Archive extraction
│   ├── classifier/                # Content classification
│   ├── processor/                 # Batch processing
│   │   └── batch.py
│   ├── utils/                     # Helper utilities
│   └── extraction.py              # Contains TwitterArchiveExtractor class
├── data/                          # Data directory (empty)
├── docs/                          # MkDocs output (empty)
├── config/                        # Configuration files (empty)
├── logs/                          # Log files (empty)
├── analyze_twitter_structure.py   # Archive analysis script
├── main.py                        # Entry point (minimal)
├── pyproject.toml                 # Python project config
├── requirements.txt               # Python dependencies
├── CLAUDE.md                      # Claude instructions
├── PROJECT_STATE.md              # Project memory
├── SESSION_MEMORY.md             # Session tracking
├── README.md                      # (empty)
├── .gitignore                     # Git ignore rules
├── .python-version                # Python 3.12
├── .mcp.json                      # MCP configuration
└── uv.lock                        # UV package manager lock
```

## Key Directories

### Source Code (`/src/`)
- Organized by functionality
- Each subdirectory handles specific pipeline phase
- Currently sparse - main implementation pending

### Documentation (`/twitter-pipeline-docs/`)
- Comprehensive 6-phase analysis complete
- Quick start guide with code examples
- Technical specifications documented

### Data Directories
- `/twitter-archives/` - Raw Twitter export (READ ONLY)
- `/data/` - Intermediate processing files
- `/docs/` - Final MkDocs output

### Configuration
- `/config/` - YAML settings (to be created)
- `.env` - API keys (not yet created)
- `pyproject.toml` - Python dependencies defined

## Missing Components (To Be Created)
- `/scripts/` - Execution scripts
- `/tests/` - Test files
- `/templates/` - Markdown templates
- `.env` - Environment variables
- `mkdocs.yml` - MkDocs configuration