# DremelDocs Pipeline Reference

## Pipeline Overview

The DremelDocs pipeline is a multi-stage data processing system that transforms raw Twitter archives into a structured, searchable knowledge base focused on revolutionary theory.

## Complete Pipeline Execution

### Quick Start
```bash
# Run the complete pipeline with one command
uv run python run_pipeline.py
```

### Manual Stage Execution
```bash
# Stage 1: Extract threads from Twitter archive
uv run python scripts/local_filter_pipeline.py

# Stage 2: Classify threads by theme
uv run python scripts/theme_classifier.py

# Stage 3: Generate markdown files
uv run python scripts/generate_themed_markdown.py

# Stage 4: Build and serve documentation
uv run mkdocs serve
```

## Stage 1: Thread Extraction

### Script: `local_filter_pipeline.py`

**Purpose**: Extract coherent threads from Twitter archive using memory-efficient streaming

### Data Flow
```
Input:  source/data/tweets.js (37MB)
Output: data/filtered_threads.json (1,363 threads)
```

### Processing Steps

1. **Archive Validation**
   - Verify tweets.js exists and is valid
   - Check JSON structure integrity
   - Initialize streaming parser

2. **Two-Stage Filtering**
   ```python
   # Stage 1: Language filter
   - English tweets only
   - Remove spam and low-quality content

   # Stage 2: Engagement filter
   - Minimum 2 favorites OR 1 retweet
   - Author is @BmoreOrganized
   ```

3. **Thread Reconstruction**
   - Build reply chains from individual tweets
   - Detect self-replies for thread continuation
   - Handle broken threads gracefully
   - Concatenate thread text for analysis

4. **Output Generation**
   ```json
   {
     "thread_id": "unique_identifier",
     "created_at": "2024-01-15T10:30:00Z",
     "text": "concatenated thread text",
     "tweet_count": 5,
     "total_favorites": 150,
     "total_retweets": 45,
     "tweets": [/* individual tweets */]
   }
   ```

### Performance Metrics
- Processing time: ~30 seconds
- Memory usage: <200MB (streaming)
- Thread detection rate: 93%
- Filter efficiency: 21,723 → 1,363 threads

## Stage 2: Theme Classification

### Script: `theme_classifier.py`

**Purpose**: Classify threads into revolutionary theory themes using NLP

### Data Flow
```
Input:  data/filtered_threads.json
Output: data/classified_threads.json
```

### Classification Themes

| Theme | Description | Key Patterns |
|-------|-------------|--------------|
| marxism_historical materialism | Marxist theory and historical analysis | class struggle, dialectical materialism, commodity fetishism |
| political economy | Economic analysis and critique | capitalism, labor theory, surplus value |
| organizational theory | Revolutionary organization strategies | vanguard, democratic centralism, praxis |
| covid_public health politics | Pandemic politics and public health | covid, vaccine, public health, biopower |
| fascism analysis | Fascist movements and resistance | fascism, white supremacy, antifascism |
| cultural criticism | Cultural and media critique | ideology, hegemony, spectacle |
| imperialism_colonialism | Imperial and colonial analysis | imperialism, settler colonialism, extraction |
| dialectics | Dialectical philosophy | contradiction, negation, synthesis |

### Classification Algorithm

1. **Vocabulary Loading**
   ```python
   # Load theme-specific vocabularies from YAML
   vocabularies/
   ├── marxism_communism.yaml
   ├── political_economy.yaml
   ├── fascism_analysis.yaml
   └── ...
   ```

2. **Pattern Matching**
   ```python
   def classify_with_patterns(text):
       scores = {}
       for theme, patterns in vocabularies.items():
           scores[theme] = calculate_pattern_matches(text, patterns)
       return assign_themes(scores)
   ```

3. **Confidence Scoring**
   - High confidence: >10 pattern matches
   - Medium confidence: 5-10 matches
   - Low confidence: <5 matches

4. **Multi-Theme Assignment**
   - Threads can have multiple themes
   - Primary theme = highest score
   - Secondary themes = scores > threshold

### Classification Statistics
- Threads classified: 1,363
- Multi-themed threads: 297
- Average confidence: 0.75
- Processing time: ~45 seconds

## Stage 3: Vocabulary Building

### Script: `vocabulary_builder.py`

**Purpose**: Extract revolutionary vocabulary from corpus for classification

### Components

#### PoliticalVocabularyExtractor
Extracts domain-specific terms using regex patterns:

```python
pattern_categories = {
    "class_analysis": [
        r"\b(working|ruling|owning) class\b",
        r"\bclass (consciousness|struggle|war)\b"
    ],
    "labor_patterns": [
        r"\blabor (power|theory|movement)\b",
        r"\b(wage|surplus) (labor|value)\b"
    ],
    # ... more patterns
}
```

#### VocabularyBuilder
Builds comprehensive vocabularies from corpus:

1. **Term Extraction**
   - Pattern-based extraction
   - Frequency analysis
   - Context validation

2. **Quality Filtering**
   - Minimum frequency threshold
   - Relevance scoring
   - Manual curation support

3. **YAML Generation**
   ```yaml
   theme: marxism_historical_materialism
   keywords:
     - class struggle
     - dialectical materialism
     - historical materialism
   patterns:
     - \bclass (consciousness|struggle)\b
     - \bmaterial (conditions|base)\b
   ```

### Vocabulary Statistics
- Total terms extracted: 858
- Unique patterns: 127
- Coverage rate: 89% of corpus

## Stage 4: Markdown Generation

### Script: `generate_themed_markdown.py`

**Purpose**: Convert classified threads to MkDocs-ready markdown

### Data Flow
```
Input:  data/classified_threads.json
Output: markdown/[theme]/[thread_files].md
```

### Generation Process

1. **Directory Structure**
   ```
   markdown/
   ├── index.md                    # Home page
   ├── themes/
   │   └── index.md               # Theme overview
   ├── marxism_historical materialism/
   │   ├── index.md               # Theme landing
   │   └── [thread_files].md      # Individual threads
   ├── political economy/
   │   └── ...
   └── tags.md                     # Tag navigation
   ```

2. **Frontmatter Generation**
   ```yaml
   ---
   title: "Thread Title"
   date: 2024-01-15
   tags:
     - capitalism
     - class struggle
   theme: marxism_historical materialism
   thread_id: abc123
   word_count: 1250
   ---
   ```

3. **Content Formatting**
   - Preserve thread structure
   - Add navigation links
   - Format quotes and citations
   - Include metadata

4. **Index Generation**
   - Theme landing pages
   - Chronological listings
   - Tag aggregation
   - Statistics

### Output Statistics
- Markdown files generated: 1,363
- Theme directories: 8
- Average file size: 2KB
- Total output size: ~3MB

## Error Handling

### Common Issues and Solutions

| Issue | Solution | Script |
|-------|----------|--------|
| Memory overflow | Increase chunk size in ijson | local_filter_pipeline.py |
| SpaCy model not found | Run `./install_spacy_model.sh` | All NLP scripts |
| Theme mismatch | Update vocabulary patterns | theme_classifier.py |
| Markdown formatting | Check frontmatter syntax | generate_themed_markdown.py |
| MkDocs build failure | Validate mkdocs.yml | - |

### Error Recovery
```python
# All scripts include comprehensive error handling
try:
    result = process_data()
except ProcessingError as e:
    logger.error(f"Processing failed: {e}")
    # Attempt recovery or graceful degradation
    result = fallback_process()
```

## Performance Optimization

### Memory Management
- **Streaming JSON**: Process large files without loading into memory
- **Batch Processing**: Process threads in configurable chunks
- **Lazy Loading**: Load resources only when needed

### Speed Optimization
- **Pattern Caching**: Pre-compile regex patterns
- **Parallel Processing**: Multi-thread where possible
- **Index Building**: Pre-build search indices

### Benchmarks
| Metric | Value | Target |
|--------|-------|--------|
| Total pipeline time | ~2 min | <5 min |
| Peak memory usage | 450MB | <1GB |
| Thread processing rate | 11/sec | >10/sec |
| Classification speed | 30/sec | >25/sec |

## Configuration Files

### Pipeline Configuration
```yaml
# config/pipeline.yml
stages:
  extraction:
    chunk_size: 1000
    min_engagement: 2
  classification:
    confidence_threshold: 0.5
    max_themes: 3
  generation:
    output_dir: markdown
    include_metadata: true
```

### NLP Configuration
```yaml
# config/nlp_settings.yaml
spacy:
  model: en_core_web_lg
  pipeline:
    - tokenizer
    - tagger
    - parser
    - ner
```

## Monitoring and Logging

### Log Levels
```python
# Set via environment variable
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Progress Tracking
```
[INFO] Starting pipeline...
[INFO] Stage 1: Extracting threads... 1363/21723 (6.3%)
[INFO] Stage 2: Classifying themes... 500/1363 (36.7%)
[INFO] Stage 3: Generating markdown... 1000/1363 (73.3%)
[INFO] Pipeline complete in 2m 15s
```

### Metrics Collection
- Processing time per stage
- Memory usage snapshots
- Error counts and types
- Output quality scores

## Validation and Testing

### Data Validation
```bash
# Validate output files
uv run python -m pytest tests/integration/test_filter_pipeline.py

# Check classification accuracy
uv run python scripts/validate_classification.py
```

### Quality Checks
- Thread integrity validation
- Classification consistency
- Markdown syntax verification
- Link validation

## Troubleshooting Guide

### Issue: Pipeline hangs during extraction
**Cause**: Large malformed JSON in archive
**Solution**:
```bash
# Validate archive structure
python -m json.tool source/data/tweets.js > /dev/null
```

### Issue: Low classification confidence
**Cause**: Insufficient vocabulary patterns
**Solution**:
```bash
# Rebuild vocabularies with lower threshold
uv run python scripts/vocabulary_builder.py --min-freq 2
```

### Issue: Markdown generation fails
**Cause**: Invalid characters in thread text
**Solution**:
```python
# Enable strict text cleaning
generate_themed_markdown.py --strict-clean
```

---

*Last Updated: 2025-09-25 | Pipeline Version: 0.8.1*