# Tweet Extraction Pipeline

## Overview

Extract and parse tweets from Twitter/X archive format, handling JavaScript wrappers and nested structures.

## Step 1: File Reading and Wrapper Removal

### Basic Extraction Script

```python
import json
import re
from pathlib import Path
from typing import List, Dict, Any

class TwitterArchiveExtractor:
    def __init__(self, archive_path: Path):
        self.archive_path = archive_path
        self.data_dir = archive_path / "data"
        
    def extract_tweets(self) -> List[Dict[str, Any]]:
        """Extract tweets from tweets.js file"""
        tweets_file = self.data_dir / "tweets.js"
        
        if not tweets_file.exists():
            raise FileNotFoundError(f"tweets.js not found at {tweets_file}")
            
        with open(tweets_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remove JavaScript wrapper
        # Pattern: window.YTD.tweets.part0 = 
        json_content = re.sub(r'^window\.YTD\.\w+\.part\d+\s*=\s*', '', content)
        
        # Parse JSON array
        raw_tweets = json.loads(json_content)
        
        # Extract nested tweet objects
        tweets = []
        for item in raw_tweets:
            if 'tweet' in item:
                tweet = item['tweet']
                tweets.append(tweet)
            else:
                # Handle potential format variations
                tweets.append(item)
                
        return tweets
```

## Step 2: Data Validation and Cleaning

```python
def validate_tweet(tweet: Dict[str, Any]) -> bool:
    """Validate that tweet has required fields"""
    required_fields = ['id_str', 'full_text', 'created_at']
    return all(field in tweet for field in required_fields)

def clean_tweet_data(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and normalize tweet data"""
    cleaned = {
        'id': tweet.get('id_str'),
        'text': tweet.get('full_text', ''),
        'created_at': tweet.get('created_at'),
        'lang': tweet.get('lang', 'unknown'),
        'reply_to_id': tweet.get('in_reply_to_status_id_str'),
        'reply_to_user': tweet.get('in_reply_to_user_id_str'),
        'conversation_id': tweet.get('conversation_id'),
        'retweet_count': int(tweet.get('retweet_count', 0)),
        'favorite_count': int(tweet.get('favorite_count', 0)),
        'is_retweet': tweet.get('retweeted', False),
        'entities': tweet.get('entities', {}),
        'possibly_sensitive': tweet.get('possibly_sensitive', False)
    }
    
    # Handle edit info if present
    if 'edit_info' in tweet and 'initial' in tweet['edit_info']:
        cleaned['edit_history'] = tweet['edit_info']['initial'].get('editTweetIds', [])
        cleaned['is_edited'] = len(cleaned['edit_history']) > 1
    
    return cleaned
```

## Step 3: Filtering and Preprocessing

```python
class TweetFilter:
    def __init__(self):
        self.excluded_count = {
            'retweets': 0,
            'non_english': 0,
            'deleted': 0
        }
    
    def should_include(self, tweet: Dict[str, Any]) -> bool:
        """Determine if tweet should be included in corpus"""
        
        # Exclude pure retweets (keep quote tweets)
        if tweet['text'].startswith('RT @'):
            self.excluded_count['retweets'] += 1
            return False
            
        # Optional: filter by language
        # if tweet['lang'] != 'en':
        #     self.excluded_count['non_english'] += 1
        #     return False
            
        # Exclude deleted placeholder tweets
        if tweet['text'] == '' or tweet['text'] is None:
            self.excluded_count['deleted'] += 1
            return False
            
        return True
    
    def get_stats(self) -> Dict[str, int]:
        """Return filtering statistics"""
        return self.excluded_count
```

## Step 4: Batch Processing for Large Files

```python
import ijson
from typing import Generator

class StreamingExtractor:
    """Memory-efficient streaming parser for very large archives"""
    
    def __init__(self, tweets_file: Path, batch_size: int = 1000):
        self.tweets_file = tweets_file
        self.batch_size = batch_size
        
    def stream_tweets(self) -> Generator[List[Dict], None, None]:
        """Stream tweets in batches"""
        with open(self.tweets_file, 'r', encoding='utf-8') as f:
            # Skip JavaScript wrapper
            first_line = f.readline()
            if 'window.YTD' in first_line:
                # Find where JSON array starts
                json_start = first_line.index('[')
                f.seek(json_start)
            else:
                f.seek(0)
            
            # Use streaming JSON parser
            parser = ijson.items(f, 'item')
            batch = []
            
            for item in parser:
                # Extract tweet from nested structure
                tweet = item.get('tweet', item)
                batch.append(tweet)
                
                if len(batch) >= self.batch_size:
                    yield batch
                    batch = []
            
            # Yield remaining tweets
            if batch:
                yield batch
```

## Step 5: Complete Extraction Pipeline

```python
from datetime import datetime
import logging

class ExtractionPipeline:
    def __init__(self, archive_path: Path, output_dir: Path):
        self.archive_path = archive_path
        self.output_dir = output_dir
        self.extractor = TwitterArchiveExtractor(archive_path)
        self.filter = TweetFilter()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def run(self) -> Dict[str, Any]:
        """Run complete extraction pipeline"""
        start_time = datetime.now()
        
        self.logger.info("Starting tweet extraction...")
        
        # Extract all tweets
        raw_tweets = self.extractor.extract_tweets()
        self.logger.info(f"Extracted {len(raw_tweets)} raw tweets")
        
        # Clean and filter
        processed_tweets = []
        for tweet in raw_tweets:
            if validate_tweet(tweet):
                cleaned = clean_tweet_data(tweet)
                if self.filter.should_include(cleaned):
                    processed_tweets.append(cleaned)
        
        # Sort by date
        processed_tweets.sort(key=lambda t: t['created_at'])
        
        # Save processed tweets
        output_file = self.output_dir / 'processed_tweets.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_tweets, f, indent=2, ensure_ascii=False)
        
        # Generate statistics
        stats = {
            'total_raw_tweets': len(raw_tweets),
            'processed_tweets': len(processed_tweets),
            'excluded': self.filter.get_stats(),
            'processing_time': (datetime.now() - start_time).total_seconds(),
            'output_file': str(output_file)
        }
        
        self.logger.info(f"Pipeline complete: {stats}")
        return stats
```

## Usage Example

```python
from pathlib import Path

# Setup paths
archive_path = Path('/home/percy/projects/astradocs/twitter-archives')
output_dir = Path('/home/percy/projects/astradocs/processed_data')
output_dir.mkdir(exist_ok=True)

# Run extraction
pipeline = ExtractionPipeline(archive_path, output_dir)
results = pipeline.run()

print(f"Processed {results['processed_tweets']} tweets")
print(f"Excluded: {results['excluded']}")
```

## Error Handling Considerations

1. **Malformed JSON**: Use try-except blocks around JSON parsing
2. **Character Encoding**: Ensure UTF-8 encoding throughout
3. **Missing Fields**: Use `.get()` method with defaults
4. **Large Files**: Implement streaming for files > 100MB
5. **Corrupted Archives**: Validate file structure before processing

## Output Format

The processed tweets will be saved as clean JSON with normalized structure:

```json
[
  {
    "id": "1234567890",
    "text": "Tweet content here",
    "created_at": "Sat Sep 20 19:20:51 +0000 2025",
    "lang": "en",
    "reply_to_id": null,
    "conversation_id": null,
    "retweet_count": 5,
    "favorite_count": 10,
    "entities": {...}
  }
]
```

This normalized format makes subsequent thread detection and classification easier.
