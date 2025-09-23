# AstraDocs Testing Guide

A practical guide for testing the Twitter archive processing pipeline with examples and best practices.

## Quick Start

### Prerequisites
```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Install SpaCy model
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

### Running Your First Test
```bash
# Run all tests
pytest

# Run with visual feedback
pytest -v

# Run and see output
pytest -s
```

## Testing Workflow

### 1. Before Making Changes
Always run tests to ensure starting from a working state:
```bash
pytest --tb=short
```

### 2. During Development
Use watch mode for continuous feedback:
```bash
# Install pytest-watch first
uv pip install pytest-watch

# Run tests on file changes
ptw -- -x --tb=short
```

### 3. After Implementation
Run full test suite with coverage:
```bash
pytest --cov=scripts --cov-report=term-missing
```

## Common Testing Scenarios

### Testing Text Processing Functions

#### Example: Testing Title Generation
```python
def test_title_generation_from_tweet():
    """Test that title is properly extracted from tweet text."""
    tweet_text = "RT @someone: This is a philosophical thread about dialectical materialism and praxis. https://t.co/abc123 #philosophy"

    title = generate_title(tweet_text)

    # Verify social media artifacts removed
    assert "RT @" not in title
    assert "https://" not in title
    assert "#philosophy" not in title

    # Verify meaningful content extracted
    assert "philosophical" in title.lower()
    assert len(title) <= 60  # Max length constraint
```

#### Example: Testing YAML Frontmatter
```python
def test_frontmatter_escaping():
    """Test that special characters are properly escaped."""
    tricky_title = 'Title with "quotes" and: colons'

    escaped = format_frontmatter_value(tricky_title)

    # Should be wrapped in quotes with internal quotes escaped
    assert escaped == '"Title with \\"quotes\\" and: colons"'

    # Verify it produces valid YAML
    yaml_content = f"title: {escaped}"
    parsed = yaml.safe_load(yaml_content)
    assert parsed['title'] == tricky_title  # Original recovered
```

### Testing File Operations

#### Example: Testing Filename Generation
```python
def test_standardized_filename_format():
    """Test filename follows the standard format."""
    sequence = 42
    date = "Wed Nov 15 14:23:45 +0000 2023"
    text = "The fundamental misunderstanding of dialectical materialism..."

    filename = generate_filename(sequence, date, text)

    # Verify format: {seq}-{YYYYMMDD}-{title}.md
    assert filename.startswith("042-20231115-")
    assert filename.endswith(".md")
    assert "dialectical_materialism" in filename

    # Verify filesystem safety
    assert not any(char in filename for char in '<>:"|?*')
```

### Testing Data Pipeline

#### Example: Testing Thread Filtering
```python
def test_thread_filtering_by_word_count():
    """Test that threads are filtered by minimum word count."""
    threads = [
        {"thread_id": "1", "word_count": 500, "smushed_text": "Long thread..."},
        {"thread_id": "2", "word_count": 100, "smushed_text": "Short thread..."},
        {"thread_id": "3", "word_count": 750, "smushed_text": "Heavy hitter..."},
    ]

    # Filter for "heavy hitters" (500+ words)
    heavy_hitters = filter_heavy_hitters(threads, min_words=500)

    assert len(heavy_hitters) == 2
    assert all(t["word_count"] >= 500 for t in heavy_hitters)
    assert "2" not in [t["thread_id"] for t in heavy_hitters]
```

## Test Data Management

### Using Fixtures

#### Shared Test Data
```python
# In conftest.py
@pytest.fixture
def sample_thread():
    """Provide a standard thread for testing."""
    return {
        "thread_id": "test_001",
        "tweet_count": 5,
        "word_count": 650,
        "first_tweet_date": "Wed Nov 15 14:23:45 +0000 2023",
        "smushed_text": "A long philosophical thread about...",
        "tweets": [...]
    }

# In your test
def test_process_thread(sample_thread):
    result = process_thread(sample_thread)
    assert result.success
```

#### Temporary Files
```python
def test_file_generation(temp_dir):
    """Test that markdown files are created correctly."""
    # temp_dir is automatically cleaned up
    output_file = temp_dir / "output.md"

    generate_markdown(data, output_file)

    assert output_file.exists()
    content = output_file.read_text()
    assert "---" in content  # Has frontmatter
```

### Parametrized Testing

#### Testing Multiple Cases
```python
@pytest.mark.parametrize("date_str,expected", [
    ("Wed Nov 15 14:23:45 +0000 2023", "20231115"),
    ("2023-11-15T14:23:45Z", "20231115"),
    ("2023-11-15", "20231115"),
    ("invalid date", "20250101"),  # Default fallback
    (None, "20250101"),  # None handling
])
def test_date_parsing_formats(date_str, expected):
    """Test various date format parsing."""
    result = parse_to_yyyymmdd(date_str)
    assert result == expected
```

## Debugging Failed Tests

### Getting More Information
```bash
# Show full error traces
pytest --tb=long

# Show local variables
pytest -l

# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb
```

### Common Failure Patterns

#### 1. SpaCy Model Issues
```python
# Problem: OSError: Can't find model 'en_core_web_sm'
# Solution: Install the model
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

#### 2. Import Errors
```python
# Problem: ImportError: cannot import name 'function_name'
# Solution: Check sys.path includes scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
```

#### 3. YAML Formatting
```python
# Problem: yaml.scanner.ScannerError
# Solution: Ensure proper escaping
value = format_frontmatter_value(raw_value)  # Always escape
```

## Test Organization Best Practices

### 1. Group Related Tests
```python
class TestTextProcessing:
    """All text processing related tests."""

    class TestTitleGeneration:
        """Specific to title generation."""
        def test_basic(self): ...
        def test_edge_cases(self): ...

    class TestDescriptionGeneration:
        """Specific to descriptions."""
        def test_basic(self): ...
        def test_length_limits(self): ...
```

### 2. Use Descriptive Names
```python
# Good
def test_yaml_escaping_preserves_special_characters():
    ...

# Bad
def test_yaml():
    ...
```

### 3. Test One Thing
```python
# Good - focused test
def test_title_removes_urls():
    text = "Check this out https://example.com"
    title = generate_title(text)
    assert "https://" not in title

# Bad - testing multiple things
def test_text_processing():
    # Tests title, description, and entities all at once
    ...
```

## Coverage Analysis

### Understanding Coverage Reports
```bash
# Generate detailed report
pytest --cov=scripts --cov-report=term-missing

# Example output:
# Name                          Stmts   Miss  Cover   Missing
# -------------------------------------------------------------
# scripts/text_processing.py      245     12    95%   45-48, 112
# scripts/theme_classifier.py      89     89     0%   1-150
```

### Improving Coverage

#### Find Untested Code
```bash
# Generate HTML report
pytest --cov=scripts --cov-report=html

# Open in browser
open htmlcov/index.html
```

#### Target Specific Areas
```python
# Write tests for missing lines
def test_error_handling():
    """Test error conditions not covered."""
    with pytest.raises(ValueError):
        generate_title("")  # Empty input

    with pytest.raises(TypeError):
        generate_title(None)  # None input
```

## Performance Testing

### Measuring Test Speed
```bash
# Show slowest tests
pytest --durations=10

# Example output:
# ======= slowest 10 durations =======
# 0.52s call     tests/integration/test_pipeline.py::test_full_processing
# 0.31s call     tests/unit/test_text.py::test_spacy_loading
```

### Optimizing Slow Tests

#### Use Fixtures Efficiently
```python
# Slow - loads model for each test
def test_one():
    nlp = spacy.load("en_core_web_sm")
    ...

def test_two():
    nlp = spacy.load("en_core_web_sm")
    ...

# Fast - loads model once
@pytest.fixture(scope="session")
def nlp_model():
    return spacy.load("en_core_web_sm")

def test_one(nlp_model):
    ...

def test_two(nlp_model):
    ...
```

## Continuous Integration

### Local CI Simulation
```bash
# Run tests as CI would
pytest --cov --cov-fail-under=80 --strict-markers

# Full CI simulation
#!/bin/bash
set -e  # Exit on error

echo "Installing dependencies..."
uv pip install -e ".[dev]"

echo "Running linters..."
black --check scripts tests
ruff check scripts tests

echo "Running tests..."
pytest --cov --cov-report=xml --cov-fail-under=80

echo "All checks passed!"
```

## Troubleshooting Checklist

### Known Issues

**PytestUnknownMarkWarning**: You'll see warnings about "Unknown pytest.mark.unit" even though marks are registered. This is a harmless pytest quirk. To run tests cleanly:
```bash
# Suppress all warnings
uv run pytest --disable-warnings

# Or just suppress marker warnings
uv run pytest -W ignore::PytestUnknownMarkWarning
```

### When Tests Fail

1. **Check Environment**
   - [ ] Virtual environment activated?
   - [ ] All dependencies installed?
   - [ ] SpaCy model downloaded?

2. **Check Code Changes**
   - [ ] Did you change function signatures?
   - [ ] Are imports still valid?
   - [ ] Did file paths change?

3. **Check Test Data**
   - [ ] Is test data still valid?
   - [ ] Are fixtures returning expected types?
   - [ ] Are mocks configured correctly?

4. **Debug Systematically**
   - [ ] Run single failing test in isolation
   - [ ] Add print statements or use debugger
   - [ ] Check test assumptions still valid

## Advanced Topics

### Property-Based Testing
```python
# Using Hypothesis for generative testing
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=1000))
def test_title_generation_never_crashes(text):
    """Test that title generation handles any text input."""
    title = generate_title(text)
    assert isinstance(title, str)
    assert len(title) <= 60
```

### Mocking External Dependencies
```python
from unittest.mock import patch, MagicMock

@patch('scripts.text_processing.nlp')
def test_without_spacy(mock_nlp):
    """Test fallback when SpaCy unavailable."""
    mock_nlp.side_effect = OSError("Model not found")

    # Should fall back gracefully
    title = generate_title("Some text")
    assert title  # Still returns something
```

### Testing Async Code
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_processing():
    """Test asynchronous tweet processing."""
    result = await process_tweets_async(tweets)
    assert result.completed
    assert len(result.threads) > 0
```

## Getting Help

### Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- Project README: `tests/README.md`
- Test examples: `tests/unit/` and `tests/integration/`

### Common Commands Reference
```bash
# Basic
pytest                      # Run all tests
pytest -v                   # Verbose output
pytest -s                   # Show print statements
pytest -x                   # Stop on first failure

# Coverage
pytest --cov=scripts       # With coverage
pytest --cov-report=html   # HTML report

# Selection
pytest tests/unit/         # Only unit tests
pytest -k "title"          # Tests matching "title"
pytest -m "not slow"       # Skip slow tests

# Debugging
pytest --pdb              # Enter debugger on failure
pytest -l                 # Show local variables
pytest --tb=short         # Shorter tracebacks
```

---

*Remember: Good tests are the foundation of maintainable code. Write tests first, code second!*