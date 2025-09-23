# Technical Learnings: SpaCy with uv Package Manager

## Key Discovery: uv Virtual Environments
uv creates minimal virtual environments without pip by default. This causes issues with tools that expect pip to be available.

## SpaCy Model Installation

### ❌ What Doesn't Work
```bash
# This fails in uv environments (no pip module)
python -m spacy download en_core_web_sm
uv run spacy download en_core_web_sm
```

### ✅ Correct Approach
Install SpaCy models as packages directly via URL:
```bash
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

## SpaCy Implementation Patterns

### Module-Level Loading
```python
# Load once at module level for efficiency
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Install with: uv pip install [URL]")
    sys.exit(1)
```

### Text Processing for Social Media
```python
def clean_social_text(doc):
    """Remove URLs, mentions, hashtags"""
    cleaned = []
    for token in doc:
        if not token.like_url and not token.text.startswith(('@', '#')):
            cleaned.append(token.text)
    return ' '.join(cleaned)
```

### Title Extraction Pattern
1. Remove RT prefix if present
2. Clean social media artifacts
3. Process with SpaCy
4. Use first sentence or extract key noun chunk
5. Fallback to truncation if needed

## File Encoding Troubleshooting

### Diagnosis Steps
1. Check encoding: `file README.md`
2. Find invalid bytes: `hexdump -C file | head -n 30`
3. Look for non-UTF-8 characters (e.g., 0xd6)

### Resolution
- Replace file with clean UTF-8 version
- Don't try to patch individual bytes
- Validate after: should show "Unicode text, UTF-8 text"

## Frontmatter Best Practices

### Escaping Values
```python
def format_frontmatter_value(value):
    if isinstance(value, str):
        # Check for special YAML characters
        if any(c in value for c in ['"', "'", ':', '\n', '#', '@', '|']):
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
    # ... handle lists, bools, etc.
```

### Date Formatting
- Parse flexibly with dateutil.parser
- Output as YYYYMMDD for filenames
- Use YYYY-MM-DD for frontmatter

## Performance Optimization

### Batch Processing
```python
# For multiple documents
docs = list(nlp.pipe(texts, batch_size=100))
```

### Pipeline Configuration
- Keep all components for full functionality
- Don't disable NER if you need entity extraction
- Load model once, use many times

## Error Handling Patterns

### Graceful Degradation
```python
try:
    # SpaCy processing
    doc = nlp(text)
    sentences = list(doc.sents)
    # ... sophisticated extraction
except:
    # Fallback to simple methods
    return text[:max_length].rsplit(' ', 1)[0]
```

## Integration Checklist

### When Adding SpaCy to Project
1. Add to pyproject.toml dependencies
2. Install with uv: `uv pip install spacy`
3. Install model via URL (not spacy download)
4. Create text_processing module
5. Load model at module level
6. Implement fallbacks for robustness
7. Test with social media text

## Common Pitfalls Avoided
- Don't use enable_pipes() - use default pipeline
- Don't reload model per function call
- Don't assume pip exists in uv environments
- Don't ignore UTF-8 encoding issues
- Don't forget to handle RT and @ mentions

This learning applies to any project using:
- uv package manager
- SpaCy for NLP
- Social media text processing
- Python virtual environments without pip