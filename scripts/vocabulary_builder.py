#!/usr/bin/env python3
"""
Revolutionary Vocabulary Builder - Dialectical Synthesis Edition
Combines the best of all vocabulary extraction approaches into one powerful tool.
No more liberal incrementalism - this is the vanguard of NLP-powered political analysis!
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml

# Import our enhanced NLP modules
try:
    from nlp_core import clean_social_text, nlp
    from tag_extraction import EnhancedTagExtractor
except ImportError:
    # Fallback for testing
    nlp = None
    def clean_social_text(x):
        return x


class PoliticalVocabularyExtractor:
    """
    Extract political and philosophical vocabulary using multiple methods:
    1. Pattern-based extraction (from extract_domain_vocabulary.py)
    2. NLP-based extraction (from enhanced approaches)
    3. Statistical extraction (frequency and co-occurrence)
    """

    def __init__(self):
        """Initialize with revolutionary fervor!"""
        # Political patterns from extract_domain_vocabulary.py
        self.marxist_patterns = {
            "class_analysis": [
                r"\b(working|ruling|owning) class\b",
                r"\bclass (consciousness|struggle|war|interest|position)\b",
                r"\b(proletaria[nt]|bourgeois\w*|petit[- ]bourgeois)\b",
                r"\bmeans of production\b",
                r"\b(wage|surplus) (labor|value)\b",
                r"\b(labor|labour) (power|theory of value)\b",
            ],
            "dialectics": [
                r"\b(dialectical|historical) materialis[mt]\b",
                r"\b(material|objective) (conditions|reality|basis)\b",
                r"\bcontradictions?\b(?! in terms)",
                r"\b(thesis|antithesis|synthesis)\b",
                r"\bnegation of the negation\b",
                r"\bbase and superstructure\b",
            ],
            "organizing": [
                r"\b(mass|base|cadre|vanguard) (work|building|organization)\b",
                r"\b(democratic|organizational) centralis[mt]\b",
                r"\bparty (line|discipline|building)\b",
                r"\b(revolutionary|communist|socialist) (party|organization)\b",
                r"\bcross-pollination\b",
                r"\bmass line\b",
                r"\b(dual|state) power\b",
            ],
            "imperialism": [
                r"\b(imperial|imperialist) (core|periphery|extraction)\b",
                r"\b(settler|internal) colonialis[mt]\b",
                r"\b(national|colonial) (oppression|liberation|question)\b",
                r"\bcomprador\b",
                r"\bglobal (north|south)\b",
                r"\b(neo|anti)-?colonialis[mt]\b",
            ],
            "revolution": [
                r"\brevolutionary (consciousness|potential|subject|praxis)\b",
                r"\b(proletarian|socialist|communist) revolution\b",
                r"\b(revolutionary|counter-revolutionary) (forces|movement)\b",
                r"\bdictatorship of the proletariat\b",
                r"\btransition to (socialism|communism)\b",
            ],
        }

        # Philosophical patterns
        self.philosophical_patterns = {
            "epistemology": [
                r"\b(material|idealist) (analysis|conception)\b",
                r"\bepistemolog\w+\b",
                r"\bphenomenolog\w+\b",
                r"\bontolog\w+\b",
                r"\bpraxis\b",
            ],
            "dialectics": [
                r"\bdialectical (reasoning|method|process)\b",
                r"\b(thesis|antithesis|synthesis)\b",
                r"\bunity of opposites\b",
                r"\bquantitative to qualitative\b",
            ],
        }

        # Core Marxist terms that should always be detected
        self.core_marxist_terms = {
            "class struggle",
            "means of production",
            "surplus value",
            "working class",
            "proletariat",
            "bourgeoisie",
            "petit bourgeois",
            "dialectical materialism",
            "historical materialism",
            "revolutionary consciousness",
            "vanguard party",
            "mass work",
            "democratic centralism",
            "dictatorship of the proletariat",
            "wage labor",
            "labor power",
            "use value",
            "exchange value",
            "commodity fetishism",
            "alienation",
            "false consciousness",
            "base and superstructure",
            "mode of production",
            "forces of production",
            "relations of production",
        }

        # Philosophical terms
        self.philosophical_terms = {
            "consciousness",
            "material conditions",
            "dialectical reasoning",
            "thesis",
            "antithesis",
            "synthesis",
            "praxis",
            "phenomenology",
            "epistemology",
            "ontology",
            "teleology",
            "materialism",
            "idealism",
            "objective reality",
            "subjective experience",
            "concrete analysis",
            "abstract thought",
            "unity of opposites",
            "negation",
            "sublation",
        }

    def extract_marxist_terms(self, text: str) -> Set[str]:
        """Extract Marxist theoretical terms from text"""
        text_lower = text.lower()
        found_terms = set()

        # Check for core terms
        for term in self.core_marxist_terms:
            if term in text_lower:
                found_terms.add(term)

        # Apply patterns
        for _category, patterns in self.marxist_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        found_terms.add(" ".join(match))
                    else:
                        found_terms.add(match)

        return found_terms

    def extract_philosophical_terms(self, text: str) -> Set[str]:
        """Extract philosophical terms from text"""
        text_lower = text.lower()
        found_terms = set()

        # Check for philosophical terms
        for term in self.philosophical_terms:
            if term in text_lower:
                found_terms.add(term)

        # Apply patterns
        for _category, patterns in self.philosophical_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        found_terms.add(" ".join(match))
                    else:
                        found_terms.add(match)

        return found_terms

    def extract_by_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract terms by category using patterns"""
        results: Dict[str, List[str]] = defaultdict(list)
        text_lower = text.lower()

        # Check Marxist patterns
        for _category, patterns in self.marxist_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    term = " ".join(match) if isinstance(match, tuple) else match
                    if term and term not in results[_category]:
                        results[_category].append(term)

        # Special handling for organizing terms
        if "vanguard" in text_lower and "party" in text_lower:
            if "organizing" not in results:
                results["organizing"] = []
            if "vanguard party" not in results["organizing"]:
                results["organizing"].append("vanguard party")

        if "mass" in text_lower and "work" in text_lower:
            if "organizing" not in results:
                results["organizing"] = []
            if "mass work" not in results["organizing"]:
                results["organizing"].append("mass work")

        if "democratic centralism" in text_lower:
            if "organizing" not in results:
                results["organizing"] = []
            if "democratic centralism" not in results["organizing"]:
                results["organizing"].append("democratic centralism")

        return dict(results)

    def extract_and_score(self, text: str) -> List[Tuple[str, float]]:
        """Extract terms and score by relevance and frequency"""
        # Get all terms
        marxist_terms = self.extract_marxist_terms(text)
        philosophical_terms = self.extract_philosophical_terms(text)
        all_terms = marxist_terms | philosophical_terms

        # Count frequencies
        text_lower = text.lower()
        term_scores = []

        for term in all_terms:
            # Count occurrences
            count = text_lower.count(term)
            # Weight by term importance (longer terms = more specific = higher weight)
            weight = len(term.split()) * 0.5 + 1
            score = count * weight
            term_scores.append((term, score))

        # Sort by score
        term_scores.sort(key=lambda x: x[1], reverse=True)
        return term_scores


class VocabularyBuilder:
    """
    Main builder that combines all vocabulary extraction methods.
    This is the revolutionary synthesis of our tools!
    """

    def __init__(self):
        """Initialize the vocabulary builder"""
        self.extractor = PoliticalVocabularyExtractor()
        self.vocabulary = defaultdict(
            lambda: {"terms": [], "patterns": [], "score": 0.0}
        )

    def build_from_corpus(self, corpus_file: Path) -> Dict[str, Any]:
        """Build vocabulary from a corpus of threads"""
        # Load corpus
        with open(corpus_file, encoding="utf-8") as f:
            data = json.load(f)

        threads = data.get("threads", [])

        # Extract vocabulary from each thread
        marxist_terms: Counter[str] = Counter()
        philosophical_terms: Counter[str] = Counter()
        colonial_terms: Counter[str] = Counter()

        for thread in threads:
            text = thread.get("smushed_text", "")

            # Get Marxist terms
            m_terms = self.extractor.extract_marxist_terms(text)
            for term in m_terms:
                marxist_terms[term] += 1

            # Get philosophical terms
            p_terms = self.extractor.extract_philosophical_terms(text)
            for term in p_terms:
                philosophical_terms[term] += 1

            # Check for colonial/imperial themes
            if any(
                word in text.lower()
                for word in ["settler", "colonial", "indigenous", "native"]
            ):
                patterns = self.extractor.extract_by_patterns(text)
                if "imperialism" in patterns:
                    for term in patterns["imperialism"]:
                        colonial_terms[term] += 1

        # Build vocabulary structure
        vocabulary = {}

        if marxist_terms:
            vocabulary["marxism"] = {
                "terms": list(marxist_terms.keys()),
                "patterns": self.extractor.marxist_patterns.get("class_analysis", []),
                "score": min(len(marxist_terms) / 10, 1.0),  # Normalize score
            }

        if philosophical_terms:
            vocabulary["philosophy"] = {
                "terms": list(philosophical_terms.keys()),
                "patterns": self.extractor.philosophical_patterns.get("dialectics", []),
                "score": min(len(philosophical_terms) / 10, 1.0),
            }

        if colonial_terms:
            vocabulary["colonialism"] = {
                "terms": list(colonial_terms.keys()),
                "patterns": self.extractor.marxist_patterns.get("imperialism", []),
                "score": min(len(colonial_terms) / 10, 1.0),
            }

        return vocabulary

    def generate_yaml(self, vocabulary: Dict[str, Any], output_file: Path) -> None:
        """Generate YAML vocabulary file"""
        # Structure for YAML
        yaml_data = {}

        for category, data in vocabulary.items():
            yaml_data[category] = {
                "description": f"Terms related to {category}",
                "terms": data["terms"],
                "patterns": data.get("patterns", []),
                "score_threshold": data.get("score", 0.5),
            }

        # Write YAML
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

    def merge_vocabularies(self, vocabularies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple vocabularies intelligently"""
        merged: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"terms": set(), "patterns": set(), "scores": []})

        for vocab in vocabularies:
            for category, data in vocab.items():
                merged[category]["terms"].update(data.get("terms", []))
                merged[category]["patterns"].update(data.get("patterns", []))
                merged[category]["scores"].append(data.get("score", 0))

        # Convert sets back to lists and average scores
        result = {}
        for category, data in merged.items():
            result[category] = {
                "terms": list(data["terms"]),
                "patterns": list(data["patterns"]),
                "score": sum(data["scores"]) / len(data["scores"])
                if data["scores"]
                else 0,
            }

        return result

    def generate_variations(self, term: str) -> List[str]:
        """Generate variations of a term (plural, verb forms, etc.)"""
        variations = [term]

        # Add plural
        if not term.endswith("s"):
            variations.append(term + "s")
            if term.endswith("y"):
                variations.append(term[:-1] + "ies")

        # Add verb forms for words ending in 'tion'
        if term.endswith("tion"):
            root = term[:-4]
            variations.append(root + "te")  # revolutionize
            variations.append(root + "ting")  # revolutionizing
            variations.append(root + "tional")  # revolutional

        # Special cases
        if term == "revolutionary":
            variations.extend(["revolution", "revolutionaries", "revolutionize"])
        elif term == "proletariat":
            variations.extend(["proletarian", "proletarians"])
        elif term == "bourgeoisie":
            variations.extend(["bourgeois", "bourgeoisification"])

        return variations

    def filter_quality_terms(self, terms: List[str]) -> List[str]:
        """Filter out low-quality or common terms"""
        # Common stop words to filter
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "a",
            "an",
            "it",
            "its",
            "they",
            "them",
            "their",
            "we",
            "us",
            "our",
        }

        filtered = []
        for term in terms:
            # Skip single-character terms and stop words
            if len(term) > 1 and term.lower() not in stop_words:
                filtered.append(term)

        return filtered


def main():
    """Main execution for testing"""
    print("🚩 Revolutionary Vocabulary Builder Initialized!")
    print("Ready to extract the language of liberation from the corpus!")

    # Test extraction
    sample_text = """
    The working class must develop revolutionary consciousness to understand
    that the means of production must be seized from the bourgeoisie. This
    dialectical materialism shows us that class struggle is the motor of history.
    """

    extractor = PoliticalVocabularyExtractor()
    terms = extractor.extract_marxist_terms(sample_text)

    print(f"\n📚 Extracted {len(terms)} Marxist terms:")
    for term in sorted(terms):
        print(f"  - {term}")


if __name__ == "__main__":
    main()
