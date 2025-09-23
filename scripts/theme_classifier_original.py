#!/usr/bin/env python3
"""
Theme-based classifier for all threads
Uses human-extracted themes from heavy hitters to classify the full archive
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, TypedDict, Optional, Any
from collections import defaultdict
from datetime import datetime

# Import our SpaCy-enhanced text processing utilities
from text_processing import (
    generate_title,
    generate_description,
    calculate_reading_time,
    format_frontmatter_value,
    extract_entities,
    generate_filename  # New filename generation function
)

# Type definitions for better structure
class Thread(TypedDict):
    thread_id: str
    themes: List[str]
    confidence: float
    category: str
    word_count: int
    tweet_count: int
    first_tweet_date: str
    smushed_text: str
    tweets: List[Dict]  # Added for full tweet access

class ThemeClassifier:
    def __init__(self, themes_file: str = 'docs/heavy_hitters/THEMES_EXTRACTED.md') -> None:
        self.themes_file = Path(themes_file)
        self.themes: Dict[str, int] = {}
        self.keywords: Dict[str, str] = {}
        self.thread_theme_map: Dict[str, List[int]] = {}

    def load_human_themes(self) -> bool:
        """Load the human-extracted themes from your manual review"""
        if not self.themes_file.exists():
            print(f"❌ Theme file not found: {self.themes_file}")
            print("   Please complete your review and save as THEMES_EXTRACTED.md")
            return False

        print(f"📖 Loading themes from {self.themes_file}")

        # This will parse your filled-out template
        # We'll extract themes, keywords, and thread mappings
        with open(self.themes_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse sections (you'll customize these based on your actual themes)
        self._parse_theme_sections(content)
        self._parse_keywords(content)
        self._parse_thread_mappings(content)

        return True

    def _parse_theme_sections(self, content: str) -> None:
        """Extract theme categories and weights from the document"""
        # This will be customized based on your actual format
        # For now, a flexible parser that looks for patterns

        theme_pattern = r'\[x\]\s+([^:]+):\s*(\d+)?'
        matches = re.findall(theme_pattern, content)

        for theme, weight in matches:
            theme = theme.strip()
            weight = int(weight) if weight else 1
            self.themes[theme] = weight
            print(f"  Found theme: {theme} (weight: {weight})")

    def _parse_keywords(self, content: str) -> None:
        """Extract your actual vocabulary from the Keywords section"""
        keywords_section = re.search(
            r'Keywords/Phrases You Actually Use.*?\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if keywords_section:
            lines = keywords_section.group(1).strip().split('\n')
            for line in lines:
                # Remove bullet points and quotes
                keyword = re.sub(r'^[-*]\s*"|"$', '', line.strip())
                if keyword and not keyword.startswith('your actual'):
                    # Assign keywords to most relevant themes based on context
                    self.keywords[keyword.lower()] = keyword
                    print(f"  Found keyword: {keyword}")

    def _parse_thread_mappings(self, content: str) -> None:
        """Extract which threads exemplify which themes"""
        mapping_section = re.search(
            r'Thread-Theme Mapping.*?\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if mapping_section:
            lines = mapping_section.group(1).strip().split('\n')
            for line in lines:
                # Parse lines like "Marxism: Threads #3, #7, #15"
                match = re.match(r'[-*]?\s*([^:]+):\s*Threads?\s*(.*)', line)
                if match:
                    theme = match.group(1).strip()
                    thread_nums = re.findall(r'#(\d+)', match.group(2))
                    self.thread_theme_map[theme] = [int(n) for n in thread_nums]
                    print(f"  Mapped {theme} to threads: {thread_nums}")

    def classify_thread(self, thread: Dict[str, Any]) -> Tuple[List[str], float]:
        """
        Classify a single thread based on learned themes
        Returns: (list of themes, confidence score)
        """
        text = thread['smushed_text'].lower()
        detected_themes: List[str] = []
        scores: defaultdict[str, float] = defaultdict(float)

        # Check for keyword matches
        for keyword in self.keywords:
            if keyword in text:
                # Boost score for this keyword's associated themes
                # (You'll map keywords to themes based on your review)
                scores['detected'] += 1

        # Check for theme patterns learned from heavy hitters
        for theme, weight in self.themes.items():
            theme_score = self._calculate_theme_score(text, theme)
            if theme_score > 0:
                scores[theme] = theme_score * weight

        # Select top themes above threshold
        threshold = 0.3  # Adjust based on your preferences
        for theme, score in scores.items():
            if score > threshold:
                detected_themes.append(theme)

        # Calculate confidence based on match strength
        confidence = min(sum(scores.values()) / 10, 1.0)  # Normalize to 0-1

        return detected_themes, confidence

    def _calculate_theme_score(self, text: str, theme: str) -> float:
        """Calculate how strongly a text matches a theme"""
        score = 0.0

        # Use patterns learned from your manual review
        # This will be customized based on your actual themes

        # For now, simple keyword density
        # Check if any keywords match this theme (currently keywords are just a flat dict)
        for keyword in self.keywords.values():
            if keyword.lower() in text:
                score += 0.1

        return min(score, 1.0)

    def process_all_threads(self) -> Optional[Dict[str, Any]]:
        """Process all 1,363 threads using human-extracted themes"""
        print("\n🚀 Processing all threads with theme classifier...")

        # Load the full thread data
        data_file = Path('data/filtered_threads.json')
        if not data_file.exists():
            print(f"❌ Error: Required data file not found: {data_file}")
            print("   Please run the filter pipeline first to generate this file")
            return None

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in {data_file}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading {data_file}: {e}")
            return None

        classified_threads: Dict[str, List[Dict[str, Any]]] = {
            'philosophical': [],
            'political': [],
            'both': [],
            'uncertain': [],
            'other': []
        }

        theme_counts: defaultdict[str, int] = defaultdict(int)

        for i, thread in enumerate(data['threads']):
            # Classify thread
            themes, confidence = self.classify_thread(thread)

            # Categorize based on themes
            category = self._categorize_thread(themes)

            # Store classified thread with full tweet data
            classified_thread = {
                'thread_id': thread['thread_id'],
                'themes': themes,
                'confidence': confidence,
                'category': category,
                'word_count': thread['word_count'],
                'tweet_count': thread['tweet_count'],
                'first_tweet_date': thread['first_tweet_date'],
                'smushed_text': thread['smushed_text'],
                'tweets': thread.get('tweets', [])  # Include full tweets for frontmatter generation
            }

            classified_threads[category].append(classified_thread)

            # Track theme frequency
            for theme in themes:
                theme_counts[theme] += 1

            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/1363 threads...")

        # Save results
        output = {
            'metadata': {
                'total_threads': len(data['threads']),
                'classified': sum(len(v) for v in classified_threads.values()),
                'theme_counts': dict(theme_counts)
            },
            'threads_by_category': classified_threads
        }

        output_file = Path('data/classified_threads.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

        print(f"\n✅ Classification complete!")
        print(f"📊 Results:")
        print(f"  • Philosophical: {len(classified_threads['philosophical'])}")
        print(f"  • Political: {len(classified_threads['political'])}")
        print(f"  • Both: {len(classified_threads['both'])}")
        print(f"  • Uncertain: {len(classified_threads['uncertain'])}")
        print(f"  • Other: {len(classified_threads['other'])}")
        print(f"\n📁 Saved to: {output_file}")

        return output

    def _categorize_thread(self, themes: List[str]) -> str:
        """Categorize thread based on detected themes"""
        if not themes:
            return 'other'

        # You'll customize these based on your actual themes
        philosophical_themes = {
            'epistemology', 'ontology', 'phenomenology', 'ethics',
            'dialectics', 'metaphysics', 'philosophy of mind'
        }

        political_themes = {
            'marxism', 'anarchism', 'fascism', 'imperialism',
            'political economy', 'class analysis', 'colonialism'
        }

        has_philosophy = any(t.lower() in philosophical_themes for t in themes)
        has_politics = any(t.lower() in political_themes for t in themes)

        if has_philosophy and has_politics:
            return 'both'
        elif has_philosophy:
            return 'philosophical'
        elif has_politics:
            return 'political'
        elif themes:
            return 'uncertain'
        else:
            return 'other'

    # Use the SpaCy-enhanced functions from text_processing module
    # These are now imported at the top of the file

    def generate_final_markdown(self, category: str = 'both', limit: Optional[int] = None) -> None:
        """Generate markdown files for classified threads with proper frontmatter."""
        print(f"\n📝 Generating markdown for '{category}' threads with frontmatter...")

        with open('data/classified_threads.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        threads = data['threads_by_category'].get(category, [])

        if limit:
            threads = threads[:limit]

        output_dir = Path(f'markdown/{category}')
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, thread in enumerate(threads):
            # Generate clean filename using standardized format
            filename = generate_filename(i + 1, thread['first_tweet_date'], thread['smushed_text'])

            # Generate title and description using SpaCy-enhanced functions
            title = generate_title(thread['smushed_text'])
            description = generate_description(thread['smushed_text'])
            reading_time = calculate_reading_time(thread['smushed_text'])  # Now uses actual text for accurate count

            # Extract entities for potential tags
            entities = extract_entities(thread['smushed_text'])

            # Format date properly
            try:
                created_date = datetime.fromisoformat(thread['first_tweet_date'].replace('Z', '+00:00'))
                date_str = created_date.strftime('%Y-%m-%d')
            except Exception as e:
                print(f"Warning: Could not parse date '{thread['first_tweet_date']}': {e}")
                date_str = thread['first_tweet_date'][:10] if thread['first_tweet_date'] else '2025-01-01'

            # Build frontmatter
            frontmatter_lines = [
                '---',
                f'title: {format_frontmatter_value(title)}',
                'date:',
                f'  created: {date_str}',
                f'categories: {format_frontmatter_value([category])}',
                f'thread_id: {format_frontmatter_value(thread["thread_id"])}',
                f'word_count: {thread["word_count"]}',
                f'reading_time: {reading_time}',
                f'description: {format_frontmatter_value(description)}'
            ]

            # Add themes as tags if available
            if thread.get('themes'):
                frontmatter_lines.append(f'tags: {format_frontmatter_value(thread["themes"])}')

            # Add extracted entities as additional metadata
            if entities:
                frontmatter_lines.append(f'entities: {format_frontmatter_value(entities)}')

            # Add original URL if we have tweet ID
            # Since we don't have individual tweet IDs in this structure, we'll skip for now
            # Could be added if tweet data is preserved

            # Add engagement metrics if available
            # These would need to be calculated from the original tweets

            # Add confidence score as custom metadata
            if thread.get('confidence'):
                frontmatter_lines.append(f'confidence_score: {thread["confidence"]:.2f}')

            frontmatter_lines.append(f'tweet_count: {thread["tweet_count"]}')
            frontmatter_lines.append(f'author: "@BmoreOrganized"')
            frontmatter_lines.append('---')
            frontmatter_lines.append('')  # Empty line after frontmatter

            # Create main content
            content_lines = [
                f'# {title}',
                '',
                thread['smushed_text'],
                '',
                '---',
                '',
                f'*Thread ID: {thread["thread_id"]}*'
            ]

            # Combine frontmatter and content
            full_content = '\n'.join(frontmatter_lines) + '\n'.join(content_lines)

            filepath = output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)

        print(f"✅ Generated {len(threads)} markdown files with frontmatter in {output_dir}")


if __name__ == "__main__":
    classifier = ThemeClassifier()

    if not classifier.load_human_themes():
        print("\n⚠️  Waiting for your theme extraction...")
        print("Please:")
        print("1. Review the threads in docs/heavy_hitters/")
        print("2. Fill out THEME_TEMPLATE.md with your insights")
        print("3. Save as THEMES_EXTRACTED.md")
        print("4. Run this script again!")
    else:
        # Process all threads with your themes
        results = classifier.process_all_threads()

        # Generate markdown for the best matches
        classifier.generate_final_markdown('both', limit=50)
        classifier.generate_final_markdown('philosophical', limit=25)
        classifier.generate_final_markdown('political', limit=25)