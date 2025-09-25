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

.PHONY: quality
quality: lint type-check test ## Run all quality checks

# Documentation
.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	mkdocs serve --dev-addr 0.0.0.0:8000

.PHONY: docs-build
docs-build: ## Build documentation
	mkdocs build --strict

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

# Git helpers
.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

.DEFAULT_GOAL := help