# Twitter Archive Data Structure Analysis

## Actual Tweet Object Structure

Based on examination of the Twitter/X export format, each tweet is structured as follows:

```json
{
  "tweet": {
    "edit_info": {
      "initial": {
        "editTweetIds": ["tweet_id"],
        "editableUntil": "ISO_date",
        "editsRemaining": "number",
        "isEditEligible": boolean
      }
    },
    "retweeted": boolean,
    "source": "html_string_with_client_info",
    "entities": {
      "hashtags": [],
      "symbols": [],
      "user_mentions": [],
      "urls": [
        {
          "url": "t.co_shortened",
          "expanded_url": "actual_url",
          "display_url": "display_version",
          "indices": ["start", "end"]
        }
      ]
    },
    "display_text_range": ["start", "end"],
    "favorite_count": "number",
    "id_str": "unique_tweet_id",
    "truncated": boolean,
    "retweet_count": "number",
    "id": "numeric_id",
    "possibly_sensitive": boolean,
    "created_at": "readable_date_string",
    "favorited": boolean,
    "full_text": "actual_tweet_content",
    "lang": "language_code"
  }
}
```

## Key Fields for Our Use Case

### Essential Fields
- **`id_str`**: Unique identifier for the tweet
- **`full_text`**: The actual tweet content (what we'll analyze and preserve)
- **`created_at`**: Timestamp for chronological ordering
- **`lang`**: Language detection (filter for English if needed)

### Thread Detection Fields (Need Investigation)
**Note**: The example tweet doesn't show these, but they should appear in replies:
- `in_reply_to_status_id_str`: ID of tweet being replied to
- `in_reply_to_user_id_str`: User being replied to
- `conversation_id`: Thread grouping (may not exist in all exports)

### Classification Signals
- **`favorite_count`**: Higher counts might indicate thoughtful content
- **`retweet_count`**: Engagement metric
- **`entities.urls`**: Presence of links/citations
- **`entities.hashtags`**: Topic markers
- **`possibly_sensitive`**: May indicate political content

### New Considerations
- **`edit_info`**: Tweets can be edited; need to decide which version to use
- **Nested structure**: Each tweet wrapped in `{"tweet": {...}}`

## File Structure in Archive

```
twitter-archives/
├── data/
│   ├── tweets.js (38MB - main tweets)
│   ├── deleted-tweets.js
│   ├── note-tweet.js (longer form tweets?)
│   ├── community-tweet.js
│   └── [various other data files]
└── tweets_media/
    └── [media files referenced in tweets]
```

## JavaScript Wrapper Format

Each `.js` file begins with a JavaScript assignment:
```javascript
window.YTD.tweets.part0 = [
  // ... array of tweet objects
]
```

This wrapper must be stripped before JSON parsing.

## Data Volume Estimation

- File size: ~38MB
- Estimated tweets: 10,000-20,000 (assuming 2-4KB per tweet object)
- Processing approach: Can likely load entire file into memory on modern systems

## Critical Questions Needing Answers

1. **Thread Detection**: Need examples of:
   - A tweet that starts a thread
   - A reply tweet within a thread
   - How self-replies are structured

2. **Content Types**: Need examples of:
   - Retweets (should these be excluded?)
   - Quote tweets (might contain commentary)
   - Tweets with media attachments

3. **Deleted Content**: 
   - How are gaps in threads handled?
   - Should deleted-tweets.js be incorporated?

## Next Steps

Before proceeding with implementation, we need:
1. Sample of a thread (multiple connected tweets)
2. Example of a retweet structure
3. Example of a quote tweet
4. Clarification on whether to include retweets/quotes in the corpus

These samples will determine the exact thread detection algorithm and filtering logic.
