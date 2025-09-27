# DremelDocs Development Makefile
# Revolutionary Theory Archive Pipeline
#
# Usage: make [target]
# Run 'make help' for available targets

# ==============================================================================
# CONFIGURATION
# ==============================================================================


# Project settings
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Tool configuration
UV := uv
PYTHON := $(UV) run python
PYTEST := $(UV) run pytest
RUFF := $(UV) run ruff
MYPY := $(UV) run mypy
BLACK := $(UV) run black
MKDOCS := $(UV) run mkdocs

# Project paths
SCRIPTS_DIR := scripts
TESTS_DIR := tests
DATA_DIR := data
DOCS_DIR := docs
MARKDOWN_DIR := markdown
SITE_DIR := site

# Test configuration
PYTEST_OPTS := -v
PYTEST_COV_OPTS := --cov=$(SCRIPTS_DIR) --cov-report=html --cov-report=term
PYTEST_MARKERS := -m

# Required files for pipeline
SOURCE_ARCHIVE := source/data/tweets.js
FILTERED_DATA := $(DATA_DIR)/filtered_threads.json
THEMES_FILE := $(DOCS_DIR)/heavy_hitters/THEMES_EXTRACTED.md

# ==============================================================================
# HELP & DOCUMENTATION
# ==============================================================================

.PHONY: help
help: ## Show this help message
	@echo "================================================================"
	@echo "     DremelDocs Development Makefile"
	@echo "     Revolutionary Theory Archive Pipeline"
	@echo "================================================================"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Quick Start:"
	@echo "  make install        # Install everything"
	@echo "  make pipeline       # Run full pipeline"
	@echo "  make quality        # Run all quality checks"
	@echo "  make serve          # Start documentation server"
	@echo ""
	@echo "Available targets by category:"
	@echo ""
	@echo "Installation:   install, install-dev, install-spacy, setup"
	@echo "Pipeline:       pipeline, filter, heavy-hitters, classify"
	@echo "Testing:        test, test-cov, test-unit, test-integration"
	@echo "Quality:        quality, lint, format, type-check"
	@echo "Docs:           serve, docs-build, docs-deploy"
	@echo "Cleanup:        clean, clean-data, clean-all"
	@echo "Dev Tools:      shell, watch, update-deps, pre-commit"
	@echo ""
	@echo "For detailed help on each target, see comments in Makefile"
	@echo ""
	@echo "Tips:"
	@echo "  - Use 'make -j2' for parallel execution"
	@echo "  - Run 'make check-deps' to verify dependencies"
	@echo "  - See Makefile for more advanced targets"

# ==============================================================================
# DEPENDENCY CHECKING
# ==============================================================================

.PHONY: check-deps
check-deps: ## Check if all dependencies are installed
	@echo "Checking dependencies..."
	@command -v uv >/dev/null 2>&1 || { echo "[ERROR] uv not found. Install from: https://github.com/astral-sh/uv"; exit 1; }
	@command -v mkdocs >/dev/null 2>&1 || { echo "[WARNING] mkdocs not found. Run: pip install mkdocs mkdocs-material"; }
	@$(PYTHON) -c "import spacy; spacy.load('en_core_web_lg')" 2>/dev/null || { echo "[WARNING] SpaCy model not installed. Run: make install-spacy"; }
	@echo "[OK] All core dependencies found"

.PHONY: check-source
check-source: ## Verify source data exists
	@if [ ! -f "$(SOURCE_ARCHIVE)" ]; then \
		echo "[ERROR] Source archive not found: $(SOURCE_ARCHIVE)"; \
		echo "  Place your Twitter archive in source/"; \
		exit 1; \
	else \
		echo "[OK] Source archive found"; \
	fi

# ==============================================================================
# INSTALLATION & SETUP
# ==============================================================================

.PHONY: install
install: ## Install project and all dependencies
	@echo "Installing DremelDocs..."
	$(UV) venv
	$(UV) pip install -e ".[dev,logging,extras]"
	@$(MAKE) install-spacy
	@echo "[OK] Installation complete"

.PHONY: install-dev
install-dev: install ## Install with development tools
	@echo "Installing development tools..."
	$(UV) pip install pre-commit
	$(UV) run pre-commit install
	@echo "[OK] Development setup complete"

.PHONY: install-spacy
install-spacy: ## Install SpaCy language model
	@echo "Installing SpaCy model..."
	@if [ -f "./install_spacy_model.sh" ]; then \
		./install_spacy_model.sh; \
	else \
		$(UV) pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl; \
	fi
	@echo "[OK] SpaCy model installed"

.PHONY: setup
setup: install-dev check-deps ## Complete development environment setup
	@echo "[OK] Development environment ready!"
	@echo "Next steps:"
	@echo "  1. Place Twitter archive in source/"
	@echo "  2. Run 'make pipeline' to process data"
	@echo "  3. Run 'make serve' to view documentation"

# ==============================================================================
# DATA PROCESSING PIPELINE
# ==============================================================================

.PHONY: pipeline
pipeline: check-source ## Run complete processing pipeline
	@echo "=="
	@echo "      Starting DremelDocs Pipeline                             "
	@echo "=="
	$(PYTHON) $(SCRIPTS_DIR)/run_full_pipeline.py

.PHONY: filter
filter: check-source ## Stage 1: Filter Twitter archive threads
	@echo "Running Stage 1: Thread Filtering..."
	$(PYTHON) $(SCRIPTS_DIR)/local_filter_pipeline.py
	@echo "[OK] Filtering complete"

.PHONY: heavy-hitters
heavy-hitters: $(FILTERED_DATA) ## Stage 2: Generate heavy hitter documents
	@echo "Running Stage 2: Heavy Hitter Generation..."
	@if [ ! -f "$(FILTERED_DATA)" ]; then \
		echo "No filtered data found. Running filter first..."; \
		$(MAKE) filter; \
	fi
	$(PYTHON) $(SCRIPTS_DIR)/generate_themed_markdown.py
	@echo "[OK] Heavy hitters generated"

.PHONY: classify
classify: ## Stage 3: Classify threads by theme
	@echo "Running Stage 3: Theme Classification..."
	@if [ ! -f "$(THEMES_FILE)" ]; then \
		echo "[ERROR] THEMES_EXTRACTED.md not found"; \
		echo "Please review docs/heavy_hitters/ and create THEMES_EXTRACTED.md"; \
		exit 1; \
	fi
	$(PYTHON) $(SCRIPTS_DIR)/theme_classifier.py
	@echo "[OK] Classification complete"

.PHONY: clean-markdown
clean-markdown: ## Clear generated markdown files
	@echo "Cleaning markdown files..."
	$(PYTHON) $(SCRIPTS_DIR)/theme_classifier.py --clear-only
	@echo "[OK] Markdown cleaned"

# ==============================================================================
# TESTING
# ==============================================================================
# Note: Tests can be run in parallel with 'make -j2 test-unit test-integration'

.PHONY: test
test: ## Run test suite
	@echo "Running tests..."
	$(PYTEST) $(TESTS_DIR)/ $(PYTEST_OPTS)

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	$(PYTEST) $(TESTS_DIR)/ $(PYTEST_COV_OPTS)
	@echo "[OK] Coverage report generated in htmlcov/"

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	$(PYTEST) $(TESTS_DIR)/unit/ $(PYTEST_OPTS)

.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	$(PYTEST) $(TESTS_DIR)/integration/ $(PYTEST_OPTS)

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "Starting test watcher..."
	$(UV) run pytest-watch $(TESTS_DIR)/ --runner "$(PYTEST)"

# ==============================================================================
# CODE QUALITY
# ==============================================================================

.PHONY: lint
lint: ## Run linting checks (ruff)
	@echo "Running linter..."
	@$(RUFF) check . && echo "[OK] No linting issues" || true

.PHONY: format
format: ## Auto-format code (ruff + black)
	@echo "Formatting code..."
	$(RUFF) format .
	$(RUFF) check --fix .
	@echo "[OK] Code formatted"

.PHONY: type-check
type-check: ## Run type checking (mypy)
	@echo "Type checking..."
	@$(MYPY) $(SCRIPTS_DIR)/ && echo "[OK] No type errors" || true

.PHONY: quality
quality: ## Run all quality checks (lint + type + test)
	@echo "=="
	@echo "      Running Quality Checks                                   "
	@echo "=="
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) test
	@echo "[OK] All quality checks passed!"

.PHONY: check
check: quality ## Alias for quality

.PHONY: check-all
check-all: check-deps quality ## Check everything (deps + quality)
	@echo "[OK] All checks passed!"

# ==============================================================================
# DOCUMENTATION
# ==============================================================================

.PHONY: serve
serve: ## Serve documentation locally (localhost:8000)
	@echo "Starting documentation server..."
	@echo "Documentation at: http://localhost:8000"
	$(MKDOCS) serve --dev-addr 0.0.0.0:8000

.PHONY: docs-serve
docs-serve: serve ## Alias for serve

.PHONY: docs-build
docs-build: ## Build static documentation site
	@echo "Building documentation..."
	$(MKDOCS) build --strict
	@echo "[OK] Documentation built in $(SITE_DIR)/"

.PHONY: docs-deploy
docs-deploy: docs-build ## Deploy documentation (configure deployment first)
	@echo "Deploying documentation..."
	$(MKDOCS) gh-deploy --force

# ==============================================================================
# MAINTENANCE & CLEANUP
# ==============================================================================

.PHONY: clean
clean: ## Clean build artifacts and caches
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info/
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@find . -type f -name '*.pyo' -delete 2>/dev/null || true
	@find . -type f -name '*.coverage' -delete 2>/dev/null || true
	@rm -rf .pytest_cache/ .ruff_cache/ .mypy_cache/ htmlcov/ $(SITE_DIR)/
	@echo "[OK] Clean complete"

.PHONY: clean-data
clean-data: ## Clean generated data files
	@echo "Cleaning data files..."
	@rm -f $(DATA_DIR)/filtered_threads.json
	@rm -f $(DATA_DIR)/classified_threads*.json
	@echo "[OK] Data files cleaned"

.PHONY: clean-all
clean-all: clean clean-data clean-markdown ## Clean everything (including venv)
	@echo "Removing virtual environment..."
	@rm -rf .venv/
	@echo "[OK] Full cleanup complete"

# ==============================================================================
# DEVELOPMENT HELPERS
# ==============================================================================

.PHONY: shell
shell: ## Open Python REPL with project context
	@echo "Starting Python shell..."
	$(PYTHON)

.PHONY: watch
watch: ## Watch for changes and run tests
	@echo "Starting file watcher..."
	@command -v watchmedo >/dev/null 2>&1 || { \
		echo "Installing watchdog..."; \
		$(UV) pip install watchdog; \
	}
	watchmedo shell-command \
		--patterns="*.py" \
		--recursive \
		--command='make test' \
		$(SCRIPTS_DIR) $(TESTS_DIR)

.PHONY: update-deps
update-deps: ## Update all dependencies
	@echo "Updating dependencies..."
	$(UV) pip compile pyproject.toml -o requirements.txt
	$(UV) pip sync requirements.txt
	@echo "[OK] Dependencies updated"

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks on all files
	@echo "Running pre-commit hooks..."
	$(UV) run pre-commit run --all-files

# ==============================================================================
# QUICK SHORTCUTS
# ==============================================================================

.PHONY: q
q: quality ## Quick alias for quality checks

.PHONY: t
t: test ## Quick alias for tests

.PHONY: f
f: format ## Quick alias for format

.PHONY: s
s: serve ## Quick alias for serve

# ==============================================================================
# SPECIAL TARGETS
# ==============================================================================

# Prevent make from trying to remake the Makefile
Makefile: ;

# Set default target
.DEFAULT_GOAL := help

# All targets are already marked as .PHONY individually
