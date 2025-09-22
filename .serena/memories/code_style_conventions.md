# Code Style and Conventions

## Python Conventions
- **Python Version**: 3.12+
- **Style Guide**: PEP 8 standard
- **Naming Convention**: 
  - Functions/variables: snake_case (e.g., `extract_tweets`, `thread_data`)
  - Classes: PascalCase (e.g., `TwitterArchiveExtractor`)
  - Constants: UPPER_SNAKE_CASE (e.g., `PHILOSOPHY_KEYWORDS`)
- **Module Structure**: Organized by function (parser/, classifier/, processor/)
- **Docstrings**: Triple quotes with description of purpose
- **Type Hints**: Not currently used but would be beneficial

## File Organization
- `/src/` - Core Python modules
  - `/parser/` - Archive extraction and parsing
  - `/classifier/` - Content classification logic
  - `/processor/` - Batch processing and output generation
  - `/utils/` - Helper utilities
- `/docs/` - Generated MkDocs content
- `/data/processed/` - Intermediate processing files
- `/config/` - YAML configuration files
- `/twitter-archives/` - Raw Twitter export data
- `/twitter-pipeline-docs/` - Project documentation

## Error Handling
- Use try/except blocks for file operations
- Implement checkpoint system for resumable processing
- Log errors with loguru for debugging

## Configuration Management
- YAML files for settings (config/settings.yaml)
- Environment variables for API keys (.env file)
- JSON for intermediate data storage