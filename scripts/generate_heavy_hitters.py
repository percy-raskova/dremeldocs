#!/usr/bin/env python3
"""
Generate markdown files for the heavy-hitter threads (500+ words)
These are the meaty philosophical/political threads worth manual review
"""

import json
import re
from pathlib import Path
from datetime import datetime

def clean_filename(text: str, max_length: int = 50) -> str:
    """Create a clean filename from tweet text"""
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove special characters
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with underscores
    text = re.sub(r'\s+', '_', text)
    # Truncate and clean up
    return text[:max_length].strip('_')

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
        # Parse the date
        date_str = thread['first_tweet_date']
        try:
            # Twitter date format: "Sat Apr 26 15:30:45 +0000 2025"
            date_obj = datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
            date_formatted = date_obj.strftime('%Y-%m-%d')
            date_display = date_obj.strftime('%B %d, %Y')
        except:
            date_formatted = 'undated'
            date_display = 'Date unknown'

        # Create filename
        first_words = thread['smushed_text'][:100]
        clean_text = clean_filename(first_words)
        filename = f"{i+1:03d}_{date_formatted}_{clean_text}.md"
        filepath = output_dir / filename

        # Generate markdown content
        content = f"""# Thread #{i+1}: {date_display}

## Metadata
- **Word count**: {thread['word_count']} words
- **Tweet count**: {thread['tweet_count']} tweets
- **Thread ID**: {thread['thread_id']}
- **Date**: {thread['first_tweet_date']}

## Content

{thread['smushed_text']}

---

### Tweet IDs
{', '.join(thread['tweet_ids'])}

### Navigation
[← Previous](#{i:03d}) | [Index](index.md) | [Next →](#{i+2:03d})
"""

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

    # Generate index file
    print("\n📚 Generating index file...")
    index_content = """# Heavy Hitter Threads Index

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
        sum(t['word_count'] for t in heavy_threads) / len(heavy_threads),
        max(t['word_count'] for t in heavy_threads)
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