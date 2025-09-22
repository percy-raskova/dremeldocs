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

        with open(tweets_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove JavaScript wrapper
        # Pattern: window.YTD.tweets.part0 =
        json_content = re.sub(r"^window\.YTD\.\w+\.part\d+\s*=\s*", "", content)

        # Parse JSON array
        raw_tweets = json.loads(json_content)

        # Extract nested tweet objects
        tweets = []
        for item in raw_tweets:
            if "tweet" in item:
                tweet = item["tweet"]
                tweets.append(tweet)
            else:
                # Handle potential format variations
                tweets.append(item)

        return tweets
