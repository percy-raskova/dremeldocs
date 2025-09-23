#!/usr/bin/env python3
"""
Integrate Political Vocabulary with MkDocs Tags
Generate properly tagged markdown files for MkDocs material theme
"""

import json
import yaml
from pathlib import Path
import re

class MkDocsTagIntegrator:
    """Integrate our vocabulary with MkDocs tags system."""

    def __init__(self):
        self.vocab_dir = Path('data/vocabularies')
        self.vocabularies = {}
        self.load_vocabularies()

    def load_vocabularies(self):
        """Load all vocabulary YAML files."""
        for vocab_file in self.vocab_dir.glob('*.yaml'):
            if vocab_file.name == 'master_vocabulary.yaml':
                continue

            with open(vocab_file, 'r') as f:
                vocab_data = yaml.safe_load(f)
                category = vocab_data['category']
                self.vocabularies[category] = vocab_data

    def extract_tags_from_text(self, text: str) -> set:
        """Extract tags from text using our political vocabularies."""
        text_lower = text.lower()
        tags = set()

        # Check each vocabulary category
        for category, vocab_data in self.vocabularies.items():
            category_matched = False

            for term, term_data in vocab_data['terms'].items():
                # Check canonical term and variations
                terms_to_check = [term] + term_data.get('variations', [])

                for check_term in terms_to_check:
                    # Use word boundaries for accurate matching
                    pattern = r'\b' + re.escape(check_term.lower()) + r'\b'
                    if re.search(pattern, text_lower):
                        # Add the category as a tag
                        if not category_matched:
                            # Clean category name for display
                            tag_name = category.replace('_', '-')
                            tags.add(tag_name)
                            category_matched = True

                        # For important terms, also add as specific tag
                        if term in ['palestine', 'covid', 'fascism', 'marxism', 'imperialism']:
                            tags.add(term.lower())
                        break

        return tags

    def update_markdown_frontmatter(self, file_path: Path) -> bool:
        """Update the tags in a markdown file's frontmatter."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter
        if not content.startswith('---'):
            return False

        parts = content.split('---', 2)
        if len(parts) < 3:
            return False

        frontmatter = parts[1]
        body = parts[2]

        # Extract tags from body text
        tags = self.extract_tags_from_text(body)

        if not tags:
            return False

        # Parse existing frontmatter
        fm_data = yaml.safe_load(frontmatter)
        if not fm_data:
            fm_data = {}

        # Update tags - use our political categories
        fm_data['tags'] = sorted(list(tags))

        # Also add category if not present
        if 'categories' not in fm_data:
            fm_data['categories'] = ['heavy_hitters']

        # Rebuild the file
        new_frontmatter = yaml.dump(fm_data, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_frontmatter}---{body}"

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    def process_heavy_hitters(self):
        """Process all heavy hitter files."""
        heavy_dir = Path('docs/heavy_hitters')
        processed = 0
        tagged = 0

        for md_file in sorted(heavy_dir.glob('[0-9]*.md')):
            processed += 1
            if self.update_markdown_frontmatter(md_file):
                tagged += 1
                print(f"  ✅ Tagged: {md_file.name}")
            else:
                print(f"  ⚠️  No tags found: {md_file.name}")

        print(f"\n📊 Processed {processed} files, tagged {tagged}")

    def generate_tag_index(self):
        """Generate a tag index page for MkDocs."""
        heavy_dir = Path('docs/heavy_hitters')
        tag_counts = {}
        tag_files = {}

        # Collect all tags
        for md_file in heavy_dir.glob('[0-9]*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm_data = yaml.safe_load(parts[1])
                    if fm_data and 'tags' in fm_data:
                        for tag in fm_data['tags']:
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1
                            if tag not in tag_files:
                                tag_files[tag] = []
                            tag_files[tag].append(md_file.name)

        # Generate index content
        content = """# Tag Index

Browse threads by political and philosophical themes.

## Tags by Category

"""

        # Group tags by type
        category_tags = []
        specific_tags = []

        for tag in sorted(tag_counts.keys()):
            if '-' in tag and any(cat in tag for cat in ['marxism', 'fascism', 'imperialism', 'political', 'dialectical', 'social', 'operational', 'public']):
                category_tags.append(tag)
            else:
                specific_tags.append(tag)

        # Category tags
        if category_tags:
            content += "### Theoretical Categories\n\n"
            for tag in category_tags:
                clean_name = tag.replace('-', ' ').title()
                content += f"- **{clean_name}** ({tag_counts[tag]} threads): [`#{tag}`](#{tag})\n"

        # Specific tags
        if specific_tags:
            content += "\n### Specific Topics\n\n"
            for tag in specific_tags:
                content += f"- **{tag}** ({tag_counts[tag]} threads): [`#{tag}`](#{tag})\n"

        # Add detailed sections
        content += "\n## Threads by Tag\n\n"

        for tag in sorted(tag_counts.keys()):
            clean_name = tag.replace('-', ' ').title()
            content += f"### {clean_name} {{: #{tag} }}\n\n"
            for filename in sorted(tag_files[tag])[:10]:  # Limit to 10 per tag
                content += f"- [{filename}]({filename})\n"
            if len(tag_files[tag]) > 10:
                content += f"- *...and {len(tag_files[tag]) - 10} more*\n"
            content += "\n"

        # Write tag index
        index_path = heavy_dir / 'tags.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Generated tag index with {len(tag_counts)} unique tags")

    def update_mkdocs_config(self):
        """Update mkdocs.yml to enable tags plugin."""
        mkdocs_path = Path('mkdocs.yml')

        if not mkdocs_path.exists():
            print("⚠️  mkdocs.yml not found, creating template...")

            config = {
                'site_name': 'DremelDocs',
                'site_description': 'Political philosophy and social criticism archive',
                'theme': {
                    'name': 'material',
                    'features': [
                        'navigation.tabs',
                        'navigation.sections',
                        'navigation.expand',
                        'navigation.top',
                        'search.suggest',
                        'search.highlight',
                        'content.tabs.link'
                    ]
                },
                'plugins': [
                    'search',
                    'tags',
                ],
                'markdown_extensions': [
                    'pymdownx.superfences',
                    'pymdownx.tabbed',
                    'pymdownx.details',
                    'admonition',
                    'attr_list',
                    'md_in_html'
                ],
                'nav': [
                    {'Home': 'index.md'},
                    {'Heavy Hitters': [
                        {'Index': 'heavy_hitters/index.md'},
                        {'By Tags': 'heavy_hitters/tags.md'}
                    ]}
                ]
            }

            with open(mkdocs_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)

            print("✅ Created mkdocs.yml with tags plugin enabled")
        else:
            print("ℹ️  mkdocs.yml exists - please manually add 'tags' to plugins if needed")

def main():
    print("🏷️ INTEGRATING POLITICAL VOCABULARY WITH MKDOCS")
    print("=" * 50)

    integrator = MkDocsTagIntegrator()

    print("\n📝 Processing heavy hitter files...")
    integrator.process_heavy_hitters()

    print("\n📑 Generating tag index...")
    integrator.generate_tag_index()

    print("\n⚙️  Configuring MkDocs...")
    integrator.update_mkdocs_config()

    print("\n✊ Tags integrated successfully!")
    print("\n🎯 Next Steps:")
    print("1. Run: mkdocs serve")
    print("2. Navigate to /heavy_hitters/tags/")
    print("3. Click on tags to see related threads")
    print("4. The political line is now navigable!")

if __name__ == "__main__":
    main()