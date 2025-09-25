# config/loader.py
"""
Configuration loader for DremelDocs
Implements hierarchical configuration with environment overrides
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class ConfigLoader:
    """Hierarchical configuration loader following MkDocs Material patterns."""

    def __init__(self, env: Optional[str] = None):
        """Initialize configuration loader.

        Args:
            env: Environment name (dev, staging, prod)
        """
        self.root = Path(__file__).parent.parent
        self.config_dir = self.root / "config"
        self.env = env or os.getenv("ENVIRONMENT", "development")

        # Load environment variables
        load_dotenv(self.root / ".env")

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def load(self, config_name: str) -> Dict[str, Any]:
        """Load configuration file with environment overrides.

        Args:
            config_name: Name of config file (without .yml)

        Returns:
            Merged configuration dictionary
        """
        config = {}

        # Load base configuration
        base_path = self.config_dir / f"{config_name}.yml"
        if base_path.exists():
            config = self._load_yaml(base_path)

        # Load environment-specific overrides
        env_path = self.config_dir / "environments" / f"{self.env}.yml"
        if env_path.exists():
            env_config = self._load_yaml(env_path)
            config = self._deep_merge(config, env_config)

        # Apply environment variable overrides
        config = self._apply_env_vars(config)

        return config

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file with variable substitution.

        Args:
            path: Path to YAML file

        Returns:
            Parsed configuration dictionary
        """
        with open(path) as f:
            content = f.read()

        # Substitute environment variables
        content = os.path.expandvars(content)

        # Parse YAML
        return yaml.safe_load(content) or {}

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries.

        Args:
            base: Base configuration
            override: Override configuration

        Returns:
            Merged configuration
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_vars(self, config: Dict) -> Dict:
        """Apply environment variable overrides using !ENV pattern.

        Args:
            config: Configuration dictionary

        Returns:
            Configuration with environment variables applied
        """

        def process_value(value):
            if isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_value(v) for v in value]
            elif isinstance(value, str) and value.startswith("!ENV"):
                # Parse !ENV pattern
                parts = value.split(None, 1)
                if len(parts) > 1:
                    var_spec = parts[1].strip("[]")
                    var_parts = var_spec.split(",")
                    var_name = var_parts[0].strip()
                    default = var_parts[1].strip() if len(var_parts) > 1 else None
                    return os.getenv(var_name, default)
            return value

        return process_value(config)

    def load_pipeline_config(self) -> Dict[str, Any]:
        """Load pipeline configuration with path resolution."""
        config = self.load("pipeline")

        # Resolve paths relative to project root
        if "paths" in config:
            for key, path in config["paths"].items():
                config["paths"][key] = str(self.root / path)

        return config

    def load_themes_config(self) -> Dict[str, Any]:
        """Load themes configuration."""
        return self.load("themes")

    def load_plugins_config(self) -> list:
        """Load plugins configuration as list."""
        plugins_file = self.config_dir / "plugins.yml"
        if plugins_file.exists():
            with open(plugins_file) as f:
                return yaml.safe_load(f) or []
        return []

    def get_mkdocs_config(self) -> Dict[str, Any]:
        """Get complete MkDocs configuration.

        Returns:
            Configuration suitable for mkdocs.yml
        """
        # Load base mkdocs.yml
        mkdocs_path = self.root / "mkdocs.yml"
        with open(mkdocs_path) as f:
            config = yaml.safe_load(f) or {}

        # Load and merge plugins
        config["plugins"] = self.load_plugins_config()

        # Apply environment overrides
        env_config = self.load(f"environments/{self.env}")
        if "site" in env_config:
            config.update(env_config["site"])

        return config


# Usage example
if __name__ == "__main__":
    loader = ConfigLoader(env="development")

    # Load pipeline configuration
    pipeline_config = loader.load_pipeline_config()
    print(f"Pipeline version: {pipeline_config['pipeline']['version']}")

    # Load themes configuration
    themes_config = loader.load_themes_config()
    print(f"Themes: {list(themes_config['themes'].keys())}")

    # Get MkDocs configuration
    mkdocs_config = loader.get_mkdocs_config()
    print(f"Site name: {mkdocs_config['site_name']}")
