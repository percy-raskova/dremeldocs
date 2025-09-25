#!/usr/bin/env python3
"""
Extract Domain Vocabulary from Corpus - The Yenan Path
Mass line approach: From the masses (corpus), to the masses (tagging)
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import yaml


class CorpusVocabularyExtractor:
    """Extract authentic political vocabulary from the people's own words."""

    def __init__(self):
        # Import the already-loaded SpaCy model from nlp_core
        from nlp_core import nlp

        self.nlp = nlp
        self.political_patterns = {
            # Marxist concepts - looking for actual usage patterns
            "class_analysis": [
                r"\b(working|ruling|owning) class\b",
                r"\bclass (consciousness|struggle|war|interest|position)\b",
                r"\b(proletaria[nt]|bourgeois\w*|petit[- ]bourgeois)\b",
                r"\bmeans of production\b",
                r"\b(wage|surplus) (labor|value)\b",
            ],
            "dialectics": [
                r"\b(dialectical|historical) materialis[mt]\b",
                r"\b(material|objective) (conditions|reality|basis)\b",
                r"\bcontradictions?\b(?! in terms)",
                r"\b(thesis|antithesis|synthesis)\b",
                r"\bnegation of the negation\b",
            ],
            "organizing": [
                r"\b(mass|base|cadre|vanguard) (work|building|organization)\b",
                r"\b(democratic|organizational) centralis[mt]\b",
                r"\bparty (line|discipline|building)\b",
                r"\b(revolutionary|communist|socialist) (party|organization)\b",
                r"\bcross-pollination\b",
            ],
            "imperialism": [
                r"\b(imperial|imperialist) (core|periphery|extraction)\b",
                r"\b(settler|internal) colonialis[mt]\b",
                r"\b(national|colonial) (oppression|liberation|question)\b",
                r"\bcomprador\b",
                r"\bglobal (north|south)\b",
            ],
            "fascism": [
                r"\b(liberal|fascis[mt]) (decay|hegemony|regime)\b",
                r"\bnational (consciousness|chauvinism|relation)\b",
                r"\b(great|oppressor) nation\b",
                r"\bclass collaboration\b",
                r"\b(proto|neo|quasi)-?fascis[mt]\b",
            ],
        }

    def extract_from_thread(self, text: str) -> Dict[str, List[str]]:
        """Extract vocabulary from a single thread using multiple methods."""
        vocab = defaultdict(set)

        # 1. Pattern-based extraction for known political concepts
        for category, patterns in self.political_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = " ".join(match)
                    vocab[category].add(match.lower().strip())

        # 2. Extract noun phrases that co-occur with political terms
        doc = self.nlp(text[:10000])  # Limit for performance

        political_triggers = {
            "capitalism",
            "socialism",
            "communism",
            "marxism",
            "imperialism",
            "revolution",
            "liberation",
            "oppression",
            "exploitation",
            "alienation",
            "praxis",
            "hegemony",
            "ideology",
            "fascism",
            "liberalism",
        }

        for sent in doc.sents:
            sent_text = sent.text.lower()
            if any(trigger in sent_text for trigger in political_triggers):
                # Extract meaningful noun phrases from this sentence
                for chunk in sent.noun_chunks:
                    if len(chunk.text.split()) <= 4:  # Max 4 words
                        if not chunk.root.pos_ in ["PRON", "DET"]:
                            vocab["contextual_phrases"].add(chunk.text.lower())

        # 3. Extract named entities relevant to political discussion
        for ent in doc.ents:
            if ent.label_ in ["ORG", "GPE", "PERSON", "EVENT"]:
                if any(
                    term in ent.text.lower()
                    for term in ["party", "movement", "conference", "revolution"]
                ):
                    vocab["organizations"].add(ent.text)
                elif ent.label_ == "GPE":
                    vocab["geopolitical"].add(ent.text)

        return {k: list(v) for k, v in vocab.items()}

    def extract_from_corpus(self, threads_file: Path) -> Dict[str, Counter]:
        """Extract vocabulary from entire corpus with frequency counts."""
        print("📚 Extracting vocabulary from the masses...")

        with open(threads_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Aggregate vocabulary across all threads
        category_vocab = defaultdict(Counter)

        for thread in data["threads"]:
            if thread["word_count"] >= 500:  # Focus on heavy hitters
                thread_vocab = self.extract_from_thread(thread["smushed_text"])

                for category, terms in thread_vocab.items():
                    for term in terms:
                        category_vocab[category][term] += 1

        return category_vocab

    def identify_key_phrases(
        self, threads_file: Path, min_df: int = 3
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Use TF-IDF to identify key multi-word phrases."""
        print("🔍 Identifying key phrases using TF-IDF...")

        with open(threads_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Collect documents by rough category
        category_docs = defaultdict(list)

        for thread in data["threads"]:
            text = thread["smushed_text"].lower()

            # Simple categorization based on content
            if any(
                term in text
                for term in ["marx", "capital", "class struggle", "proletariat"]
            ):
                category_docs["marxism"].append(text)
            if any(
                term in text
                for term in ["fascis", "liberal decay", "national consciousness"]
            ):
                category_docs["fascism"].append(text)
            if any(
                term in text
                for term in ["imperial", "colonial", "palestine", "settler"]
            ):
                category_docs["imperialism"].append(text)
            if any(
                term in text
                for term in ["covid", "pandemic", "public health", "vaccine"]
            ):
                category_docs["public_health"].append(text)
            if any(
                term in text for term in ["organiz", "party", "movement", "mass work"]
            ):
                category_docs["organizing"].append(text)

        # Extract top phrases per category
        category_phrases = {}

        for category, docs in category_docs.items():
            if len(docs) >= 3:  # Need minimum docs for TF-IDF
                vectorizer = TfidfVectorizer(
                    ngram_range=(2, 4),  # 2-4 word phrases
                    max_features=50,
                    min_df=2,
                    stop_words="english",
                )

                try:
                    X = vectorizer.fit_transform(docs)
                    features = vectorizer.get_feature_names_out()
                    scores = X.sum(axis=0).A1
                    phrase_scores = [
                        (features[i], scores[i]) for i in scores.argsort()[-20:][::-1]
                    ]
                    category_phrases[category] = phrase_scores
                except Exception as e:
                    print(f"    ⚠️ Failed to extract TF-IDF phrases for {category}: {e}")
                    continue

        return category_phrases

    def generate_yaml_vocabulary(
        self, vocab_counts: Dict, tfidf_phrases: Dict, output_dir: Path
    ):
        """Generate YAML vocabulary files for each category."""
        print("✍️ Generating YAML vocabulary files...")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Map our extraction categories to the user's desired categories
        category_mapping = {
            "class_analysis": "marxism_communism",
            "dialectics": "dialectical_historical_materialism",
            "organizing": "operational_organizational_theory",
            "imperialism": "imperialism_colonialism",
            "fascism": "fascism_analysis",
            "contextual_phrases": "social_criticism",
        }

        # Build comprehensive vocabulary for each category
        for extract_cat, output_cat in category_mapping.items():
            if extract_cat not in vocab_counts:
                continue

            vocab_data = {
                "category": output_cat,
                "description": f"Vocabulary for {output_cat.replace('_', ' ').title()}",
                "source": "Extracted from DremelDocs corpus using mass line method",
                "terms": {},
            }

            # Add high-frequency terms
            for term, count in vocab_counts[extract_cat].most_common(30):
                if count >= 2:  # Appears in at least 2 threads
                    vocab_data["terms"][term] = {
                        "weight": min(2.0, 1.0 + (count / 10)),  # Weight by frequency
                        "frequency": count,
                        "type": "extracted_pattern",
                    }

            # Add TF-IDF phrases if available
            if extract_cat in tfidf_phrases:
                for phrase, score in tfidf_phrases[extract_cat][:15]:
                    if phrase not in vocab_data["terms"]:
                        vocab_data["terms"][phrase] = {
                            "weight": float(min(1.8, 1.2 + (score / 100))),
                            "tfidf_score": float(score),
                            "type": "tfidf_phrase",
                        }

            # Write to YAML file
            output_file = output_dir / f"{output_cat}.yaml"
            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(vocab_data, f, default_flow_style=False, sort_keys=False)

            print(
                f"  ✅ Generated {output_file.name} with {len(vocab_data['terms'])} terms"
            )

    def analyze_corpus_statistics(self, threads_file: Path):
        """Provide statistics about the corpus vocabulary."""
        print("\n📊 Corpus Statistics:")

        with open(threads_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        total_words = sum(t["word_count"] for t in data["threads"])
        heavy_hitters = [t for t in data["threads"] if t["word_count"] >= 500]

        print(f"  Total threads: {len(data['threads'])}")
        print(f"  Heavy hitters (500+ words): {len(heavy_hitters)}")
        print(f"  Total words in corpus: {total_words:,}")
        print(
            f"  Words in heavy hitters: {sum(t['word_count'] for t in heavy_hitters):,}"
        )

        # Sample vocabulary richness
        all_text = " ".join(t["smushed_text"] for t in heavy_hitters[:10])
        doc = self.nlp(all_text[:50000])

        unique_lemmas = set(
            token.lemma_ for token in doc if token.is_alpha and not token.is_stop
        )
        print(f"  Unique lemmas in sample: {len(unique_lemmas)}")

        # Political term density
        political_terms = sum(
            1
            for token in doc
            if token.text.lower()
            in {
                "class",
                "capital",
                "marx",
                "revolution",
                "imperialism",
                "fascism",
                "liberation",
                "oppression",
                "dialectical",
                "material",
                "praxis",
            }
        )
        print(f"  Political term density: {political_terms / len(doc) * 100:.2f}%")


def main():
    """Extract vocabulary from the corpus using the mass line method."""
    print("🚩 EXTRACTING VOCABULARY FROM THE MASSES")
    print("=" * 50)

    extractor = CorpusVocabularyExtractor()

    # Input and output paths
    threads_file = Path("data/filtered_threads.json")
    output_dir = Path("data/vocabularies")

    if not threads_file.exists():
        print(f"❌ Error: {threads_file} not found. Run the pipeline first!")
        return

    # Extract vocabulary with frequency counts
    vocab_counts = extractor.extract_from_corpus(threads_file)

    # Extract key phrases using TF-IDF
    tfidf_phrases = extractor.identify_key_phrases(threads_file)

    # Generate YAML vocabulary files
    extractor.generate_yaml_vocabulary(vocab_counts, tfidf_phrases, output_dir)

    # Provide corpus statistics
    extractor.analyze_corpus_statistics(threads_file)

    print("\n🎯 Next Steps:")
    print("1. Review generated vocabularies in data/vocabularies/")
    print("2. Manually add/remove terms based on your expertise")
    print("3. Integrate with your EnhancedTagExtractor")
    print("4. Test on sample threads to verify quality")
    print("\n✊ From the masses, to the masses!")


if __name__ == "__main__":
    main()
