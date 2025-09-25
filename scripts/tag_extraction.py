#!/usr/bin/env python3
"""
Tag extraction classes for enhanced content analysis.
Contains EnhancedTagExtractor, ChunkScorer, DomainVocabulary, and PatternMatcher.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

# Import from our new nlp_core module
from nlp_core import MODEL_TYPE, NLP_CONFIG, nlp
from spacy.tokens import Doc, Token


class DomainVocabulary:
    """Manages domain-specific vocabulary for political/philosophical content."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.vocabulary_terms = set()
        self.category_terms = {}

        # Load domain vocabulary from config
        domain_vocab = config.get("tags", {}).get("domain_vocabulary", {})
        for category, terms in domain_vocab.items():
            self.category_terms[category] = {term.lower() for term in terms}
            self.vocabulary_terms.update(self.category_terms[category])

    def contains_domain_term(self, text: str) -> bool:
        """Check if text contains any domain-specific terms."""
        text_lower = text.lower()
        return any(term in text_lower for term in self.vocabulary_terms)

    def get_domain_categories(self, text: str) -> List[str]:
        """Get categories that match terms in the text."""
        text_lower = text.lower()
        matching_categories = []
        for category, terms in self.category_terms.items():
            if any(term in text_lower for term in terms):
                matching_categories.append(category)
        return matching_categories

    def count_domain_terms(self, text: str) -> int:
        """Count number of domain terms in text."""
        text_lower = text.lower()
        return sum(1 for term in self.vocabulary_terms if term in text_lower)


class PatternMatcher:
    """Detects domain-specific patterns in text."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.patterns = config.get("patterns", {})
        self.compiled_patterns = {}

        # Compile regex patterns
        for pattern_type, patterns in self.patterns.items():
            self.compiled_patterns[pattern_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]

    def extract_quoted_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases from quotes."""
        phrases = []
        for pattern in self.compiled_patterns.get("quote_patterns", []):
            matches = pattern.findall(text)
            phrases.extend(matches)
        return [phrase.strip() for phrase in phrases if len(phrase.strip()) > 10]

    def extract_theory_patterns(self, text: str) -> List[str]:
        """Extract theory-related patterns like 'theory of X' or 'X theory'."""
        patterns = []
        for pattern in self.compiled_patterns.get("theory_patterns", []):
            matches = pattern.findall(text)
            patterns.extend(matches)
        return [match.strip() for match in patterns if len(match.strip()) > 5]

    def extract_relationship_patterns(self, text: str) -> List[str]:
        """Extract conceptual relationship patterns."""
        relationships = []
        for pattern in self.compiled_patterns.get("relationship_patterns", []):
            matches = pattern.findall(text)
            relationships.extend(matches)
        return [match.strip() for match in relationships if len(match.strip()) > 8]


class ChunkScorer:
    """Scores text chunks for relevance using multiple factors."""

    def __init__(self, config: Dict[str, Any], domain_vocab: DomainVocabulary) -> None:
        self.config = config
        self.weights = config.get("tags", {}).get("weights", {})
        self.domain_vocab = domain_vocab
        self.skip_phrases = {
            phrase.lower()
            for phrase in config.get("content_filters", {}).get("skip_phrases", [])
        }

        # SEMANTIC SIMILARITY POWER! Cache domain concept vectors
        self.domain_concept_docs = {}
        if MODEL_TYPE in ["transformer", "medium"]:
            print("⚡ Initializing semantic similarity scoring...")
            # Pre-process domain concepts for similarity comparison
            for _category, terms in domain_vocab.category_terms.items():
                for term in terms:
                    self.domain_concept_docs[term] = nlp(term)

    def score_chunk(
        self, chunk_text: str, chunk_tokens: List[Token], doc: Doc
    ) -> float:
        """Calculate relevance score for a text chunk with SEMANTIC POWER!"""
        score = 0.0
        text_lower = chunk_text.lower().strip()

        # Skip if it's a generic phrase
        if text_lower in self.skip_phrases:
            return 0.0

        # Base score from number of words
        word_count = len(chunk_tokens)
        score += word_count * self.weights.get("length_bonus", 0.1)

        # Multi-word bonus
        if word_count > 1:
            score += self.weights.get("multi_word", 1.2)

        # 🚀 SEMANTIC SIMILARITY SCORING - THE NUCLEAR OPTION!
        if MODEL_TYPE in ["transformer", "medium"]:
            semantic_score = self.calculate_semantic_similarity(chunk_text)
            if semantic_score > 0:
                score += semantic_score
                # Extra boost if ALSO contains explicit domain terms
                if self.domain_vocab.contains_domain_term(chunk_text):
                    score += 1.0  # Synergy bonus!

        # Domain vocabulary bonus (still useful even with semantic scoring)
        if self.domain_vocab.contains_domain_term(chunk_text):
            score += self.weights.get("domain_term", 2.5)
            # Extra bonus for multiple domain terms
            domain_count = self.domain_vocab.count_domain_terms(chunk_text)
            if domain_count > 1:
                score += domain_count * 0.5

        # Named entity bonus
        if any(token.ent_type_ for token in chunk_tokens):
            score += self.weights.get("named_entity", 2.0)

        # Proper noun bonus
        if any(token.pos_ == "PROPN" for token in chunk_tokens):
            score += self.weights.get("proper_noun", 1.5)

        # Check if appears in quotes (important concepts often quoted)
        for sent in doc.sents:
            if chunk_text in sent.text and ('"' in sent.text or "'" in sent.text):
                score += self.weights.get("quoted_phrase", 1.8)
                break

        # Capitalization indicates importance
        if any(token.is_upper or token.is_title for token in chunk_tokens):
            score += 0.5

        # Penalize very common words
        common_words = {"people", "thing", "way", "time", "year", "day", "place"}
        if any(token.text.lower() in common_words for token in chunk_tokens):
            score -= 1.0

        return max(0.0, score)

    def calculate_semantic_similarity(self, text: str) -> float:
        """Calculate semantic similarity to domain concepts using LARGE/MEDIUM vector power!"""
        if MODEL_TYPE in ["small", "transformer"] or not self.domain_concept_docs:
            return 0.0  # No semantic similarity for small/transformer models (no word vectors)

        try:
            # Process the text
            text_doc = nlp(text)

            # Find maximum similarity to any domain concept
            max_similarity = 0.0
            best_match = None

            for concept, concept_doc in self.domain_concept_docs.items():
                # Calculate cosine similarity between vectors
                if text_doc.has_vector and concept_doc.has_vector:
                    similarity = text_doc.similarity(concept_doc)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_match = concept

            # Log high-similarity matches for debugging
            if max_similarity > 0.7 and best_match:
                print(
                    f"    🎯 Semantic match: '{text}' ≈ '{best_match}' (similarity: {max_similarity:.2f})"
                )

            # Scale similarity score (0-1 range to 0-5 point bonus)
            return max_similarity * 5.0

        except Exception as e:
            # Graceful degradation if similarity calculation fails
            print(f"⚠️  Semantic similarity failed for '{text}': {e}")
            return 0.0


class EnhancedTagExtractor:
    """Advanced tag extraction using domain knowledge and multiple strategies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or NLP_CONFIG
        self.domain_vocab = DomainVocabulary(self.config)
        self.pattern_matcher = PatternMatcher(self.config)
        self.chunk_scorer = ChunkScorer(self.config, self.domain_vocab)

        # Tag extraction settings
        tag_config = self.config.get("tags", {})
        self.min_chunk_words = tag_config.get("min_chunk_words", 2)
        self.max_chunk_words = tag_config.get("max_chunk_words", 5)
        self.max_tags = tag_config.get("max_tags", 10)
        self.min_concept_length = self.config.get("content_filters", {}).get(
            "min_concept_length", 8
        )

    def extract_noun_chunks(self, doc: Doc) -> List[Tuple[str, float]]:
        """Extract and score noun chunks."""
        scored_chunks = []
        seen_normalized = set()

        for chunk in doc.noun_chunks:
            # Get clean tokens
            chunk_tokens = [t for t in chunk if not t.is_punct and not t.is_space]
            word_count = len(chunk_tokens)

            # Filter by length
            if word_count < self.min_chunk_words or word_count > self.max_chunk_words:
                continue

            # Skip if too many stop words
            stop_count = sum(1 for t in chunk_tokens if t.is_stop)
            if stop_count > word_count / 2:
                continue

            chunk_text = chunk.text.strip()

            # Skip if too short
            if len(chunk_text) < self.min_concept_length:
                continue

            # Normalize for deduplication
            normalized = " ".join([t.lemma_.lower() for t in chunk_tokens])
            if normalized in seen_normalized:
                continue
            seen_normalized.add(normalized)

            # Score the chunk
            score = self.chunk_scorer.score_chunk(chunk_text, chunk_tokens, doc)
            if score > 0:
                scored_chunks.append((chunk_text, score))

        return scored_chunks

    def extract_quoted_phrases(self, text: str) -> List[Tuple[str, float]]:
        """Extract meaningful quoted phrases."""
        quoted_phrases = self.pattern_matcher.extract_quoted_phrases(text)
        scored_phrases = []

        for phrase in quoted_phrases:
            if len(phrase) >= self.min_concept_length:
                # Score quoted phrases highly since they're often key concepts
                score = 3.0
                if self.domain_vocab.contains_domain_term(phrase):
                    score += 2.0
                scored_phrases.append((phrase, score))

        return scored_phrases

    def extract_theory_patterns(self, text: str) -> List[Tuple[str, float]]:
        """Extract theory and conceptual patterns."""
        theory_patterns = self.pattern_matcher.extract_theory_patterns(text)
        relationship_patterns = self.pattern_matcher.extract_relationship_patterns(text)

        scored_patterns = []

        for pattern in theory_patterns + relationship_patterns:
            if len(pattern) >= self.min_concept_length:
                score = 2.0
                if self.domain_vocab.contains_domain_term(pattern):
                    score += 1.5
                scored_patterns.append((pattern, score))

        return scored_patterns

    def extract_domain_phrases(self, doc: Doc) -> List[Tuple[str, float]]:
        """Extract phrases that contain domain-specific terms."""
        scored_phrases = []

        # Look for sentences containing domain terms
        for sent in doc.sents:
            sent_text = sent.text.strip()
            if (
                self.domain_vocab.contains_domain_term(sent_text)
                and len(sent_text.split()) <= self.max_chunk_words
                and len(sent_text) >= self.min_concept_length
            ):
                score = 2.5 + self.domain_vocab.count_domain_terms(sent_text) * 0.5
                scored_phrases.append((sent_text, score))

        return scored_phrases

    def extract_enhanced_tags(
        self, text: str, max_tags: Optional[int] = None
    ) -> List[str]:
        """
        Extract enhanced tags using multiple strategies.

        Args:
            text: Text to extract tags from
            max_tags: Maximum number of tags (uses config default if None)

        Returns:
            List of enhanced concept tags
        """
        if max_tags is None:
            max_tags = self.max_tags

        # Process text with SpaCy
        doc = nlp(text[:2000])  # Limit for performance

        all_scored_chunks = []
        seen_normalized = set()

        # Strategy 1: Enhanced noun chunks
        noun_chunks = self.extract_noun_chunks(doc)
        all_scored_chunks.extend(noun_chunks)

        # Strategy 2: Quoted phrases
        quoted_phrases = self.extract_quoted_phrases(text)
        all_scored_chunks.extend(quoted_phrases)

        # Strategy 3: Theory and pattern matching
        theory_patterns = self.extract_theory_patterns(text)
        all_scored_chunks.extend(theory_patterns)

        # Strategy 4: Domain-specific phrases
        domain_phrases = self.extract_domain_phrases(doc)
        all_scored_chunks.extend(domain_phrases)

        # Deduplicate and normalize
        final_chunks = []
        for chunk_text, score in all_scored_chunks:
            normalized = chunk_text.lower().strip()
            if (
                normalized not in seen_normalized
                and len(normalized) >= self.min_concept_length
            ):
                final_chunks.append((chunk_text, score))
                seen_normalized.add(normalized)

        # Sort by score and return top N
        final_chunks.sort(key=lambda x: x[1], reverse=True)
        return [text for text, _ in final_chunks[:max_tags]]


def extract_concept_tags(
    doc: Doc, max_tags: int = 10, min_words: int = 2, max_words: int = 5
) -> List[str]:
    """
    Extract meaningful concept phrases as tags using noun chunks.

    Args:
        doc: SpaCy Doc object
        max_tags: Maximum number of tags to return
        min_words: Minimum words in a valid tag
        max_words: Maximum words in a valid tag

    Returns:
        List of concept phrase tags
    """
    scored_chunks = []
    seen_normalized = set()

    for chunk in doc.noun_chunks:
        # Get clean tokens (no punct/space)
        chunk_tokens = [t for t in chunk if not t.is_punct and not t.is_space]
        word_count = len(chunk_tokens)

        # Filter by length
        if word_count < min_words or word_count > max_words:
            continue

        # Skip if too many stop words
        stop_count = sum(1 for t in chunk_tokens if t.is_stop)
        if stop_count > word_count / 2:
            continue

        # Normalize for deduplication
        normalized = " ".join([t.lemma_.lower() for t in chunk_tokens])
        if normalized in seen_normalized:
            continue
        seen_normalized.add(normalized)

        # Score the chunk
        score = 0

        # Prefer multi-word concepts
        score += word_count * 2

        # Boost if contains named entities
        if any(token.ent_type_ for token in chunk):
            score += 3

        # Boost if contains proper nouns
        if any(token.pos_ == "PROPN" for token in chunk):
            score += 2

        # Boost if not all lowercase (suggests importance)
        if any(token.is_upper or token.is_title for token in chunk):
            score += 1

        # Penalize if very common (appears in many documents)
        # This would need corpus analysis in production
        common_words = {"people", "thing", "way", "time", "year", "day"}
        if any(t.text.lower() in common_words for t in chunk_tokens):
            score -= 2

        # Store with score
        scored_chunks.append((chunk.text.strip(), score))

    # Sort by score and return top N
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return [text for text, _ in scored_chunks[:max_tags]]
