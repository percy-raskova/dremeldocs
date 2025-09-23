#!/usr/bin/env python3
"""
Build Political Vocabulary - The Yenan Path
Learning from the actual language of the masses (your corpus)
"""

import json
import yaml
from pathlib import Path
from collections import Counter
import re

def extract_quality_terms():
    """Extract high-quality political terms from YOUR actual corpus."""

    # Load the heavy hitters
    heavy_hitters_dir = Path('docs/heavy_hitters')
    threads_file = Path('data/filtered_threads.json')

    # These are terms YOU actually use based on the analysis
    vocabulary_structure = {
        'marxism_communism': {
            'description': 'Marxist theory and communist organizing',
            'core_terms': [
                # From Thread #1 - Lake Quonnipaug Conference
                'communist organization',
                'communist party',
                'cadre formation',
                'mass work',
                'political education',
                'reproduction of communists',
                'organizing committee',
                'social investigation',
                'cross-pollination',
                'party formation',
                'organizational development',
                'principled marxists',
                # Core Marxist concepts from corpus
                'class consciousness',
                'means of production',
                'dialectical materialism',
                'historical materialism',
                'praxis',
                'base and superstructure',
                'surplus value',
                'wage labor',
                'proletariat',
                'bourgeoisie',
                'petit bourgeois',
                'class struggle',
                'class war',
                'working class',
                'ruling class',
                'owning class',
            ],
            'weight': 2.0
        },

        'fascism_analysis': {
            'description': 'Fascism theory and resistance',
            'core_terms': [
                # From Thread #13 - Fascism misunderstanding
                'great-nation consciousness',
                'national consciousness',
                'bourgeois hegemony',
                'liberal regime',
                'fascist hegemony',
                'national relation',
                'oppressor nation',
                'national hierarchy',
                'class collaboration',
                'false consciousness',
                # Additional fascism terms
                'liberal decay',
                'capitalism in decay',
                'colonialism applied to metropole',
                'proto-fascism',
                'neo-fascism',
                'fascist violence',
                'national chauvinism',
            ],
            'weight': 1.8
        },

        'imperialism_colonialism': {
            'description': 'Imperial and colonial analysis',
            'core_terms': [
                # From your corpus
                'settler colonialism',
                'national oppression',
                'national liberation',
                'imperial core',
                'imperial periphery',
                'global north',
                'global south',
                'comprador bourgeoisie',
                'colonial extraction',
                'resource extraction',
                'palestine',
                'zionist entity',
                'us empire',
                'imperial interests',
                'anti-imperialism',
                'internal colonialism',
            ],
            'weight': 1.8
        },

        'public_health_politics': {
            'description': 'Pandemic and public health as class struggle',
            'core_terms': [
                # From COVID threads
                'long covid',
                'covid wave',
                'pandemic erasure',
                'public health',
                'collective care',
                'disability justice',
                'exercise intolerance',
                'immune system',
                'variant',
                'mask',
                'n95',
                'kn95',
                'viral persistence',
                'cumulative risk',
                'vascular damage',
                'neurological effects',
            ],
            'weight': 1.6
        },

        'political_economy': {
            'description': 'Economic analysis and critique',
            'core_terms': [
                # From economic threads
                'primitive accumulation',
                'capital accumulation',
                'debt mechanics',
                'money creation',
                'labor exploitation',
                'prison labor',
                'slave labor',
                'wealth inequality',
                'effective altruism',
                'noblesse oblige',
                'economic hegemony',
                'financial imperialism',
                'rent extraction',
                'surplus extraction',
                'labor aristocracy',
            ],
            'weight': 1.7
        },

        'dialectical_historical_materialism': {
            'description': 'Philosophical method and analysis',
            'core_terms': [
                'dialectical materialism',
                'historical materialism',
                'material conditions',
                'material basis',
                'objective reality',
                'contradictions',
                'thesis antithesis synthesis',
                'negation of the negation',
                'quantity into quality',
                'scientific socialism',
                'idealism',
                'metaphysics',
                'empiricism',
                'vulgar materialism',
            ],
            'weight': 1.8
        },

        'social_criticism': {
            'description': 'Media and cultural critique',
            'core_terms': [
                'cultural hegemony',
                'manufacturing consent',
                'media manipulation',
                'statistical manipulation',
                'ideological apparatus',
                'false consciousness',
                'commodity fetishism',
                'alienation',
                'reification',
                'spectacle',
                'propaganda',
                'social reproduction',
                'individualization of oppression',
            ],
            'weight': 1.5
        },

        'operational_organizational_theory': {
            'description': 'Revolutionary organizing and strategy',
            'core_terms': [
                'democratic centralism',
                'party line',
                'party discipline',
                'mass line',
                'vanguard party',
                'base building',
                'cadre development',
                'united front',
                'dual power',
                'revolutionary strategy',
                'protracted peoples war',
                'serve the people',
                'criticism and self-criticism',
                'social investigation',
                'from the masses to the masses',
            ],
            'weight': 1.9
        }
    }

    return vocabulary_structure

def create_enhanced_vocabulary_yaml():
    """Create enhanced YAML files with your actual vocabulary."""

    vocab_structure = extract_quality_terms()
    output_dir = Path('data/vocabularies')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Also create a master vocabulary file
    master_vocab = {
        'name': 'DremelDocs Political Vocabulary',
        'version': '1.0',
        'description': 'Extracted from 59 heavy hitter threads using the mass line method',
        'categories': {}
    }

    for category, data in vocab_structure.items():
        # Individual category file
        category_vocab = {
            'category': category,
            'description': data['description'],
            'weight': data['weight'],
            'terms': {}
        }

        # Add terms with proper structure
        for term in data['core_terms']:
            category_vocab['terms'][term] = {
                'canonical': term,
                'variations': generate_variations(term),
                'weight': data['weight']
            }

        # Write individual file
        output_file = output_dir / f'{category}.yaml'
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(category_vocab, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Created {output_file.name} with {len(data['core_terms'])} terms")

        # Add to master
        master_vocab['categories'][category] = category_vocab

    # Write master vocabulary
    master_file = output_dir / 'master_vocabulary.yaml'
    with open(master_file, 'w', encoding='utf-8') as f:
        yaml.dump(master_vocab, f, default_flow_style=False, sort_keys=False)

    print(f"\n📚 Created master vocabulary with {len(vocab_structure)} categories")

def generate_variations(term):
    """Generate variations of a term for matching."""
    variations = [term]

    # Singular/plural
    if term.endswith('s') and not term.endswith('ss'):
        variations.append(term[:-1])
    elif not term.endswith('s'):
        variations.append(term + 's')

    # With/without hyphen
    if '-' in term:
        variations.append(term.replace('-', ' '))
        variations.append(term.replace('-', ''))

    # Abbreviations
    abbrev_map = {
        'communist': 'ML',
        'marxist': 'ML',
        'united states': 'US',
        'covid': 'coronavirus',
    }

    for key, val in abbrev_map.items():
        if key in term.lower():
            variations.append(term.lower().replace(key, val))

    return list(set(variations))

def test_vocabulary_on_sample():
    """Test the vocabulary on a sample thread."""

    print("\n🧪 Testing vocabulary on sample thread...")

    # Load a sample thread
    with open('data/filtered_threads.json', 'r') as f:
        data = json.load(f)

    # Get the first heavy hitter
    sample = next(t for t in data['threads'] if t['word_count'] >= 500)
    text = sample['smushed_text'].lower()

    # Load our vocabulary
    vocab_dir = Path('data/vocabularies')
    matches = Counter()

    for vocab_file in vocab_dir.glob('*.yaml'):
        if vocab_file.name == 'master_vocabulary.yaml':
            continue

        with open(vocab_file, 'r') as f:
            vocab_data = yaml.safe_load(f)

        category = vocab_data['category']
        for term in vocab_data['terms']:
            if term in text:
                matches[category] += 1

    print(f"\nMatches in sample thread ({sample['word_count']} words):")
    for category, count in matches.most_common():
        print(f"  {category}: {count} matches")

def main():
    print("🚩 BUILDING POLITICAL VOCABULARY - THE YENAN PATH")
    print("=" * 50)

    # Create enhanced vocabulary
    create_enhanced_vocabulary_yaml()

    # Test on sample
    test_vocabulary_on_sample()

    print("\n✊ The correct political line emerges from practice!")
    print("\n🎯 Next Steps:")
    print("1. Review vocabularies in data/vocabularies/")
    print("2. Test with your EnhancedTagExtractor")
    print("3. Integrate with MkDocs tags plugin")
    print("4. The masses have made their language known!")

if __name__ == "__main__":
    main()