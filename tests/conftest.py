"""
Shared pytest configuration and fixtures for the Twitter archive processing pipeline tests.
"""

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Add the scripts directory to Python path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Set test environment variable to help security_utils recognize test context
import os
os.environ['PYTEST_CURRENT_TEST'] = 'true'


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_dir():
    """Fixture providing a temporary directory for test operations."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_workspace(temp_dir):
    """Fixture providing a complete workspace structure for testing."""
    workspace = {
        "root": temp_dir,
        "data": temp_dir / "data",
        "docs": temp_dir / "docs",
        "heavy_hitters": temp_dir / "docs" / "heavy_hitters",
        "scripts": temp_dir / "scripts",
    }

    # Create all directories
    for dir_path in workspace.values():
        if isinstance(dir_path, Path):
            dir_path.mkdir(parents=True, exist_ok=True)

    return workspace


@pytest.fixture(scope="session")
def spacy_model():
    """Fixture to ensure spaCy model is available for tests."""
    try:
        import spacy

        nlp = spacy.load("en_core_web_sm")
        return nlp
    except (ImportError, OSError):
        pytest.skip("spaCy model 'en_core_web_sm' not available")


# Pytest collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically.

    NOTE: This causes PytestUnknownMarkWarning warnings even though marks are registered
    in pytest.ini. This is a known pytest behavior - the warnings are harmless and can be
    ignored or suppressed with --disable-warnings flag.
    """
    for item in items:
        # Add unit marker to tests in unit/ directory
        if "unit" in str(item.fspath):
            item.add_marker("unit")

        # Add integration marker to tests in integration/ directory
        if "integration" in str(item.fspath):
            item.add_marker("integration")

        # Add slow marker to tests that likely take time
        if any(
            keyword in item.name.lower()
            for keyword in ["end_to_end", "large", "complete"]
        ):
            item.add_marker("slow")


# Test data validation
@pytest.fixture(autouse=True, scope="session")
def validate_test_environment():
    """Validate that the test environment is properly set up."""
    # Check that required directories exist
    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / "scripts"

    if not scripts_dir.exists():
        pytest.exit(
            "Scripts directory not found. Tests require access to pipeline scripts."
        )

    # Check for required Python modules (non-critical)
    missing_modules = []
    try:
        import yaml
    except ImportError:
        missing_modules.append("yaml")

    try:
        import spacy
    except ImportError:
        missing_modules.append("spacy")

    if missing_modules:
        print(f"Warning: Missing optional modules: {missing_modules}")
        print("Some tests may be skipped.")


# Skip conditions
def pytest_runtest_setup(item):
    """Setup hook to skip tests based on conditions."""
    # Skip spaCy-dependent tests if spaCy is not available
    if "spacy" in item.keywords:
        try:
            import spacy

            spacy.load("en_core_web_sm")
        except (ImportError, OSError):
            pytest.skip("spaCy with en_core_web_sm model required")

    # Skip slow tests if --fast option is used (custom option)
    if item.config.getoption("--fast", default=False) and "slow" in item.keywords:
        pytest.skip("Skipping slow test due to --fast option")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--fast", action="store_true", default=False, help="Skip slow tests"
    )
    parser.addoption(
        "--integration-only",
        action="store_true",
        default=False,
        help="Run only integration tests",
    )
    parser.addoption(
        "--unit-only", action="store_true", default=False, help="Run only unit tests"
    )


def pytest_configure(config):
    """Configure test collection based on options."""
    if config.getoption("--integration-only"):
        config.option.markexpr = "integration"
    elif config.getoption("--unit-only"):
        config.option.markexpr = "unit"


@pytest.fixture
def make_valid_tweet():
    """Factory for creating valid tweets with all required fields."""
    def _make_tweet(**kwargs):
        tweet = {
            "id": kwargs.get("id", "123456789"),
            "full_text": kwargs.get("full_text", "Default tweet text"),
            "created_at": kwargs.get("created_at", "2024-01-15T10:30:00Z"),
            "favorite_count": kwargs.get("favorite_count", 0),
            "retweet_count": kwargs.get("retweet_count", 0),
            "lang": kwargs.get("lang", "en"),
        }
        # Allow additional fields to be added
        for key, value in kwargs.items():
            if key not in tweet:
                tweet[key] = value
        return tweet
    return _make_tweet
