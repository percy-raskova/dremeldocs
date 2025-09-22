# Testing Documentation

## Overview

Comprehensive testing framework for the astradocs Twitter archive processing pipeline using pytest.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests for individual modules
│   ├── test_local_filter_pipeline.py
│   ├── test_generate_heavy_hitters.py
│   └── test_theme_classifier.py
├── integration/             # End-to-end pipeline tests
│   └── test_pipeline_integration.py
└── fixtures/                # Test data fixtures
```

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test Categories
```bash
# Unit tests only
pytest tests/unit -m unit

# Integration tests only
pytest tests/integration -m integration

# Exclude slow tests
pytest -m "not slow"

# Performance tests
pytest -m performance
```

### With Coverage
```bash
# Generate coverage report
pytest --cov=scripts --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Verbose Output
```bash
pytest -v  # Verbose
pytest -vv # Very verbose
```

## Test Categories

### Unit Tests
- **Purpose**: Test individual functions and classes in isolation
- **Location**: `tests/unit/`
- **Coverage Target**: 80%+
- **Key Areas**:
  - Tweet filtering logic
  - Thread detection
  - Markdown generation
  - Theme classification

### Integration Tests
- **Purpose**: Test complete pipeline flow
- **Location**: `tests/integration/`
- **Markers**: `@pytest.mark.integration`
- **Key Scenarios**:
  - End-to-end data flow
  - Format consistency
  - Error handling
  - Performance benchmarks

### Performance Tests
- **Purpose**: Ensure pipeline handles large datasets efficiently
- **Markers**: `@pytest.mark.slow`, `@pytest.mark.performance`
- **Benchmarks**:
  - Process 1000 tweets < 10 seconds
  - Memory usage < 500MB for 37MB input

## Key Test Fixtures

### `sample_tweet`
Single tweet for basic testing

### `sample_thread_tweets`
Connected tweets forming a thread

### `sample_heavy_thread`
Thread with 500+ words for heavy hitter testing

### `temp_source_dir`
Temporary directory mimicking Twitter archive structure

### `temp_work_dir`
Temporary working directory for outputs

## Writing New Tests

### Unit Test Template
```python
class TestNewFeature:
    """Test suite for new feature."""

    @pytest.fixture
    def setup(self):
        """Setup test environment."""
        return TestData()

    def test_normal_case(self, setup):
        """Test normal operation."""
        result = function_under_test(setup.data)
        assert result == expected

    def test_edge_case(self, setup):
        """Test edge cases."""
        result = function_under_test(edge_data)
        assert result is not None

    @pytest.mark.parametrize("input,expected", [
        ("case1", "result1"),
        ("case2", "result2"),
    ])
    def test_multiple_scenarios(self, input, expected):
        """Test multiple scenarios."""
        assert function(input) == expected
```

### Integration Test Template
```python
@pytest.mark.integration
def test_pipeline_scenario(setup_test_environment):
    """Test complete pipeline scenario."""
    # Stage 1: Setup
    test_dir = setup_test_environment

    # Stage 2: Execute
    result = run_pipeline(test_dir)

    # Stage 3: Verify
    assert result.success
    assert len(result.threads) > 0
```

## Coverage Requirements

### Core Modules
- `local_filter_pipeline.py`: 85%+
- `generate_heavy_hitters.py`: 80%+
- `theme_classifier.py`: 80%+

### Critical Functions
- Thread detection: 100%
- Filtering logic: 100%
- Classification: 90%+

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    - name: Run tests
      run: |
        pytest --cov --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Common Testing Patterns

### Mocking File I/O
```python
with patch('builtins.open', mock_open(read_data=content)):
    result = read_file("test.txt")
```

### Testing Streaming
```python
def generate_tweets():
    for i in range(1000):
        yield {"id": str(i), "text": f"Tweet {i}"}

with patch.object(extractor, 'stream_tweets', side_effect=generate_tweets):
    extractor.process()
```

### Testing Date Parsing
```python
@pytest.mark.parametrize("date_str,expected", [
    ("Mon Sep 06 18:00:00 +0000 2024", "2024-09-06"),
    ("invalid", "undated"),
])
def test_date_parsing(date_str, expected):
    result = parse_date(date_str)
    assert result == expected
```

## Debugging Tests

### Run specific test
```bash
pytest tests/unit/test_local_filter_pipeline.py::TestLocalThreadExtractor::test_thread_detection -v
```

### Show print statements
```bash
pytest -s
```

### Drop into debugger on failure
```bash
pytest --pdb
```

### Generate detailed failure report
```bash
pytest --tb=long
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Speed**: Unit tests should be fast (< 0.1s each)
4. **Coverage**: Aim for 80%+ coverage, 100% for critical paths
5. **Fixtures**: Use fixtures for reusable test data
6. **Mocking**: Mock external dependencies (file I/O, network)
7. **Parametrization**: Test multiple scenarios with `@pytest.mark.parametrize`
8. **Markers**: Use markers to categorize tests
9. **Documentation**: Document complex test scenarios
10. **Maintenance**: Keep tests updated with code changes