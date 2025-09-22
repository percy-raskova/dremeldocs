# Quick Start Guide

## Overview

This guide will help you quickly convert your Twitter archive into a searchable MkDocs website containing your philosophical and political threads.

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check pip is installed
pip --version

# Check git is installed
git --version
```

## Step 1: Download Your Twitter Archive

1. Go to Twitter/X Settings → "Your account" → "Download an archive of your data"
2. Request your archive (may take 24-48 hours)
3. Download the ZIP file when ready
4. Extract to a folder (e.g., `~/twitter-archive/`)

## Step 2: Quick Setup

```bash
# Clone or create project directory
mkdir twitter-to-mkdocs
cd twitter-to-mkdocs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create essential directories
mkdir -p data/processed docs config logs

# Install minimal requirements
pip install anthropic pyyaml tqdm python-dotenv
```

## Step 3: Create Minimal Extractor

Create `extract_tweets.py`:

```python
#!/usr/bin/env python3
import json
import re
from pathlib import Path
import sys

def extract_tweets(archive_path):
    """Quick extraction of tweets from archive"""
    tweets_file = Path(archive_path) / "data" / "tweets.js"
    
    if not tweets_file.exists():
        print(f"Error: {tweets_file} not found!")
        return None
    
    # Read file
    with open(tweets_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove JavaScript wrapper
    json_str = re.sub(r'^window\.YTD\.tweets\.part\d+\s*=\s*', '', content)
    
    # Parse JSON
    raw_data = json.loads(json_str)
    
    # Extract tweets
    tweets = []
    for item in raw_data:
        tweet = item.get('tweet', item)
        tweets.append(tweet)
    
    print(f"Extracted {len(tweets)} tweets")
    
    # Save to file
    output = Path("data/processed/tweets.json")
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(tweets, f, indent=2, ensure_ascii=False)
    
    return tweets

if __name__ == "__main__":
    archive_path = sys.argv[1] if len(sys.argv) > 1 else "twitter-archive"
    extract_tweets(archive_path)
```

Run it:
```bash
python extract_tweets.py /path/to/twitter-archive
```

## Step 4: Quick Thread Detection

Create `find_threads.py`:

```python
#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def find_threads(tweets):
    """Simple thread detection based on replies and time"""
    tweets_by_id = {t['id_str']: t for t in tweets}
    threads = []
    processed = set()
    
    # Method 1: Follow reply chains
    for tweet in tweets:
        if tweet['id_str'] in processed:
            continue
            
        if tweet.get('in_reply_to_status_id_str'):
            # This is a reply, try to build thread
            thread = []
            current_id = tweet['id_str']
            
            # Go backwards to find root
            while current_id and current_id in tweets_by_id:
                t = tweets_by_id[current_id]
                thread.insert(0, t)
                processed.add(current_id)
                current_id = t.get('in_reply_to_status_id_str')
            
            if len(thread) > 2:  # Only keep threads with 3+ tweets
                threads.append(thread)
    
    # Method 2: Find remaining orphan tweets for temporal clustering
    orphans = [t for t in tweets if t['id_str'] not in processed]
    
    print(f"Found {len(threads)} reply threads")
    print(f"Orphan tweets: {len(orphans)}")
    
    # Save threads
    output = Path("data/processed/threads.json")
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            'threads': threads,
            'orphans': orphans,
            'stats': {
                'total_threads': len(threads),
                'total_orphans': len(orphans)
            }
        }, f, indent=2, ensure_ascii=False)
    
    return threads

if __name__ == "__main__":
    with open("data/processed/tweets.json") as f:
        tweets = json.load(f)
    
    find_threads(tweets)
```

Run it:
```bash
python find_threads.py
```

## Step 5: Quick Classification (No AI)

Create `classify_threads.py` for rule-based classification:

```python
#!/usr/bin/env python3
import json
from pathlib import Path

# Keywords for classification
PHILOSOPHY_KEYWORDS = [
    'philosophy', 'epistemology', 'ontology', 'metaphysics',
    'consciousness', 'being', 'existence', 'phenomenology',
    'ethics', 'moral', 'categorical', 'dialectic'
]

POLITICS_KEYWORDS = [
    'capitalism', 'socialism', 'political', 'economy',
    'democracy', 'fascism', 'ideology', 'neoliberal',
    'imperialism', 'colonialism', 'class', 'labor'
]

def classify_thread(thread):
    """Simple keyword-based classification"""
    text = ' '.join([t.get('full_text', '') for t in thread]).lower()
    word_count = len(text.split())
    
    # Count keyword matches
    phil_score = sum(1 for kw in PHILOSOPHY_KEYWORDS if kw in text)
    pol_score = sum(1 for kw in POLITICS_KEYWORDS if kw in text)
    
    # Classification logic
    if word_count < 100:
        return 'casual', 0.9
    
    if phil_score > 0 or pol_score > 0:
        confidence = min(0.5 + (phil_score + pol_score) * 0.1, 0.95)
        return 'serious', confidence
    
    return 'casual', 0.7

def classify_all():
    with open("data/processed/threads.json") as f:
        data = json.load(f)
    
    serious = []
    casual = []
    
    for thread in data['threads']:
        classification, confidence = classify_thread(thread)
        
        result = {
            'thread': thread,
            'classification': classification,
            'confidence': confidence
        }
        
        if classification == 'serious':
            serious.append(result)
        else:
            casual.append(result)
    
    print(f"Classified: {len(serious)} serious, {len(casual)} casual")
    
    # Save results
    output = Path("data/processed/classified.json")
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            'serious': serious,
            'casual': casual
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    classify_all()
```

Run it:
```bash
python classify_threads.py
```

## Step 6: Generate Markdown

Create `generate_markdown.py`:

```python
#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime
import re

def create_markdown(thread_data):
    """Convert thread to markdown"""
    thread = thread_data['thread']
    
    # Get first tweet for metadata
    first = thread[0]
    date = datetime.strptime(first['created_at'], '%a %b %d %H:%M:%S %z %Y')
    
    # Create title from first tweet
    title = first.get('full_text', '')[:50]
    title = re.sub(r'https?://\S+', '', title).strip()
    
    # Create filename
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
    slug = '-'.join(slug.split()[:5])
    filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
    
    # Generate content
    content = f"""---
title: "{title}"
date: {date.strftime('%Y-%m-%d')}
tweet_count: {len(thread)}
---

# {title}

*Originally posted on {date.strftime('%B %d, %Y')}*

---

"""
    
    # Add tweets
    for tweet in thread:
        text = tweet.get('full_text', '')
        content += text + "\n\n"
    
    content += f"---\n\n*Thread: {len(thread)} tweets*\n"
    
    return filename, content

def generate_all():
    # Create docs directory
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Load classified threads
    with open("data/processed/classified.json") as f:
        data = json.load(f)
    
    # Generate markdown for serious threads
    for item in data['serious']:
        filename, content = create_markdown(item)
        
        # Write file
        output_path = docs_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"Generated {len(data['serious'])} markdown files in docs/")
    
    # Create index
    index_content = f"""# Twitter Philosophy Archive

This archive contains {len(data['serious'])} philosophical and political threads.

## Recent Threads

"""
    
    for item in data['serious'][:10]:
        first = item['thread'][0]
        title = first.get('full_text', '')[:100]
        date = datetime.strptime(first['created_at'], '%a %b %d %H:%M:%S %z %Y')
        index_content += f"- {date.strftime('%Y-%m-%d')}: {title}...\n"
    
    with open(docs_dir / "index.md", 'w') as f:
        f.write(index_content)

if __name__ == "__main__":
    generate_all()
```

Run it:
```bash
python generate_markdown.py
```

## Step 7: Setup MkDocs

```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Create mkdocs.yml
cat > mkdocs.yml << EOF
site_name: Twitter Philosophy Archive
theme:
  name: material
  features:
    - search.suggest
    - search.highlight
  palette:
    scheme: slate
    primary: indigo
nav:
  - Home: index.md
plugins:
  - search
EOF

# Build and serve
mkdocs serve
```

Visit http://127.0.0.1:8000 to see your site!

## Step 8: Deploy to GitHub Pages

```bash
# Initialize git repo
git init
git add .
git commit -m "Initial Twitter archive"

# Create GitHub repo and push
git remote add origin https://github.com/USERNAME/twitter-philosophy.git
git push -u origin main

# Deploy to GitHub Pages
mkdocs gh-deploy
```

Your site will be live at: `https://USERNAME.github.io/twitter-philosophy/`

## Complete Quick Pipeline

Create `run_all.sh`:

```bash
#!/bin/bash

# Check if archive path provided
if [ -z "$1" ]; then
    echo "Usage: ./run_all.sh /path/to/twitter-archive"
    exit 1
fi

echo "🐦 Twitter to MkDocs Pipeline"
echo "============================="

echo "Step 1: Extracting tweets..."
python extract_tweets.py "$1"

echo "Step 2: Finding threads..."
python find_threads.py

echo "Step 3: Classifying threads..."
python classify_threads.py

echo "Step 4: Generating markdown..."
python generate_markdown.py

echo "Step 5: Building site..."
mkdocs build

echo "✅ Complete! Run 'mkdocs serve' to preview"
```

Make it executable and run:
```bash
chmod +x run_all.sh
./run_all.sh /path/to/twitter-archive
```

## Troubleshooting

### Common Issues

**Issue**: "No module named 'anthropic'"
```bash
# Solution: Install the module
pip install anthropic
```

**Issue**: Large archive takes too long
```python
# Solution: Process in batches
# Modify extract_tweets.py to limit tweets:
tweets = tweets[:1000]  # Process first 1000 only for testing
```

**Issue**: No threads detected
```python
# Solution: Check if your tweets have reply chains
# Try lowering minimum thread length in find_threads.py:
if len(thread) > 1:  # Changed from > 2
```

**Issue**: All threads classified as casual
```python
# Solution: Add your specific keywords to classify_threads.py
# Or lower the word count threshold:
if word_count < 50:  # Changed from 100
```

## Next Steps

After getting the basic pipeline working:

1. **Add AI Classification**: Integrate Claude or GPT for better classification
2. **Improve Thread Detection**: Add temporal clustering
3. **Enhance Tagging**: Generate topic tags automatically
4. **Customize Theme**: Modify MkDocs theme for better aesthetics
5. **Add Analytics**: Track which essays get most views

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [GitHub Pages Guide](https://pages.github.com/)
- [Twitter Archive Format](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive)

---

*This quick start guide gets you running in under 30 minutes. For production use, see the complete implementation documentation.*
