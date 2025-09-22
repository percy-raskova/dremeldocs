#!/usr/bin/env python3
"""
Quick analysis script to understand Twitter archive structure
"""

import json
import re

def analyze_twitter_archive():
    # Read first 10KB of the file to understand structure
    with open('/home/percy/projects/astradocs/twitter-archives/data/tweets.js', 'r', encoding='utf-8') as f:
        content = f.read(10000)  # First 10KB
        
    print("First 10KB of tweets.js:")
    print("=" * 50)
    print(content[:5000])  # Print first 5KB
    print("\n" + "=" * 50)
    
    # Try to extract the JavaScript variable assignment
    js_pattern = r'window\.YTD\.tweets\.part\d+\s*=\s*'
    match = re.search(js_pattern, content)
    
    if match:
        print(f"Found JavaScript wrapper: {match.group()}")
        # Remove the JS wrapper to get to the JSON
        json_start = match.end()
        json_content = content[json_start:]
        
        # Try to parse a portion as JSON
        try:
            # Find the first complete tweet object
            first_bracket = json_content.find('[')
            if first_bracket != -1:
                # Extract enough to get at least one complete tweet
                sample = json_content[first_bracket:first_bracket+3000]
                print("\nSample JSON structure (first tweet):")
                print(sample)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
    else:
        print("No JavaScript wrapper found, might be pure JSON")

if __name__ == "__main__":
    analyze_twitter_archive()
