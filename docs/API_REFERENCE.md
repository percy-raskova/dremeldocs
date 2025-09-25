# DremelDocs API Reference

## Core Pipeline Modules

### `scripts/local_filter_pipeline.py`
Extract and filter Twitter threads from archive data.

#### Functions

##### `process_archive(archive_path: str) -> List[Thread]`
Main entry point for processing Twitter archive.
- **Parameters**:
  - `archive_path`: Path to Twitter archive JSON file
- **Returns**: List of filtered thread objects
- **Raises**: `FileNotFoundError` if archive doesn't exist

##### `detect_threads(tweets: List[Tweet]) -> List[Thread]`
Identify reply chains and group into threads.
- **Algorithm**: Builds graph of reply relationships
- **Minimum**: 2 tweets to qualify as thread
- **Returns**: List of thread objects with metadata

##### `filter_quality(threads: List[Thread]) -> List[Thread]`
Apply quality filters to extracted threads.
- **Filters**:
  - Minimum length: 100 characters
  - Language: English only
  - Quality score threshold
- **Returns**: Filtered thread list

---

### `scripts/theme_classifier.py`
Classify threads by themes and generate markdown output.

#### Functions

##### `classify_threads(threads: List, themes: Dict) -> Dict[str, List]`
Apply theme classification to threads.
- **Parameters**:
  - `threads`: List of thread objects
  - `themes`: Dictionary of theme definitions
- **Returns**: Dictionary mapping themes to thread lists

##### `generate_markdown(classified: Dict, output_dir: str) -> int`
Generate markdown files from classified threads.
- **Parameters**:
  - `classified`: Theme-to-threads mapping
  - `output_dir`: Target directory for markdown
- **Returns**: Number of files generated

##### `clear_markdown(output_dir: str) -> None`
Clean markdown output directory.
- **Usage**: `--clear-only` flag
- **Safety**: Prompts for confirmation

---

### `scripts/nlp_core.py`
Natural language processing utilities.

#### Classes

##### `EnhancedTagExtractor`
Advanced tag extraction with relevance scoring.

**Methods**:
- `extract_tags(text: str, max_tags: int = 5) -> List[Tag]`
  - Extract and score noun phrases
  - Returns ranked tag list

- `score_chunk(chunk: str) -> float`
  - Calculate relevance score for text chunk
  - Uses TF-IDF and domain vocabulary

##### `ChunkScorer`
Score text chunks for relevance.

**Methods**:
- `calculate_score(text: str, vocabulary: List[str]) -> float`
  - Score text against domain vocabulary
  - Returns normalized score 0-1

##### `DomainVocabulary`
Manage domain-specific terminology.

**Methods**:
- `load_vocabulary(path: str) -> Dict`
  - Load vocabulary from YAML file
  - Supports hierarchical categories

- `match_terms(text: str) -> List[str]`
  - Find domain terms in text
  - Returns matched vocabulary items

---

### `scripts/text_utilities.py`
Text processing and manipulation utilities.

#### Functions

##### `clean_text(text: str) -> str`
Remove artifacts and normalize text.
- **Operations**: Strip URLs, mentions, hashtags
- **Returns**: Cleaned text string

##### `extract_metadata(tweet: Dict) -> Dict`
Extract relevant metadata from tweet object.
- **Fields**: id, created_at, reply_to, user info
- **Returns**: Metadata dictionary

##### `format_thread(thread: Thread) -> str`
Format thread for markdown output.
- **Template**: Frontmatter + formatted content
- **Returns**: Markdown-ready string

---

### `scripts/tag_extraction.py`
Tag extraction and management.

#### Functions

##### `extract_hashtags(text: str) -> List[str]`
Extract hashtags from text.
- **Pattern**: `#\w+`
- **Returns**: List of hashtags without #

##### `extract_mentions(text: str) -> List[str]`
Extract user mentions.
- **Pattern**: `@\w+`
- **Returns**: List of usernames without @

##### `generate_tag_cloud(tags: List[str]) -> Dict`
Generate tag frequency distribution.
- **Returns**: Tag-to-count mapping

---

### `scripts/error_handling.py`
Centralized error handling and logging.

#### Classes

##### `PipelineError(Exception)`
Base exception for pipeline errors.
- **Attributes**: message, error_code, context

##### `DataValidationError(PipelineError)`
Data validation failures.
- **Usage**: Invalid JSON, missing fields

##### `ProcessingError(PipelineError)`
Processing stage failures.
- **Usage**: NLP errors, classification failures

#### Functions

##### `setup_logging(level: str = "INFO") -> None`
Configure application logging.
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Output**: Console and file logging

##### `handle_error(error: Exception, context: Dict) -> None`
Centralized error handler.
- **Actions**: Log, notify, recover
- **Context**: Error details and state

---

### `scripts/vocabulary_builder.py`
Build and manage domain vocabularies.

#### Classes

##### `VocabularyBuilder`
Construct domain-specific vocabularies.

**Methods**:
- `build_from_corpus(texts: List[str]) -> Dict`
  - Extract domain vocabulary from corpus
  - Uses TF-IDF and pattern matching

- `merge_vocabularies(vocabs: List[Dict]) -> Dict`
  - Combine multiple vocabulary sources
  - Resolves conflicts and duplicates

- `save_vocabulary(vocab: Dict, path: str) -> None`
  - Persist vocabulary to YAML
  - Maintains hierarchy and metadata

---

## Data Structures

### Thread
```python
@dataclass
class Thread:
    id: str
    tweets: List[Tweet]
    created_at: datetime
    author: str
    word_count: int
    tags: List[str]
    themes: List[str] = field(default_factory=list)
```

### Tweet
```python
@dataclass
class Tweet:
    id: str
    text: str
    created_at: str
    reply_to_status_id: Optional[str]
    user: Dict[str, Any]
    metrics: Dict[str, int]
```

### Tag
```python
@dataclass
class Tag:
    text: str
    score: float
    category: Optional[str]
    frequency: int = 1
```

---

## Configuration

### Pipeline Configuration
Location: `config/pipeline.yml`

```yaml
pipeline:
  input:
    archive_path: "twitter-archives/data/tweets.js"
    encoding: "utf-8"

  filtering:
    min_length: 100
    min_thread_size: 2
    heavy_hitter_threshold: 500

  output:
    threads_file: "data/filtered_threads.json"
    heavy_hitters_dir: "docs/heavy_hitters"
    markdown_dir: "markdown/themes"
```

### NLP Configuration
Location: `config/nlp_settings.yaml`

```yaml
nlp:
  model: "en_core_web_lg"
  chunk_size: 512
  overlap: 50

  scoring:
    tf_idf_weight: 0.6
    domain_weight: 0.4
    min_score: 0.3
```

---

## Error Codes

| Code | Error | Description |
|------|-------|-------------|
| E001 | FileNotFound | Input file doesn't exist |
| E002 | InvalidJSON | Malformed JSON structure |
| E003 | ModelLoadError | SpaCy model loading failed |
| E004 | ClassificationError | Theme classification failed |
| E005 | OutputError | File writing failed |
| E006 | ValidationError | Data validation failed |

---

## CLI Usage

### local_filter_pipeline.py
```bash
uv run python scripts/local_filter_pipeline.py \
  --input twitter-archives/data/tweets.js \
  --output data/filtered_threads.json \
  --min-length 100 \
  --verbose
```

### theme_classifier.py
```bash
# Clear and regenerate
uv run python scripts/theme_classifier.py

# Clear only
uv run python scripts/theme_classifier.py --clear-only

# Skip clearing
uv run python scripts/theme_classifier.py --no-clear
```

### run_full_pipeline.py
```bash
# Run complete pipeline
uv run python scripts/run_full_pipeline.py

# Dry run
uv run python scripts/run_full_pipeline.py --dry-run

# Verbose output
uv run python scripts/run_full_pipeline.py --verbose
```

---

## Testing

### Unit Test Coverage
```python
# Test a specific module
uv run pytest tests/unit/test_nlp_core.py -v

# Test with coverage
uv run pytest tests/unit/ --cov=scripts.nlp_core

# Generate HTML report
uv run pytest tests/ --cov=scripts --cov-report=html
```

### Integration Testing
```python
# Full pipeline test
uv run pytest tests/integration/test_end_to_end.py

# Test with sample data
uv run pytest tests/integration/ --use-fixtures
```

---

## Performance Benchmarks

| Operation | Average Time | Memory Usage |
|-----------|-------------|--------------|
| Archive parsing | 1.2s | 45MB |
| Thread detection | 0.8s | 30MB |
| NLP processing | 15s | 120MB |
| Classification | 5s | 50MB |
| Markdown generation | 2s | 20MB |
| **Total Pipeline** | ~24s | 50MB peak |

---

*API Reference v1.0 | Generated: 2025-09-23*