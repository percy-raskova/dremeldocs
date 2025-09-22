# Thread Detection Strategy

## Challenge: Missing Thread Markers

Based on the data structure analysis, Twitter/X exports may not always include explicit thread markers like `conversation_id`. We need multiple strategies to reconstruct threads.

## Detection Strategies (Priority Order)

### Strategy 1: Reply Chain Following

```python
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime, timedelta

class ThreadDetector:
    def __init__(self, tweets: List[Dict]):
        self.tweets = tweets
        self.tweets_by_id = {t['id']: t for t in tweets}
        self.threads = []
        
    def find_reply_chains(self) -> List[List[Dict]]:
        """Follow in_reply_to chains to reconstruct threads"""
        
        # Build reply mapping
        reply_map = defaultdict(list)
        thread_roots = set()
        all_replies = set()
        
        for tweet in self.tweets:
            if tweet.get('reply_to_id'):
                reply_map[tweet['reply_to_id']].append(tweet['id'])
                all_replies.add(tweet['id'])
            else:
                # Potential thread root
                thread_roots.add(tweet['id'])
        
        # Build threads from roots
        threads = []
        for root_id in thread_roots:
            thread = self._build_thread_from_root(root_id, reply_map)
            if len(thread) > 1:  # Only keep multi-tweet threads
                threads.append(thread)
        
        return threads
    
    def _build_thread_from_root(self, root_id: str, reply_map: Dict) -> List[Dict]:
        """Recursively build thread from root tweet"""
        thread = []
        to_process = [root_id]
        processed = set()
        
        while to_process:
            tweet_id = to_process.pop(0)
            if tweet_id in processed or tweet_id not in self.tweets_by_id:
                continue
                
            tweet = self.tweets_by_id[tweet_id]
            thread.append(tweet)
            processed.add(tweet_id)
            
            # Add replies to this tweet
            if tweet_id in reply_map:
                to_process.extend(reply_map[tweet_id])
        
        # Sort thread by timestamp
        thread.sort(key=lambda t: datetime.strptime(t['created_at'], '%a %b %d %H:%M:%S %z %Y'))
        return thread
```

### Strategy 2: Self-Reply Detection

```python
def find_self_reply_threads(self) -> List[List[Dict]]:
    """Find threads where user replies to themselves"""
    
    # Group tweets by user (assuming we have user_id)
    # For personal archive, all tweets are from same user
    
    self_threads = []
    processed_ids = set()
    
    for tweet in self.tweets:
        if tweet['id'] in processed_ids:
            continue
            
        # Check if this tweet is a self-reply
        if tweet.get('reply_to_user') == 'self' or self._is_self_reply(tweet):
            thread = self._follow_self_reply_chain(tweet)
            if len(thread) > 1:
                self_threads.append(thread)
                processed_ids.update([t['id'] for t in thread])
    
    return self_threads

def _is_self_reply(self, tweet: Dict) -> bool:
    """Check if tweet is replying to user's own tweet"""
    if not tweet.get('reply_to_id'):
        return False
    
    replied_to = self.tweets_by_id.get(tweet['reply_to_id'])
    if replied_to:
        # In personal archive, all tweets are from same user
        return True
    return False
```

### Strategy 3: Temporal Clustering

```python
def find_temporal_threads(self, time_window_minutes: int = 30) -> List[List[Dict]]:
    """Find potential threads based on temporal proximity"""
    
    # Sort tweets by timestamp
    sorted_tweets = sorted(
        self.tweets, 
        key=lambda t: datetime.strptime(t['created_at'], '%a %b %d %H:%M:%S %z %Y')
    )
    
    temporal_threads = []
    current_thread = []
    last_timestamp = None
    
    for tweet in sorted_tweets:
        timestamp = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
        
        if last_timestamp and (timestamp - last_timestamp) <= timedelta(minutes=time_window_minutes):
            # Part of current temporal cluster
            current_thread.append(tweet)
        else:
            # Start new cluster
            if len(current_thread) > 1:
                # Validate this is actually a thread (not just temporal coincidence)
                if self._validate_thread_coherence(current_thread):
                    temporal_threads.append(current_thread)
            current_thread = [tweet]
        
        last_timestamp = timestamp
    
    # Don't forget last thread
    if len(current_thread) > 1 and self._validate_thread_coherence(current_thread):
        temporal_threads.append(current_thread)
    
    return temporal_threads

def _validate_thread_coherence(self, tweets: List[Dict]) -> bool:
    """Check if temporally clustered tweets form a coherent thread"""
    
    # Heuristics for thread coherence:
    # 1. Similar length (continuing a thought)
    # 2. No @ mentions to others (not a conversation)
    # 3. Sequential numbering (1/, 2/, etc.)
    
    # Check for thread numbering
    has_numbering = any(
        self._has_thread_numbering(t['text']) for t in tweets
    )
    if has_numbering:
        return True
    
    # Check for @ mentions to others
    has_external_mentions = any(
        '@' in t['text'] and not t['text'].startswith('@') 
        for t in tweets
    )
    if has_external_mentions:
        return False
    
    # Check text similarity/continuation
    # (This is a simple heuristic - could use more sophisticated NLP)
    return True

def _has_thread_numbering(self, text: str) -> bool:
    """Check if tweet has thread numbering like 1/, (1/n), etc."""
    import re
    patterns = [
        r'^\d+/',  # 1/, 2/, etc.
        r'^\d+\.',  # 1., 2., etc.
        r'\(\d+/\d+\)',  # (1/5), (2/5), etc.
        r'^\[\d+\]',  # [1], [2], etc.
    ]
    return any(re.search(pattern, text) for pattern in patterns)
```

### Strategy 4: Conversation ID (If Available)

```python
def find_conversation_threads(self) -> List[List[Dict]]:
    """Use conversation_id if available in export"""
    
    conversations = defaultdict(list)
    
    for tweet in self.tweets:
        conv_id = tweet.get('conversation_id')
        if conv_id:
            conversations[conv_id].append(tweet)
    
    # Filter and sort
    threads = []
    for conv_id, tweets in conversations.items():
        if len(tweets) > 1:
            # Sort by timestamp
            tweets.sort(key=lambda t: datetime.strptime(t['created_at'], '%a %b %d %H:%M:%S %z %Y'))
            threads.append(tweets)
    
    return threads
```

## Complete Thread Detection Pipeline

```python
class ComprehensiveThreadDetector:
    def __init__(self, tweets: List[Dict]):
        self.tweets = tweets
        self.detector = ThreadDetector(tweets)
        self.threads = []
        self.orphan_tweets = []
        
    def detect_all_threads(self) -> Dict[str, Any]:
        """Run all detection strategies and merge results"""
        
        all_threads = []
        thread_sources = {}
        
        # Strategy 1: Reply chains
        reply_threads = self.detector.find_reply_chains()
        all_threads.extend(reply_threads)
        thread_sources['reply_chains'] = len(reply_threads)
        
        # Strategy 2: Self-replies
        self_threads = self.detector.find_self_reply_threads()
        all_threads.extend(self_threads)
        thread_sources['self_replies'] = len(self_threads)
        
        # Strategy 3: Temporal clustering
        temporal_threads = self.detector.find_temporal_threads()
        all_threads.extend(temporal_threads)
        thread_sources['temporal'] = len(temporal_threads)
        
        # Strategy 4: Conversation ID (if available)
        conv_threads = self.detector.find_conversation_threads()
        all_threads.extend(conv_threads)
        thread_sources['conversation_id'] = len(conv_threads)
        
        # Deduplicate threads
        self.threads = self._deduplicate_threads(all_threads)
        
        # Find orphan tweets
        threaded_ids = set()
        for thread in self.threads:
            threaded_ids.update([t['id'] for t in thread])
        
        self.orphan_tweets = [
            t for t in self.tweets 
            if t['id'] not in threaded_ids
        ]
        
        return {
            'total_threads': len(self.threads),
            'total_threaded_tweets': len(threaded_ids),
            'orphan_tweets': len(self.orphan_tweets),
            'detection_sources': thread_sources,
            'threads': self.threads
        }
    
    def _deduplicate_threads(self, threads: List[List[Dict]]) -> List[List[Dict]]:
        """Remove duplicate threads (same tweets in different orders)"""
        
        unique_threads = []
        seen_combinations = set()
        
        for thread in threads:
            # Create a unique identifier for this thread
            thread_ids = frozenset([t['id'] for t in thread])
            
            if thread_ids not in seen_combinations:
                seen_combinations.add(thread_ids)
                unique_threads.append(thread)
        
        return unique_threads
```

## Thread Validation and Metrics

```python
class ThreadValidator:
    def __init__(self):
        self.validation_stats = {
            'valid_threads': 0,
            'broken_threads': 0,
            'single_tweets': 0
        }
    
    def validate_thread(self, thread: List[Dict]) -> Dict[str, Any]:
        """Validate thread integrity and return metrics"""
        
        validation = {
            'is_valid': True,
            'tweet_count': len(thread),
            'gaps': [],
            'total_words': 0,
            'time_span_minutes': 0
        }
        
        # Check for gaps in conversation
        for i in range(len(thread) - 1):
            current = thread[i]
            next_tweet = thread[i + 1]
            
            # Check if next tweet replies to current
            if next_tweet.get('reply_to_id') != current['id']:
                validation['gaps'].append(i)
        
        # Calculate metrics
        validation['total_words'] = sum(
            len(t['text'].split()) for t in thread
        )
        
        # Time span
        first_time = datetime.strptime(thread[0]['created_at'], '%a %b %d %H:%M:%S %z %Y')
        last_time = datetime.strptime(thread[-1]['created_at'], '%a %b %d %H:%M:%S %z %Y')
        validation['time_span_minutes'] = (last_time - first_time).total_seconds() / 60
        
        # Mark as invalid if too many gaps
        if len(validation['gaps']) > len(thread) / 2:
            validation['is_valid'] = False
            self.validation_stats['broken_threads'] += 1
        else:
            self.validation_stats['valid_threads'] += 1
        
        return validation
```

## Output Format

Threads will be saved in a structured format:

```json
{
  "thread_id": "root_tweet_id",
  "created_at": "first_tweet_timestamp",
  "tweet_count": 5,
  "total_words": 523,
  "detection_method": "reply_chain",
  "tweets": [
    {
      "id": "123",
      "text": "First tweet in thread",
      "created_at": "timestamp",
      "position": 1
    },
    {
      "id": "124",
      "text": "Second tweet in thread",
      "created_at": "timestamp",
      "position": 2
    }
  ]
}
```

## Key Decisions for Implementation

1. **Minimum thread length**: Include threads with 2+ tweets or 3+ tweets?
2. **Time window for temporal clustering**: 30 minutes? 1 hour?
3. **Handling broken threads**: Include with gaps marked, or exclude?
4. **Orphan tweets**: Process as individual essays or exclude entirely?
5. **Thread numbering**: Trust explicit numbering (1/, 2/) over other signals?

These parameters should be configurable to allow experimentation.
