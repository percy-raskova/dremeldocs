#!/usr/bin/env python3
"""
Vocabulary loading module for theme classification
Handles loading vocabularies from YAML files and parsing human themes from markdown
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

try:
    from . import security_utils
except ImportError:
    # Support direct imports when not run as package
    import security_utils


class VocabularyLoader:
    """Handles loading and parsing vocabularies and human themes"""

    def __init__(self):
        self.themes: Dict[str, int] = {}
        self.keywords: Dict[str, str] = {}
        self.thread_theme_map: Dict[str, List[int]] = {}

    def load_vocabulary(self, vocab_file: Path) -> Dict[str, Any]:
        """Load vocabulary from YAML file for enhanced classification"""
        import yaml

        if not vocab_file.exists():
            print(f"⚠️  Vocabulary file not found: {vocab_file}")
            return {}

        with security_utils.safe_open(vocab_file, encoding="utf-8") as f:
            vocabulary = yaml.safe_load(f)

        print(f"✅ Loaded vocabulary with {len(vocabulary)} categories")
        return vocabulary

    def load_human_themes(self, themes_file: Path) -> bool:
        """Load the human-extracted themes from manual review"""
        if not themes_file.exists():
            print(f"❌ Theme file not found: {themes_file}")
            print("   Please complete your review and save as THEMES_EXTRACTED.md")
            return False

        print(f"📖 Loading themes from {themes_file}")

        # Parse your filled-out template
        # Extract themes, keywords, and thread mappings
        with security_utils.safe_open(themes_file, encoding="utf-8") as f:
            content = f.read()

        # Parse sections
        self._parse_theme_sections(content)
        self._parse_keywords(content)
        self._parse_thread_mappings(content)

        return True

    def _parse_theme_sections(self, content: str) -> None:
        """Extract theme categories and weights from the document"""
        # Flexible parser that looks for patterns
        theme_pattern = r"\[x\]\s+\*{0,2}([^:*]+)\*{0,2}:\s*(\d+)?"
        matches = re.findall(theme_pattern, content)

        for theme, weight in matches:
            # Clean up the theme name - remove asterisks and normalize
            theme = theme.strip().strip("*").lower()
            # Replace forward slashes and spaces with underscores for URL/directory safety
            theme = theme.replace("/", "_").replace(" ", "_")
            weight = int(weight) if weight else 1
            self.themes[theme] = weight
            print(f"  Found theme: {theme} (weight: {weight})")

    def _parse_keywords(self, content: str) -> None:
        """Extract vocabulary from the Keywords section"""
        keywords_section = re.search(
            r"Keywords/Phrases You Actually Use.*?\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL,
        )

        if keywords_section:
            lines = keywords_section.group(1).strip().split("\n")
            for line in lines:
                # Remove bullet points and quotes
                keyword = re.sub(r'^[-*]\s*"|"$', "", line.strip())
                if keyword and not keyword.startswith("your actual"):
                    # Assign keywords to most relevant themes based on context
                    self.keywords[keyword.lower()] = keyword
                    print(f"  Found keyword: {keyword}")

    def _parse_thread_mappings(self, content: str) -> None:
        """Extract which threads exemplify which themes"""
        mapping_section = re.search(
            r"Thread-Theme Mapping.*?\n(.*?)(?=\n##|\Z)", content, re.DOTALL
        )

        if mapping_section:
            lines = mapping_section.group(1).strip().split("\n")
            for line in lines:
                # Parse lines like "Marxism: Threads #3, #7, #15"
                # Handle optional bullet points (-, *)
                match = re.match(r"[-*]?\s*([^:]+):\s*Threads?\s*(.*)", line)
                if match:
                    # Normalize theme name to match theme parsing
                    theme = match.group(1).strip()
                    # Remove any remaining asterisks or dashes at the start
                    theme = theme.lstrip("*- ").strip().lower()
                    theme = theme.replace("/", "_").replace(" ", "_")
                    thread_nums = re.findall(r"#(\d+)", match.group(2))
                    self.thread_theme_map[theme] = [int(n) for n in thread_nums]
                    print(f"  Mapped {theme} to threads: {thread_nums}")

    def get_themes(self) -> Dict[str, int]:
        """Get loaded themes dictionary"""
        return self.themes

    def get_keywords(self) -> Dict[str, str]:
        """Get loaded keywords dictionary"""
        return self.keywords

    def get_thread_theme_map(self) -> Dict[str, List[int]]:
        """Get thread theme mapping dictionary"""
        return self.thread_theme_map