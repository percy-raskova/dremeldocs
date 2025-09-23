#!/usr/bin/env python3
"""
Test script to validate the enhanced tag extraction system.
Shows before/after comparison of tag quality.
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path to import modules
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from text_processing import (
    extract_entities,
    extract_entities_basic,
    EnhancedTagExtractor
)

def test_enhanced_extraction():
    """Test enhanced extraction against sample threads."""

    print("🧪 Testing Enhanced Tag Extraction on Real Threads")
    print("=" * 70)

    # Load a sample of threads to test with
    data_path = Path("data/filtered_threads.json")
    if not data_path.exists():
        print("❌ No sample data found. Please run the main pipeline first.")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Test with first 3 heavy hitter threads (500+ words)
    heavy_threads = [t for t in data['threads'] if t['word_count'] >= 500][:3]

    for i, thread in enumerate(heavy_threads, 1):
        print(f"\n📝 Thread {i}: {thread['word_count']} words")
        print(f"ID: {thread['thread_id']}")
        print("Content:", thread['smushed_text'][:150] + "...")
        print("-" * 50)

        # Test enhanced vs basic extraction
        print("🏷️  Enhanced Tags:")
        enhanced_tags = extract_entities(thread['smushed_text'], limit=8)
        for j, tag in enumerate(enhanced_tags, 1):
            print(f"  {j}. {tag}")

        print("\n🔖 Basic Tags (for comparison):")
        basic_tags = extract_entities_basic(thread['smushed_text'], limit=8)
        for j, tag in enumerate(basic_tags, 1):
            print(f"  {j}. {tag}")

        # Test domain detection
        try:
            extractor = EnhancedTagExtractor()
            domain_categories = extractor.domain_vocab.get_domain_categories(thread['smushed_text'])
            if domain_categories:
                print(f"\n🎯 Domain Categories: {', '.join(domain_categories)}")
            else:
                print("\n🎯 Domain Categories: None detected")

            domain_count = extractor.domain_vocab.count_domain_terms(thread['smushed_text'])
            print(f"📊 Domain Terms Found: {domain_count}")

        except Exception as e:
            print(f"\n⚠️  Domain detection error: {e}")

    print("\n" + "=" * 70)
    print("✅ Testing Complete!")

    print("\n📊 Quality Assessment:")
    print("- Enhanced tags should show more political/philosophical concepts")
    print("- Should detect domain categories (political_theory, philosophy, etc.)")
    print("- Tags should be more meaningful than basic extraction")
    print("\n💡 Look for tags like:")
    print("  - 'dialectical materialism', 'class consciousness'")
    print("  - 'bourgeois ideology', 'revolutionary praxis'")
    print("  - 'historical materialism', 'means of production'")

if __name__ == "__main__":
    test_enhanced_extraction()