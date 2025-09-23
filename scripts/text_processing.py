#!/usr/bin/env python3
"""
Backward compatibility module for text processing utilities.
Imports and re-exports functions from the split modules for existing code.
"""

# Import from the new split modules
from nlp_core import (
    nlp,
    MODEL_TYPE,
    NLP_CONFIG,
    load_nlp_config,
    clean_social_text,
    calculate_reading_time,
    process_batch
)

from tag_extraction import (
    DomainVocabulary,
    PatternMatcher,
    ChunkScorer,
    EnhancedTagExtractor,
    extract_concept_tags
)

from text_utilities import (
    skip_common_starters,
    extract_key_phrase,
    generate_title,
    generate_description,
    extract_entities,
    extract_entities_basic,
    format_frontmatter_value,
    parse_to_yyyymmdd,
    generate_brief_title,
    generate_filename
)

# Re-export everything for backward compatibility
__all__ = [
    # Core NLP
    'nlp', 'MODEL_TYPE', 'NLP_CONFIG', 'load_nlp_config',
    'clean_social_text', 'calculate_reading_time', 'process_batch',

    # Tag extraction classes
    'DomainVocabulary', 'PatternMatcher', 'ChunkScorer', 'EnhancedTagExtractor',
    'extract_concept_tags',

    # Text utilities
    'skip_common_starters', 'extract_key_phrase', 'generate_title',
    'generate_description', 'extract_entities', 'extract_entities_basic',
    'format_frontmatter_value', 'parse_to_yyyymmdd', 'generate_brief_title',
    'generate_filename'
]

if __name__ == "__main__":
    # Test the enhanced functionality
    test_texts = [
        """RT @someone: This is an amazing philosophical thread about dialectical materialism!
        https://t.co/abc123 Check it out. #philosophy #marxism
        The relationship between theory and praxis is fundamental to understanding revolutionary change.
        We must examine the 'means of production' and class consciousness in our analysis.""",

        """I've been thinking about Marx's theory of surplus value and how it applies to modern capitalism.
        The bourgeois ideology perpetuates false consciousness among the working class.
        Revolutionary praxis requires both theoretical understanding and material action.""",

        """That's not how dialectical materialism works. Historical materialism shows us that
        the 'base and superstructure' relationship determines social change.
        Class struggle is the motor of history, not individual agency."""
    ]

    print("🧪 Testing Enhanced Tag Extraction")
    print("=" * 60)

    for i, test_text in enumerate(test_texts, 1):
        print(f"\n📝 Test Case {i}:")
        print("Text:", test_text[:100] + "..." if len(test_text) > 100 else test_text)
        print("-" * 50)

        # Test basic functions
        print("Title:", generate_title(test_text))
        print("Description:", generate_description(test_text)[:100] + "...")
        print("Reading Time:", calculate_reading_time(test_text), "min")

        # Test enhanced entity extraction
        print("\n🏷️  Enhanced Tags:")
        enhanced_tags = extract_entities(test_text, limit=8)
        for j, tag in enumerate(enhanced_tags, 1):
            print(f"  {j}. {tag}")

        # Test basic extraction for comparison
        print("\n🔖 Basic Tags (for comparison):")
        basic_tags = extract_entities_basic(test_text, limit=8)
        for j, tag in enumerate(basic_tags, 1):
            print(f"  {j}. {tag}")

        # Test domain vocabulary detection
        try:
            extractor = EnhancedTagExtractor()
            domain_categories = extractor.domain_vocab.get_domain_categories(test_text)
            if domain_categories:
                print(f"\n🎯 Domain Categories: {', '.join(domain_categories)}")
        except Exception as e:
            print(f"\n⚠️  Domain detection error: {e}")

    # Test filename generation
    print("\n" + "=" * 60)
    print("📁 Filename Generation Tests:")
    test_dates = [
        "Sat Apr 26 15:30:45 +0000 2025",
        "2025-04-26T15:30:45Z",
        "2025-04-26",
        None
    ]
    for i, date in enumerate(test_dates, 1):
        filename = generate_filename(i, date, test_texts[0])
        print(f"  Date: {date}")
        print(f"  Filename: {filename}")
        print()

    print("✅ Testing complete!")
    print("\n💡 To see the enhanced extraction in action:")
    print("   cd scripts/")
    print("   python text_processing.py")