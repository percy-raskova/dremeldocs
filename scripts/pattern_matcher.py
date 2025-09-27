#!/usr/bin/env python3
"""
Pattern matching module for theme classification
Handles pattern compilation, builtin patterns, and theme scoring
"""

import re
from typing import Any, Dict, List


class PatternMatcher:
    """Handles pattern-based text matching and scoring for theme classification"""

    def __init__(self):
        self.pattern_matchers: Dict[str, List] = {}

    def compile_patterns(self, vocabulary: Dict[str, Any]) -> None:
        """Compile regex patterns from vocabulary for efficient matching"""
        self.pattern_matchers.clear()

        for category, data in vocabulary.items():
            if "patterns" in data and isinstance(data["patterns"], list):
                self.pattern_matchers[category] = [
                    re.compile(pattern, re.IGNORECASE) for pattern in data["patterns"]
                ]

    def get_builtin_patterns(self) -> Dict[str, Any]:
        """Return built-in patterns when no vocabulary is loaded"""
        return {
            "organizing": {
                "terms": [
                    "vanguard party",
                    "mass work",
                    "democratic centralism",
                    "party discipline",
                    "organization",
                    "revolutionary",
                ],
                "patterns": [
                    r"\bvanguard\s+party\b",
                    r"\bmass\s+work\b",
                    r"\bdemocratic\s+centralism\b",
                    r"\brevolutionary\s+organization\b",
                ],
                "score_threshold": 0.3,
            },
            "marxism": {
                "terms": [
                    "class struggle",
                    "proletariat",
                    "bourgeoisie",
                    "means of production",
                    "working class",
                    "proletarian",
                    "revolutionary",
                    "class",
                ],
                "patterns": [
                    r"\bclass\s+struggle\b",
                    r"\bproletariat\b",
                    r"\bbourgeoisie\b",
                    r"\bproletarian\b",
                    r"\brevolutionary\b",
                    r"\bworking\s+class\b",
                    r"\bmeans\s+of\s+production\b",
                ],
                "score_threshold": 0.3,
            },
            "colonialism": {
                "terms": ["settler colonial", "colonialism", "indigenous", "native"],
                "patterns": [r"\bsettler\s+colonial\b", r"\bcolonialis[mt]\b"],
                "score_threshold": 0.3,
            },
            "race": {
                "terms": ["racial hierarchy", "racism", "racial oppression", "racial"],
                "patterns": [r"\bracial\s+\w+", r"\bracis[mt]\b"],
                "score_threshold": 0.3,
            },
            "philosophy": {
                "terms": [
                    "consciousness",
                    "material conditions",
                    "dialectical reasoning",
                    "praxis",
                ],
                "patterns": [r"\bconsciousness\b", r"\bpraxis\b"],
                "score_threshold": 0.3,
            },
        }

    def calculate_theme_score(self, text: str, theme: str) -> float:
        """Calculate how strongly a text matches a theme based on keywords"""
        score = 0.0
        text_lower = text.lower()

        # Map themes to their relevant keywords
        theme_keywords = {
            "marxism_historical materialism": [
                "marx",
                "class",
                "proletariat",
                "bourgeois",
                "capital",
                "labor",
                "surplus",
                "material",
            ],
            "fascism analysis": [
                "fascis",
                "authoritarian",
                "reaction",
                "nationalist",
                "totalitarian",
            ],
            "political economy": [
                "economy",
                "economic",
                "market",
                "capital",
                "production",
                "commodity",
                "value",
            ],
            "imperialism_colonialism": [
                "imperial",
                "colonial",
                "empire",
                "settler",
                "occupation",
                "extraction",
            ],
            "dialectics": [
                "dialectic",
                "thesis",
                "antithesis",
                "synthesis",
                "contradiction",
                "negation",
            ],
            "cultural criticism": [
                "culture",
                "cultural",
                "ideology",
                "hegemony",
                "discourse",
                "representation",
            ],
            "covid_public health politics": [
                "covid",
                "pandemic",
                "vaccine",
                "lockdown",
                "public health",
                "virus",
            ],
            "organizational theory": [
                "organiz",
                "union",
                "party",
                "movement",
                "solidarity",
                "collective",
            ],
        }

        # Check if this theme has keywords defined
        if theme in theme_keywords:
            for keyword in theme_keywords[theme]:
                if keyword in text_lower:
                    score += 0.2  # Increase score for each matching keyword

        # Also check if the theme name itself appears in text
        theme_parts = theme.replace("_", " ").split()
        for part in theme_parts:
            if len(part) > 3 and part in text_lower:  # Skip short words
                score += 0.15

        return min(score, 1.0)

    def find_pattern_matches(self, text: str, category: str, matched_terms: set) -> tuple[int, float]:
        """Find pattern matches for a category, avoiding double counting with terms"""
        matches = 0
        score = 0.0

        if category in self.pattern_matchers:
            for pattern in self.pattern_matchers[category]:
                pattern_matches = pattern.findall(text)
                for match in pattern_matches:
                    # Only count pattern match if it doesn't overlap with term matches
                    match_text = (
                        match.lower()
                        if isinstance(match, str)
                        else " ".join(match).lower()
                    )
                    if not any(
                        term in match_text or match_text in term
                        for term in matched_terms
                    ):
                        matches += 1
                        score += 0.8  # Patterns slightly less weight than exact terms

        return matches, score