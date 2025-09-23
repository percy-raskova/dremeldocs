#!/usr/bin/env python3
"""
Local-first filtering pipeline for Twitter archive
No AI, no API costs - just smart filtering to get from 37MB → ~4MB
Then we can actually look at what we got, capeesh?
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Generator, Optional, Set
import ijson

class LocalThreadExtractor:
    def __init__(self, archive_path: Path) -> None:
        self.archive_path = Path(archive_path)

        # Validate archive directory structure
        self._validate_archive_structure()

        self.tweets_file = self.archive_path / "data" / "tweets.js"
        self.tweets_by_id: Dict[str, Dict[str, Any]] = {}
        self.reply_map: Dict[str, List[str]] = defaultdict(list)
        self.threads: List[List[Dict[str, Any]]] = []
        self.filtered_tweets: List[Dict[str, Any]] = []

    def _validate_archive_structure(self) -> None:
        """Validate that the archive directory has the expected structure."""
        if not self.archive_path.exists():
            raise ValueError(f"❌ Archive directory does not exist: {self.archive_path}")

        if not self.archive_path.is_dir():
            raise ValueError(f"❌ Archive path is not a directory: {self.archive_path}")

        # Check for required files and directories
        required_paths = [
            self.archive_path / "data",
            self.archive_path / "data" / "tweets.js",
            self.archive_path / "Your archive.html"
        ]

        missing_paths = []
        for path in required_paths:
            if not path.exists():
                missing_paths.append(path)

        if missing_paths:
            print("❌ Missing required files/directories in archive:")
            for path in missing_paths:
                print(f"   - {path}")
            print("\n💡 This should be a Twitter/X data export directory containing:")
            print("   - data/ directory with tweets.js")
            print("   - Your archive.html file")
            raise ValueError("Invalid archive structure - see missing files above")

        # Validate tweets.js file
        tweets_file = self.archive_path / "data" / "tweets.js"
        if tweets_file.stat().st_size == 0:
            raise ValueError(f"❌ tweets.js file is empty: {tweets_file}")

        # Quick validation that it looks like a tweets.js file
        try:
            with open(tweets_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if not first_line.startswith('window.YTD.tweets.part0'):
                    raise ValueError(f"❌ tweets.js does not appear to be a valid Twitter archive file")
        except UnicodeDecodeError:
            raise ValueError(f"❌ tweets.js file appears to be corrupted or not a text file")

        print(f"✅ Archive structure validated: {self.archive_path}")

    def stream_tweets(self) -> Generator[Dict[str, Any], None, None]:
        """Stream tweets from the JS file without loading it all into memory"""
        print("🔄 Streaming tweets from archive...")

        with open(self.tweets_file, 'rb') as f:
            # Read first 100 bytes to find where JSON starts
            header = f.read(100)

            # Find the opening bracket
            json_start = header.find(b'[')
            if json_start == -1:
                raise ValueError("Could not find JSON array start")

            # Reset to start of JSON
            f.seek(json_start)

            # Stream parse with ijson
            parser = ijson.items(f, 'item')
            count = 0
            for item in parser:
                count += 1
                if count % 1000 == 0:
                    print(f"  Processed {count} tweets...")

                # Handle nested structure
                if 'tweet' in item:
                    yield item['tweet']
                else:
                    yield item

        print(f"✅ Streamed {count} total tweets")

    def apply_stage1_filter(self, tweet: Dict[str, Any]) -> bool:
        """Stage 1: Length filter - must be >100 chars"""
        text = tweet.get('full_text', '')
        return len(text) > 100

    def apply_stage2_filter(self, tweet: Dict[str, Any]) -> bool:
        """Stage 2: Thread detection - must be part of a conversation"""
        # It's in a thread if it's either a reply OR has replies to it
        tweet_id = tweet.get('id_str')
        is_reply = tweet.get('in_reply_to_status_id_str') is not None

        # We'll check for replies in a second pass
        # For now, mark replies and store all tweets
        if is_reply or tweet_id:
            return True
        return False

    def process_tweets(self) -> None:
        """Apply the two-stage filter"""
        print("\n🎯 Applying two-stage filter...")
        stage1_passed = 0
        stage2_passed = 0

        # First pass: collect tweets and build reply map
        for tweet in self.stream_tweets():
            # Stage 1: Length filter
            if not self.apply_stage1_filter(tweet):
                continue
            stage1_passed += 1

            # Store tweet for thread building
            tweet_id = tweet.get('id_str')
            if tweet_id:
                self.tweets_by_id[tweet_id] = tweet

                # Build reply map
                reply_to = tweet.get('in_reply_to_status_id_str')
                if reply_to:
                    self.reply_map[reply_to].append(tweet_id)

        print(f"  Stage 1 (length >100): {stage1_passed} tweets passed")

        # Second pass: identify tweets that are part of threads
        for tweet_id, tweet in self.tweets_by_id.items():
            is_reply = tweet.get('in_reply_to_status_id_str') is not None
            has_replies = tweet_id in self.reply_map

            if is_reply or has_replies:
                self.filtered_tweets.append(tweet)
                stage2_passed += 1

        print(f"  Stage 2 (thread detection): {stage2_passed} tweets passed")
        print(f"  Reduction: {21723} → {stage2_passed} ({stage2_passed/21723*100:.1f}% remaining)")

    def reconstruct_threads(self) -> None:
        """Reconstruct conversation threads from filtered tweets"""
        print("\n🔨 Reconstructing threads...")
        processed: Set[str] = set()

        # Find thread roots (tweets that are not replies but have replies)
        thread_roots = []
        for tweet_id, tweet in self.tweets_by_id.items():
            if tweet_id in processed:
                continue

            # Is this a thread root?
            if not tweet.get('in_reply_to_status_id_str') and tweet_id in self.reply_map:
                thread_roots.append(tweet_id)

        print(f"  Found {len(thread_roots)} thread roots")

        # Build threads from roots
        for root_id in thread_roots:
            thread = self._build_thread(root_id, processed)
            if len(thread) >= 2:  # At least 2 tweets to be a thread
                self.threads.append(thread)

        # Also find reply chains that might not have roots in our dataset
        for tweet_id, tweet in self.tweets_by_id.items():
            if tweet_id in processed:
                continue

            if tweet.get('in_reply_to_status_id_str'):
                # Build a partial thread
                thread = self._build_partial_thread(tweet_id, processed)
                if len(thread) >= 2:
                    self.threads.append(thread)

        print(f"✅ Reconstructed {len(self.threads)} threads")

        # Sort threads by first tweet date
        self.threads.sort(key=lambda t: t[0].get('created_at', ''), reverse=True)

    def _build_thread(self, root_id: str, processed: Set[str]) -> List[Dict[str, Any]]:
        """Build a thread starting from root"""
        thread: List[Dict[str, Any]] = []
        to_process = [root_id]

        while to_process:
            tweet_id = to_process.pop(0)
            if tweet_id in processed or tweet_id not in self.tweets_by_id:
                continue

            tweet = self.tweets_by_id[tweet_id]
            thread.append(tweet)
            processed.add(tweet_id)

            # Add replies to process queue
            if tweet_id in self.reply_map:
                to_process.extend(self.reply_map[tweet_id])

        return thread

    def _build_partial_thread(self, start_id: str, processed: Set[str]) -> List[Dict[str, Any]]:
        """Build a thread from any starting point"""
        thread: List[Dict[str, Any]] = []
        current_id: Optional[str] = start_id

        # Go up to find the root we have
        while current_id and current_id in self.tweets_by_id:
            tweet = self.tweets_by_id[current_id]
            thread.insert(0, tweet)
            processed.add(current_id)
            current_id = tweet.get('in_reply_to_status_id_str')

        # Then go down from the starting point
        if start_id in self.reply_map:
            for reply_id in self.reply_map[start_id]:
                if reply_id not in processed and reply_id in self.tweets_by_id:
                    thread.append(self.tweets_by_id[reply_id])
                    processed.add(reply_id)

        return thread

    def generate_json_output(self) -> Dict[str, Any]:
        """Generate JSON output optimized for Claude"""
        print("\n📝 Generating JSON output...")

        output: Dict[str, Any] = {
            "metadata": {
                "total_original_tweets": 21723,
                "filtered_tweets": len(self.filtered_tweets),
                "threads_found": len(self.threads),
                "processing_date": datetime.now().isoformat(),
                "filter_stages": ["length>100", "thread_detection"]
            },
            "threads": []
        }

        for i, thread in enumerate(self.threads):
            # Smush the text together as requested
            smushed_text = " ".join([tweet.get('full_text', '') for tweet in thread])

            thread_data = {
                "thread_id": f"thread_{i:04d}",
                "tweet_count": len(thread),
                "first_tweet_date": thread[0].get('created_at', ''),
                "smushed_text": smushed_text,
                "word_count": len(smushed_text.split()),
                "tweet_ids": [t.get('id_str') for t in thread],
                "individual_tweets": thread  # Full data if needed
            }
            output["threads"].append(thread_data)

        # Save to file
        output_file = Path("data/filtered_threads.json")
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved JSON to {output_file}")
        return output

    def generate_sample_markdown(self, sample_count: int = 5) -> None:
        """Generate a few sample markdown files to see what they look like"""
        print(f"\n📄 Generating {sample_count} sample markdown files...")

        md_dir = Path("data/sample_threads")
        md_dir.mkdir(exist_ok=True)

        # Get the longest threads as samples (likely most interesting)
        sorted_threads = sorted(self.threads, key=lambda t: len(t), reverse=True)

        for i, thread in enumerate(sorted_threads[:sample_count]):
            # Create filename from date and first few words
            first_tweet = thread[0]
            date_str = first_tweet.get('created_at', '')[:10]
            first_words = first_tweet.get('full_text', '')[:50]
            first_words = re.sub(r'[^\w\s]', '', first_words)[:30]

            filename = f"{date_str}_{first_words.replace(' ', '_')}.md"
            filepath = md_dir / filename

            # Smush the text together as requested - no formatting, just raw
            smushed_text = " ".join([tweet.get('full_text', '') for tweet in thread])

            # Create simple markdown
            content = f"""# Thread from {date_str}

**Tweets in thread**: {len(thread)}
**Total words**: {len(smushed_text.split())}

---

{smushed_text}

---

*Thread IDs: {', '.join([t.get('id_str', '') for t in thread])}*
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  Created: {filename}")

        print(f"✅ Sample markdowns in {md_dir}")

    def run_pipeline(self) -> Dict[str, Any]:
        """Run the complete local filtering pipeline"""
        print("🚀 Starting local filtering pipeline...")
        print("=" * 50)

        # Run the pipeline
        self.process_tweets()
        self.reconstruct_threads()
        output = self.generate_json_output()
        self.generate_sample_markdown()

        print("\n" + "=" * 50)
        print("🎉 Pipeline complete!")
        print(f"📊 Results:")
        print(f"  • Filtered from 21,723 to {len(self.filtered_tweets)} tweets")
        print(f"  • Found {len(self.threads)} conversation threads")
        print(f"  • Average thread length: {sum(len(t) for t in self.threads)/len(self.threads):.1f} tweets")
        print(f"  • Longest thread: {max(len(t) for t in self.threads)} tweets")
        print(f"\n📁 Output files:")
        print(f"  • JSON for Claude: data/filtered_threads.json")
        print(f"  • Sample markdowns: data/sample_threads/")

        return output


if __name__ == "__main__":
    # Run it!
    extractor = LocalThreadExtractor(Path("source"))
    extractor.run_pipeline()