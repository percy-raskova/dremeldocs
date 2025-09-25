# tests/test_configuration.py
"""Test configuration loading and validation."""

import unittest

from config.validator import ConfigValidator

from config.loader import ConfigLoader


class TestConfiguration(unittest.TestCase):
    """Test configuration system."""

    def setUp(self):
        """Setup test environment."""
        self.loader = ConfigLoader(env="development")
        self.validator = ConfigValidator()

    def test_pipeline_config_loads(self):
        """Test pipeline configuration loading."""
        config = self.loader.load_pipeline_config()
        self.assertIn("pipeline", config)
        self.assertIn("stages", config)

    def test_themes_config_valid(self):
        """Test themes configuration validation."""
        config = self.loader.load_themes_config()
        self.assertTrue(self.validator.validate("themes", config))

    def test_environment_override(self):
        """Test environment-specific overrides."""
        dev_loader = ConfigLoader(env="development")
        prod_loader = ConfigLoader(env="production")

        dev_config = dev_loader.load("pipeline")
        prod_config = prod_loader.load("pipeline")

        # Development should have debug enabled
        self.assertNotEqual(
            dev_config.get("logging", {}).get("level"),
            prod_config.get("logging", {}).get("level"),
        )
