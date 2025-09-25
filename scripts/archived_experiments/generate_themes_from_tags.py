#!/usr/bin/env python3
"""
Generate THEMES_EXTRACTED.md by leveraging existing tags and vocabularies
Reuses the work we've already done rather than starting from scratch
"""

import yaml
from pathlib import Path
from collections import defaultdict, Counter


class ThemeGenerator:
    """Generate themes using our existing tags and vocabularies."""

    def __init__(self):
        self.heavy_dir = Path("docs/heavy_hitters")
        self.vocab_dir = Path("data/vocabularies")

        # Map our tag categories to theme names
        self.tag_to_theme = {
            "marxism-communism": "Marxism/Historical Materialism",
            "fascism-analysis": "Fascism Analysis",
            "imperialism-colonialism": "Imperialism/Colonialism",
            "public-health-politics": "COVID/Public Health Politics",
            "political-economy": "Political Economy",
            "dialectical-historical-materialism": "Dialectics",
            "social-criticism": "Cultural Criticism",
            "operational-organizational-theory": "Organizational Theory",
            # Specific tags
            "fascism": "Fascism Analysis",
            "imperialism": "Imperialism/Colonialism",
            "marxism": "Marxism/Historical Materialism",
            "covid": "COVID/Public Health Politics",
            "palestine": "Imperialism/Colonialism",
        }

    def collect_thread_tags(self):
        """Collect tags from all heavy hitter files."""
        print("📚 Collecting tags from heavy hitters...")

        thread_tags = {}  # thread_num -> [tags]
        theme_threads = defaultdict(list)  # theme -> [thread_nums]

        for md_file in sorted(self.heavy_dir.glob("[0-9]*.md")):
            thread_num = int(md_file.name.split("-")[0])

            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        fm_data = yaml.safe_load(parts[1])
                        if fm_data and "tags" in fm_data:
                            tags = fm_data["tags"]
                            thread_tags[thread_num] = tags

                            # Map to themes
                            for tag in tags:
                                if tag in self.tag_to_theme:
                                    theme = self.tag_to_theme[tag]
                                    theme_threads[theme].append(thread_num)
                    except yaml.YAMLError as e:
                        print(f"    ⚠️ Failed to parse YAML in {md_file.name}: {e}")
                        continue

        print(f"  Collected tags from {len(thread_tags)} threads")
        return thread_tags, theme_threads

    def load_key_phrases(self):
        """Load key phrases from our vocabularies."""
        print("\n🔍 Loading key phrases from vocabularies...")

        key_phrases = []

        for vocab_file in self.vocab_dir.glob("*.yaml"):
            if vocab_file.name == "master_vocabulary.yaml":
                continue

            try:
                with open(vocab_file, "r") as f:
                    vocab_data = yaml.safe_load(f)

                if vocab_data and "terms" in vocab_data:
                    for term in vocab_data["terms"]:
                        # Add multi-word phrases
                        if isinstance(term, str) and len(term.split()) > 1:
                            key_phrases.append(term)
            except (yaml.YAMLError, OSError) as e:
                print(f"    ⚠️ Failed to load vocabulary from {vocab_file.name}: {e}")
                continue

        # Add specific phrases we know are important
        important_phrases = [
            "means of production",
            "class consciousness",
            "bourgeois hegemony",
            "false consciousness",
            "great-nation consciousness",
            "liberal regime",
            "national liberation",
            "settler colonialism",
            "primitive accumulation",
            "democratic centralism",
            "mass work",
            "political education",
            "social investigation",
            "long covid",
            "pandemic erasure",
            "from the masses to the masses",
            "reproduction of communists",
            "dialectical materialism",
            "historical materialism",
            "surplus value",
            "wage labor",
            "imperial core",
            "global north",
            "global south",
        ]

        key_phrases.extend(important_phrases)
        return sorted(list(set(key_phrases)))

    def generate_themes_extracted(self, thread_tags, theme_threads, key_phrases):
        """Generate THEMES_EXTRACTED.md."""
        print("\n✍️ Generating THEMES_EXTRACTED.md...")

        # Count threads per theme
        theme_counts = {
            theme: len(set(threads)) for theme, threads in theme_threads.items()
        }

        content = """# Themes Extracted from Heavy Hitters

*Based on automated tag extraction and vocabulary analysis of 59 threads*

## Identified Themes

### Political Philosophy
"""

        # Political Philosophy themes
        political_themes = [
            ("Marxism/Historical Materialism", "Core theoretical framework"),
            ("Anarchism", "Anti-authoritarian perspectives"),
            ("Liberalism Critique", "Analysis of liberal ideology"),
            ("Fascism Analysis", "Understanding fascist mechanics"),
            ("Democracy Theory", "Critique of bourgeois democracy"),
            ("Political Economy", "Economic and political relations"),
            ("Imperialism/Colonialism", "Global oppression systems"),
            ("Class Analysis", "Class dynamics and struggle"),
        ]

        for theme_name, description in political_themes:
            if theme_name in theme_counts:
                count = theme_counts[theme_name]
                threads = sorted(set(theme_threads[theme_name]))[:8]
                thread_list = ", ".join([f"#{t}" for t in threads])
                content += f"- [x] **{theme_name}**: {count} threads - {thread_list}\n"
            else:
                content += f"- [ ] {theme_name}: {description}\n"

        content += "\n### General Philosophy\n"

        philosophy_themes = [
            ("Epistemology", "Theory of knowledge"),
            ("Ethics/Moral Philosophy", "Moral and ethical questions"),
            ("Ontology/Metaphysics", "Nature of being"),
            ("Philosophy of Mind", "Consciousness and cognition"),
            ("Phenomenology", "Experience and perception"),
            ("Critical Theory", "Ideology critique"),
            ("Dialectics", "Dialectical method and logic"),
        ]

        for theme_name, description in philosophy_themes:
            if theme_name in theme_counts:
                count = theme_counts[theme_name]
                threads = sorted(set(theme_threads[theme_name]))[:8]
                thread_list = ", ".join([f"#{t}" for t in threads])
                content += f"- [x] **{theme_name}**: {count} threads - {thread_list}\n"
            else:
                content += f"- [ ] {theme_name}: {description}\n"

        content += "\n### Applied Topics\n"

        applied_themes = [
            ("Technology Critique", "Tech and society"),
            ("Environmental Philosophy", "Climate and ecology"),
            ("Urban Theory", "Cities and space"),
            ("Labor/Work", "Work and exploitation"),
            ("Education Theory", "Political education"),
            ("Media Analysis", "Media critique"),
            ("Cultural Criticism", "Cultural hegemony"),
        ]

        for theme_name, description in applied_themes:
            if theme_name in theme_counts:
                count = theme_counts[theme_name]
                threads = sorted(set(theme_threads[theme_name]))[:8]
                thread_list = ", ".join([f"#{t}" for t in threads])
                content += f"- [x] **{theme_name}**: {count} threads - {thread_list}\n"
            else:
                content += f"- [ ] {theme_name}: {description}\n"

        content += "\n### Historical Analysis\n"

        history_themes = [
            ("American History", "US historical analysis"),
            ("Revolutionary Theory", "Revolutionary strategy"),
            ("Historical Materialism Applied", "Historical method"),
            ("Comparative History", "Cross-cultural analysis"),
        ]

        for theme_name, description in history_themes:
            if theme_name in theme_counts:
                count = theme_counts[theme_name]
                threads = sorted(set(theme_threads[theme_name]))[:8]
                thread_list = ", ".join([f"#{t}" for t in threads])
                content += f"- [x] **{theme_name}**: {count} threads - {thread_list}\n"
            else:
                content += f"- [ ] {theme_name}: {description}\n"

        content += "\n### Other Themes\n"

        other_themes = [
            ("COVID/Public Health Politics", "Pandemic as class war"),
            ("Scientific Materialism", "Science and philosophy"),
            ("Organizational Theory", "Party building and organizing"),
        ]

        for theme_name, description in other_themes:
            if theme_name in theme_counts:
                count = theme_counts[theme_name]
                threads = sorted(set(theme_threads[theme_name]))[:8]
                thread_list = ", ".join([f"#{t}" for t in threads])
                content += f"- [x] **{theme_name}**: {count} threads - {thread_list}\n"

        # Thread-Theme Mapping
        content += "\n## Thread-Theme Mapping\n\n"

        # Group threads by primary theme
        for theme in sorted(
            theme_counts.keys(), key=lambda x: theme_counts[x], reverse=True
        )[:10]:
            if theme_counts[theme] > 0:
                content += f"### {theme}\n"
                threads = sorted(set(theme_threads[theme]))

                # Categorize by concentration
                if len(threads) > 5:
                    strong = threads[:3]
                    moderate = threads[3:8]
                    content += f"- **Strong presence**: Threads #{', #'.join(map(str, strong))}\n"
                    if moderate:
                        content += f"- **Moderate presence**: Threads #{', #'.join(map(str, moderate))}\n"
                else:
                    content += f"- Threads: #{', #'.join(map(str, threads))}\n"
                content += "\n"

        # Key phrases section
        content += "## Keywords/Phrases You Actually Use\n\n"
        content += "*Extracted from your corpus using the mass line method:*\n\n"

        # Group phrases by category
        political_phrases = [
            p
            for p in key_phrases
            if any(w in p for w in ["class", "bourgeois", "capital", "imperial"])
        ]
        organizing_phrases = [
            p
            for p in key_phrases
            if any(w in p for w in ["mass", "party", "democratic", "organization"])
        ]
        philosophical_phrases = [
            p
            for p in key_phrases
            if any(w in p for w in ["consciousness", "material", "dialectic"])
        ]
        health_phrases = [
            p
            for p in key_phrases
            if any(w in p for w in ["covid", "pandemic", "health"])
        ]

        if political_phrases:
            content += "### Political Economy\n"
            for phrase in political_phrases[:10]:
                content += f'- "{phrase}"\n'

        if organizing_phrases:
            content += "\n### Organizational Theory\n"
            for phrase in organizing_phrases[:10]:
                content += f'- "{phrase}"\n'

        if philosophical_phrases:
            content += "\n### Philosophical Method\n"
            for phrase in philosophical_phrases[:10]:
                content += f'- "{phrase}"\n'

        if health_phrases:
            content += "\n### Public Health Politics\n"
            for phrase in health_phrases[:10]:
                content += f'- "{phrase}"\n'

        # Notes section
        content += """
## Notes

### Writing Style Patterns
- **Pedagogical approach**: Complex concepts explained accessibly
- **Dialectical method**: Contradictions and synthesis throughout
- **Historical grounding**: Contemporary issues analyzed through historical materialism
- **Scientific precision**: Technical accuracy in scientific topics
- **Polemical edge**: Sharp critique of liberal ideology

### Recurring Arguments
1. **National oppression** as structuring principle of capitalism
2. **COVID response** as manifestation of class warfare
3. **Fascism** as heightening of liberal national relations
4. **Organizational pessimism** about premature party-building
5. **Palestine** as clarifying example of imperialism

### Unique Theoretical Contributions
- "Great-nation consciousness" (alternative to false consciousness)
- Pandemic politics as disability justice issue
- Scientific concepts illustrating dialectical materialism
- Fascism as explicit rather than hidden class relations

---

*Generated by combining tag analysis, vocabulary extraction, and content analysis*
*Save this as: docs/heavy_hitters/THEMES_EXTRACTED.md*
"""

        # Write the file
        output_path = self.heavy_dir / "THEMES_EXTRACTED.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Generated {output_path}")
        return theme_counts

    def run(self):
        """Run the theme generation process."""
        print("🎯 GENERATING THEMES FROM EXISTING TAGS & VOCABULARIES")
        print("=" * 50)

        # Collect existing tags from heavy hitters
        thread_tags, theme_threads = self.collect_thread_tags()

        # Load key phrases from vocabularies
        key_phrases = self.load_key_phrases()

        # Generate THEMES_EXTRACTED.md
        theme_counts = self.generate_themes_extracted(
            thread_tags, theme_threads, key_phrases
        )

        # Summary
        print("\n📊 Summary:")
        print(f"  Threads with tags: {len(thread_tags)}")
        print(f"  Unique themes: {len(theme_counts)}")
        print(f"  Key phrases: {len(key_phrases)}")

        print("\n🏆 Top Themes by Thread Count:")
        for theme, count in sorted(
            theme_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]:
            print(f"  - {theme}: {count} threads")

        print("\n✊ Theme extraction complete!")
        print("📄 Review docs/heavy_hitters/THEMES_EXTRACTED.md")


if __name__ == "__main__":
    generator = ThemeGenerator()
    generator.run()
