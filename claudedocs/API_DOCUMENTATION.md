# DremelDocs API Documentation

## Core Modules

### scripts.local_filter_pipeline

#### Class: LocalThreadExtractor

**Purpose**: Extract and reconstruct Twitter threads from raw archive data.

##### Constructor
```python
LocalThreadExtractor(archive_path: str)
```

**Parameters:**
- `archive_path` (str): Path to Twitter archive directory containing tweets.js

**Raises:**
- `FileNotFoundError`: If tweets.js not found in archive
- `ValueError`: If archive structure is invalid

##### Methods

###### stream_tweets()
```python
def stream_tweets(self) -> Generator[Dict[str, Any], None, None]
```
Stream tweets from archive using memory-efficient parsing.

**Yields:**
- `Dict[str, Any]`: Individual tweet objects

**Example:**
```python
extractor = LocalThreadExtractor("source/data")
for tweet in extractor.stream_tweets():
    print(tweet['full_text'])
```

###### apply_stage1_filter()
```python
def apply_stage1_filter(self, tweet: Dict[str, Any]) -> bool
```
Apply language and quality filters.

**Parameters:**
- `tweet` (Dict): Tweet object to filter

**Returns:**
- `bool`: True if tweet passes filter

###### reconstruct_threads()
```python
def reconstruct_threads(self) -> None
```
Build conversation threads from individual tweets.

**Side Effects:**
- Populates `self.threads` with reconstructed threads
- Updates `self.reply_map` with conversation chains

###### generate_json_output()
```python
def generate_json_output(self, output_file: str = "data/filtered_threads.json") -> Dict[str, Any]
```
Generate filtered thread JSON output.

**Parameters:**
- `output_file` (str): Path for output JSON file

**Returns:**
- `Dict`: Statistics about processed threads

### scripts.theme_classifier

#### Class: ThemeClassifier

**Purpose**: Classify threads into revolutionary theory themes using NLP pattern matching.

##### Constructor
```python
ThemeClassifier(themes_file: Optional[str] = None)
```

**Parameters:**
- `themes_file` (str, optional): Path to themes configuration file

##### Methods

###### load_vocabulary()
```python
def load_vocabulary(self, vocab_dir: str = "data/vocabularies") -> Dict[str, Dict]
```
Load theme vocabularies from YAML files.

**Parameters:**
- `vocab_dir` (str): Directory containing vocabulary YAML files

**Returns:**
- `Dict[str, Dict]`: Theme vocabularies with patterns and keywords

**Example:**
```python
classifier = ThemeClassifier()
vocabs = classifier.load_vocabulary("data/vocabularies")
print(vocabs.keys())  # ['marxism', 'fascism_analysis', ...]
```

###### classify_with_patterns()
```python
def classify_with_patterns(self, text: str, use_cached: bool = True) -> Dict[str, Any]
```
Classify text using pattern matching against vocabularies.

**Parameters:**
- `text` (str): Text content to classify
- `use_cached` (bool): Use cached classification if available

**Returns:**
```python
{
    "themes": ["marxism", "political_economy"],
    "confidence": 0.85,
    "matched_terms": ["class struggle", "surplus value"],
    "scores": {"marxism": 15, "political_economy": 12}
}
```

###### process_all_threads()
```python
def process_all_threads(
    self,
    input_file: str = "data/filtered_threads.json",
    output_file: str = "data/classified_threads.json"
) -> Dict[str, Any]
```
Process and classify all threads from input file.

**Parameters:**
- `input_file` (str): Path to filtered threads JSON
- `output_file` (str): Path for classified output

**Returns:**
- `Dict`: Processing statistics and theme distribution

### scripts.vocabulary_builder

#### Class: PoliticalVocabularyExtractor

**Purpose**: Extract political and philosophical vocabulary using regex patterns.

##### Pattern Categories
```python
PATTERN_CATEGORIES = {
    "class_analysis": [...],
    "labor_patterns": [...],
    "revolutionary_org": [...],
    "imperialism": [...],
    "philosophical": [...]
}
```

##### Methods

###### extract_terms()
```python
def extract_terms(self, text: str) -> Dict[str, List[str]]
```
Extract vocabulary terms from text using patterns.

**Parameters:**
- `text` (str): Source text for extraction

**Returns:**
- `Dict[str, List[str]]`: Categorized extracted terms

#### Class: VocabularyBuilder

**Purpose**: Build and manage domain-specific vocabularies.

##### Constructor
```python
VocabularyBuilder(min_freq: int = 3, quality_threshold: float = 0.7)
```

**Parameters:**
- `min_freq` (int): Minimum term frequency for inclusion
- `quality_threshold` (float): Quality score threshold

##### Methods

###### build_from_corpus()
```python
def build_from_corpus(
    self,
    texts: List[str],
    category: str = "general"
) -> Dict[str, Any]
```
Build vocabulary from text corpus.

**Parameters:**
- `texts` (List[str]): Corpus of texts
- `category` (str): Vocabulary category name

**Returns:**
```python
{
    "terms": ["term1", "term2", ...],
    "frequencies": {"term1": 5, "term2": 3},
    "patterns": ["pattern1", "pattern2"],
    "statistics": {...}
}
```

### scripts.text_utilities

#### Functions

##### clean_text()
```python
def clean_text(
    text: str,
    remove_urls: bool = True,
    remove_mentions: bool = True,
    normalize_whitespace: bool = True
) -> str
```
Clean and normalize text content.

**Parameters:**
- `text` (str): Input text
- `remove_urls` (bool): Remove URLs
- `remove_mentions` (bool): Remove @mentions
- `normalize_whitespace` (bool): Normalize whitespace

**Returns:**
- `str`: Cleaned text

##### extract_hashtags()
```python
def extract_hashtags(text: str) -> List[str]
```
Extract and normalize hashtags from text.

**Parameters:**
- `text` (str): Source text

**Returns:**
- `List[str]`: List of hashtags (without #)

##### generate_slug()
```python
def generate_slug(text: str, max_length: int = 50) -> str
```
Generate URL-safe slug from text.

**Parameters:**
- `text` (str): Source text
- `max_length` (int): Maximum slug length

**Returns:**
- `str`: URL-safe slug

### scripts.nlp_core

#### Functions

##### load_spacy_model()
```python
def load_spacy_model(model_name: str = "en_core_web_lg") -> spacy.Language
```
Load and cache SpaCy language model.

**Parameters:**
- `model_name` (str): SpaCy model name

**Returns:**
- `spacy.Language`: Loaded NLP model

**Raises:**
- `OSError`: If model not installed

##### extract_entities()
```python
def extract_entities(
    text: str,
    entity_types: List[str] = ["PERSON", "ORG", "GPE"]
) -> List[Dict[str, str]]
```
Extract named entities from text.

**Parameters:**
- `text` (str): Source text
- `entity_types` (List[str]): Entity types to extract

**Returns:**
```python
[
    {"text": "Marx", "type": "PERSON"},
    {"text": "Paris Commune", "type": "EVENT"}
]
```

### scripts.error_handling

#### Class: ErrorHandler

**Purpose**: Centralized error handling and recovery.

##### Methods

###### handle_error()
```python
@staticmethod
def handle_error(
    error: Exception,
    context: str,
    critical: bool = False
) -> Optional[Any]
```
Handle errors with appropriate logging and recovery.

**Parameters:**
- `error` (Exception): The exception to handle
- `context` (str): Error context description
- `critical` (bool): Whether error is critical

**Returns:**
- `Optional[Any]`: Recovery result or None

#### Custom Exceptions

##### ProcessingError
```python
class ProcessingError(Exception):
    """Raised when pipeline processing fails."""
    pass
```

##### ValidationError
```python
class ValidationError(Exception):
    """Raised when data validation fails."""
    pass
```

## Data Formats

### Thread Object
```json
{
  "thread_id": "1234567890",
  "created_at": "2024-01-15T10:30:00Z",
  "author": "BmoreOrganized",
  "text": "Full concatenated thread text...",
  "tweet_count": 5,
  "total_favorites": 150,
  "total_retweets": 45,
  "hashtags": ["theory", "marxism"],
  "urls": ["https://example.com"],
  "tweets": [
    {
      "id": "1234567890",
      "full_text": "Individual tweet text...",
      "created_at": "2024-01-15T10:30:00Z",
      "favorite_count": 30,
      "retweet_count": 10
    }
  ]
}
```

### Classification Result
```json
{
  "thread_id": "1234567890",
  "themes": ["marxism_historical_materialism", "political_economy"],
  "primary_theme": "marxism_historical_materialism",
  "confidence": 0.85,
  "matched_terms": ["class struggle", "dialectical", "capital"],
  "scores": {
    "marxism_historical_materialism": 15,
    "political_economy": 12,
    "dialectics": 5
  },
  "classification_metadata": {
    "classifier_version": "0.8.1",
    "timestamp": "2025-09-25T10:30:00Z"
  }
}
```

### Vocabulary Format (YAML)
```yaml
theme: marxism_historical_materialism
description: Marxist theory and historical materialism concepts
keywords:
  - class struggle
  - dialectical materialism
  - historical materialism
  - mode of production
patterns:
  - \bclass (consciousness|struggle|war)\b
  - \bmaterial (conditions|base|reality)\b
  - \bmode of production\b
statistics:
  term_count: 45
  pattern_count: 12
  coverage: 0.89
```

## Extension Points

### Custom Classifiers

Implement custom classification logic:

```python
from scripts.theme_classifier import ThemeClassifier

class CustomClassifier(ThemeClassifier):
    def custom_classify(self, text: str) -> Dict:
        # Your classification logic
        base_result = self.classify_with_patterns(text)

        # Add custom scoring
        if "specific_term" in text.lower():
            base_result["themes"].append("custom_theme")

        return base_result
```

### Custom Filters

Add custom filtering stages:

```python
from scripts.local_filter_pipeline import LocalThreadExtractor

class CustomExtractor(LocalThreadExtractor):
    def apply_custom_filter(self, tweet: Dict) -> bool:
        # Custom filter logic
        if tweet.get('user', {}).get('verified'):
            return True
        return self.apply_stage2_filter(tweet)
```

### Plugin Architecture

Register custom processors:

```python
# plugins/custom_processor.py
class CustomProcessor:
    def process(self, data: Dict) -> Dict:
        # Processing logic
        return modified_data

# Register in pipeline
from plugins.custom_processor import CustomProcessor

pipeline.register_processor(CustomProcessor())
```

## Configuration API

### Pipeline Configuration
```python
# config/loader.py
from config.loader import ConfigLoader

config = ConfigLoader("config/pipeline.yml")
settings = config.get_settings()

# Access configuration
chunk_size = settings['extraction']['chunk_size']
themes = settings['classification']['themes']
```

### Dynamic Configuration
```python
# Runtime configuration override
classifier = ThemeClassifier()
classifier.update_config({
    'confidence_threshold': 0.7,
    'max_themes': 5
})
```

## Testing Utilities

### Test Fixtures
```python
from tests.fixtures.sample_data import (
    sample_tweet,
    sample_thread,
    sample_classification
)

def test_classification():
    thread = sample_thread()
    result = classifier.classify_thread(thread)
    assert result['themes']
```

### Validation Utilities
```python
from tests.utils.validation import (
    validate_thread_structure,
    validate_classification,
    validate_markdown
)

def test_output_validation():
    data = load_json("output.json")
    is_valid = validate_thread_structure(data)
    assert is_valid
```

## Performance APIs

### Monitoring
```python
from scripts.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()
with monitor.track("classification"):
    result = classifier.process_all_threads()

print(monitor.get_metrics())
# {'classification': {'duration': 45.2, 'memory': 234}}
```

### Batch Processing
```python
from scripts.batch import BatchProcessor

processor = BatchProcessor(chunk_size=100)
results = processor.process_in_batches(
    data=threads,
    handler=classifier.classify_thread
)
```

## Integration Examples

### Web API Integration
```python
from flask import Flask, jsonify
from scripts.theme_classifier import ThemeClassifier

app = Flask(__name__)
classifier = ThemeClassifier()

@app.route('/classify', methods=['POST'])
def classify_text():
    text = request.json['text']
    result = classifier.classify_with_patterns(text)
    return jsonify(result)
```

### Database Integration
```python
import sqlite3
from scripts.local_filter_pipeline import LocalThreadExtractor

def save_to_database(threads):
    conn = sqlite3.connect('threads.db')
    cursor = conn.cursor()

    for thread in threads:
        cursor.execute(
            "INSERT INTO threads (id, text, themes) VALUES (?, ?, ?)",
            (thread['thread_id'], thread['text'], json.dumps(thread['themes']))
        )

    conn.commit()
    conn.close()
```

### Streaming Processing
```python
from scripts.streaming import StreamProcessor

processor = StreamProcessor()
for result in processor.stream_process("tweets.js"):
    # Process results as they become available
    print(f"Processed thread: {result['thread_id']}")
```

---

*API Documentation v0.8.1 | Last Updated: 2025-09-25*