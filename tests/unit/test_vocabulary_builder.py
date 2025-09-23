#!/usr/bin/env python3
"""
Test Suite for Revolutionary Vocabulary Builder
Testing the dialectical synthesis of vocabulary extraction tools
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from typing import Dict, List, Set

# Import the module we're about to create (TDD style - it doesn't exist yet!)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))


class TestPoliticalVocabularyExtractor:
    """Test extraction of political and philosophical vocabulary from corpus"""

    @pytest.fixture
    def sample_marxist_text(self):
        """Sample text with clear Marxist theoretical content"""
        return """
        The fundamental contradiction of capitalism lies in the social nature of
        production versus the private appropriation of surplus value. The working class,
        through their collective labor power, creates all value but the bourgeoisie
        controls the means of production. This dialectical materialism reveals how
        class struggle is the motor of historical change. The proletariat must develop
        revolutionary consciousness to overthrow the capitalist mode of production.
        """

    @pytest.fixture
    def sample_philosophical_text(self):
        """Sample text with philosophical content"""
        return """
        The question of consciousness and material conditions forms the basis of
        epistemological inquiry. Through dialectical reasoning, we can understand
        the synthesis that emerges from thesis and antithesis. The phenomenology
        of revolutionary praxis requires both theoretical understanding and practical
        application in concrete historical circumstances.
        """

    def test_extract_marxist_vocabulary(self, sample_marxist_text):
        """Test extraction of Marxist theoretical terms"""
        from vocabulary_builder import PoliticalVocabularyExtractor

        extractor = PoliticalVocabularyExtractor()
        vocab = extractor.extract_marxist_terms(sample_marxist_text)

        # Should identify key Marxist concepts
        assert 'class struggle' in vocab
        assert 'means of production' in vocab
        assert 'surplus value' in vocab
        assert 'working class' in vocab
        assert 'proletariat' in vocab
        assert 'bourgeoisie' in vocab
        assert 'dialectical materialism' in vocab
        assert 'revolutionary consciousness' in vocab

    def test_extract_philosophical_vocabulary(self, sample_philosophical_text):
        """Test extraction of philosophical terms"""
        from vocabulary_builder import PoliticalVocabularyExtractor

        extractor = PoliticalVocabularyExtractor()
        vocab = extractor.extract_philosophical_terms(sample_philosophical_text)

        assert 'consciousness' in vocab
        assert 'material conditions' in vocab
        assert 'dialectical reasoning' in vocab
        assert 'thesis' in vocab
        assert 'antithesis' in vocab
        assert 'synthesis' in vocab
        assert 'praxis' in vocab

    def test_pattern_based_extraction(self):
        """Test regex pattern-based extraction for political concepts"""
        from vocabulary_builder import PoliticalVocabularyExtractor

        text = """
        The vanguard party must engage in mass work among the proletarian base.
        Democratic centralism ensures party discipline while maintaining internal debate.
        The national question intersects with class analysis in settler colonial contexts.
        """

        extractor = PoliticalVocabularyExtractor()
        patterns = extractor.extract_by_patterns(text)

        assert 'organizing' in patterns
        assert 'vanguard party' in patterns['organizing']
        assert 'mass work' in patterns['organizing']
        assert 'democratic centralism' in patterns['organizing']

    def test_vocabulary_scoring(self):
        """Test that terms are scored by relevance and frequency"""
        from vocabulary_builder import PoliticalVocabularyExtractor

        text = """
        Class struggle class struggle class struggle. The means of production
        must be seized. Class struggle defines history. Capitalism creates its
        own contradictions through class struggle.
        """

        extractor = PoliticalVocabularyExtractor()
        scored_vocab = extractor.extract_and_score(text)

        # 'class struggle' should score highest due to frequency
        assert scored_vocab[0][0] == 'class struggle'
        assert scored_vocab[0][1] > 3  # mentioned 5 times


class TestVocabularyBuilder:
    """Test the main vocabulary builder that combines all extraction methods"""

    @pytest.fixture
    def sample_threads(self):
        """Sample thread data matching actual corpus structure"""
        return [
            {
                "thread_id": "1",
                "word_count": 500,
                "smushed_text": """The working class must understand that capitalism
                creates the conditions for its own destruction through internal contradictions.
                The bourgeoisie cannot resolve these contradictions."""
            },
            {
                "thread_id": "2",
                "word_count": 300,
                "smushed_text": """Settler colonialism operates through different mechanisms
                than traditional colonialism. The elimination of the native is central to
                settler colonial projects."""
            }
        ]

    def test_build_vocabulary_from_corpus(self, sample_threads, tmp_path):
        """Test building complete vocabulary from corpus"""
        from vocabulary_builder import VocabularyBuilder

        # Write sample data
        threads_file = tmp_path / "threads.json"
        threads_file.write_text(json.dumps({"threads": sample_threads}))

        builder = VocabularyBuilder()
        vocabulary = builder.build_from_corpus(threads_file)

        assert 'marxism' in vocabulary
        assert 'colonialism' in vocabulary
        assert len(vocabulary['marxism']['terms']) > 0
        assert len(vocabulary['colonialism']['terms']) > 0

    def test_generate_yaml_vocabulary(self, tmp_path):
        """Test YAML vocabulary generation with proper structure"""
        from vocabulary_builder import VocabularyBuilder

        builder = VocabularyBuilder()
        vocab_data = {
            'marxism': {
                'terms': ['class struggle', 'means of production', 'surplus value'],
                'patterns': [r'\bclass\s+\w+', r'\w+\s+of\s+production'],
                'score': 0.95
            }
        }

        output_file = tmp_path / "vocabulary.yaml"
        builder.generate_yaml(vocab_data, output_file)

        assert output_file.exists()
        loaded = yaml.safe_load(output_file.read_text())
        assert 'marxism' in loaded
        assert 'class struggle' in loaded['marxism']['terms']

    def test_merge_vocabularies(self):
        """Test merging vocabularies from different extractors"""
        from vocabulary_builder import VocabularyBuilder

        vocab1 = {
            'marxism': {'terms': ['class struggle', 'proletariat'], 'score': 0.8}
        }
        vocab2 = {
            'marxism': {'terms': ['bourgeoisie', 'proletariat'], 'score': 0.7},
            'philosophy': {'terms': ['dialectics', 'materialism'], 'score': 0.6}
        }

        builder = VocabularyBuilder()
        merged = builder.merge_vocabularies([vocab1, vocab2])

        # Should combine terms and average scores
        assert 'marxism' in merged
        assert 'philosophy' in merged
        assert len(merged['marxism']['terms']) == 3  # Combined unique terms
        assert merged['marxism']['score'] == 0.75  # Average of 0.8 and 0.7

    def test_generate_term_variations(self):
        """Test generation of term variations (plural, verb forms, etc.)"""
        from vocabulary_builder import VocabularyBuilder

        builder = VocabularyBuilder()
        variations = builder.generate_variations('revolutionary')

        assert 'revolutionary' in variations
        assert 'revolutionaries' in variations
        assert 'revolution' in variations
        assert 'revolutionize' in variations

    def test_filter_quality_terms(self):
        """Test filtering of low-quality or common terms"""
        from vocabulary_builder import VocabularyBuilder

        builder = VocabularyBuilder()
        terms = ['the', 'and', 'class struggle', 'of', 'means of production', 'it']

        filtered = builder.filter_quality_terms(terms)

        assert 'the' not in filtered
        assert 'and' not in filtered
        assert 'it' not in filtered
        assert 'class struggle' in filtered
        assert 'means of production' in filtered


class TestThemeClassifierEnhancements:
    """Test enhanced theme classification features to be integrated"""

    @pytest.fixture
    def enhanced_classifier(self):
        """Mock enhanced classifier with new features"""
        from theme_classifier import ThemeClassifier
        return ThemeClassifier()

    def test_pattern_based_classification(self, enhanced_classifier):
        """Test classification using political patterns"""
        text = """
        The vanguard party must maintain democratic centralism while engaging
        in mass work among the proletarian base. This is essential for
        revolutionary organization.
        """

        themes = enhanced_classifier.classify_with_patterns(text)

        assert 'organizing' in themes
        assert 'marxism' in themes
        assert enhanced_classifier.confidence_scores['organizing'] > 0.7

    def test_multi_theme_detection(self, enhanced_classifier):
        """Test detection of multiple intersecting themes"""
        text = """
        The settler colonial state reproduces capitalist relations through
        racial hierarchy. Class struggle in this context must account for
        the national question and indigenous sovereignty.
        """

        themes = enhanced_classifier.classify_with_patterns(text)

        assert 'colonialism' in themes
        assert 'marxism' in themes
        assert 'race' in themes
        assert len(themes) >= 3

    def test_confidence_scoring(self, enhanced_classifier):
        """Test confidence scoring for theme assignments"""
        weak_text = "Maybe something about class or whatever"
        strong_text = "Class struggle is the motor of history. The proletariat must seize the means of production."

        weak_themes = enhanced_classifier.classify_with_patterns(weak_text)
        strong_themes = enhanced_classifier.classify_with_patterns(strong_text)

        # Strong text should have higher confidence
        assert enhanced_classifier.confidence_scores.get('marxism', 0) < 0.3  # Weak

        enhanced_classifier.classify_with_patterns(strong_text)
        assert enhanced_classifier.confidence_scores.get('marxism', 0) > 0.8  # Strong

    def test_vocabulary_integration(self, enhanced_classifier, tmp_path):
        """Test integration with vocabulary builder output"""
        vocab_file = tmp_path / "vocabulary.yaml"
        vocab_data = {
            'marxism': {
                'terms': ['class struggle', 'proletariat', 'bourgeoisie'],
                'patterns': [r'\bclass\s+\w+']
            }
        }
        vocab_file.write_text(yaml.dump(vocab_data))

        enhanced_classifier.load_vocabulary(vocab_file)

        text = "The proletariat and bourgeoisie are locked in class struggle"
        themes = enhanced_classifier.classify_with_patterns(text)

        assert 'marxism' in themes
        # Should match all three terms from vocabulary
        assert enhanced_classifier.matched_terms['marxism'] == 3


class TestIntegration:
    """Integration tests for the complete enhanced pipeline"""

    def test_full_pipeline_with_vocabulary(self, tmp_path):
        """Test the complete pipeline with vocabulary-enhanced classification"""
        from vocabulary_builder import VocabularyBuilder
        from theme_classifier import ThemeClassifier

        # Sample corpus
        threads = [
            {"thread_id": "1", "smushed_text": "The dictatorship of the proletariat is necessary for the transition to communism."},
            {"thread_id": "2", "smushed_text": "Dialectical materialism provides the philosophical foundation for revolutionary praxis."}
        ]

        threads_file = tmp_path / "threads.json"
        threads_file.write_text(json.dumps({"threads": threads}))

        # Build vocabulary
        builder = VocabularyBuilder()
        vocabulary = builder.build_from_corpus(threads_file)
        vocab_file = tmp_path / "vocabulary.yaml"
        builder.generate_yaml(vocabulary, vocab_file)

        # Classify with enhanced classifier
        classifier = ThemeClassifier()
        classifier.load_vocabulary(vocab_file)

        for thread in threads:
            themes = classifier.classify_with_patterns(thread['smushed_text'])
            assert len(themes) > 0
            assert 'marxism' in themes or 'philosophy' in themes

    def test_backwards_compatibility(self):
        """Ensure enhanced features don't break existing functionality"""
        from theme_classifier import ThemeClassifier

        # Should still work with manual themes file
        classifier = ThemeClassifier()

        # Method should return tuple with themes and confidence
        themes, confidence = classifier.classify_thread({"smushed_text": "Some political text"})
        assert isinstance(themes, list)
        assert isinstance(confidence, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])