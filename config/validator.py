from typing import Any, ClassVar, Dict

from jsonschema import validate


class ConfigValidator:
    """Validate configuration against schemas."""

    SCHEMAS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "pipeline": {
            "type": "object",
            "required": ["pipeline", "source", "stages", "paths"],
            "properties": {
                "pipeline": {"type": "object", "required": ["name", "version"]}
            },
        },
        "themes": {
            "type": "object",
            "required": ["themes", "classification"],
            "properties": {
                "themes": {"type": "object"},
                "classification": {
                    "type": "object",
                    "required": ["confidence_threshold"],
                },
            },
        },
    }

    def validate(self, config_name, config_data):
        """Validate configuration against schema."""
        if config_name in self.SCHEMAS:
            validate(config_data, self.SCHEMAS[config_name])
        return True
