# Configuration Management Architecture Specification

## Executive Summary

This specification defines a comprehensive configuration management system for DremelDocs based on MkDocs Material best practices. It establishes a hierarchical, environment-aware configuration architecture that separates concerns between site generation, data processing, and deployment settings.

### Configuration Hierarchy

```
dremeldocs/
├── mkdocs.yml                    # Primary MkDocs site configuration
├── .env                          # Local environment variables (not in git)
├── .env.example                  # Environment variable template
│
├── config/                       # Centralized configuration directory
│   ├── pipeline.yml             # Data processing pipeline settings
│   ├── themes.yml               # Theme definitions and categorization
│   ├── plugins.yml              # MkDocs plugin configurations
│   ├── cache.yml                # Cache and performance settings
│   ├── validation.yml           # Data validation rules
│   │
│   └── environments/            # Environment-specific overrides
│       ├── dev.yml             # Development settings
│       ├── staging.yml         # Staging settings
│       └── prod.yml            # Production settings
│
└── markdown/                    # Content directory
    ├── .meta.yml               # Global content settings
    └── themes/
        └── .meta.yml           # Theme-specific settings
```

### Configuration Precedence

1. Environment variables (highest priority)
2. Environment-specific config (dev/staging/prod)
3. Directory-level .meta.yml files
4. Central configuration files
5. Default values (lowest priority)

## Migration Strategy

### Phase 1: Setup (Week 1)

1. Create config/ directory structure
2. Copy existing mkdocs.yml to backup
3. Create .env.example and .env files
4. Implement ConfigLoader class
5. Create initial YAML configurations

### Phase 2: Pipeline Migration (Week 2)

1. Extract hardcoded paths from Python scripts
2. Create config/pipeline.yml with all paths
3. Update scripts to use ConfigLoader
4. Test pipeline with new configuration
5. Document configuration options

### Phase 3: Theme Configuration (Week 3)

1. Extract theme definitions to config/themes.yml
2. Update theme_classifier.py to use configuration
3. Implement vocabulary enhancement
4. Test classification with configuration
5. Create theme-specific .meta.yml files

### Phase 4: Environment Setup (Week 4)

1. Create environment-specific configurations
2. Setup staging environment
3. Configure production settings
4. Implement CI/CD integration
5. Test deployment pipeline

## Usage Examples

### Theme Classification with Configuration

```python
#!/usr/bin/env python3
"""Example: Theme classification with configuration."""

from config.loader import ConfigLoader
from pathlib import Path

class ConfiguredThemeClassifier:
    """Theme classifier using configuration."""

    def __init__(self, env="development"):
        """Initialize with configuration."""
        self.loader = ConfigLoader(env=env)
        self.config = self.loader.load_themes_config()
        self.pipeline_config = self.loader.load_pipeline_config()

    def classify_thread(self, thread_text):
        """Classify thread using configured themes."""
        scores = {}

        for theme_key, theme_config in self.config["themes"].items():
            for subcat_key, subcat in theme_config["subcategories"].items():
                score = self._calculate_score(thread_text, subcat["keywords"])
                scores[subcat_key] = score * subcat.get("weight", 1.0)

        # Apply confidence threshold
        threshold = self.config["classification"]["confidence_threshold"]
        return {k: v for k, v in scores.items() if v >= threshold}

    def _calculate_score(self, text, keywords):
        """Calculate theme score based on keywords."""
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        return matches / len(keywords) if keywords else 0
```

## Best Practices

### Configuration Management

1. **Environment Isolation**: Never commit .env files
2. **Secret Management**: Use environment variables for sensitive data
3. **Version Control**: Track all config files except .env
4. **Documentation**: Document all configuration options
5. **Validation**: Validate configuration on load

### MkDocs Material Alignment

1. **Plugin Order**: Search plugin always first
2. **Feature Flags**: Use standard Material feature names
3. **Color Palette**: Use Material color names
4. **Icon Library**: Use Material icon set
5. **Extensions**: Enable recommended extensions

### Performance Optimization

1. **Caching**: Enable caching in production
2. **Parallel Processing**: Use for large datasets
3. **Lazy Loading**: Load configs on demand
4. **CDN**: Disable privacy plugin for CDN usage
5. **Optimization**: Enable optimize plugin for production

### Security Considerations

1. **Environment Variables**: Use for all secrets
2. **File Permissions**: Restrict config file access
3. **Input Validation**: Validate all configuration inputs
4. **Path Traversal**: Prevent directory escape
5. **SSL/HTTPS**: Enforce in production

## Monitoring and Maintenance

### Configuration Validation

```python
# config/validator.py
"""Configuration validator."""

from jsonschema import validate
import yaml

class ConfigValidator:
    """Validate configuration against schemas."""

    SCHEMAS = {
        "pipeline": {
            "type": "object",
            "required": ["pipeline", "source", "stages", "paths"],
            "properties": {
                "pipeline": {
                    "type": "object",
                    "required": ["name", "version"]
                }
            }
        },
        "themes": {
            "type": "object",
            "required": ["themes", "classification"],
            "properties": {
                "themes": {"type": "object"},
                "classification": {
                    "type": "object",
                    "required": ["confidence_threshold"]
                }
            }
        }
    }

    def validate(self, config_name, config_data):
        """Validate configuration against schema."""
        if config_name in self.SCHEMAS:
            validate(config_data, self.SCHEMAS[config_name])
        return True
```

## Conclusion

This configuration management architecture provides:

1. **Centralized Configuration**: All settings in one organized location
2. **Environment Flexibility**: Easy switching between dev/staging/prod
3. **MkDocs Material Compliance**: Follows all best practices
4. **Maintainability**: Clear structure and documentation
5. **Scalability**: Supports project growth
6. **Security**: Proper secret management
7. **Performance**: Optimization settings
8. **Validation**: Configuration verification

The system separates concerns between site generation, data processing, and deployment while maintaining the flexibility needed for the DremelDocs revolutionary theory archive project.

## Appendices

### Appendix A: Configuration Checklist

- [x] Create config/ directory structure
- [x] Setup .env and .env.example
- [x] Create pipeline.yml configuration
- [ ] Create themes.yml configuration
- [x] Create plugins.yml configuration
- [ ] Setup environment configurations
- [ ] Implement ConfigLoader class
- [ ] Update Python scripts to use configuration
- [x] Create .meta.yml files
- [ ] Test all environments
- [x] Document configuration options
- [ ] Setup CI/CD integration

### Appendix B: Common Issues and Solutions

| Issue                             | Solution                             |
| --------------------------------- | ------------------------------------ |
| Environment variables not loading | Check .env file location and format  |
| Configuration merge conflicts     | Review override precedence           |
| Path resolution errors            | Use absolute paths in configuration  |
| Plugin configuration errors       | Verify plugin installation and order |
| Theme classification failures     | Check confidence thresholds          |

### Appendix C: References

- [MkDocs Material Documentation](https://squidfunk.github.io/mkdocs-material/)
- [MkDocs Configuration](https://www.mkdocs.org/user-guide/configuration/)
- [YAML Specification](https://yaml.org/spec/1.2/spec.html)
- [Python ConfigLoader Pattern](https://docs.python.org/3/library/configparser.html)
- [Environment Variables Best Practices](https://12factor.net/config)
