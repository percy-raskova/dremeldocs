# Twitter Archive Processing Pipeline Test Suite

Comprehensive unit and integration tests for the Twitter archive processing pipeline that converts Twitter/X data exports into markdown files for human analysis and tagging.

## Overview

This test suite validates the entire pipeline from raw Twitter data through to final markdown output, ensuring:

- **Pipeline execution**: Verifies the pipeline runs without errors
- **Filename generation**: Tests that filenames follow the format `{3-digit}-{YYYYMMDD}-{brief_title}.md`
- **Text compression**: Verifies that thread texts are properly combined ("smushed") together
- **Frontmatter generation**: Ensures YAML frontmatter includes all required fields
- **Human readability**: Validates that generated markdown files are readable and ready for human tagging

## Test Structure

```
tests/
├── conftest.py                     # Pytest configuration and shared fixtures
├── fixtures/                      # Test data and sample inputs
│   ├── __init__.py
│   └── sample_data.py             # Sample Twitter threads and expected outputs
├── unit/                          # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_text_processing.py    # Text processing functions
│   └── test_frontmatter_generation.py # YAML frontmatter generation
├── integration/                   # Integration tests (slower, multiple components)
│   ├── __init__.py
│   ├── test_filter_pipeline.py    # Pipeline filtering and thread extraction
│   └── test_end_to_end.py         # Complete pipeline workflows
└── utils/                         # Test utilities and validation helpers
    ├── __init__.py
    └── validation.py              # Validation functions for outputs
```

## Test Categories

### Unit Tests (`tests/unit/`)

**Text Processing Tests** (`test_text_processing.py`):
- `generate_title()` - Creates clean, meaningful titles from text
- `generate_description()` - Creates proper summaries
- `generate_filename()` - Produces correct format: `001-20250122-title_here.md`
- `parse_to_yyyymmdd()` - Handles various date formats
- `format_frontmatter_value()` - Properly escapes YAML special characters
- `calculate_reading_time()` - Estimates reading time from word count

**Frontmatter Generation Tests** (`test_frontmatter_generation.py`):
- YAML frontmatter structure validation
- Required field presence and type checking
- Special character escaping for YAML safety
- Date formatting and validation
- Boolean and integer value handling

### Integration Tests (`tests/integration/`)

**Filter Pipeline Tests** (`test_filter_pipeline.py`):
- Thread extraction from Twitter archive data
- Word count and tweet count filtering
- Thread reconstruction from individual tweets
- Memory efficiency with large datasets
- Error handling with malformed data

**End-to-End Tests** (`test_end_to_end.py`):
- Complete pipeline from raw data to markdown output
- File generation and validation
- Performance testing with larger datasets
- Memory usage monitoring
- Output consistency across multiple runs

## Running Tests

### Quick Start

```bash
# Run all tests
./run_pipeline_tests.sh

# Run only unit tests (fast)
./run_pipeline_tests.sh --unit-only

# Run only integration tests
./run_pipeline_tests.sh --integration-only

# Skip slow tests
./run_pipeline_tests.sh --fast
```

### Using pytest directly

```bash
# All tests with coverage
pytest --cov=scripts --cov-report=html

# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_text_processing.py

# Run specific test
pytest tests/unit/test_text_processing.py::TestGenerateTitle::test_generate_title_basic
```

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests with multiple components
- `@pytest.mark.slow` - Tests that may take several seconds
- `@pytest.mark.performance` - Performance and benchmarking tests

## Test Data

### Sample Data (`tests/fixtures/sample_data.py`)

Contains realistic sample Twitter thread data including:

- **SAMPLE_THREAD_DATA**: Main philosophical thread (756 words, 18 tweets)
- **SAMPLE_SHORT_THREAD_DATA**: Short thread for boundary testing (45 words, 3 tweets)
- **SAMPLE_COMPLEX_THREAD_DATA**: Complex political content with special characters (523 words, 12 tweets)
- **Expected outputs**: Frontmatter structures, filename formats, date parsing cases

### Test Cases

- **Date parsing**: Various Twitter date formats → YYYYMMDD conversion
- **Filename generation**: Sequence numbers, dates, title sanitization
- **Text processing edge cases**: Empty text, long titles, social media artifacts
- **YAML escaping**: Special characters, quotes, colons, brackets

## Validation Utilities (`tests/utils/validation.py`)

Comprehensive validation functions:

- `validate_filename_format()` - Checks `{3-digit}-{YYYYMMDD}-{brief_title}.md` format
- `validate_frontmatter_structure()` - Validates YAML frontmatter completeness
- `validate_yaml_syntax()` - Ensures syntactically correct YAML
- `validate_markdown_structure()` - Checks complete markdown file structure
- `validate_reading_time_calculation()` - Verifies reasonable reading time estimates
- `validate_smushed_text_quality()` - Checks text processing quality

## Expected Output Format

### Filename Format
```
001-20240906-I_have_been_asked_by_multiple_comrades_to_comment.md
059-20231115-The_fundamental_misunderstanding_of_dialectical.md
100-20240122-Palestine_A_Case_Study_in_Settler_Colonialism.md
```

### Frontmatter Structure
```yaml
---
title: "The fundamental misunderstanding of dialectical materialism"
date:
  created: 2023-11-15
categories: [heavy_hitters]
thread_id: thread_1189
word_count: 756
reading_time: 4
description: "Analysis of dialectical materialism as dynamic framework rather than rigid formula"
tweet_count: 18
heavy_hitter: true
thread_number: 1
author: "@BmoreOrganized"
---
```

### Markdown Structure
```markdown
# Thread #1: The fundamental misunderstanding of dialectical materialism

*756 words • 18 tweets • ~4 min read*

---

[Smushed thread content here...]

---

### Tweet IDs
1832118564494700976, 1832141155208687738, ...

### Navigation
[← Previous](#000) | [Index](index.md) | [Next →](#002)
```

## Prerequisites

### Required Dependencies
- Python 3.8+
- pytest
- PyYAML (for YAML processing)

### Optional Dependencies
- spaCy with `en_core_web_sm` model (for NLP features)
- coverage (for test coverage reporting)

### Installation
```bash
# Install required dependencies
pip install pytest PyYAML

# Install optional dependencies for full functionality
pip install spacy coverage
python -m spacy download en_core_web_sm
```

## Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
addopts =
    --strict-markers
    --cov=scripts
    --cov-report=html
    --cov-report=term-missing
    -v
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (multiple components)
    slow: Slow tests (may take several seconds)
    performance: Performance tests
```

### Test Environment Variables
- `FAST_MODE`: Skip slow tests
- `UNIT_ONLY`: Run only unit tests
- `INTEGRATION_ONLY`: Run only integration tests

## Troubleshooting

### Common Issues

**spaCy model not found**:
```bash
python -m spacy download en_core_web_sm
```

**Import errors for pipeline modules**:
- Ensure you're running tests from the project root directory
- Check that `scripts/` directory contains the pipeline modules

**Test failures due to missing data**:
- Verify that test fixtures in `tests/fixtures/` are complete
- Check that sample data matches expected formats

**YAML parsing errors**:
- Ensure PyYAML is installed: `pip install PyYAML`
- Check that frontmatter test data has valid YAML syntax

### Performance Issues

**Slow test execution**:
- Use `--fast` flag to skip slow tests
- Run unit tests only: `pytest -m unit`
- Use pytest-xdist for parallel execution: `pip install pytest-xdist`

**Memory issues with large datasets**:
- Tests use streaming processing to handle large Twitter archives
- Monitor memory usage during performance tests
- Reduce test dataset sizes if necessary

## Contributing

When adding new tests:

1. **Place tests in appropriate directory**:
   - `tests/unit/` for isolated function tests
   - `tests/integration/` for multi-component tests

2. **Use appropriate markers**:
   - `@pytest.mark.unit` for unit tests
   - `@pytest.mark.integration` for integration tests
   - `@pytest.mark.slow` for tests taking >2 seconds

3. **Follow naming conventions**:
   - Test files: `test_module_name.py`
   - Test classes: `TestClassName`
   - Test methods: `test_specific_functionality`

4. **Add validation**:
   - Use validation utilities from `tests/utils/validation.py`
   - Add new validation functions as needed

5. **Update documentation**:
   - Update this README for new test categories
   - Document new sample data in `tests/fixtures/sample_data.py`

## Coverage Goals

Target coverage levels:
- **Unit tests**: >90% coverage of individual functions
- **Integration tests**: >80% coverage of complete workflows
- **Overall pipeline**: >85% coverage of critical paths

Current coverage can be viewed in `htmlcov/index.html` after running tests with coverage enabled.