# Implementation Plan

## Project Setup

### Prerequisites

```bash
# Required Python version
python >= 3.9

# Required system packages
git
python3-pip
python3-venv
```

### Step 1: Environment Setup

```bash
# Create project directory
mkdir -p ~/projects/twitter-to-mkdocs
cd ~/projects/twitter-to-mkdocs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create project structure
mkdir -p src/{parser,classifier,processor,utils}
mkdir -p data/{input,output,processed}
mkdir -p docs/{philosophy,politics,archive}
mkdir -p config
mkdir -p logs
```

### Step 2: Install Dependencies

```bash
# Create requirements.txt
cat > requirements.txt << EOF
# Core dependencies
python-dotenv==1.0.0
pyyaml==6.0.1
click==8.1.7

# Data processing
pandas==2.1.3
ijson==3.2.3  # For streaming large JSON

# AI/ML
anthropic==0.7.0  # For Claude API
openai==1.3.0  # Alternative
aiohttp==3.9.0  # For async API calls
tiktoken==0.5.1  # Token counting

# Text processing
nltk==3.8.1
textstat==0.7.3  # Readability metrics

# MkDocs
mkdocs==1.5.3
mkdocs-material==9.4.0
mkdocs-minify-plugin==0.7.1
pymdown-extensions==10.4

# Utilities
tqdm==4.66.1  # Progress bars
loguru==0.7.2  # Better logging
python-dateutil==2.8.2
EOF

pip install -r requirements.txt
```

## Phase 1: Data Extraction (Week 1)

### Day 1-2: Archive Analysis

```python
# src/analyze_archive.py
"""
First script to run - analyzes the Twitter archive structure
"""
import json
from pathlib import Path
import sys

def analyze_archive(archive_path: Path):
    """Analyze Twitter archive structure and content"""
    
    data_dir = archive_path / "data"
    
    # Check for required files
    required_files = ['tweets.js', 'profile.js', 'account.js']
    found_files = []
    missing_files = []
    
    for file in required_files:
        if (data_dir / file).exists():
            found_files.append(file)
        else:
            missing_files.append(file)
    
    print(f"Found files: {found_files}")
    print(f"Missing files: {missing_files}")
    
    # Analyze tweets.js structure
    tweets_file = data_dir / "tweets.js"
    if tweets_file.exists():
        # Read first few tweets to understand structure
        with open(tweets_file, 'r', encoding='utf-8') as f:
            content = f.read(10000)  # First 10KB
            
        print("\nSample of tweets.js:")
        print(content[:500])
        
        # Detect format
        if 'window.YTD' in content:
            print("\n✓ Detected GDPR export format")
        else:
            print("\n✓ Detected legacy export format")
    
    return found_files, missing_files

if __name__ == "__main__":
    archive_path = Path(sys.argv[1] if len(sys.argv) > 1 else "twitter-archives")
    analyze_archive(archive_path)
```

### Day 3-4: Build Extraction Pipeline

```python
# src/parser/extract.py
"""
Main extraction script
"""
from pathlib import Path
import json
import re
from typing import List, Dict
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TweetExtractor:
    def __init__(self, archive_path: Path):
        self.archive_path = archive_path
        self.data_dir = archive_path / "data"
        
    def extract_all(self) -> Dict[str, List]:
        """Extract all tweets and metadata"""
        
        results = {
            'tweets': self.extract_tweets(),
            'profile': self.extract_profile(),
            'stats': {}
        }
        
        # Calculate statistics
        results['stats'] = {
            'total_tweets': len(results['tweets']),
            'date_range': self.get_date_range(results['tweets']),
            'languages': self.get_language_distribution(results['tweets'])
        }
        
        return results
    
    def extract_tweets(self) -> List[Dict]:
        """Extract and clean tweets"""
        tweets_file = self.data_dir / "tweets.js"
        
        logger.info(f"Reading {tweets_file}")
        with open(tweets_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Strip JavaScript wrapper
        json_str = re.sub(r'^window\.YTD\.tweets\.part\d+\s*=\s*', '', content)
        
        # Parse JSON
        raw_data = json.loads(json_str)
        
        # Extract tweets from nested structure
        tweets = []
        for item in tqdm(raw_data, desc="Extracting tweets"):
            tweet = item.get('tweet', item)
            tweets.append(tweet)
        
        logger.info(f"Extracted {len(tweets)} tweets")
        return tweets
    
    def extract_profile(self) -> Dict:
        """Extract profile information"""
        profile_file = self.data_dir / "profile.js"
        
        if not profile_file.exists():
            return {}
        
        with open(profile_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Strip wrapper and parse
        json_str = re.sub(r'^window\.YTD\.\w+\.part\d+\s*=\s*', '', content)
        profile_data = json.loads(json_str)
        
        return profile_data[0] if profile_data else {}
    
    def get_date_range(self, tweets: List[Dict]) -> Dict:
        """Get earliest and latest tweet dates"""
        if not tweets:
            return {}
        
        dates = [t.get('created_at', '') for t in tweets]
        dates = [d for d in dates if d]  # Filter empty
        
        if dates:
            return {
                'earliest': min(dates),
                'latest': max(dates)
            }
        return {}
    
    def get_language_distribution(self, tweets: List[Dict]) -> Dict:
        """Count tweets by language"""
        from collections import Counter
        
        languages = [t.get('lang', 'unknown') for t in tweets]
        return dict(Counter(languages))

# Run extraction
if __name__ == "__main__":
    extractor = TweetExtractor(Path("twitter-archives"))
    data = extractor.extract_all()
    
    # Save extracted data
    output_file = Path("data/processed/extracted_tweets.json")
    output_file.parent.mkdir(exist_ok=True, parents=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {data['stats']['total_tweets']} tweets to {output_file}")
```

### Day 5: Test and Validate Extraction

```bash
# Create test script
python src/analyze_archive.py /path/to/twitter-archive
python src/parser/extract.py

# Validate output
python -c "
import json
with open('data/processed/extracted_tweets.json') as f:
    data = json.load(f)
    print(f'Tweets: {len(data[\"tweets\"])}')
    print(f'Date range: {data[\"stats\"][\"date_range\"]}')
    print(f'Languages: {data[\"stats\"][\"languages\"]}')
"
```

## Phase 2: Thread Detection (Week 2)

### Day 6-8: Implement Thread Detection

```python
# src/parser/thread_detector.py
"""
Thread detection implementation
"""
from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path

class ThreadDetector:
    def __init__(self, tweets: List[Dict]):
        self.tweets = tweets
        self.tweets_by_id = {t['id_str']: t for t in tweets}
        
    def detect_threads(self, save_path: Path = None) -> Dict:
        """Run all thread detection methods"""
        
        print("Detecting threads...")
        
        # Method 1: Reply chains
        reply_threads = self.find_reply_chains()
        print(f"Found {len(reply_threads)} reply chains")
        
        # Method 2: Temporal clusters
        temporal_threads = self.find_temporal_threads()
        print(f"Found {len(temporal_threads)} temporal threads")
        
        # Merge and deduplicate
        all_threads = self.merge_threads(reply_threads + temporal_threads)
        print(f"Total unique threads: {len(all_threads)}")
        
        # Find orphan tweets
        threaded_ids = set()
        for thread in all_threads:
            threaded_ids.update([t['id_str'] for t in thread])
        
        orphans = [t for t in self.tweets if t['id_str'] not in threaded_ids]
        print(f"Orphan tweets: {len(orphans)}")
        
        results = {
            'threads': all_threads,
            'orphan_tweets': orphans,
            'statistics': {
                'total_threads': len(all_threads),
                'total_tweets': len(self.tweets),
                'threaded_tweets': len(threaded_ids),
                'orphan_tweets': len(orphans),
                'average_thread_length': sum(len(t) for t in all_threads) / len(all_threads) if all_threads else 0
            }
        }
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Saved threads to {save_path}")
        
        return results
    
    # [Include methods from 03-thread-detection-strategy.md]

# Run thread detection
if __name__ == "__main__":
    # Load extracted tweets
    with open('data/processed/extracted_tweets.json', 'r') as f:
        data = json.load(f)
    
    detector = ThreadDetector(data['tweets'])
    threads = detector.detect_threads(Path('data/processed/detected_threads.json'))
```

## Phase 3: Classification (Week 3)

### Day 9-11: Setup AI Classification

```python
# config/classification_config.yaml
classification:
  api: "anthropic"  # or "openai"
  model: "claude-3-opus-20240229"
  api_key_env: "ANTHROPIC_API_KEY"
  
  thresholds:
    min_thread_length: 3
    min_word_count: 100
    confidence_threshold: 0.6
  
  rate_limiting:
    requests_per_minute: 10
    retry_attempts: 3
    retry_delay: 5
```

```python
# src/classifier/ai_classifier.py
"""
AI-powered thread classification
"""
import os
import asyncio
import json
from typing import List, Dict
from pathlib import Path
import anthropic
from dotenv import load_dotenv
import yaml
from tqdm import tqdm

load_dotenv()

class ThreadClassifier:
    def __init__(self, config_path: Path = Path("config/classification_config.yaml")):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)['classification']
        
        # Initialize AI client
        api_key = os.getenv(self.config['api_key_env'])
        if not api_key:
            raise ValueError(f"API key not found in {self.config['api_key_env']}")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        
    async def classify_threads(self, threads_file: Path) -> Dict:
        """Classify all threads"""
        
        # Load threads
        with open(threads_file) as f:
            data = json.load(f)
        
        threads = data['threads']
        print(f"Classifying {len(threads)} threads...")
        
        classified = []
        for thread in tqdm(threads):
            # Pre-filter
            if self.pre_filter(thread):
                result = await self.classify_single_thread(thread)
                classified.append(result)
            else:
                classified.append({
                    'thread': thread,
                    'classification': 'casual',
                    'confidence': 1.0,
                    'reason': 'Failed pre-filter'
                })
            
            # Rate limiting
            await asyncio.sleep(60 / self.config['rate_limiting']['requests_per_minute'])
        
        # Separate serious and casual
        serious = [c for c in classified if c['classification'] == 'serious']
        casual = [c for c in classified if c['classification'] == 'casual']
        
        results = {
            'serious_threads': serious,
            'casual_threads': casual,
            'statistics': {
                'total_threads': len(threads),
                'serious_count': len(serious),
                'casual_count': len(casual),
                'serious_percentage': len(serious) / len(threads) * 100
            }
        }
        
        # Save results
        output_file = Path('data/processed/classified_threads.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Classification complete: {len(serious)} serious, {len(casual)} casual")
        return results
    
    def pre_filter(self, thread: List[Dict]) -> bool:
        """Quick pre-filter check"""
        if len(thread) < self.config['thresholds']['min_thread_length']:
            return False
        
        total_words = sum(len(t.get('full_text', '').split()) for t in thread)
        if total_words < self.config['thresholds']['min_word_count']:
            return False
        
        return True
    
    async def classify_single_thread(self, thread: List[Dict]) -> Dict:
        """Classify a single thread using AI"""
        
        # Prepare thread text
        thread_text = '\n---\n'.join([
            f"Tweet {i+1}: {t.get('full_text', '')}"
            for i, t in enumerate(thread)
        ])
        
        prompt = self.create_classification_prompt(thread_text)
        
        try:
            message = self.client.messages.create(
                model=self.config['model'],
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = message.content[0].text
            classification = json.loads(response_text)
            
            return {
                'thread': thread,
                'classification': classification['classification'],
                'confidence': classification['confidence'],
                'tags': classification.get('key_concepts', []),
                'reason': classification.get('reasoning', '')
            }
        except Exception as e:
            print(f"Classification error: {e}")
            return {
                'thread': thread,
                'classification': 'serious',  # Default to inclusion
                'confidence': 0.5,
                'reason': f'Error: {str(e)}'
            }
    
    def create_classification_prompt(self, thread_text: str) -> str:
        """Create classification prompt"""
        return f"""Analyze this Twitter thread for philosophical/political content.

Thread:
{thread_text}

Classify as "serious" if it contains:
- Philosophical arguments or theory
- Political analysis or criticism
- Academic discourse
- Substantive social commentary

Classify as "casual" if it's:
- Jokes, memes, shitposting
- Personal anecdotes without analysis
- Simple observations
- Social interactions

Respond with JSON:
{{
    "classification": "serious" or "casual",
    "confidence": 0.0 to 1.0,
    "key_concepts": ["concept1", "concept2"],
    "reasoning": "brief explanation"
}}"""

# Run classification
if __name__ == "__main__":
    classifier = ThreadClassifier()
    asyncio.run(classifier.classify_threads(Path('data/processed/detected_threads.json')))
```

### Day 12: Test Classification

```python
# src/test_classification.py
"""
Test classification on sample threads
"""
import json
from pathlib import Path
import random

def test_classification_sample():
    # Load classified threads
    with open('data/processed/classified_threads.json') as f:
        data = json.load(f)
    
    # Sample for review
    serious = data['serious_threads']
    casual = data['casual_threads']
    
    print("=== SERIOUS THREADS SAMPLE ===")
    for item in random.sample(serious, min(3, len(serious))):
        thread = item['thread']
        print(f"\nConfidence: {item['confidence']}")
        print(f"Reason: {item['reason']}")
        print(f"First tweet: {thread[0].get('full_text', '')[:200]}...")
        print("-" * 50)
    
    print("\n=== CASUAL THREADS SAMPLE ===")
    for item in random.sample(casual, min(3, len(casual))):
        thread = item['thread']
        print(f"\nReason: {item['reason']}")
        print(f"First tweet: {thread[0].get('full_text', '')[:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_classification_sample()
```

## Phase 4: Content Processing (Week 4)

### Day 13-15: Generate Markdown Files

```python
# src/processor/markdown_generator.py
"""
Convert classified threads to Markdown essays
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import re

class MarkdownGenerator:
    def __init__(self, output_dir: Path = Path("docs")):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        
    def process_all_threads(self, classified_file: Path):
        """Convert all serious threads to Markdown"""
        
        with open(classified_file) as f:
            data = json.load(f)
        
        serious_threads = data['serious_threads']
        print(f"Processing {len(serious_threads)} serious threads...")
        
        for item in serious_threads:
            self.thread_to_markdown(item)
        
        # Generate index files
        self.generate_index_files(serious_threads)
        
        print(f"Generated {len(serious_threads)} Markdown files")
    
    def thread_to_markdown(self, thread_data: Dict) -> Path:
        """Convert single thread to Markdown file"""
        
        thread = thread_data['thread']
        
        # Generate filename
        first_tweet = thread[0]
        date = datetime.strptime(first_tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
        
        # Create slug from first few words
        text = first_tweet.get('full_text', '')
        slug = self.create_slug(text)
        filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
        
        # Determine category
        tags = thread_data.get('tags', [])
        if any('philosoph' in tag.lower() for tag in tags):
            category = 'philosophy'
        elif any('politic' in tag.lower() for tag in tags):
            category = 'politics'
        else:
            category = 'archive'
        
        # Create output path
        category_dir = self.output_dir / category
        category_dir.mkdir(exist_ok=True)
        output_path = category_dir / filename
        
        # Generate content
        content = self.generate_markdown_content(thread_data, date)
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def generate_markdown_content(self, thread_data: Dict, date: datetime) -> str:
        """Generate Markdown content with frontmatter"""
        
        thread = thread_data['thread']
        
        # Generate title (first 50 chars of first tweet)
        first_text = thread[0].get('full_text', 'Untitled Thread')
        title = first_text[:50] + ('...' if len(first_text) > 50 else '')
        title = title.replace('\n', ' ').strip()
        
        # Frontmatter
        frontmatter = f"""---
title: "{title}"
date: {date.strftime('%Y-%m-%d')}
time: {date.strftime('%H:%M:%S')}
tags: {thread_data.get('tags', [])}
confidence: {thread_data.get('confidence', 0)}
tweet_count: {len(thread)}
thread_id: {thread[0].get('id_str', '')}
---

"""
        
        # Content header
        content = frontmatter
        content += f"# {title}\n\n"
        content += f"*Originally posted as a Twitter thread on {date.strftime('%B %d, %Y')}*\n\n"
        content += "---\n\n"
        
        # Thread content (no modifications!)
        for i, tweet in enumerate(thread, 1):
            text = tweet.get('full_text', '')
            
            # Preserve exact text
            content += text
            
            # Add separator between tweets
            if i < len(thread):
                content += "\n\n"
        
        # Footer
        content += f"\n\n---\n\n"
        content += f"*Thread: {len(thread)} tweets, "
        content += f"{sum(len(t.get('full_text', '').split()) for t in thread)} words*\n"
        
        return content
    
    def create_slug(self, text: str, max_length: int = 30) -> str:
        """Create URL-safe slug from text"""
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Convert to lowercase and replace spaces
        slug = text.lower().strip().replace(' ', '-')
        # Limit length
        words = slug.split('-')[:5]
        slug = '-'.join(words)[:max_length]
        return slug or 'untitled'
    
    def generate_index_files(self, threads: List[Dict]):
        """Generate index pages for each category"""
        
        categories = {
            'philosophy': [],
            'politics': [],
            'archive': []
        }
        
        # Categorize threads
        for item in threads:
            tags = item.get('tags', [])
            if any('philosoph' in tag.lower() for tag in tags):
                categories['philosophy'].append(item)
            elif any('politic' in tag.lower() for tag in tags):
                categories['politics'].append(item)
            else:
                categories['archive'].append(item)
        
        # Generate index for each category
        for category, items in categories.items():
            self.generate_category_index(category, items)
    
    def generate_category_index(self, category: str, threads: List[Dict]):
        """Generate index page for category"""
        
        content = f"# {category.capitalize()}\n\n"
        content += f"*{len(threads)} threads*\n\n"
        
        # Sort by date
        threads.sort(key=lambda x: x['thread'][0]['created_at'], reverse=True)
        
        for item in threads:
            thread = item['thread']
            first_tweet = thread[0]
            
            # Generate link
            date = datetime.strptime(first_tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
            slug = self.create_slug(first_tweet.get('full_text', ''))
            filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
            
            # Add to index
            title = first_tweet.get('full_text', '')[:100] + '...'
            content += f"- [{title}](./{filename}) - {date.strftime('%B %d, %Y')}\n"
        
        # Write index file
        index_path = self.output_dir / category / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

# Run generation
if __name__ == "__main__":
    generator = MarkdownGenerator()
    generator.process_all_threads(Path('data/processed/classified_threads.json'))
```

## Phase 5: MkDocs Site Generation (Week 5)

### Day 16-17: Configure MkDocs

```yaml
# mkdocs.yml
site_name: "Twitter Philosophy Archive"
site_description: "A curated collection of philosophical and political threads"
site_url: "https://username.github.io/twitter-philosophy"
site_author: "Your Name"

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight
    - content.code.copy
  palette:
    - scheme: slate
      primary: indigo
      accent: amber
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
    - scheme: default
      primary: indigo
      accent: amber
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode

nav:
  - Home: index.md
  - Philosophy:
    - Overview: philosophy/index.md
  - Politics:
    - Overview: politics/index.md
  - Archive:
    - All Threads: archive/index.md

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
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - pymdownx.tasklist:
      custom_checkbox: true

extra:
  social:
    - icon: fontawesome/brands/twitter
      link: https://twitter.com/username
    - icon: fontawesome/brands/github
      link: https://github.com/username
```

### Day 18: Create Main Pipeline Script

```python
# run_pipeline.py
"""
Main pipeline orchestrator
"""
import click
from pathlib import Path
import subprocess
import sys
import asyncio

@click.command()
@click.option('--archive', type=click.Path(exists=True), required=True, help='Path to Twitter archive')
@click.option('--output', type=click.Path(), default='docs', help='Output directory for Markdown files')
@click.option('--skip-extraction', is_flag=True, help='Skip extraction phase')
@click.option('--skip-detection', is_flag=True, help='Skip thread detection phase')
@click.option('--skip-classification', is_flag=True, help='Skip classification phase')
@click.option('--build-site', is_flag=True, help='Build MkDocs site after processing')
def run_pipeline(archive, output, skip_extraction, skip_detection, skip_classification, build_site):
    """Run the complete Twitter to MkDocs pipeline"""
    
    archive_path = Path(archive)
    output_path = Path(output)
    
    print("🐦 Twitter to MkDocs Pipeline")
    print("=" * 50)
    
    # Phase 1: Extraction
    if not skip_extraction:
        print("\n📊 Phase 1: Extracting tweets...")
        from src.parser.extract import TweetExtractor
        
        extractor = TweetExtractor(archive_path)
        data = extractor.extract_all()
        
        output_file = Path("data/processed/extracted_tweets.json")
        output_file.parent.mkdir(exist_ok=True, parents=True)
        
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Extracted {data['stats']['total_tweets']} tweets")
    
    # Phase 2: Thread Detection
    if not skip_detection:
        print("\n🔗 Phase 2: Detecting threads...")
        from src.parser.thread_detector import ThreadDetector
        
        import json
        with open('data/processed/extracted_tweets.json') as f:
            data = json.load(f)
        
        detector = ThreadDetector(data['tweets'])
        threads = detector.detect_threads(Path('data/processed/detected_threads.json'))
        
        print(f"✅ Found {threads['statistics']['total_threads']} threads")
    
    # Phase 3: Classification
    if not skip_classification:
        print("\n🤖 Phase 3: Classifying threads...")
        from src.classifier.ai_classifier import ThreadClassifier
        
        classifier = ThreadClassifier()
        results = asyncio.run(classifier.classify_threads(Path('data/processed/detected_threads.json')))
        
        print(f"✅ Classified: {results['statistics']['serious_count']} serious, {results['statistics']['casual_count']} casual")
    
    # Phase 4: Markdown Generation
    print("\n📝 Phase 4: Generating Markdown files...")
    from src.processor.markdown_generator import MarkdownGenerator
    
    generator = MarkdownGenerator(output_path)
    generator.process_all_threads(Path('data/processed/classified_threads.json'))
    
    print(f"✅ Generated Markdown files in {output_path}")
    
    # Phase 5: Build MkDocs site
    if build_site:
        print("\n🌐 Phase 5: Building MkDocs site...")
        subprocess.run(['mkdocs', 'build'], check=True)
        print("✅ Site built in ./site directory")
        
        # Optionally serve locally
        if click.confirm("Would you like to preview the site locally?"):
            subprocess.run(['mkdocs', 'serve'])
    
    print("\n🎉 Pipeline complete!")

if __name__ == '__main__':
    run_pipeline()
```

## Deployment

### GitHub Pages Deployment

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material mkdocs-minify-plugin pymdown-extensions
      
      - name: Build site
        run: mkdocs build
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: ./site
      
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v3
```

## Final Checklist

### Pre-Launch

- [ ] Test with sample data (10-20 tweets)
- [ ] Verify thread detection accuracy
- [ ] Review classification results manually
- [ ] Check Markdown formatting
- [ ] Test MkDocs build locally
- [ ] Review generated site navigation

### Launch

```bash
# Final run
python run_pipeline.py --archive /path/to/twitter-archive --output docs --build-site

# Deploy
git add -A
git commit -m "Add processed Twitter archive"
git push origin main

# GitHub Actions will automatically deploy to GitHub Pages
```

### Post-Launch

- [ ] Verify GitHub Pages deployment
- [ ] Test search functionality
- [ ] Check mobile responsiveness
- [ ] Review analytics after 1 week
- [ ] Consider feedback and improvements

## Monitoring and Maintenance

```python
# src/utils/stats.py
"""Generate statistics about the processed archive"""

def generate_stats():
    import json
    from pathlib import Path
    from collections import Counter
    
    # Load processed data
    with open('data/processed/classified_threads.json') as f:
        data = json.load(f)
    
    # Calculate statistics
    stats = {
        'total_serious_threads': len(data['serious_threads']),
        'total_words': sum(
            sum(len(t.get('full_text', '').split()) for t in item['thread'])
            for item in data['serious_threads']
        ),
        'tag_frequency': Counter(
            tag for item in data['serious_threads']
            for tag in item.get('tags', [])
        ),
        'average_confidence': sum(
            item['confidence'] for item in data['serious_threads']
        ) / len(data['serious_threads'])
    }
    
    print("Archive Statistics")
    print("=" * 50)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    return stats

if __name__ == "__main__":
    generate_stats()
```

This completes the implementation plan with concrete, runnable code for each phase of the project.
