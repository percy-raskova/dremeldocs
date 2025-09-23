#!/usr/bin/env python3
"""
SpaCy-enhanced text processing utilities for generating titles and descriptions.
Provides linguistic-aware text extraction for better frontmatter generation.
"""

import re
import yaml
from typing import Optional, List, Tuple, Dict, Set
from pathlib import Path
import spacy
from spacy.tokens import Doc, Span

# Load SpaCy model once at module level for efficiency
# NUCLEAR FUSION MODE: Using LARGE model for MAXIMUM VOCABULARY POWER!
try:
    # First try the LARGE model for MASSIVE vocabulary and vectors
    nlp = spacy.load("en_core_web_lg")
    print("🚀💥 LARGE MODEL LOADED - MAXIMUM VOCABULARY POWER ENGAGED!")
    MODEL_TYPE = "large"
except OSError:
    try:
        # Fallback to transformer for contextual understanding
        nlp = spacy.load("en_core_web_trf")
        print("🚀 TRANSFORMER MODEL LOADED - CONTEXTUAL POWER ENGAGED!")
        MODEL_TYPE = "transformer"
    except OSError:
        try:
            # Fallback to medium if large/transformer not available
            nlp = spacy.load("en_core_web_md")
            print("💪 Medium model loaded with word vectors")
            MODEL_TYPE = "medium"
        except OSError:
            try:
                # Final fallback to small model
                nlp = spacy.load("en_core_web_sm")
                print("📦 Small model loaded - basic functionality")
                MODEL_TYPE = "small"
            except OSError:
                print("⚠️  No SpaCy model found. Please install one with:")
                print("    # For MAXIMUM VOCABULARY (recommended):")
                print("    uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl")
                print("    # Or for contextual understanding:")
                print("    uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0-py3-none-any.whl")
                import sys
                sys.exit(1)

# Keep all components enabled for full functionality

# Load NLP configuration
def load_nlp_config() -> Dict:
    """Load NLP configuration from YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "nlp_settings.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Fallback configuration if file doesn't exist
        return {
            'tags': {
                'min_chunk_words': 2,
                'max_chunk_words': 5,
                'max_tags': 10,
                'weights': {
                    'domain_term': 2.5,
                    'named_entity': 2.0,
                    'quoted_phrase': 1.8,
                    'proper_noun': 1.5,
                    'multi_word': 1.2,
                    'length_bonus': 0.1
                },
                'domain_vocabulary': {'political_theory': [], 'philosophy': []}
            },
            'content_filters': {
                'skip_phrases': ['the people', 'the way', 'the thing'],
                'min_concept_length': 8
            },
            'patterns': {
                'quote_patterns': [r'"([^"]{10,100})"', r"'([^']{10,100})'"],
                'theory_patterns': [r"theory of \w+", r"\w+ theory"],
                'relationship_patterns': [r"\w+ is \w+", r"\w+ means \w+"]
            }
        }

# Global configuration
NLP_CONFIG = load_nlp_config()


class DomainVocabulary:
    """Manages domain-specific vocabulary for political/philosophical content."""

    def __init__(self, config: Dict):
        self.vocabulary_terms = set()
        self.category_terms = {}

        # Load domain vocabulary from config
        domain_vocab = config.get('tags', {}).get('domain_vocabulary', {})
        for category, terms in domain_vocab.items():
            self.category_terms[category] = set(term.lower() for term in terms)
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

    def __init__(self, config: Dict):
        self.patterns = config.get('patterns', {})
        self.compiled_patterns = {}

        # Compile regex patterns
        for pattern_type, patterns in self.patterns.items():
            self.compiled_patterns[pattern_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]

    def extract_quoted_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases from quotes."""
        phrases = []
        for pattern in self.compiled_patterns.get('quote_patterns', []):
            matches = pattern.findall(text)
            phrases.extend(matches)
        return [phrase.strip() for phrase in phrases if len(phrase.strip()) > 10]

    def extract_theory_patterns(self, text: str) -> List[str]:
        """Extract theory-related patterns like 'theory of X' or 'X theory'."""
        patterns = []
        for pattern in self.compiled_patterns.get('theory_patterns', []):
            matches = pattern.findall(text)
            patterns.extend(matches)
        return [match.strip() for match in patterns if len(match.strip()) > 5]

    def extract_relationship_patterns(self, text: str) -> List[str]:
        """Extract conceptual relationship patterns."""
        relationships = []
        for pattern in self.compiled_patterns.get('relationship_patterns', []):
            matches = pattern.findall(text)
            relationships.extend(matches)
        return [match.strip() for match in relationships if len(match.strip()) > 8]


class ChunkScorer:
    """Scores text chunks for relevance using multiple factors."""

    def __init__(self, config: Dict, domain_vocab: DomainVocabulary):
        self.config = config
        self.weights = config.get('tags', {}).get('weights', {})
        self.domain_vocab = domain_vocab
        self.skip_phrases = set(
            phrase.lower() for phrase in
            config.get('content_filters', {}).get('skip_phrases', [])
        )

        # SEMANTIC SIMILARITY POWER! Cache domain concept vectors
        self.domain_concept_docs = {}
        if MODEL_TYPE in ["transformer", "medium"]:
            print("⚡ Initializing semantic similarity scoring...")
            # Pre-process domain concepts for similarity comparison
            for category, terms in domain_vocab.category_terms.items():
                for term in terms:
                    self.domain_concept_docs[term] = nlp(term)

    def score_chunk(self, chunk_text: str, chunk_tokens: List, doc: Doc) -> float:
        """Calculate relevance score for a text chunk with SEMANTIC POWER!"""
        score = 0.0
        text_lower = chunk_text.lower().strip()

        # Skip if it's a generic phrase
        if text_lower in self.skip_phrases:
            return 0.0

        # Base score from number of words
        word_count = len(chunk_tokens)
        score += word_count * self.weights.get('length_bonus', 0.1)

        # Multi-word bonus
        if word_count > 1:
            score += self.weights.get('multi_word', 1.2)

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
            score += self.weights.get('domain_term', 2.5)
            # Extra bonus for multiple domain terms
            domain_count = self.domain_vocab.count_domain_terms(chunk_text)
            if domain_count > 1:
                score += domain_count * 0.5

        # Named entity bonus
        if any(token.ent_type_ for token in chunk_tokens):
            score += self.weights.get('named_entity', 2.0)

        # Proper noun bonus
        if any(token.pos_ == 'PROPN' for token in chunk_tokens):
            score += self.weights.get('proper_noun', 1.5)

        # Check if appears in quotes (important concepts often quoted)
        for sent in doc.sents:
            if chunk_text in sent.text and ('"' in sent.text or "'" in sent.text):
                score += self.weights.get('quoted_phrase', 1.8)
                break

        # Capitalization indicates importance
        if any(token.is_upper or token.is_title for token in chunk_tokens):
            score += 0.5

        # Penalize very common words
        common_words = {'people', 'thing', 'way', 'time', 'year', 'day', 'place'}
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
                print(f"    🎯 Semantic match: '{text}' ≈ '{best_match}' (similarity: {max_similarity:.2f})")

            # Scale similarity score (0-1 range to 0-5 point bonus)
            return max_similarity * 5.0

        except Exception as e:
            # Graceful degradation if similarity calculation fails
            print(f"⚠️  Semantic similarity failed for '{text}': {e}")
            return 0.0


class EnhancedTagExtractor:
    """Advanced tag extraction using domain knowledge and multiple strategies."""

    def __init__(self, config: Dict = None):
        self.config = config or NLP_CONFIG
        self.domain_vocab = DomainVocabulary(self.config)
        self.pattern_matcher = PatternMatcher(self.config)
        self.chunk_scorer = ChunkScorer(self.config, self.domain_vocab)

        # Tag extraction settings
        tag_config = self.config.get('tags', {})
        self.min_chunk_words = tag_config.get('min_chunk_words', 2)
        self.max_chunk_words = tag_config.get('max_chunk_words', 5)
        self.max_tags = tag_config.get('max_tags', 10)
        self.min_concept_length = self.config.get('content_filters', {}).get('min_concept_length', 8)

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
            normalized = ' '.join([t.lemma_.lower() for t in chunk_tokens])
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
            if (self.domain_vocab.contains_domain_term(sent_text) and
                len(sent_text.split()) <= self.max_chunk_words and
                len(sent_text) >= self.min_concept_length):

                score = 2.5 + self.domain_vocab.count_domain_terms(sent_text) * 0.5
                scored_phrases.append((sent_text, score))

        return scored_phrases

    def extract_enhanced_tags(self, text: str, max_tags: int = None) -> List[str]:
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
            if normalized not in seen_normalized and len(normalized) >= self.min_concept_length:
                final_chunks.append((chunk_text, score))
                seen_normalized.add(normalized)

        # Sort by score and return top N
        final_chunks.sort(key=lambda x: x[1], reverse=True)
        return [text for text, _ in final_chunks[:max_tags]]


def skip_common_starters(doc: Doc, min_chunk_words: int = 2) -> Optional[str]:
    """
    Skip common starting words (pronouns, articles) and find first meaningful content.

    Args:
        doc: SpaCy Doc object
        min_chunk_words: Minimum words in a meaningful chunk

    Returns:
        First meaningful phrase text, or None if not found
    """
    SKIP_WORDS = {
        # Pronouns
        'i', 'we', 'you', 'they', 'it', 'he', 'she', 'that', 'this', 'these', 'those',
        # Articles
        'the', 'a', 'an',
        # Common verbs that don't add meaning alone
        'is', 'are', 'was', 'were', 'have', 'has', 'had',
        # Other common starters
        'so', 'but', 'and', 'or', 'if', 'when', 'while',
        # Contractions (both forms)
        "that's", "it's", "there's", "here's", "what's", "who's",
        "thats", "its", "whats", "whos", "'s"
    }

    for sent in doc.sents:
        sent_text = sent.text.strip()

        # Look for quoted phrases (often important)
        if '"' in sent_text or "'" in sent_text:
            import re
            # Find quoted content
            quoted_pattern = r'["\']([^"\']+)["\']'
            matches = re.findall(quoted_pattern, sent_text)
            for match in matches:
                if len(match.split()) >= min_chunk_words:
                    return match

        # Get meaningful tokens
        tokens = [t for t in sent if not t.is_punct and not t.is_space]
        if not tokens:
            continue

        # Check if starts with skip word (including contractions)
        first_word_lower = tokens[0].text.lower()

        # If not a skip word, look for substantial content
        if first_word_lower not in SKIP_WORDS:
            # Try noun chunks first
            for chunk in sent.noun_chunks:
                chunk_text = chunk.text.strip()
                # Ensure we get complete phrases
                if len(chunk_text.split()) >= min_chunk_words and len(chunk_text) > 15:
                    return chunk_text

            # Return sentence if meaningful
            if len(sent_text) > 20 and not sent_text.lower().startswith(tuple(SKIP_WORDS)):
                return sent_text[:100]  # Cap length but keep meaningful

        # First word is skip word - find content after it
        # Look for the best noun chunk
        best_chunk = None
        best_score = 0

        for chunk in sent.noun_chunks:
            chunk_text = chunk.text.strip()
            chunk_words = chunk_text.split()

            # Score chunks
            score = len(chunk_words)
            # Boost for proper nouns
            if any(t.pos_ == 'PROPN' for t in chunk):
                score += 3
            # Boost for named entities
            if any(t.ent_type_ for t in chunk):
                score += 2

            if score > best_score and len(chunk_words) >= min_chunk_words:
                best_chunk = chunk_text
                best_score = score

        if best_chunk and len(best_chunk) > 10:
            return best_chunk

        # Try verb phrases with objects as fallback
        for token in sent:
            if token.pos_ == 'VERB' and token.dep_ == 'ROOT':
                # Get full verb phrase with modifiers and objects
                children = list(token.subtree)
                if len(children) >= min_chunk_words:
                    phrase_start = min(t.i for t in children)
                    phrase_end = max(t.i for t in children) + 1
                    phrase = doc[phrase_start:phrase_end]
                    phrase_text = ' '.join([t.text for t in phrase if not t.is_space])

                    # Clean up the phrase
                    phrase_text = phrase_text.strip()
                    # Remove leading skip words
                    for skip in SKIP_WORDS:
                        if phrase_text.lower().startswith(skip + ' '):
                            phrase_text = phrase_text[len(skip)+1:]
                            break

                    if len(phrase_text.split()) >= min_chunk_words and len(phrase_text) > 15:
                        return phrase_text

    return None


def extract_concept_tags(doc: Doc, max_tags: int = 10, min_words: int = 2, max_words: int = 5) -> List[str]:
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
        normalized = ' '.join([t.lemma_.lower() for t in chunk_tokens])
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
        if any(token.pos_ == 'PROPN' for token in chunk):
            score += 2

        # Boost if not all lowercase (suggests importance)
        if any(token.is_upper or token.is_title for token in chunk):
            score += 1

        # Penalize if very common (appears in many documents)
        # This would need corpus analysis in production
        common_words = {'people', 'thing', 'way', 'time', 'year', 'day'}
        if any(t.text.lower() in common_words for t in chunk_tokens):
            score -= 2

        # Store with score
        scored_chunks.append((chunk.text.strip(), score))

    # Sort by score and return top N
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return [text for text, _ in scored_chunks[:max_tags]]


def clean_social_text(doc: Doc) -> str:
    """
    Remove URLs, mentions, and hashtags using SpaCy token attributes.

    Args:
        doc: SpaCy Doc object

    Returns:
        Cleaned text without social media artifacts
    """
    cleaned_tokens = []

    for token in doc:
        # Skip URLs using SpaCy's built-in URL detection
        if token.like_url:
            continue

        # Skip social media mentions and hashtags
        if token.text.startswith(('@', '#')):
            continue

        # Skip standalone 'RT' (retweet indicator)
        if token.text.upper() == 'RT' and token.i == 0:
            continue

        cleaned_tokens.append(token.text)

    # Reconstruct with proper spacing
    cleaned = ' '.join(cleaned_tokens)

    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def extract_key_phrase(sent: Span) -> Optional[str]:
    """
    Extract the most important phrase from a sentence using dependency parsing.

    Args:
        sent: SpaCy Span representing a sentence

    Returns:
        Key phrase if found, None otherwise
    """
    # Look for the main subject (nsubj) or root verb's object
    subject = None
    root = None

    for token in sent:
        if token.dep_ == "ROOT":
            root = token
        if token.dep_ in ("nsubj", "nsubjpass"):
            subject = token

    # If we have a subject, try to expand it to its full noun chunk
    if subject:
        for chunk in sent.noun_chunks:
            if subject in chunk:
                return chunk.text

    # Otherwise, try to find the most important noun chunk
    noun_chunks = list(sent.noun_chunks)
    if noun_chunks:
        # Prefer longer, more descriptive chunks
        noun_chunks.sort(key=lambda x: len(x.text), reverse=True)
        return noun_chunks[0].text

    return None


def generate_title(text: str, max_length: int = 60) -> str:
    """
    Generate a title using SpaCy sentence segmentation and linguistic analysis.
    Now with smart starter skipping for better titles.

    Args:
        text: Raw text to generate title from
        max_length: Maximum character length for title

    Returns:
        Generated title string
    """
    if not text:
        return ""

    # Remove RT prefix if present
    if text.startswith('RT '):
        text = text[3:].lstrip()

    # Process with SpaCy (process more text for better context)
    doc = nlp(text[:2000])  # Increased from 1000 for better analysis

    # Strategy 1: Try smart starter skipping first
    meaningful_start = skip_common_starters(doc)
    if meaningful_start:
        # Clean and truncate if needed
        meaningful_start = meaningful_start.strip('.!?,;:')
        if len(meaningful_start) <= max_length:
            return meaningful_start
        # Truncate at word boundary
        return meaningful_start[:max_length].rsplit(' ', 1)[0] + '...'

    # Strategy 2: Fall back to original method with improvements
    # Clean social media artifacts first
    cleaned_full = clean_social_text(doc)

    # Re-process cleaned text to get better sentence segmentation
    doc_cleaned = nlp(cleaned_full)
    sentences = list(doc_cleaned.sents)

    if not sentences:
        # Fallback if no sentences detected
        return cleaned_full[:max_length].rsplit(' ', 1)[0] + ('...' if len(cleaned_full) > max_length else '')

    first_sent = sentences[0]
    first_text = first_sent.text.strip()

    # If first sentence is short enough, use it
    if len(first_text) <= max_length:
        # Remove trailing punctuation for titles
        first_text = first_text.rstrip('.!?,;:')
        return first_text

    # Try to extract the key phrase
    key_phrase = extract_key_phrase(first_sent)
    if key_phrase and len(key_phrase) <= max_length:
        return key_phrase

    # Fallback: truncate at word boundary
    truncated = first_text[:max_length].rsplit(' ', 1)[0]

    # Remove incomplete punctuation at end
    truncated = truncated.rstrip('.!?,;:')

    return truncated + '...'


def generate_description(text: str, max_length: int = 160) -> str:
    """
    Generate a description using multiple complete sentences when possible.

    Args:
        text: Raw text to generate description from
        max_length: Maximum character length for description

    Returns:
        Generated description string
    """
    if not text:
        return ""

    # Process with SpaCy (limit for efficiency)
    doc = nlp(text[:2000])

    # Get sentences
    sentences = list(doc.sents)
    if not sentences:
        # Fallback if no sentences detected
        return text[:max_length].rsplit(' ', 1)[0] + ('...' if len(text) > max_length else '')

    # Collect complete sentences up to max_length
    description_parts = []
    char_count = 0

    for sent in sentences[:3]:  # Consider up to 3 sentences
        cleaned = clean_social_text(sent.as_doc())

        # Skip very short sentences (likely fragments)
        if len(cleaned) < 10:
            continue

        # Check if adding this sentence would exceed limit
        space_needed = 1 if description_parts else 0  # Space between sentences
        if char_count + len(cleaned) + space_needed <= max_length:
            description_parts.append(cleaned)
            char_count += len(cleaned) + space_needed
        else:
            # If we haven't added anything yet, we need to truncate the first sentence
            if not description_parts:
                truncated = cleaned[:max_length].rsplit(' ', 1)[0]
                return truncated + '...'
            break

    if description_parts:
        return ' '.join(description_parts).strip()

    # Fallback: use first sentence truncated
    first_cleaned = clean_social_text(sentences[0].as_doc())
    if len(first_cleaned) <= max_length:
        return first_cleaned

    truncated = first_cleaned[:max_length].rsplit(' ', 1)[0]
    return truncated + '...'


def extract_entities(text: str, limit: int = 5) -> List[str]:
    """
    Extract meaningful tags from text using enhanced tag extraction.
    This function provides backward compatibility with the original interface
    but uses the new EnhancedTagExtractor for better results.

    Args:
        text: Text to extract entities from
        limit: Maximum number of entities to return

    Returns:
        List of entity/concept strings for use as tags
    """
    try:
        # Use the new enhanced extractor
        extractor = EnhancedTagExtractor()
        enhanced_tags = extractor.extract_enhanced_tags(text, max_tags=limit)

        if enhanced_tags:
            return enhanced_tags

    except Exception as e:
        # Fallback to original method if enhanced extraction fails
        print(f"⚠️  Enhanced extraction failed: {e}")
        print("Falling back to basic extraction...")

    # Fallback: Use the original basic method
    return extract_entities_basic(text, limit)


def extract_entities_basic(text: str, limit: int = 5) -> List[str]:
    """
    Original basic entity extraction method (kept as fallback).
    Extract meaningful tags from text using noun chunks and named entities.

    Args:
        text: Text to extract entities from
        limit: Maximum number of entities to return

    Returns:
        List of entity/concept strings for use as tags
    """
    # Process with full pipeline for better analysis
    doc = nlp(text[:2000])

    # Get concept tags from noun chunks (better for philosophical content)
    concept_tags = extract_concept_tags(doc, max_tags=limit * 2)  # Get extra for filtering

    # Also get traditional named entities
    traditional_entities = []
    seen = set()

    for ent in doc.ents:
        # Skip temporal/numeric entities
        if ent.label_ in ("DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"):
            continue

        # Normalize and deduplicate
        normalized = ent.text.strip().lower()
        if normalized not in seen and len(normalized) > 2:
            traditional_entities.append(ent.text.strip())
            seen.add(normalized)

    # Combine and deduplicate, preferring concept tags
    combined_tags = []
    seen_normalized = set()

    # Add concept tags first (higher priority)
    for tag in concept_tags:
        normalized = tag.lower()
        if normalized not in seen_normalized:
            combined_tags.append(tag)
            seen_normalized.add(normalized)
            if len(combined_tags) >= limit:
                return combined_tags

    # Add traditional entities if space remains
    for entity in traditional_entities:
        normalized = entity.lower()
        if normalized not in seen_normalized:
            combined_tags.append(entity)
            seen_normalized.add(normalized)
            if len(combined_tags) >= limit:
                return combined_tags

    return combined_tags


def calculate_reading_time(text: str) -> int:
    """
    Calculate reading time using SpaCy's tokenization for more accurate word count.

    Args:
        text: Text to calculate reading time for

    Returns:
        Estimated reading time in minutes
    """
    doc = nlp.make_doc(text)  # Fast tokenization only

    # Count only alphabetic tokens (exclude punctuation, symbols)
    word_count = sum(1 for token in doc if token.is_alpha)

    # Average reading speed: 225 words per minute
    return max(1, round(word_count / 225))


def format_frontmatter_value(value) -> str:
    """
    Properly format values for YAML frontmatter, escaping as needed.

    Args:
        value: Value to format (string, list, or other)

    Returns:
        Properly formatted string for YAML
    """
    if value is None:
        return '""'

    if isinstance(value, str):
        # Always quote strings for consistency and predictability
        # Replace inner double quotes with single quotes for better readability
        # Then escape any remaining quotes and backslashes
        value = value.replace('"', "'")
        escaped = value.replace('\\', '\\\\')
        return f'"{escaped}"'

    elif isinstance(value, list):
        if not value:
            return '[]'
        formatted_items = [format_frontmatter_value(item) for item in value]
        return '[' + ', '.join(formatted_items) + ']'

    elif isinstance(value, bool):
        return 'true' if value else 'false'

    else:
        return str(value)


# Filename generation functions for consistent naming
def parse_to_yyyymmdd(date_str) -> str:
    """
    Parse various date formats to YYYYMMDD format.

    Handles:
    - Twitter format: "Sat Apr 26 15:30:45 +0000 2025"
    - ISO format: "2025-04-26T15:30:45Z"
    - Date strings: "2025-04-26"
    - Datetime objects

    Args:
        date_str: Date string or datetime object to parse

    Returns:
        Date string in YYYYMMDD format
    """
    from datetime import datetime
    from dateutil import parser

    if not date_str:
        return "20250101"  # Default

    try:
        if isinstance(date_str, datetime):
            date_obj = date_str
        else:
            # Try flexible parsing
            date_obj = parser.parse(str(date_str))

        return date_obj.strftime('%Y%m%d')
    except:
        # Fallback to default
        return "20250101"


def generate_brief_title(text: str, max_length: int = 50) -> str:
    """
    Generate a brief, filename-safe title using SpaCy NLP.

    Process:
    1. Use SpaCy to extract meaningful title from text
    2. Convert to filename-safe format
    3. Replace spaces with underscores
    4. Ensure lowercase for consistency

    Args:
        text: Source text
        max_length: Maximum title length

    Returns:
        Filename-safe title like: "dialectical_materialism_and_praxis"
    """
    # Use SpaCy-enhanced title generation
    title = generate_title(text, max_length + 10)  # Allow extra for processing

    # Convert to filename-safe format
    safe_title = re.sub(r'[^\w\s-]', '', title)  # Keep alphanumeric, spaces, hyphens
    safe_title = safe_title.replace(' ', '_')     # Spaces to underscores
    safe_title = re.sub(r'_+', '_', safe_title)   # Collapse multiple underscores
    safe_title = safe_title.strip('_')            # Remove leading/trailing underscores

    # Ensure not empty
    if not safe_title:
        safe_title = 'untitled'

    # Truncate if needed (at word boundary)
    if len(safe_title) > max_length:
        safe_title = safe_title[:max_length].rsplit('_', 1)[0]

    return safe_title.lower()


def generate_filename(sequence_num: int, date_str, text: str, max_title_length: int = 50) -> str:
    """
    Generate standardized filename: {sequence}-{YYYYMMDD}-{title}.md

    Args:
        sequence_num: Thread sequence number (1-based, zero-padded to 3 digits)
        date_str: Date string in various formats (Twitter, ISO, etc.)
        text: Source text to generate title from
        max_title_length: Maximum length for title portion

    Returns:
        Formatted filename like: 001-20250122-dialectical_materialism.md
    """
    # Format sequence number with zero-padding
    seq = f"{sequence_num:03d}"

    # Parse and format date as YYYYMMDD
    date_formatted = parse_to_yyyymmdd(date_str)

    # Generate brief, filename-safe title
    title = generate_brief_title(text, max_title_length)

    return f"{seq}-{date_formatted}-{title}.md"


# Batch processing optimization for multiple documents
def process_batch(texts: List[str], batch_size: int = 100) -> List[Doc]:
    """
    Process multiple texts efficiently using SpaCy's pipe method.

    Args:
        texts: List of texts to process
        batch_size: Size of processing batches

    Returns:
        List of processed Doc objects
    """
    return list(nlp.pipe(texts, batch_size=batch_size))


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
    print("   cd /home/percy/projects/DremelDocs/scripts")
    print("   python text_processing.py")