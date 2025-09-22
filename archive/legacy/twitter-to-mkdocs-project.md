# Twitter Archive to MkDocs Knowledge Base

## 🎯 Project Overview

Transform a Twitter archive into a curated MkDocs-powered knowledge base, extracting philosophical and political threads to create a permanent, searchable collection of serious intellectual content.

### Core Objectives
- Parse ~1GB Twitter archive (JSON format)
- Identify and extract serious philosophical/political content using AI
- Reconstruct Twitter threads into coherent essays
- Generate a static documentation site with MkDocs
- Deploy to GitHub Pages

### Key Constraints
- **Content Integrity**: No modification of original tweet content (only mechanical corrections)
- **Selective Curation**: Filter out casual posts, memes, and "shitposting"
- **Thread Preservation**: Maintain original thread structure and chronology
- **Scalable Processing**: Handle large archive files efficiently

## 📁 Project Structure

```
twitter-to-mkdocs/
├── README.md                      # This file
├── pyproject.toml                 # Python project configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                    
├── mkdocs.yml                     # MkDocs configuration
│
├── config/
│   ├── settings.yaml              # Project settings
│   ├── classification_rules.yaml  # AI classification parameters
│   └── taxonomy.yaml              # Tag categories and hierarchy
│
├── src/
│   ├── __init__.py
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── archive_extractor.py  # Extract JSON from Twitter archive
│   │   ├── tweet_parser.py       # Parse individual tweets
│   │   └── thread_builder.py     # Reconstruct threads
│   │
│   ├── classifier/
│   │   ├── __init__.py
│   │   ├── ai_classifier.py      # AI-powered content classification
│   │   ├── filters.py            # Rule-based filters
│   │   └── confidence_scorer.py  # Score classification confidence
│   │
│   ├── processor/
│   │   ├── __init__.py
│   │   ├── essay_generator.py    # Convert threads to essays
│   │   ├── tagger.py             # Apply taxonomic tags
│   │   └── markdown_writer.py    # Generate Markdown files
│   │
│   └── utils/
│       ├── __init__.py
│       ├── batch_processor.py    # Handle large file batching
│       ├── rate_limiter.py       # AI API rate limiting
│       └── checkpoint.py         # Resume interrupted processing
│
├── scripts/
│   ├── run_pipeline.py           # Main execution script
│   ├── validate_archive.py       # Validate Twitter archive format
│   ├── preview_classification.py # Test classification on sample
│   └── deploy.sh                 # Deploy to GitHub Pages
│
├── docs/                          # MkDocs content directory
│   ├── index.md                  # Site homepage
│   ├── philosophy/               # Philosophy essays
│   ├── politics/                 # Political essays
│   └── archive/                  # Chronological archive
│
├── templates/
│   ├── essay.md.j2               # Essay markdown template
│   └── index.md.j2               # Index page template
│
├── tests/
│   ├── test_parser/
│   ├── test_classifier/
│   └── test_processor/
│
└── .github/
    └── workflows/
        └── deploy.yml             # GitHub Actions deployment
```

## 🔧 Technical Architecture

### Phase 1: Archive Extraction & Parsing

#### Input Format Detection
```python
# Twitter archives come in different formats:
# - GDPR export: data/tweets.js or data/tweet.js
# - Older format: single JSON file

ARCHIVE_PATTERNS = {
    'gdpr_export': {
        'identifier': 'data/tweets.js',
        'wrapper': 'window.YTD.tweets.part0 = ',
        'structure': 'nested_with_tweet_key'
    },
    'legacy_export': {
        'identifier': '*.json',
        'wrapper': None,
        'structure': 'flat_array'
    }
}
```

#### Key Fields to Extract
```yaml
essential_fields:
  - id_str                 # Unique tweet ID
  - created_at            # Timestamp
  - full_text             # Complete tweet text
  - in_reply_to_status_id_str  # Thread detection
  - conversation_id       # Thread grouping (if available)
  
optional_fields:
  - retweet_count        # Engagement metrics
  - favorite_count       # For relevance scoring
  - entities             # Links, mentions, hashtags
  - extended_entities    # Media attachments
```

### Phase 2: Thread Reconstruction

#### Thread Detection Strategy
```python
class ThreadDetectionStrategy:
    """
    Hierarchical approach to thread detection:
    1. Use conversation_id if available (modern exports)
    2. Follow in_reply_to_status_id chains
    3. Detect temporal proximity patterns (tweets within N minutes)
    4. Identify self-reply chains
    """
    
    def detect_threads(tweets):
        # Primary: conversation_id grouping
        if has_conversation_ids(tweets):
            return group_by_conversation_id(tweets)
            
        # Secondary: reply chain following
        threads = follow_reply_chains(tweets)
        
        # Tertiary: temporal clustering
        threads.extend(detect_temporal_threads(tweets))
        
        return deduplicate_threads(threads)
```

### Phase 3: Content Classification

#### Classification Parameters
```yaml
# classification_rules.yaml
serious_content_indicators:
  vocabulary_markers:
    philosophy:
      - epistemology
      - ontology
      - phenomenology
      - dialectic
      - praxis
      - metaphysics
    politics:
      - political economy
      - governance
      - ideology
      - hegemony
      - sovereignty
      
  structural_markers:
    - multi_tweet_thread: weight: 0.3
    - contains_arguments: weight: 0.4
    - academic_language: weight: 0.2
    - citations_or_quotes: weight: 0.1
    
  minimum_thresholds:
    thread_length: 3         # Minimum tweets for serious thread
    word_count: 280          # Minimum total words
    coherence_score: 0.7     # Semantic coherence threshold
    
edge_case_handling:
  satirical_political: include_if_substantive
  philosophical_popculture: evaluate_depth
  mixed_content_threads: truncate_at_topic_shift
```

#### AI Classification Prompt Template
```python
CLASSIFICATION_PROMPT = """
Analyze the following Twitter thread for philosophical or political content.

Thread content:
{thread_text}

Evaluation criteria:
1. Is this a serious theoretical, philosophical, or political discussion?
2. Does it contain substantive argumentation or analysis?
3. Is it primarily casual, humorous, or social in nature?

Respond with:
- classification: "serious" or "casual"
- confidence: 0.0 to 1.0
- primary_topic: main subject matter
- suggested_tags: list of relevant tags
- reason: brief explanation

Be inclusive rather than exclusive - if unsure, classify as serious.
"""
```

### Phase 4: Batch Processing Strategy

#### Processing Approaches
```yaml
strategies:
  chronological:
    description: Process tweets by time period
    batch_size: 1000 tweets or 1 month
    advantages:
      - Maintains temporal context
      - Natural thread boundaries
    use_when: Standard processing
    
  thread_based:
    description: Process complete threads
    batch_size: 50 threads
    advantages:
      - Complete context for classification
      - No thread fragmentation
    use_when: Thread-heavy archives
    
  memory_optimized:
    description: Stream processing with minimal memory
    batch_size: 100 tweets
    advantages:
      - Handles very large files
      - Checkpoint-friendly
    use_when: Limited system resources
```

### Phase 5: Tagging Taxonomy

#### Hierarchical Tag Structure
```yaml
# taxonomy.yaml
taxonomy:
  philosophy:
    metaphysics:
      - ontology
      - cosmology
      - consciousness
    epistemology:
      - knowledge
      - truth
      - skepticism
    ethics:
      - moral philosophy
      - virtue ethics
      - consequentialism
    political_philosophy:
      - justice
      - liberty
      - authority
      
  politics:
    theory:
      - marxism
      - liberalism
      - anarchism
    economy:
      - capitalism
      - labor
      - inequality
    governance:
      - democracy
      - institutions
      - policy
      
  interdisciplinary:
    - technology-philosophy
    - political-economy
    - social-theory
    
tagging_rules:
  max_tags_per_essay: 5
  require_primary_tag: true
  allow_custom_tags: true
```

### Phase 6: Markdown Generation

#### Frontmatter Template
```yaml
---
title: "{thread_title}"
date: {original_date}
last_updated: {processing_date}
tags: {tags_list}
thread_id: {original_thread_id}
tweet_count: {number_of_tweets}
confidence_score: {classification_confidence}
---
```

#### Essay Structure
```markdown
# {title}

*Originally posted as a Twitter thread on {date}*

{concatenated_tweet_content}

---
*Thread metadata: {tweet_count} tweets, {word_count} words*
```

## 🚀 Implementation Guide

### Step 1: Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Step 2: Configure Processing Parameters
```yaml
# config/settings.yaml
processing:
  batch_size: 1000
  checkpoint_interval: 100
  max_parallel_threads: 4
  
classification:
  api_provider: "anthropic"  # or "openai"
  model: "claude-3-opus"
  confidence_threshold: 0.7
  rate_limit: 10  # requests per minute
  
output:
  markdown_dir: "docs"
  organize_by: "taxonomy"  # or "chronological"
  generate_indexes: true
```

### Step 3: Run Processing Pipeline
```bash
# Validate archive format
python scripts/validate_archive.py path/to/twitter-archive.zip

# Preview classification on sample
python scripts/preview_classification.py --sample-size 100

# Run full pipeline
python scripts/run_pipeline.py \
  --archive path/to/twitter-archive.zip \
  --output docs/ \
  --config config/settings.yaml \
  --checkpoint-file processing.checkpoint
```

### Step 4: MkDocs Configuration
```yaml
# mkdocs.yml
site_name: "Philosophical Tweets Archive"
site_description: "A curated collection of theoretical threads"
site_url: "https://username.github.io/twitter-philosophy"

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - search.suggest
    - search.highlight
  palette:
    scheme: slate
    primary: indigo
    accent: amber

nav:
  - Home: index.md
  - Philosophy:
    - Overview: philosophy/index.md
    - Metaphysics: philosophy/metaphysics/
    - Ethics: philosophy/ethics/
    - Epistemology: philosophy/epistemology/
  - Politics:
    - Overview: politics/index.md
    - Theory: politics/theory/
    - Economy: politics/economy/
  - Archive: archive/

plugins:
  - search:
      lang: en
  - tags:
      tags_file: tags.md
  - minify:
      minify_html: true

markdown_extensions:
  - admonition
  - footnotes
  - meta
  - toc:
      permalink: true
```

### Step 5: Deploy to GitHub Pages
```yaml
# .github/workflows/deploy.yml
name: Deploy MkDocs to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material mkdocs-minify-plugin
          
      - name: Build site
        run: mkdocs build
        
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: ./site
          
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v3
```

## 📊 Performance Considerations

### Memory Management
```python
# Streaming JSON parser for large files
def stream_parse_tweets(filepath, chunk_size=1000):
    """
    Parse tweets in chunks to avoid loading entire file
    """
    with open(filepath, 'r') as f:
        # Skip JavaScript wrapper if present
        first_line = f.readline()
        if 'window.YTD' in first_line:
            # Read until we find the array start
            json_start = first_line.index('[')
            f.seek(json_start)
        else:
            f.seek(0)
            
        parser = ijson.items(f, 'item')
        chunk = []
        
        for tweet in parser:
            chunk.append(tweet)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
                
        if chunk:  # Yield remaining tweets
            yield chunk
```

### Rate Limiting for AI Classification
```python
class RateLimiter:
    def __init__(self, calls_per_minute=10):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0
        
    async def acquire(self):
        current = time.time()
        time_since_last = current - self.last_call
        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)
        self.last_call = time.time()
```

### Checkpoint System
```python
class ProcessingCheckpoint:
    """
    Save processing state for resume capability
    """
    def __init__(self, checkpoint_file='processing.checkpoint'):
        self.checkpoint_file = checkpoint_file
        self.state = self.load_checkpoint()
        
    def save_checkpoint(self, state):
        with open(self.checkpoint_file, 'w') as f:
            json.dump({
                'processed_tweets': state['processed_ids'],
                'completed_threads': state['thread_ids'],
                'timestamp': datetime.now().isoformat(),
                'statistics': state['stats']
            }, f, indent=2)
            
    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {'processed_tweets': [], 'completed_threads': []}
```

## 🎯 Quality Assurance

### Classification Validation
- Manual review sample (1% of classified content)
- Confidence score distribution analysis
- False positive/negative tracking
- A/B testing different classification prompts

### Output Validation
- Markdown syntax validation
- Frontmatter completeness check
- Thread continuity verification
- Broken link detection

### Metrics to Track
```yaml
processing_metrics:
  - total_tweets_processed
  - threads_identified
  - serious_content_ratio
  - average_thread_length
  - processing_time_per_tweet
  
classification_metrics:
  - confidence_score_distribution
  - tag_frequency_distribution
  - classification_agreement_rate
  - manual_override_rate
  
output_metrics:
  - total_essays_generated
  - average_essay_length
  - tags_per_essay
  - orphaned_tweets_count
```

## 🔍 Troubleshooting Guide

### Common Issues

#### Issue: Memory overflow with large archives
**Solution**: Use streaming JSON parser and reduce batch size
```python
# Adjust in config/settings.yaml
processing:
  batch_size: 100  # Reduce from 1000
  use_streaming: true
```

#### Issue: AI classification rate limits
**Solution**: Implement exponential backoff
```python
@retry(wait=wait_exponential(multiplier=1, min=4, max=60))
async def classify_with_ai(content):
    # Classification logic
    pass
```

#### Issue: Broken threads due to deleted tweets
**Solution**: Implement gap detection and marking
```python
def detect_thread_gaps(thread):
    """Mark potential gaps in thread continuity"""
    for i in range(len(thread) - 1):
        time_gap = thread[i+1].timestamp - thread[i].timestamp
        if time_gap > timedelta(hours=24):
            thread[i].add_note("Potential gap in thread")
```

## 📈 Future Enhancements

### Potential Features
- **Semantic Search**: Implement vector search for similar content
- **Citation Network**: Build graph of internal references
- **Reading Time Estimates**: Calculate and display per essay
- **Export Options**: PDF compilation, EPUB generation
- **Analytics Dashboard**: Processing statistics and content insights
- **Multi-language Support**: Detect and categorize non-English content

### Scalability Improvements
- Distributed processing with job queue
- Cloud storage integration for archives
- Containerized deployment with Docker
- Database backend for metadata
- CDN integration for static assets

## 📚 Resources

### Documentation
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Twitter Archive Format Guide](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive)

### Libraries Used
- `mkdocs`: Static site generator
- `mkdocs-material`: Modern theme
- `python-twitter`: Archive parsing utilities
- `anthropic`/`openai`: AI classification
- `ijson`: Streaming JSON parser
- `pyyaml`: Configuration management
- `jinja2`: Template rendering
- `click`: CLI interface

---

*This project preserves intellectual discourse from the ephemeral nature of social media, creating a permanent, searchable archive of philosophical and political thought.*