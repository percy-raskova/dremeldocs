#!/usr/bin/env python3
"""
Test script for the new filename generation functionality.
"""

import sys
from pathlib import Path

# Add scripts directory to path to import modules
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from text_utilities import generate_brief_title, generate_filename, parse_to_yyyymmdd


def test_filename_generation():
    """Test various filename generation scenarios."""

    print("Testing Filename Generation")
    print("=" * 60)

    # Test cases with different text and dates
    test_cases = [
        {
            "seq": 1,
            "date": "Sat Apr 26 15:30:45 +0000 2025",
            "text": "RT @someone: This is an amazing philosophical thread about dialectical materialism and the relationship between theory and praxis!",
            "expected_pattern": "001-20250426-",
        },
        {
            "seq": 42,
            "date": "2025-01-22T10:30:00Z",
            "text": "The contradictions of capitalism reveal themselves in every crisis. What we're seeing is not a bug but a feature of the system.",
            "expected_pattern": "042-20250122-",
        },
        {
            "seq": 999,
            "date": None,
            "text": "A thread about revolutionary consciousness and organizing strategies for the 21st century.",
            "expected_pattern": "999-20250101-",  # Default date
        },
        {
            "seq": 5,
            "date": "2024-12-25",
            "text": "@someone Have you considered how Spinoza's concept of conatus relates to Marx's species-being? Thread:",
            "expected_pattern": "005-20241225-",
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Sequence: {test['seq']}")
        print(f"  Date: {test['date']}")
        print(f"  Text: {test['text'][:60]}...")

        # Generate filename
        filename = generate_filename(test["seq"], test["date"], test["text"])
        print(f"  Generated: {filename}")

        # Check if it matches expected pattern
        if filename.startswith(test["expected_pattern"]):
            print(f"  ✅ Pattern matches: {test['expected_pattern']}*")
        else:
            print(f"  ❌ Expected pattern: {test['expected_pattern']}*")

        # Validate format
        parts = filename[:-3].split("-", 2)  # Remove .md and split
        if len(parts) == 3:
            seq_part, date_part, title_part = parts
            print(
                f"  Parts: seq={seq_part}, date={date_part}, title={title_part[:30]}..."
            )

            # Validate each part
            if seq_part.isdigit() and len(seq_part) == 3:
                print("    ✅ Sequence format correct")
            else:
                print("    ❌ Sequence format incorrect")

            if date_part.isdigit() and len(date_part) == 8:
                print("    ✅ Date format correct (YYYYMMDD)")
            else:
                print("    ❌ Date format incorrect")

            if title_part and "_" in title_part:
                print("    ✅ Title has underscores")
            elif title_part:
                print("    ⚠️  Title exists but no underscores")
        else:
            print("  ❌ Could not parse filename parts")

    print("\n" + "=" * 60)
    print("Additional Function Tests:")

    # Test date parsing
    print("\n1. Date Parsing (parse_to_yyyymmdd):")
    dates = [
        "Sat Apr 26 15:30:45 +0000 2025",
        "2025-04-26T15:30:45Z",
        "2025-04-26",
        "April 26, 2025",
        None,
    ]
    for date in dates:
        result = parse_to_yyyymmdd(date)
        print(f"  {date!s:40} → {result}")

    # Test brief title generation
    print("\n2. Brief Title Generation (generate_brief_title):")
    texts = [
        "This is a simple title",
        "RT @someone: This should remove the RT and mention!",
        "A very long title that definitely exceeds the maximum length limit and should be truncated at a word boundary not in the middle",
        "Title with special chars: it's & that, plus 100% more!",
        "UPPERCASE TITLE SHOULD BECOME LOWERCASE",
    ]
    for text in texts:
        result = generate_brief_title(text, 30)
        print(f"  Input:  {text[:40]}...")
        print(f"  Output: {result}")
        print()


if __name__ == "__main__":
    test_filename_generation()
