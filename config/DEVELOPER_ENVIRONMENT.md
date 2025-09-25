# Developer Environment Configuration Specification

## Executive Summary

This specification defines a comprehensive developer environment configuration for the DremelDocs project, establishing professional standards for code quality, documentation, testing, and deployment. It emphasizes local-first development, academic rigor, and revolutionary discipline in software engineering practices.

## Table of Contents
1. [Core Philosophy](#core-philosophy)
2. [Python Configuration](#python-configuration)
3. [Linting & Formatting](#linting--formatting)
4. [Documentation Standards](#documentation-standards)
5. [Editor Configuration](#editor-configuration)
6. [Git Workflow](#git-workflow)
7. [Testing Framework](#testing-framework)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Task Automation](#task-automation)
10. [Environment Variables](#environment-variables)
11. [Development Containers](#development-containers)
12. [Implementation Guide](#implementation-guide)

## Core Philosophy

### Principles
- **Local-First**: No cloud dependencies, full offline capability
- **Privacy-Focused**: No telemetry, no external API calls during development
- **Academic Rigor**: Documentation and code quality suitable for citation
- **Revolutionary Discipline**: Consistent standards, collective development practices
- **Performance-Aware**: Optimized for processing large Twitter archives

### Technology Stack
- **Package Manager**: uv (modern, fast Python package management)
- **Python Version**: 3.8+ (broad compatibility)
- **Documentation**: MkDocs Material (professional documentation)
- **NLP**: SpaCy (local processing, no cloud APIs)
- **Testing**: pytest with coverage
- **Linting**: Ruff (fast, comprehensive)
- **Type Checking**: mypy (static type safety)

## Python Configuration

### Enhanced pyproject.toml

```toml
[project]
name = "dremeldocs"
version = "1.0.0"
description = "Revolutionary Theory Archive - Twitter to MkDocs Pipeline"
readme = "README.md"
authors = [{ name = "@BmoreOrganized" }]
license = { text = "MIT" }
requires-python = ">=3.8"
keywords = [
    "twitter",
    "archive",
    "mkdocs",
    "documentation",
    "revolutionary-theory",
    "political-economy",
    "marxism"
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Documentation",
    "Topic :: Text Processing :: Linguistic",
]

dependencies = [
    # Core processing
    "ijson>=3.2.3",              # Streaming JSON for 37MB files
    "spacy>=3.7.0",              # NLP processing

    # MkDocs ecosystem
    "mkdocs>=1.5.3",
    "mkdocs-material>=9.4.0",
    "mkdocs-minify-plugin>=0.7.1",
    "pymdown-extensions>=10.4",

    # Utilities
    "click>=8.1.7",              # CLI framework
    "python-dateutil>=2.8.2",    # Date parsing
    "pyyaml>=6.0.1",            # Configuration
    "python-dotenv>=1.0.0",      # Environment management
    "loguru>=0.7.2",            # Enhanced logging
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.3.0",       # Parallel testing
    "pytest-mock>=3.11.0",       # Mocking support
    "black>=23.0.0",             # Code formatting
    "ruff>=0.1.0",               # Linting
    "mypy>=1.5.0",               # Type checking
    "types-python-dateutil>=2.8.0",
    "types-pyyaml>=6.0.0",
    "pre-commit>=3.3.0",         # Git hooks
]

docs = [
    "mkdocs-awesome-pages-plugin>=2.9.0",
    "mkdocs-git-revision-date-localized-plugin>=1.2.0",
    "mkdocs-rss-plugin>=1.8.0",
    "mkdocs-macros-plugin>=1.0.4",
]

[project.urls]
"Homepage" = "https://github.com/yourusername/dremeldocs"
"Documentation" = "https://dremeldocs.org"
"Bug Tracker" = "https://github.com/yourusername/dremeldocs/issues"
"Changelog" = "https://github.com/yourusername/dremeldocs/blob/main/CHANGELOG.md"

[project.scripts]
dremeldocs = "scripts.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["scripts"]

# ============================================================================
# TOOL CONFIGURATIONS
# ============================================================================

[tool.ruff]
# Ruff configuration - fast Python linter
target-version = "py38"
line-length = 88
indent-width = 4

# Exclude common directories
exclude = [
    ".git",
    ".venv",
    "venv",
    ".tox",
    "dist",
    "build",
    "*.egg-info",
    "__pycache__",
    "site",
    "source/data",  # Twitter archive
    ".cache",
]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # Pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "ARG",  # flake8-unused-arguments
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "DTZ",  # flake8-datetimez
    "RUF",  # Ruff-specific rules
]

ignore = [
    "E501",  # Line too long (handled by formatter)
    "B008",  # Do not perform function calls in argument defaults
    "B904",  # Allow raising without from in except
    "SIM105", # Use contextlib.suppress - too aggressive
]

# Allow autofix for all enabled rules
fixable = ["ALL"]
unfixable = []

# Allow unused variables when underscore-prefixed
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]
"tests/*" = ["ARG", "PLR2004", "S101"]
"scripts/archived_experiments/*" = ["ALL"]

[tool.ruff.lint.isort]
known-first-party = ["scripts", "tests"]
force-single-line = false
lines-after-imports = 2

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = true
docstring-code-line-length = 72

[tool.mypy]
# Type checking configuration
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
check_untyped_defs = true
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
check_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",
    "--strict-markers",
    "--cov=scripts",
    "--cov-report=html",
    "--cov-report=term-missing:skip-covered",
    "--cov-fail-under=80",
    "-v",
]
markers = [
    "integration: Integration tests requiring external resources",
    "unit: Unit tests with no external dependencies",
    "slow: Tests that take > 5 seconds",
    "nlp: Tests requiring SpaCy models",
]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]

[tool.coverage.run]
source = ["scripts"]
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/archived_experiments/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]

[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | venv
  | build
  | dist
  | site
)/
'''
```

## Linting & Formatting

### .ruff.toml (Alternative dedicated configuration)

```toml
# Ruff - Fast Python Linter Configuration
# For DremelDocs revolutionary theory archive project

# Python version target
target-version = "py38"

# Line length matching Black
line-length = 88
indent-width = 4

# Files to process
include = ["*.py", "*.pyi", "**/pyproject.toml"]

# Exclusions
exclude = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".git-rewrite",
    ".hg",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pyenv",
    ".pytest_cache",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    ".vscode",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "site",
    "site-packages",
    "source/data",  # Twitter archive
    "venv",
    ".cache",
    ".serena",
]

[lint]
# Enable comprehensive rule sets
select = [
    # Core
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort

    # Extensions
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "DTZ",    # flake8-datetimez
    "PD",     # pandas-vet
    "PL",     # Pylint
    "TRY",    # tryceratops
    "NPY",    # NumPy-specific rules
    "RUF",    # Ruff-specific rules
    "D",      # pydocstyle
]

ignore = [
    "E501",   # Line too long (formatter handles)
    "D100",   # Missing module docstring
    "D104",   # Missing public package docstring
    "D203",   # 1 blank line before class docstring
    "D213",   # Multi-line summary second line
    "PD901",  # Avoid `df` variable name
    "PLR0913", # Too many arguments
]

# Autofix configuration
fixable = ["ALL"]
unfixable = ["B"]  # Don't auto-fix bugbear findings

# Type checking imports
[lint.isort]
known-first-party = ["scripts", "tests"]
section-order = [
    "future",
    "standard-library",
    "third-party",
    "first-party",
    "local-folder"
]

[lint.pydocstyle]
convention = "google"  # Academic documentation style

[lint.per-file-ignores]
"__init__.py" = ["E402", "F401", "D104"]
"tests/**/*.py" = ["D", "S101", "ARG", "PLR2004"]
"scripts/cli.py" = ["D"]
"scripts/archived_experiments/**/*.py" = ["ALL"]

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

# Format docstrings
docstring-code-format = true
docstring-code-line-length = 72

# Preserve quotes in f-strings
skip-source-first-line = false
```

## Documentation Standards

### .markdownlint.yml

```yaml
# Markdown Linting Configuration
# For MkDocs Material documentation

# Default state for rules
default: true

# Line length
MD013:
  line_length: 100
  heading_line_length: 100
  code_blocks: false
  tables: false

# Heading style
MD003:
  style: "atx"

# Lists
MD004:
  style: "dash"

MD007:
  indent: 2

# Trailing spaces (allow for line breaks)
MD009: false

# Hard tabs
MD010:
  code_blocks: false

# Multiple consecutive blank lines
MD012:
  maximum: 2

# Heading hierarchy
MD025: true
MD041: true  # First line should be top-level heading

# Code block style
MD046:
  style: "fenced"

# Links
MD042: false  # Allow empty links (for MkDocs macros)

# Inline HTML (allowed for MkDocs)
MD033: false

# Bare URLs
MD034: false

# Emphasis style
MD049:
  style: "underscore"

MD050:
  style: "asterisk"

# Custom rules for MkDocs
MD024:
  siblings_only: true  # Allow duplicate headings in different sections
```

### .yamllint

```yaml
# YAML Linting Configuration
# For configuration files and MkDocs

extends: default

rules:
  line-length:
    max: 120
    level: warning

  comments:
    min-spaces-from-content: 2

  comments-indentation: disable

  document-start: disable

  truthy:
    allowed-values: ['true', 'false', 'yes', 'no', 'on', 'off']

  indentation:
    spaces: 2
    indent-sequences: true

  brackets:
    max-spaces-inside: 1

  braces:
    max-spaces-inside: 1

  colons:
    max-spaces-after: 1

  commas:
    max-spaces-after: 1

  empty-lines:
    max: 2
    max-start: 0
    max-end: 1

  hyphens:
    max-spaces-after: 1

  key-duplicates: enable

  new-line-at-end-of-file: enable

  trailing-spaces: enable

ignore: |
  .venv/
  venv/
  site/
  .cache/
  source/data/
```

## Editor Configuration

### .editorconfig

```ini
# EditorConfig for DremelDocs
# https://editorconfig.org

root = true

# Universal settings
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

# Python files
[*.py]
indent_size = 4
max_line_length = 88

# YAML files (including MkDocs config)
[*.{yml,yaml}]
indent_size = 2

# Markdown files
[*.md]
indent_size = 2
trim_trailing_whitespace = false  # Preserve line breaks
max_line_length = 100

# JavaScript/TypeScript (if needed for MkDocs)
[*.{js,ts,jsx,tsx}]
indent_size = 2

# JSON files
[*.json]
indent_size = 2

# TOML files
[*.toml]
indent_size = 4

# Shell scripts
[*.{sh,bash}]
indent_size = 2

# Makefile
[Makefile]
indent_style = tab

# Git files
[{.gitignore,.gitattributes}]
indent_size = 2
```

### .vscode/settings.json

```json
{
  // DremelDocs VS Code Workspace Settings

  // Python configuration
  "python.linting.enabled": false,  // Use Ruff instead
  "python.formatting.provider": "none",  // Use Ruff
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": true,
      "source.organizeImports.ruff": true
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  },

  // Ruff extension
  "ruff.lint": true,
  "ruff.format": true,
  "ruff.organizeImports": true,
  "ruff.fixAll": true,

  // Python type checking
  "python.analysis.typeCheckingMode": "strict",
  "python.analysis.autoImportCompletions": true,

  // Markdown configuration
  "[markdown]": {
    "editor.formatOnSave": true,
    "editor.wordWrap": "on",
    "editor.rulers": [100],
    "editor.defaultFormatter": "DavidAnson.vscode-markdownlint"
  },

  // YAML configuration
  "[yaml]": {
    "editor.insertSpaces": true,
    "editor.tabSize": 2,
    "editor.formatOnSave": true
  },

  // File associations
  "files.associations": {
    "*.md": "markdown",
    ".env*": "dotenv",
    "*.yml": "yaml",
    "*.yaml": "yaml"
  },

  // Exclude patterns
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.ruff_cache": true,
    "**/.mypy_cache": true,
    "**/site": true,
    "**/.venv": true
  },

  // Search exclusions
  "search.exclude": {
    "**/source/data": true,
    "**/site": true,
    "**/.venv": true,
    "**/.cache": true,
    "**/node_modules": true,
    "**/__pycache__": true
  },

  // Terminal configuration
  "terminal.integrated.env.linux": {
    "PYTHONPATH": "${workspaceFolder}"
  },
  "terminal.integrated.env.osx": {
    "PYTHONPATH": "${workspaceFolder}"
  },

  // Testing
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests",
    "-v",
    "--cov=scripts"
  ],

  // Git
  "git.ignoreLimitWarning": true,

  // Editor
  "editor.formatOnSave": true,
  "editor.rulers": [88, 100],
  "editor.wordWrapColumn": 100,

  // Spell checker
  "cSpell.words": [
    "dremeldocs",
    "bmore",
    "mkdocs",
    "pyproject",
    "ruff",
    "mypy",
    "pytest",
    "spacy",
    "ijson",
    "loguru"
  ],

  // Task automation
  "task.problemMatchers": [],

  // Extensions recommendations
  "extensions.json": {
    "recommendations": [
      "charliermarsh.ruff",
      "ms-python.python",
      "ms-python.vscode-pylance",
      "DavidAnson.vscode-markdownlint",
      "redhat.vscode-yaml",
      "EditorConfig.EditorConfig",
      "streetsidesoftware.code-spell-checker",
      "donjayamanne.githistory",
      "GitHub.vscode-pull-request-github"
    ]
  }
}
```

## Git Workflow

### .pre-commit-config.yaml

```yaml
# Pre-commit hooks for code quality
# https://pre-commit.com

default_language_version:
  python: python3.8

repos:
  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=1000']
        exclude: 'source/data/.*'
      - id: check-ast
      - id: check-case-conflict
      - id: check-merge-conflict
      - id: check-toml
      - id: check-yaml
        args: ['--unsafe']
      - id: debug-statements
      - id: detect-private-key
      - id: end-of-file-fixer
      - id: mixed-line-ending
      - id: trailing-whitespace
        args: ['--markdown-linebreak-ext=md']

  # Python formatting and linting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.13
    hooks:
      - id: ruff
        args: ['--fix', '--exit-non-zero-on-fix']
      - id: ruff-format

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [
          types-python-dateutil,
          types-pyyaml
        ]
        args: ['--ignore-missing-imports']

  # Markdown linting
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.38.0
    hooks:
      - id: markdownlint
        args: ['--fix']

  # YAML linting
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.33.0
    hooks:
      - id: yamllint
        args: ['-c', '.yamllint']

  # Security checks
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: '.*/tests/.*|source/data/.*'

  # Documentation checks
  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.27.3
    hooks:
      - id: check-github-workflows
      - id: check-github-actions

  # Custom local hooks
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: ['tests/', '--maxfail=1', '-q']

      - id: no-twitter-data
        name: Check for Twitter data
        entry: 'source/data/tweets\.js'
        language: pygrep
        files: '\.gitignore$'

      - id: mkdocs-validate
        name: Validate MkDocs config
        entry: mkdocs build --strict --quiet
        language: system
        pass_filenames: false
        files: 'mkdocs\.yml$|markdown/.*\.md$'
```

### Updated .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/
eggs/
.eggs/
*.manifest
*.spec
pip-log.txt
pip-delete-this-directory.txt

# Virtual Environments
.venv/
venv/
ENV/
env/
.python-version

# Environment Variables
.env
.env.*
!.env.example

# Testing
.coverage
.coverage.*
htmlcov/
.tox/
.pytest_cache/
.hypothesis/
*.cover
coverage.xml
coverage.json
*.log
.benchmarks/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json
.pytype/
.pyre/

# Linting
.ruff_cache/
.pylint.d/

# IDE
.vscode/
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
.idea/
*.swp
*.swo
*~
.DS_Store

# Project Specific
.zk/
.serena/
.cache/
work/
archive/
source/data/
*.bak
*.tmp
backups/

# Data files
data/filtered_threads.json
data/classified_threads*.json
data/tweets_media/
data/direct_messages_media/

# Documentation builds
site/
docs/_build/
docs/.doctrees/

# MkDocs
site/
.cache/

# Package managers
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Jupyter
.ipynb_checkpoints/
*.ipynb

# OS Files
.DS_Store
.AppleDouble
.LSOverride
Icon
._*
.Spotlight-V100
.Trashes
Thumbs.db
ehthumbs.db
Desktop.ini
$RECYCLE.BIN/
*.lnk
.directory
.Trash-*

# Security
.secrets.baseline
*.key
*.pem
*.crt

# CI/CD
.github/actions/*/dist/
.gitlab-ci-local/

# Docker
.dockerignore
docker-compose.override.yml

# Logs
logs/
*.log
*.pid
*.seed
*.pid.lock

# Debug files
*.stackdump
core.*
```

## Testing Framework

### pytest.ini (Corrected)

```ini
# pytest configuration for DremelDocs

[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Command line options
addopts =
    -ra
    --strict-markers
    --cov=scripts
    --cov-report=html
    --cov-report=term-missing:skip-covered
    --cov-fail-under=80
    -v
    --tb=short
    --maxfail=3
    --disable-warnings

# Test markers
markers =
    unit: Unit tests with no external dependencies
    integration: Integration tests requiring external resources
    slow: Tests that take > 5 seconds
    nlp: Tests requiring SpaCy models
    network: Tests requiring network access
    wip: Work in progress tests

# Coverage configuration
[coverage:run]
source = scripts
omit =
    */tests/*
    */test_*.py
    */__init__.py
    */archived_experiments/*
    */cli.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod

# Warnings
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
    ignore::ResourceWarning
    error::UserWarning:scripts
```

## CI/CD Pipeline

### .github/workflows/ci.yml

```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

env:
  PYTHON_VERSION: '3.11'
  UV_VERSION: '0.1.0'

jobs:
  lint:
    name: Lint & Format Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: |
          uv venv
          uv pip install -r pyproject.toml --extra dev

      - name: Run Ruff
        run: |
          uv run ruff check .
          uv run ruff format --check .

      - name: Run mypy
        run: uv run mypy scripts/

      - name: Lint Markdown
        uses: DavidAnson/markdownlint-cli2-action@v15
        with:
          globs: '**/*.md'

      - name: Lint YAML
        run: |
          pip install yamllint
          yamllint .

  test:
    name: Test Suite
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: |
          uv venv
          uv pip install -e . --extra dev

      - name: Install SpaCy model
        run: |
          uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl

      - name: Run tests
        run: |
          uv run pytest tests/ --cov=scripts --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-${{ matrix.os }}-py${{ matrix.python-version }}

  docs:
    name: Documentation Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: |
          uv venv
          uv pip install -e . --extra docs

      - name: Build docs
        run: |
          uv run mkdocs build --strict

      - name: Check for broken links
        run: |
          pip install linkchecker
          linkchecker site/

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
```

## Task Automation

### Makefile

```makefile
# DremelDocs Development Makefile
# Revolutionary Theory Archive Pipeline

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment setup
.PHONY: install
install: ## Install project and dependencies
	uv venv
	uv pip install -e . --extra dev --extra docs
	./install_spacy_model.sh

.PHONY: install-dev
install-dev: install ## Install with development dependencies
	uv pip install pre-commit
	pre-commit install

# Data processing pipeline
.PHONY: pipeline
pipeline: ## Run complete processing pipeline
	uv run python scripts/run_full_pipeline.py

.PHONY: filter
filter: ## Filter Twitter archive threads
	uv run python scripts/local_filter_pipeline.py

.PHONY: heavy-hitters
heavy-hitters: ## Generate heavy hitter documents
	uv run python scripts/generate_heavy_hitters.py

.PHONY: classify
classify: ## Classify threads by theme
	uv run python scripts/theme_classifier.py

.PHONY: clean-markdown
clean-markdown: ## Clear generated markdown files
	uv run python scripts/theme_classifier.py --clear-only

# Testing
.PHONY: test
test: ## Run test suite
	uv run pytest tests/ -v

.PHONY: test-cov
test-cov: ## Run tests with coverage
	uv run pytest tests/ --cov=scripts --cov-report=html --cov-report=term

.PHONY: test-unit
test-unit: ## Run unit tests only
	uv run pytest tests/unit/ -v -m unit

.PHONY: test-integration
test-integration: ## Run integration tests
	uv run pytest tests/integration/ -v -m integration

# Code quality
.PHONY: lint
lint: ## Run linting checks
	uv run ruff check .

.PHONY: format
format: ## Format code with Ruff
	uv run ruff format .
	uv run ruff check --fix .

.PHONY: type-check
type-check: ## Run type checking
	uv run mypy scripts/

.PHONY: security
security: ## Run security checks
	pip-audit
	uv run bandit -r scripts/

.PHONY: quality
quality: lint type-check test ## Run all quality checks

# Documentation
.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	mkdocs serve --dev-addr 0.0.0.0:8000

.PHONY: docs-build
docs-build: ## Build documentation
	mkdocs build --strict

.PHONY: docs-deploy
docs-deploy: ## Deploy docs to GitHub Pages
	mkdocs gh-deploy --force

# Cleaning
.PHONY: clean
clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.coverage' -delete
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf site/

.PHONY: clean-all
clean-all: clean clean-markdown ## Clean everything
	rm -rf .venv/
	rm -rf data/filtered_threads.json
	rm -rf data/classified_threads*.json

# Development helpers
.PHONY: shell
shell: ## Open Python shell with project context
	uv run python

.PHONY: update-deps
update-deps: ## Update all dependencies
	uv pip compile pyproject.toml -o requirements.txt
	uv pip sync requirements.txt

.PHONY: check-deps
check-deps: ## Check for dependency updates
	uv pip list --outdated

# Git helpers
.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

# Docker operations
.PHONY: docker-build
docker-build: ## Build Docker image
	docker build -t dremeldocs:latest .

.PHONY: docker-run
docker-run: ## Run Docker container
	docker-compose up

.PHONY: docker-shell
docker-shell: ## Open shell in Docker container
	docker-compose run --rm app bash

# Release
.PHONY: release-patch
release-patch: ## Create patch release
	bump2version patch
	git push --tags

.PHONY: release-minor
release-minor: ## Create minor release
	bump2version minor
	git push --tags

.PHONY: release-major
release-major: ## Create major release
	bump2version major
	git push --tags

.DEFAULT_GOAL := help
```

## Environment Variables

### .env.example (Enhanced)

```bash
# DremelDocs Environment Configuration
# Copy to .env and customize for your environment

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT=development  # development, staging, production
DEBUG=false
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# ============================================================================
# PATHS
# ============================================================================
# Data directories
SOURCE_DATA_PATH=source/data
INTERMEDIATE_DATA_PATH=data
MARKDOWN_OUTPUT_PATH=markdown
SITE_OUTPUT_PATH=site
CACHE_PATH=.cache
LOG_PATH=logs

# ============================================================================
# MKDOCS CONFIGURATION
# ============================================================================
SITE_NAME="DremelDocs - Revolutionary Theory Archive"
SITE_URL="http://localhost:8000"
SITE_DESCRIPTION="Curated revolutionary theory from @BmoreOrganized"
SITE_AUTHOR="@BmoreOrganized"

# Feature flags
SEARCH_ENABLED=true
SOCIAL_ENABLED=false
OPTIMIZE_ENABLED=false
PRIVACY_ENABLED=false
RSS_ENABLED=false

# ============================================================================
# PROCESSING PIPELINE
# ============================================================================
# Performance
MAX_WORKERS=4
CHUNK_SIZE=100
MEMORY_LIMIT=2GB
PARALLEL_PROCESSING=true
CACHE_ENABLED=true

# Processing thresholds
MIN_THREAD_LENGTH=100
MIN_WORD_COUNT=500
MAX_THREADS=100
CONFIDENCE_THRESHOLD=0.7

# ============================================================================
# NLP CONFIGURATION
# ============================================================================
SPACY_MODEL=en_core_web_lg
NLP_BATCH_SIZE=50
NLP_N_PROCESS=2

# ============================================================================
# API KEYS (Optional)
# ============================================================================
# Only if using cloud services (not recommended for privacy)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# ============================================================================
# DEVELOPMENT
# ============================================================================
HOT_RELOAD=true
MOCK_DATA=false
VERBOSE_OUTPUT=false
PROFILE_ENABLED=false

# ============================================================================
# TESTING
# ============================================================================
TEST_PARALLEL=true
TEST_COVERAGE_MIN=80
TEST_FAIL_FAST=false

# ============================================================================
# CI/CD
# ============================================================================
CI=false
GITHUB_TOKEN=
DEPLOY_KEY=
CODECOV_TOKEN=

# ============================================================================
# SECURITY
# ============================================================================
SECRET_KEY=change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ORIGINS=

# ============================================================================
# MONITORING
# ============================================================================
SENTRY_DSN=
TELEMETRY_ENABLED=false
ANALYTICS_ID=

# ============================================================================
# DOCKER
# ============================================================================
DOCKER_REGISTRY=
DOCKER_IMAGE_NAME=dremeldocs
DOCKER_TAG=latest
```

## Development Containers

### Dockerfile

```dockerfile
# DremelDocs Development Container
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    PATH="/root/.cargo/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY scripts/ scripts/
COPY tests/ tests/
COPY markdown/ markdown/
COPY mkdocs.yml .

# Install Python dependencies
RUN uv venv && \
    uv pip install -e . --extra dev --extra docs

# Install SpaCy model
RUN uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl

# Expose MkDocs port
EXPOSE 8000

# Default command
CMD ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    image: dremeldocs:latest
    container_name: dremeldocs
    volumes:
      - .:/app
      - /app/.venv  # Don't mount venv
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - PYTHONPATH=/app
    env_file:
      - .env
    command: mkdocs serve --dev-addr 0.0.0.0:8000

  test:
    build: .
    image: dremeldocs:latest
    container_name: dremeldocs-test
    volumes:
      - .:/app
      - /app/.venv
    environment:
      - ENVIRONMENT=testing
      - PYTHONPATH=/app
    env_file:
      - .env
    command: pytest tests/ --cov=scripts

  lint:
    build: .
    image: dremeldocs:latest
    container_name: dremeldocs-lint
    volumes:
      - .:/app
      - /app/.venv
    environment:
      - ENVIRONMENT=development
      - PYTHONPATH=/app
    command: ruff check .
```

## Implementation Guide

### Priority Order

#### Phase 1: Essential (Day 1)
1. ✅ Update `pyproject.toml` with tool configurations
2. ✅ Create `.ruff.toml` for linting
3. ✅ Add `.editorconfig` for consistency
4. ✅ Update `.gitignore`
5. ✅ Fix `pytest.ini` syntax

```bash
# Quick setup commands
curl -LsSf https://raw.githubusercontent.com/yourusername/dremeldocs/main/config/DEVELOPER_ENVIRONMENT.md | grep -A 1000 "Enhanced pyproject.toml" > pyproject.toml
touch .ruff.toml
touch .editorconfig
```

#### Phase 2: Quality (Week 1)
1. Add `.markdownlint.yml`
2. Add `.yamllint`
3. Create `.pre-commit-config.yaml`
4. Install pre-commit hooks

```bash
# Install pre-commit
uv pip install pre-commit
pre-commit install
pre-commit run --all-files
```

#### Phase 3: Automation (Week 2)
1. Create `Makefile`
2. Set up VS Code settings
3. Add GitHub Actions workflows

```bash
# Test Makefile
make install-dev
make test
make quality
```

#### Phase 4: Containerization (Week 3)
1. Create `Dockerfile`
2. Add `docker-compose.yml`
3. Test containerized development

```bash
# Test Docker setup
docker-compose build
docker-compose run --rm test
```

### Verification Checklist

```bash
# Verify installation
✓ uv --version
✓ ruff --version
✓ mypy --version
✓ pytest --version
✓ mkdocs --version

# Verify configurations
✓ ruff check .
✓ mypy scripts/
✓ pytest tests/
✓ mkdocs serve

# Verify automation
✓ make help
✓ pre-commit run --all-files
✓ docker-compose build
```

## Best Practices

### Code Quality Standards
1. **Type Hints**: All functions must have type annotations
2. **Docstrings**: Google-style docstrings for all public functions
3. **Testing**: Minimum 80% code coverage
4. **Linting**: Zero tolerance for Ruff errors
5. **Documentation**: Update docs with code changes

### Commit Standards
```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Format code
refactor: Refactor code
test: Add tests
chore: Update dependencies
```

### Branch Strategy
- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `hotfix/*`: Emergency fixes

### Review Requirements
- All PRs require review
- Passing CI/CD pipeline
- Updated documentation
- Test coverage maintained

## Security Considerations

### Secrets Management
- Never commit `.env` files
- Use `.secrets.baseline` for tracking
- Rotate keys regularly
- Use environment variables

### Dependency Security
```bash
# Regular security audits
pip-audit
safety check
bandit -r scripts/
```

### Data Privacy
- No telemetry in development
- Local processing only
- No cloud API calls
- Secure data handling

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Ruff conflicts with Black | Use Ruff for both linting and formatting |
| SpaCy model not found | Run `./install_spacy_model.sh` |
| Coverage below threshold | Add tests or adjust threshold |
| Pre-commit fails | Run `pre-commit run --all-files` to fix |
| Docker build fails | Check Dockerfile syntax and dependencies |

### Performance Optimization

1. **Parallel Testing**: Use `pytest-xdist`
2. **Caching**: Enable `.ruff_cache/`
3. **Incremental Type Checking**: Use `mypy --incremental`
4. **Docker Layer Caching**: Order Dockerfile efficiently

## Conclusion

This comprehensive developer environment configuration provides:

1. **Professional Standards**: Industry-best practices for Python development
2. **MkDocs Integration**: Optimized for documentation projects
3. **Quality Assurance**: Automated testing and linting
4. **Developer Experience**: Consistent, efficient workflow
5. **Revolutionary Discipline**: Collective development standards

The configuration emphasizes local-first development, privacy protection, and academic-quality code suitable for a revolutionary theory archive project.

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [Pre-commit Hooks](https://pre-commit.com/)
- [Python Testing](https://docs.pytest.org/)