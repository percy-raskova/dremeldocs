# Technical Specifications

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows 10+
- **Python**: 3.9 or higher
- **RAM**: 4GB (8GB recommended for large archives)
- **Storage**: 2x size of Twitter archive
- **Network**: Stable internet for AI API calls

### Development Environment
- **IDE**: VS Code or PyCharm recommended
- **Git**: Version control
- **Terminal**: Bash or PowerShell

## Data Specifications

### Input Format

#### Twitter Archive Structure
```
twitter-archive.zip
├── data/
│   ├── tweets.js          # Main tweet data (10-100MB typical)
│   ├── deleted-tweets.js  # Deleted tweet records
│   ├── profile.js         # User profile information
│   ├── account.js         # Account settings
│   ├── follower.js        # Follower list
│   ├── following.js       # Following list
│   └── [other data files]
└── assets/
    └── [media files]
```

#### Tweet Object Schema
```typescript
interface Tweet {
  tweet: {
    id_str: string;
    created_at: string;  // "Sat Sep 20 19:20:51 +0000 2025"
    full_text: string;
    lang: string;
    favorite_count: string;
    retweet_count: string;
    
    // Thread detection fields (may be null)
    in_reply_to_status_id_str?: string;
    in_reply_to_user_id_str?: string;
    conversation_id?: string;
    
    // Edit information (new feature)
    edit_info?: {
      initial: {
        editTweetIds: string[];
        editableUntil: string;
        editsRemaining: string;
        isEditEligible: boolean;
      }
    };
    
    // Entities
    entities: {
      hashtags: Array<{text: string; indices: number[]}>;
      user_mentions: Array<{screen_name: string; id_str: string}>;
      urls: Array<{
        url: string;  // t.co shortened
        expanded_url: string;  // actual URL
        display_url: string;
        indices: number[];
      }>;
    };
    
    // Metadata
    source: string;  // HTML string with client info
    possibly_sensitive?: boolean;
    retweeted: boolean;
    favorited: boolean;
  }
}
```

### Processing Specifications

#### Thread Detection Algorithm

```python
# Pseudocode for thread detection priority
def detect_thread(tweets):
    threads = []
    
    # Priority 1: Explicit conversation_id
    if has_conversation_ids(tweets):
        threads.extend(group_by_conversation_id(tweets))
    
    # Priority 2: Reply chains
    threads.extend(follow_reply_chains(tweets))
    
    # Priority 3: Self-replies
    threads.extend(find_self_replies(tweets))
    
    # Priority 4: Temporal clustering
    threads.extend(cluster_by_time(tweets, window=30_minutes))
    
    # Priority 5: Thread numbering patterns
    threads.extend(find_numbered_threads(tweets))
    
    return deduplicate(threads)
```

#### Classification Criteria

| Category | Indicators | Weight |
|----------|-----------|--------|
| **Philosophical** | Keywords: epistemology, ontology, metaphysics, consciousness | 0.4 |
| **Political** | Keywords: capitalism, democracy, ideology, hegemony | 0.4 |
| **Theoretical** | Abstract reasoning, citations, academic language | 0.3 |
| **Thread Length** | 3+ tweets in sequence | 0.2 |
| **Engagement** | High retweet/favorite ratio | 0.1 |

### Output Specifications

#### Markdown Format
```markdown
---
title: "Thread Title (first 50 chars)"
date: 2025-09-20
time: 19:20:51
tags: [philosophy, epistemology, consciousness]
confidence: 0.85
tweet_count: 7
thread_id: "1234567890"
word_count: 523
---

# Thread Title

*Originally posted as a Twitter thread on September 20, 2025*

---

[Original tweet text, unmodified]

[Second tweet text, unmodified]

[Continue for all tweets...]

---

*Thread: 7 tweets, 523 words*
```

#### Directory Structure
```
docs/
├── index.md                 # Main landing page
├── philosophy/
│   ├── index.md            # Philosophy section index
│   ├── metaphysics/
│   │   └── 2025-09-20-consciousness-and-being.md
│   └── epistemology/
│       └── 2025-09-15-knowledge-and-truth.md
├── politics/
│   ├── index.md            # Politics section index
│   ├── theory/
│   │   └── 2025-09-10-marxist-analysis.md
│   └── economy/
│       └── 2025-09-05-labor-and-capital.md
├── archive/
│   ├── index.md            # Chronological archive
│   └── 2025/
│       └── september/
└── tags.md                 # Tag index page
```

## API Specifications

### Anthropic Claude API

```python
# API Request Structure
{
    "model": "claude-3-opus-20240229",
    "max_tokens": 500,
    "temperature": 0.3,
    "messages": [
        {
            "role": "user",
            "content": "Classification prompt with thread text"
        }
    ]
}

# Expected Response
{
    "content": [
        {
            "type": "text",
            "text": "{\"classification\": \"serious\", \"confidence\": 0.85, ...}"
        }
    ]
}
```

### Rate Limiting
- **Default**: 10 requests/minute
- **Backoff Strategy**: Exponential backoff with jitter
- **Retry Attempts**: 3 with 5-second delays

## Performance Specifications

### Processing Benchmarks

| Operation | Expected Time | Memory Usage |
|-----------|--------------|--------------|
| Extract 10K tweets | 5-10 seconds | ~200MB |
| Detect threads (10K tweets) | 10-15 seconds | ~300MB |
| Classify 100 threads | 10-15 minutes | ~100MB |
| Generate Markdown | 5 seconds | ~50MB |
| Build MkDocs site | 10-20 seconds | ~100MB |

### Optimization Strategies

#### Memory Optimization
```python
# Stream processing for large files
def stream_process_tweets(file_path, batch_size=1000):
    with open(file_path, 'r') as f:
        batch = []
        for line in f:
            batch.append(json.loads(line))
            if len(batch) >= batch_size:
                yield process_batch(batch)
                batch = []
        if batch:
            yield process_batch(batch)
```

#### Parallel Processing
```python
# Parallel classification with worker pool
async def parallel_classify(threads, max_workers=5):
    semaphore = asyncio.Semaphore(max_workers)
    
    async def classify_with_limit(thread):
        async with semaphore:
            return await classify_thread(thread)
    
    tasks = [classify_with_limit(t) for t in threads]
    return await asyncio.gather(*tasks)
```

## Error Handling

### Error Recovery Matrix

| Error Type | Recovery Strategy | User Action |
|------------|------------------|-------------|
| API Rate Limit | Exponential backoff | Wait or reduce rate |
| API Timeout | Retry with longer timeout | Check network |
| Malformed JSON | Skip and log | Review logs |
| Missing Fields | Use defaults | Manual review |
| Classification Failure | Default to "serious" | Manual review |
| File I/O Error | Retry with checkpoint | Check permissions |

### Logging Specification

```python
# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/pipeline.log',
            'formatter': 'default'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
    }
}
```

## Security Considerations

### API Key Management
```python
# .env file (never commit!)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Usage
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("API key not found in environment")
```

### Data Privacy
- Twitter archive remains local
- No tweets sent to third parties except AI API
- Classified data stored locally
- No personal information in logs

## Configuration Schema

```yaml
# config/pipeline_config.yaml
pipeline:
  version: "1.0.0"
  
extraction:
  batch_size: 1000
  encoding: "utf-8"
  skip_retweets: true
  skip_deleted: false
  
thread_detection:
  methods:
    - conversation_id
    - reply_chains
    - temporal_clustering
  temporal_window_minutes: 30
  min_thread_length: 2
  
classification:
  provider: "anthropic"  # or "openai"
  model: "claude-3-opus-20240229"
  temperature: 0.3
  max_tokens: 500
  rate_limit_rpm: 10
  confidence_threshold: 0.6
  
  pre_filter:
    min_word_count: 100
    min_thread_length: 3
    
output:
  format: "markdown"
  include_metadata: true
  preserve_formatting: true
  max_title_length: 50
  
mkdocs:
  theme: "material"
  site_name: "Twitter Philosophy Archive"
  features:
    - search
    - tags
    - dark_mode
```

## Testing Specifications

### Unit Test Coverage

```python
# tests/test_extraction.py
def test_javascript_wrapper_removal():
    input_data = 'window.YTD.tweets.part0 = [{"tweet": {...}}]'
    expected = '[{"tweet": {...}}]'
    assert remove_wrapper(input_data) == expected

def test_tweet_parsing():
    tweet = {"tweet": {"id_str": "123", "full_text": "Test"}}
    parsed = parse_tweet(tweet)
    assert parsed["id"] == "123"
    assert parsed["text"] == "Test"
```

### Integration Test Scenarios

1. **Small Archive Test** (10 tweets)
   - Extract → Detect → Classify → Generate
   - Verify all phases complete without errors

2. **Thread Detection Test**
   - Input: Known thread structure
   - Output: Correctly reconstructed thread

3. **Classification Test**
   - Input: Pre-classified samples
   - Output: >80% accuracy on test set

4. **End-to-End Test**
   - Input: Sample archive
   - Output: Complete MkDocs site

## Monitoring and Metrics

### Key Performance Indicators

```python
# Metrics to track
metrics = {
    'extraction': {
        'tweets_processed': 0,
        'extraction_time': 0,
        'errors': []
    },
    'thread_detection': {
        'threads_found': 0,
        'orphan_tweets': 0,
        'detection_time': 0
    },
    'classification': {
        'serious_threads': 0,
        'casual_threads': 0,
        'api_calls': 0,
        'api_errors': 0,
        'average_confidence': 0
    },
    'output': {
        'files_generated': 0,
        'total_word_count': 0,
        'tag_distribution': {}
    }
}
```

### Health Checks

```python
def health_check():
    checks = {
        'api_accessible': check_api_connection(),
        'disk_space': check_disk_space() > 1_000_000_000,  # 1GB
        'memory_available': check_memory() > 500_000_000,  # 500MB
        'python_version': sys.version_info >= (3, 9)
    }
    return all(checks.values()), checks
```

This technical specification provides the detailed requirements and implementation guidelines for the Twitter to MkDocs conversion pipeline.
