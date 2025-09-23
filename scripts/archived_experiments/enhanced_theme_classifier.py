#!/usr/bin/env python3
"""
Enhanced Theme Classifier
Uses the human-extracted themes from THEMES_EXTRACTED.md to classify all 1,363 threads
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from datetime import datetime

# Import our text processing utilities
from text_processing import (
    generate_title,
    generate_description,
    calculate_reading_time,
    format_frontmatter_value,
    extract_entities,
    generate_filename,
    parse_to_yyyymmdd
)


class EnhancedThemeClassifier:
    """Enhanced classifier using THEMES_EXTRACTED.md structure."""

    def __init__(self, themes_file: str = 'docs/heavy_hitters/THEMES_EXTRACTED.md'):
        self.themes_file = Path(themes_file)

        # Theme data structures
        self.themes: Dict[str, List[int]] = {}  # theme -> thread numbers
        self.keywords: Dict[str, str] = {}  # keyword -> category
        self.thread_theme_map: Dict[int, List[str]] = defaultdict(list)  # thread_num -> themes

        # Categories for classification
        self.philosophical_themes = set()
        self.political_themes = set()

    def load_human_themes(self) -> bool:
        """Load and parse the THEMES_EXTRACTED.md file."""
        if not self.themes_file.exists():
            print(f"❌ Theme file not found: {self.themes_file}")
            return False

        print(f"📖 Loading themes from {self.themes_file}")

        with open(self.themes_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse different sections
        self._parse_identified_themes(content)
        self._parse_thread_mappings(content)
        self._parse_keywords(content)

        print(f"✅ Loaded {len(self.themes)} themes with {len(self.keywords)} keywords")
        print(f"   Thread mappings for {len(self.thread_theme_map)} threads")

        return True

    def _parse_identified_themes(self, content: str) -> None:
        """Parse the Identified Themes section with checkboxes."""
        # Find all checked themes with thread numbers
        pattern = r'\[x\]\s+\*?\*?([^:*]+)\*?\*?:\s*(\d+)\s*threads?\s*-\s*([^\\n]+)'
        matches = re.findall(pattern, content)

        for theme_name, count, thread_list in matches:
            theme = theme_name.strip()

            # Extract thread numbers
            thread_nums = re.findall(r'#(\d+)', thread_list)
            thread_nums = [int(n) for n in thread_nums]

            self.themes[theme] = thread_nums

            # Track themes for each thread
            for thread_num in thread_nums:
                self.thread_theme_map[thread_num].append(theme)

            print(f"  ✓ {theme}: {count} threads → {len(thread_nums)} mapped")

            # Categorize themes
            if any(word in theme.lower() for word in ['marxism', 'fascism', 'imperialism', 'political', 'colonialism']):
                self.political_themes.add(theme)
            elif any(word in theme.lower() for word in ['dialectics', 'epistemology', 'ontology', 'philosophy']):
                self.philosophical_themes.add(theme)

    def _parse_thread_mappings(self, content: str) -> None:
        """Parse the Thread-Theme Mapping section for strength indicators."""
        # Find mapping sections
        sections = re.findall(r'### ([^\\n]+)\\n- \*\*Strong presence\*\*: Threads ([^\\n]+)\\n- \*\*Moderate presence\*\*: Threads ([^\\n]+)', content)

        for theme, strong_threads, moderate_threads in sections:
            theme = theme.strip()

            # Extract strong presence threads
            strong_nums = re.findall(r'#(\d+)', strong_threads)
            for num in strong_nums:
                thread_num = int(num)
                if theme not in self.thread_theme_map[thread_num]:
                    self.thread_theme_map[thread_num].append(theme)

            # Extract moderate presence threads
            moderate_nums = re.findall(r'#(\d+)', moderate_threads)
            for num in moderate_nums:
                thread_num = int(num)
                if theme not in self.thread_theme_map[thread_num]:
                    self.thread_theme_map[thread_num].append(theme)

    def _parse_keywords(self, content: str) -> None:
        """Parse the Keywords/Phrases section."""
        # Find keywords section
        keywords_match = re.search(r'## Keywords/Phrases You Actually Use(.*?)(?=##|\\Z)', content, re.DOTALL)

        if keywords_match:
            keywords_section = keywords_match.group(1)

            # Parse each category of keywords
            category_pattern = r'### ([^\\n]+)\\n((?:- "[^"]+"\n)+)'
            category_matches = re.findall(category_pattern, keywords_section)

            for category, keywords_text in category_matches:
                # Extract individual keywords
                keyword_matches = re.findall(r'- "([^"]+)"', keywords_text)
                for keyword in keyword_matches:
                    self.keywords[keyword.lower()] = category

            print(f"  ✓ Loaded {len(self.keywords)} keywords across {len(set(self.keywords.values()))} categories")

    def classify_thread(self, thread: Dict[str, Any]) -> Tuple[List[str], float, Dict[str, float]]:
        """
        Classify a thread based on themes and keywords.

        Returns:
            Tuple of (themes list, confidence score, detailed scores dict)
        """
        text = thread.get('smushed_text', '').lower()
        word_count = thread.get('word_count', 0)

        # Score tracking
        theme_scores: Dict[str, float] = defaultdict(float)
        keyword_matches: List[str] = []

        # Check for keyword matches
        for keyword, category in self.keywords.items():
            if keyword in text:
                keyword_matches.append(keyword)
                # Map keyword categories to themes
                if 'political economy' in category.lower():
                    theme_scores['Political Economy'] += 2.0
                elif 'organizational' in category.lower():
                    theme_scores['Organizational Theory'] += 2.0
                elif 'philosophical method' in category.lower():
                    theme_scores['Dialectics'] += 1.5
                elif 'public health' in category.lower():
                    theme_scores['COVID/Public Health Politics'] += 2.0

        # Check for theme-specific patterns
        theme_patterns = {
            'Marxism/Historical Materialism': [
                'class struggle', 'bourgeois', 'proletariat', 'capital', 'labor power',
                'means of production', 'historical materialism', 'marx'
            ],
            'Fascism Analysis': [
                'fascis', 'authoritarian', 'reactionary', 'ultranational', 'corporatis'
            ],
            'Imperialism/Colonialism': [
                'imperial', 'colonial', 'settler', 'extraction', 'periphery', 'core',
                'palestine', 'occupation', 'zionism'
            ],
            'COVID/Public Health Politics': [
                'covid', 'pandemic', 'mask', 'vaccine', 'long covid', 'public health',
                'disability', 'eugenics'
            ],
            'Dialectics': [
                'dialectic', 'contradiction', 'synthesis', 'thesis', 'antithesis',
                'negation', 'qualitative', 'quantitative'
            ],
            'Political Economy': [
                'capital', 'labor', 'profit', 'exploitation', 'commodity', 'exchange',
                'surplus', 'accumulation'
            ],
            'Cultural Criticism': [
                'ideology', 'hegemony', 'culture', 'spectacle', 'alienation', 'reification'
            ]
        }

        for theme, patterns in theme_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    theme_scores[theme] += 1.0

        # Boost scores for longer threads (more substantial content)
        if word_count > 1000:
            for theme in theme_scores:
                theme_scores[theme] *= 1.2
        elif word_count > 500:
            for theme in theme_scores:
                theme_scores[theme] *= 1.1

        # Select themes above threshold
        threshold = 1.5
        selected_themes = [theme for theme, score in theme_scores.items() if score >= threshold]

        # Calculate confidence
        total_score = sum(theme_scores.values())
        confidence = min(total_score / 10, 1.0) if total_score > 0 else 0.0

        # If no themes detected but significant word count, mark as uncertain
        if not selected_themes and word_count > 200:
            confidence = 0.3

        return selected_themes, confidence, dict(theme_scores)

    def process_all_threads(self) -> Optional[Dict[str, Any]]:
        """Process and classify all 1,363 threads."""
        print("\n🚀 Processing all threads with enhanced classifier...")

        # Load filtered threads
        data_file = Path('data/filtered_threads.json')
        if not data_file.exists():
            print(f"❌ Data file not found: {data_file}")
            return None

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Classification results
        classified_threads = {
            'philosophical': [],
            'political': [],
            'both': [],
            'uncertain': [],
            'other': []
        }

        theme_frequency = defaultdict(int)
        high_confidence_count = 0
        detailed_results = []

        print(f"📊 Classifying {len(data['threads'])} threads...")

        for i, thread in enumerate(data['threads']):
            # Classify thread
            themes, confidence, scores = self.classify_thread(thread)

            # Determine category
            has_philosophy = any(t in self.philosophical_themes for t in themes)
            has_politics = any(t in self.political_themes for t in themes)

            if has_philosophy and has_politics:
                category = 'both'
            elif has_philosophy:
                category = 'philosophical'
            elif has_politics:
                category = 'political'
            elif themes and confidence > 0.5:
                category = 'uncertain'
            else:
                category = 'other'

            # Create enhanced thread record
            classified_thread = {
                'thread_id': thread['thread_id'],
                'themes': themes,
                'confidence': round(confidence, 3),
                'category': category,
                'word_count': thread['word_count'],
                'tweet_count': thread['tweet_count'],
                'first_tweet_date': thread['first_tweet_date'],
                'theme_scores': {k: round(v, 2) for k, v in scores.items() if v > 0}
            }

            classified_threads[category].append(classified_thread)
            detailed_results.append(classified_thread)

            # Track statistics
            for theme in themes:
                theme_frequency[theme] += 1

            if confidence > 0.7:
                high_confidence_count += 1

            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(data['threads'])} threads...")

        # Generate summary statistics
        total_classified = sum(len(v) for k, v in classified_threads.items() if k != 'other')

        output = {
            'metadata': {
                'total_threads': len(data['threads']),
                'classified': total_classified,
                'high_confidence': high_confidence_count,
                'classification_rate': round(total_classified / len(data['threads']) * 100, 1),
                'timestamp': datetime.now().isoformat()
            },
            'statistics': {
                'by_category': {
                    'philosophical': len(classified_threads['philosophical']),
                    'political': len(classified_threads['political']),
                    'both': len(classified_threads['both']),
                    'uncertain': len(classified_threads['uncertain']),
                    'other': len(classified_threads['other'])
                },
                'theme_frequency': dict(sorted(theme_frequency.items(), key=lambda x: x[1], reverse=True))
            },
            'threads_by_category': classified_threads,
            'detailed_results': detailed_results
        }

        # Save classification results
        output_file = Path('data/classified_threads_enhanced.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

        print(f"\n✅ Classification complete!")
        print(f"📈 Results:")
        print(f"  • Total threads: {output['metadata']['total_threads']}")
        print(f"  • Successfully classified: {total_classified} ({output['metadata']['classification_rate']}%)")
        print(f"  • High confidence: {high_confidence_count}")
        print(f"\n📊 By Category:")
        for category, count in output['statistics']['by_category'].items():
            percentage = round(count / len(data['threads']) * 100, 1)
            print(f"  • {category.capitalize()}: {count} ({percentage}%)")

        print(f"\n🏆 Top Themes:")
        for theme, count in list(theme_frequency.items())[:5]:
            print(f"  • {theme}: {count} threads")

        print(f"\n💾 Saved to: {output_file}")

        return output

    def generate_report(self, classification_data: Dict[str, Any]) -> None:
        """Generate a detailed classification report."""
        report_file = Path('docs/CLASSIFICATION_REPORT.md')

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Thread Classification Report\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")

            # Summary
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Threads Analyzed**: {classification_data['metadata']['total_threads']}\n")
            f.write(f"- **Successfully Classified**: {classification_data['metadata']['classified']} ")
            f.write(f"({classification_data['metadata']['classification_rate']}%)\n")
            f.write(f"- **High Confidence Classifications**: {classification_data['metadata']['high_confidence']}\n\n")

            # Category breakdown
            f.write("## Classification by Category\n\n")
            f.write("| Category | Count | Percentage |\n")
            f.write("|----------|-------|------------|\n")

            for category, count in classification_data['statistics']['by_category'].items():
                percentage = round(count / classification_data['metadata']['total_threads'] * 100, 1)
                f.write(f"| {category.capitalize()} | {count} | {percentage}% |\n")

            # Theme frequency
            f.write("\n## Most Frequent Themes\n\n")
            f.write("| Theme | Thread Count |\n")
            f.write("|-------|-------------|\n")

            for theme, count in list(classification_data['statistics']['theme_frequency'].items())[:10]:
                f.write(f"| {theme} | {count} |\n")

            # Sample classifications
            f.write("\n## Sample Classifications\n\n")

            for category in ['political', 'philosophical', 'both']:
                threads = classification_data['threads_by_category'].get(category, [])
                if threads:
                    f.write(f"### {category.capitalize()} Threads (Top 3)\n\n")
                    for thread in threads[:3]:
                        f.write(f"**Thread {thread['thread_id']}**\n")
                        f.write(f"- Themes: {', '.join(thread['themes'])}\n")
                        f.write(f"- Confidence: {thread['confidence']}\n")
                        f.write(f"- Word Count: {thread['word_count']}\n\n")

            f.write("\n## Next Steps\n\n")
            f.write("1. Review classified threads for accuracy\n")
            f.write("2. Generate themed markdown pages for MkDocs\n")
            f.write("3. Create navigation structure based on themes\n")
            f.write("4. Build and deploy the knowledge base\n")

        print(f"📄 Report saved to: {report_file}")


def main():
    """Run the enhanced classification process."""
    print("=" * 60)
    print("🎯 Enhanced Theme Classification System")
    print("=" * 60)

    # Initialize classifier
    classifier = EnhancedThemeClassifier()

    # Load themes
    if not classifier.load_human_themes():
        print("❌ Failed to load themes. Please ensure THEMES_EXTRACTED.md exists.")
        return

    # Process all threads
    results = classifier.process_all_threads()

    if results:
        # Generate report
        classifier.generate_report(results)

        print("\n" + "=" * 60)
        print("✨ Classification Complete!")
        print("=" * 60)
        print("\nNext: Run 'generate_mkdocs_content.py' to create the final site")


if __name__ == "__main__":
    main()