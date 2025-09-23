# AstraDocs API Reference 📚

Complete API documentation for all scripts and modules in the AstraDocs pipeline.

## Scripts Overview

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `local_filter_pipeline.py` | Main filtering pipeline | Twitter archive | Filtered threads JSON |
| `generate_heavy_hitters.py` | Extract long threads | Filtered threads | Markdown files |
| `theme_classifier.py` | Apply theme classification | Themes + threads | Classified JSON |

---

## `local_filter_pipeline.py`

Main script for processing Twitter archive and extracting meaningful threads.

### Classes

#### `LocalThreadExtractor`
```python
class LocalThreadExtractor:
    def __init__(self, archive_dir: str)
```

**Parameters:**
- `archive_dir` (str): Path to Twitter archive directory containing `data/tweets.js`

**Methods:**

##### `stream_tweets() -> Generator[Dict[str, Any], None, None]`
Stream tweets from the archive file without loading into memory.

**Returns:**
- Generator yielding individual tweet dictionaries

**Example:**
```python
extractor = LocalThreadExtractor("source")
for tweet in extractor.stream_tweets():
    print(tweet['text'])
```

##### `extract_threads(tweets: List[Dict]) -> List[List[Dict]]`
Reconstruct thread conversations from individual tweets.

**Parameters:**
- `tweets`: List of tweet dictionaries

**Returns:**
- List of threads (each thread is a list of tweets)

##### `filter_threads(threads: List[List[Dict]]) -> List[Dict]`
Apply filtering criteria to identify meaningful threads.

**Parameters:**
- `threads`: List of thread arrays

**Returns:**
- List of filtered thread objects with metadata

##### `run_pipeline() -> None`
Execute the complete filtering pipeline.

**Side Effects:**
- Creates `data/filtered_threads.json`
- Creates sample markdown files in `data/sample_threads/`

### Usage
```bash
python scripts/local_filter_pipeline.py
```

### Output Format
```json
{
    "thread_id": "1234567890",
    "created_at": "2023-01-01T12:00:00Z",
    "tweet_count": 5,
    "word_count": 523,
    "smushed_text": "Full thread text concatenated...",
    "tweets": [...]
}
```

---

## `generate_heavy_hitters.py`

Extract threads with 500+ words for manual theme extraction.

### Functions

#### `load_threads(filepath: str = "data/filtered_threads.json") -> List[Dict]`
Load filtered threads from JSON file.

**Parameters:**
- `filepath`: Path to filtered threads JSON

**Returns:**
- List of thread dictionaries

#### `filter_heavy_hitters(threads: List[Dict], min_words: int = 500) -> List[Dict]`
Filter threads by word count threshold.

**Parameters:**
- `threads`: List of thread objects
- `min_words`: Minimum word count (default: 500)

**Returns:**
- List of threads meeting word count criteria

#### `generate_markdown(thread: Dict, output_dir: Path) -> str`
Generate markdown file for a single thread.

**Parameters:**
- `thread`: Thread dictionary
- `output_dir`: Directory for output files

**Returns:**
- Filename of generated markdown

**Markdown Format:**
```markdown
# Thread from [date]

**Thread ID**: 1234567890
**Word Count**: 523
**Tweet Count**: 5

---

[Thread content in readable format]

---

## Metadata
- Created: 2023-01-01
- URL: https://twitter.com/user/status/1234567890
```

#### `create_index(threads: List[Dict], output_dir: Path) -> None`
Generate index file listing all heavy hitter threads.

**Parameters:**
- `threads`: List of heavy hitter threads
- `output_dir`: Output directory

**Creates:**
- `index.md` with links to all threads
- `THEME_TEMPLATE.md` for manual theme extraction

### Usage
```bash
python scripts/generate_heavy_hitters.py
```

### Output
- Individual markdown files in `docs/heavy_hitters/`
- `index.md` with thread listing
- `THEME_TEMPLATE.md` for theme extraction

---

## `theme_classifier.py`

Apply theme classification to all threads based on extracted patterns.

### Classes

#### `ThemeClassifier`
```python
class ThemeClassifier:
    def __init__(self, themes_file: str = "THEMES_EXTRACTED.md")
```

**Parameters:**
- `themes_file`: Path to file containing extracted themes

**Methods:**

##### `load_themes() -> Dict[str, List[str]]`
Load theme definitions from markdown file.

**Returns:**
- Dictionary mapping theme names to keyword lists

**Expected Format:**
```markdown
## Philosophy
- epistemology, ontology, metaphysics
- ethics, morality, virtue

## Politics
- capitalism, socialism, imperialism
- class, labor, revolution
```

##### `classify_thread(thread: Dict) -> Tuple[List[str], float]`
Classify a single thread based on theme patterns.

**Parameters:**
- `thread`: Thread dictionary with 'smushed_text'

**Returns:**
- Tuple of (detected_themes, confidence_score)

##### `classify_all_threads() -> Dict[str, List[Dict]]`
Classify all filtered threads and organize by category.

**Returns:**
- Dictionary mapping categories to thread lists

##### `generate_markdown_output(classified: Dict[str, List[Dict]]) -> None`
Generate markdown files organized by theme.

**Parameters:**
- `classified`: Dictionary of categorized threads

**Creates:**
- Markdown files in `markdown/[category]/`
- Index files for each category

### Usage
```bash
# First, create THEMES_EXTRACTED.md with your themes
python scripts/theme_classifier.py
```

### Output Format
```json
{
    "philosophy": [
        {
            "thread_id": "123",
            "themes": ["epistemology", "ethics"],
            "confidence": 0.85,
            "content": {...}
        }
    ],
    "politics": [...],
    "both": [...]
}
```

---

## Data Formats

### Thread Object Schema
```typescript
interface Thread {
    thread_id: string;
    created_at: string;  // ISO 8601
    tweet_count: number;
    word_count: number;
    smushed_text: string;
    tweets: Tweet[];

    // Added by classifier
    themes?: string[];
    confidence?: number;
    category?: string;
}
```

### Tweet Object Schema
```typescript
interface Tweet {
    id_str: string;
    text: string;
    created_at: string;
    in_reply_to_status_id?: string;
    favorite_count: number;
    retweet_count: number;
}
```

---

## Error Handling

### Common Errors

#### FileNotFoundError
```python
# Thrown when Twitter archive not found
LocalThreadExtractor("missing_dir")
# Solution: Ensure archive is in correct location
```

#### JSONDecodeError
```python
# Thrown when tweets.js is malformed
# Solution: Check Twitter export integrity
```

#### MemoryError
```python
# Should not occur with streaming
# If it does, check ijson installation
```

### Error Recovery
All scripts include try-catch blocks with graceful failure:
```python
try:
    extractor.run_pipeline()
except Exception as e:
    print(f"Pipeline failed: {e}")
    # Partial results saved in data/
```

---

## Performance Tuning

### Memory Optimization
```python
# Adjust chunk size for streaming
parser = ijson.items(f, 'item', buf_size=65536)
```

### Threading
```python
# Future improvement: parallel thread extraction
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    threads = executor.map(extract_thread, chunks)
```

### Caching
```python
# Cache intermediate results
import pickle
with open('cache/threads.pkl', 'wb') as f:
    pickle.dump(threads, f)
```

---

## CLI Usage (Future)

### Planned CLI Interface
```bash
# Full pipeline
astradocs process --input source/ --output markdown/

# Individual stages
astradocs filter --input source/
astradocs classify --themes THEMES.md
astradocs generate --format markdown

# Options
--verbose       # Detailed logging
--dry-run      # Preview without writing
--parallel     # Use multiple cores
--cache        # Use cached results
```

---

*API designed for simplicity and modularity*