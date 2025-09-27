#!/usr/bin/env python3
"""
TEST THE TRANSFORMER POWER! 🚀🔥⚡
"""

import sys
from pathlib import Path

# Add scripts directory to path to import modules
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from nlp_core import MODEL_TYPE
from interfaces import get_nlp_instance

# Get the nlp instance
nlp = get_nlp_instance()
from text_utilities import extract_entities, generate_title

print("=" * 80)
print("🚀 NUCLEAR FUSION TRANSFORMER TEST 🚀")
print(f"Model Type: {MODEL_TYPE.upper()}")
print("=" * 80)

# Test texts with rich political/philosophical content
test_texts = [
    """The dialectical relationship between base and superstructure reveals
    the fundamental contradictions within capitalism. As Marx argued, the
    means of production determine social relations, but revolutionary praxis
    can transform these material conditions.""",
    """Solidarity with Palestinian liberation requires understanding imperialism
    as the highest stage of capitalism. The struggle against colonialism is
    inseparable from class struggle.""",
    """That's not how historical materialism works. The bourgeoisie creates
    false consciousness through ideological state apparatuses, but the
    proletariat develops class consciousness through struggle.""",
]

for i, text in enumerate(test_texts, 1):
    print(f"\n📝 Test Case {i}:")
    print("-" * 60)
    print(f"Text preview: {text[:100]}...")

    # Test title generation
    title = generate_title(text)
    print(f"\n🏷️  Generated Title: {title}")

    # Test enhanced entity extraction with SEMANTIC POWER
    print("\n⚡ Enhanced Tags (with semantic similarity):")
    tags = extract_entities(text, limit=8)
    for j, tag in enumerate(tags, 1):
        print(f"  {j}. {tag}")

    # If we have semantic capabilities, test similarity
    if MODEL_TYPE in ["large", "medium"]:
        print("\n🧠 Semantic Understanding Test (with word vectors):")
        # Test semantic similarity between related concepts
        doc1 = nlp("dialectical materialism")
        doc2 = nlp("historical materialism")
        if doc1.has_vector and doc2.has_vector:
            similarity = doc1.similarity(doc2)
            print(
                f"  'dialectical materialism' ≈ 'historical materialism': {similarity:.3f}"
            )

        doc3 = nlp("capitalism")
        doc4 = nlp("exploitation")
        if doc3.has_vector and doc4.has_vector:
            similarity = doc3.similarity(doc4)
            print(f"  'capitalism' ≈ 'exploitation': {similarity:.3f}")

        doc5 = nlp("revolutionary praxis")
        doc6 = nlp("political action")
        if doc5.has_vector and doc6.has_vector:
            similarity = doc5.similarity(doc6)
            print(f"  'revolutionary praxis' ≈ 'political action': {similarity:.3f}")
    elif MODEL_TYPE == "transformer":
        print(
            "\n🧠 Note: Transformer model excels at contextual understanding but lacks word vectors for similarity calculations"
        )

print("\n" + "=" * 80)
print("🎯 TRANSFORMER POWER TEST COMPLETE!")
print("=" * 80)
