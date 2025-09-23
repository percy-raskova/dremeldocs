#!/usr/bin/env python3
"""
Generate markdown files for the heavy-hitter threads (500+ words)
These are the meaty philosophical/political threads worth manual review
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Import our SpaCy-enhanced text processing utilities
from text_processing import (
    generate_title,
    generate_description,
    calculate_reading_time,
    format_frontmatter_value,
    extract_entities,
    generate_filename,  # New filename generation function
    parse_to_yyyymmdd  # Date parsing function
)

# SpaCy-enhanced text processing functions are now imported from text_processing module
# clean_filename is no longer needed as we use generate_filename from text_processing

def generate_navigation_links(current_index, total_threads):
    """Generate navigation links with proper file references based on expected filenames."""
    prev_link = ""
    next_link = ""

    # Previous link
    if current_index > 0:
        # Generate the previous filename pattern (no # symbol)
        prev_link = f"[← Previous]({current_index:03d}-*.md)"
    else:
        prev_link = "← Previous"

    # Next link
    if current_index < total_threads - 1:
        # Generate the next filename pattern (no # symbol)
        next_link = f"[Next →]({current_index + 2:03d}-*.md)"
    else:
        next_link = "Next →"

    return f'{prev_link} | [Index](index.md) | {next_link}'

def generate_heavy_hitter_markdowns():
    """Generate markdown files for threads with 500+ words"""
    print("🏋️ Generating markdown for heavy-hitter threads (500+ words)...")

    # Load the filtered threads
    with open('data/filtered_threads.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create output directory
    output_dir = Path('docs/heavy_hitters')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Filter for 500+ word threads
    heavy_threads = [t for t in data['threads'] if t['word_count'] >= 500]
    print(f"Found {len(heavy_threads)} threads with 500+ words")

    # Sort by word count (longest first)
    heavy_threads.sort(key=lambda x: x['word_count'], reverse=True)

    # Track generated files for index
    generated_files = []

    for i, thread in enumerate(heavy_threads):
        # Parse the date for display
        date_str = thread['first_tweet_date']
        try:
            # Twitter date format: "Sat Apr 26 15:30:45 +0000 2025"
            date_obj = datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
            date_display = date_obj.strftime('%B %d, %Y')
        except:
            date_display = 'Date unknown'

        # Generate standardized filename
        filename = generate_filename(i + 1, thread['first_tweet_date'], thread['smushed_text'])
        filepath = output_dir / filename

        # Generate title and description using SpaCy-enhanced functions
        title = generate_title(thread['smushed_text'])
        description = generate_description(thread['smushed_text'])
        reading_time = calculate_reading_time(thread['smushed_text'])  # Now uses actual text

        # Extract entities for additional metadata
        entities = extract_entities(thread['smushed_text'])

        # Get date in YYYY-MM-DD format for frontmatter
        date_for_frontmatter = parse_to_yyyymmdd(thread['first_tweet_date'])
        date_for_frontmatter = f"{date_for_frontmatter[:4]}-{date_for_frontmatter[4:6]}-{date_for_frontmatter[6:8]}"

        # Build frontmatter with enhanced metadata
        frontmatter_lines = [
            '---',
            f'title: {format_frontmatter_value(title)}',
            'date:',
            f'  created: {date_for_frontmatter}',
            f'categories: [heavy_hitters]',
            f'thread_id: {format_frontmatter_value(thread["thread_id"])}',
            f'word_count: {thread["word_count"]}',
            f'reading_time: {reading_time}',
            f'description: {format_frontmatter_value(description)}',
            f'tweet_count: {thread["tweet_count"]}',
            f'thread_number: {i+1}',
            f'author: "@BmoreOrganized"'
        ]

        # Add tags (extracted entities) if found
        if entities:
            frontmatter_lines.append(f'tags: {format_frontmatter_value(entities)}')
        else:
            frontmatter_lines.append('tags: []')

        frontmatter_lines.extend(['---', ''])

        # Generate markdown content
        content_lines = [
            f'# Thread #{i+1}: {title}',
            '',
            f'*{date_display} • {thread["word_count"]} words • {thread["tweet_count"]} tweets • ~{reading_time} min read*',
            '',
            '---',
            '',
            thread['smushed_text'],
            '',
            '---',
            '',
            '### Tweet IDs',
            ', '.join(thread['tweet_ids']),
            '',
            '### Navigation',
            generate_navigation_links(i, len(heavy_threads))
        ]

        # Combine frontmatter and content
        content = '\n'.join(frontmatter_lines) + '\n'.join(content_lines)

        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Track for index
        generated_files.append({
            'number': i+1,
            'filename': filename,
            'date': date_display,
            'word_count': thread['word_count'],
            'tweet_count': thread['tweet_count'],
            'preview': thread['smushed_text'][:200] + '...'
        })

        print(f"  [{i+1:3d}/{len(heavy_threads)}] {filename}")

    # Generate index file with frontmatter
    print("\n📚 Generating index file with frontmatter...")

    # Calculate total stats
    total_words = sum(t['word_count'] for t in heavy_threads)
    avg_words = total_words / len(heavy_threads) if heavy_threads else 0
    max_words = max(t['word_count'] for t in heavy_threads) if heavy_threads else 0
    # Calculate total reading time based on word count
    total_reading_time = max(1, round(total_words / 225))  # Simple calculation for total

    index_frontmatter = [
        '---',
        'title: "Heavy Hitter Threads Index"',
        'date:',
        f'  created: {datetime.now().strftime("%Y-%m-%d")}',
        'categories: [index]',
        f'total_threads: {len(heavy_threads)}',
        f'total_words: {total_words}',
        f'total_reading_time: {total_reading_time}',
        'description: "Substantial threads with 500+ words - the philosophical and political meat of the archive"',
        '---',
        ''
    ]

    index_content = '\n'.join(index_frontmatter) + """# Heavy Hitter Threads Index

These are the substantial threads with 500+ words - the philosophical and political meat of the archive.

## Statistics
- **Total heavy threads**: {}
- **Total words**: {:,}
- **Average thread length**: {:.0f} words
- **Longest thread**: {:,} words

## Threads by Size

""".format(
        len(heavy_threads),
        sum(t['word_count'] for t in heavy_threads),
        sum(t['word_count'] for t in heavy_threads) / len(heavy_threads) if heavy_threads else 0,
        max(t['word_count'] for t in heavy_threads) if heavy_threads else 0
    )

    # Add thread listing
    for file_info in generated_files:
        index_content += f"""
### {file_info['number']}. [{file_info['date']}]({file_info['filename']})

- **{file_info['word_count']} words** across {file_info['tweet_count']} tweets
- Preview: *{file_info['preview']}*
"""

    # Write index
    index_path = output_dir / 'index.md'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"✅ Generated {len(heavy_threads)} markdown files in docs/heavy_hitters/")
    print(f"📖 Index available at docs/heavy_hitters/index.md")

    return generated_files

def generate_theme_template():
    """Generate a template for manual theme extraction"""
    print("\n📝 Generating theme extraction template...")

    template = """# Theme Extraction Template

## Instructions
After reading the heavy-hitter threads, fill in the themes you identify along with their frequency/weight.

## Identified Themes

### Political Philosophy
- [ ] Marxism/Historical Materialism:
- [ ] Anarchism:
- [ ] Liberalism Critique:
- [ ] Fascism Analysis:
- [ ] Democracy Theory:
- [ ] Political Economy:
- [ ] Imperialism/Colonialism:
- [ ] Class Analysis:

### General Philosophy
- [ ] Epistemology:
- [ ] Ethics/Moral Philosophy:
- [ ] Ontology/Metaphysics:
- [ ] Philosophy of Mind:
- [ ] Phenomenology:
- [ ] Critical Theory:
- [ ] Dialectics:

### Applied Topics
- [ ] Technology Critique:
- [ ] Environmental Philosophy:
- [ ] Urban Theory:
- [ ] Labor/Work:
- [ ] Education Theory:
- [ ] Media Analysis:
- [ ] Cultural Criticism:

### Historical Analysis
- [ ] American History:
- [ ] Revolutionary Theory:
- [ ] Historical Materialism Applied:
- [ ] Comparative History:

### Other Themes
(Add any additional themes you identify)
- [ ]
- [ ]
- [ ]

## Thread-Theme Mapping
(Note which thread numbers strongly represent each theme)

### Example:
- Marxism: Threads #3, #7, #15, #22 (strong), #31 (moderate)
- Technology Critique: Threads #5 (strong), #12, #18

## Keywords/Phrases You Actually Use
(List specific terms that appear in YOUR writing, not generic philosophy terms)

### Examples:
- "primitive accumulation"
- "means of production"
- "your actual phrases here"

## Notes
(Any observations about your writing style, recurring arguments, or patterns)

---

Save this as: docs/heavy_hitters/THEMES_EXTRACTED.md
"""

    template_path = Path('docs/heavy_hitters/THEME_TEMPLATE.md')
    template_path.parent.mkdir(parents=True, exist_ok=True)

    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"✅ Theme template saved to: {template_path}")

if __name__ == "__main__":
    # Generate the heavy hitters
    files = generate_heavy_hitter_markdowns()

    # Generate the theme template
    generate_theme_template()

    print("\n" + "="*50)
    print("🎯 Next Steps:")
    print("1. Review the threads in docs/heavy_hitters/")
    print("2. Fill out docs/heavy_hitters/THEME_TEMPLATE.md")
    print("3. Save as THEMES_EXTRACTED.md with your insights")
    print("4. We'll use your themes to classify all 1,363 threads!")