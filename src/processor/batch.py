from typing import Dict, Any


def validate_tweet(tweet: Dict[str, Any]) -> bool:
    """Validate that tweet has required fields"""
    required_fields = ["id_str", "full_text", "created_at"]
    return all(field in tweet for field in required_fields)


def clean_tweet_data(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and normalize tweet data"""
    cleaned = {
        "id": tweet.get("id_str"),
        "text": tweet.get("full_text", ""),
        "created_at": tweet.get("created_at"),
        "lang": tweet.get("lang", "unknown"),
        "reply_to_id": tweet.get("in_reply_to_status_id_str"),
        "reply_to_user": tweet.get("in_reply_to_user_id_str"),
        "conversation_id": tweet.get("conversation_id"),
        "retweet_count": int(tweet.get("retweet_count", 0)),
        "favorite_count": int(tweet.get("favorite_count", 0)),
        "is_retweet": tweet.get("retweeted", False),
        "entities": tweet.get("entities", {}),
        "possibly_sensitive": tweet.get("possibly_sensitive", False),
    }

    # Handle edit info if present
    if "edit_info" in tweet and "initial" in tweet["edit_info"]:
        cleaned["edit_history"] = tweet["edit_info"]["initial"].get("editTweetIds", [])
        cleaned["is_edited"] = len(cleaned["edit_history"]) > 1

    return cleaned


class TweetFilter:
    def __init__(self):
        self.excluded_count = {"retweets": 0, "non_english": 0, "deleted": 0}

    def should_include(self, tweet: Dict[str, Any]) -> bool:
        """Determine if tweet should be included in corpus"""

        # Exclude pure retweets (keep quote tweets)
        if tweet["text"].startswith("RT @"):
            self.excluded_count["retweets"] += 1
            return False

        # Exclude deleted placeholder tweets
        if tweet["text"] == "" or tweet["text"] is None:
            self.excluded_count["deleted"] += 1
            return False

        return True

    def get_stats(self) -> Dict[str, int]:
        """Return filtering statistics"""
        return self.excluded_count
