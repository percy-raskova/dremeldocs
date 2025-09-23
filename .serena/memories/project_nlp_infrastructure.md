# NLP Infrastructure - Astradocs Project

## Current Setup

### SpaCy Pipeline
- **Model**: en_core_web_lg (Large model, 685k vocabulary)
- **Location**: scripts/text_processing.py
- **Performance**: 10k tokens/sec

### Core Components

#### EnhancedTagExtractor
```python
# Located in scripts/text_processing.py
- DomainVocabulary: Political/philosophical terms
- PatternMatcher: Theory patterns ("theory of X")
- ChunkScorer: Multi-factor scoring
- Semantic similarity calculation
```

#### Configuration
- **File**: config/nlp_settings.yaml
- **Domain Terms**: 70+ categorized terms
  - political_theory: marxism, capitalism, imperialism
  - philosophy: dialectical, materialism, praxis
  - social_movements: solidarity, liberation, resistance

#### Key Functions
- `generate_title()`: Extracts conceptual titles from text
- `extract_entities()`: Enhanced tag extraction with domain awareness
- `generate_filename()`: Smart filename generation
- `format_frontmatter_value()`: YAML-safe formatting

### Testing Infrastructure
- **Unit Tests**: tests/unit/test_text_processing.py
- **Fixtures**: tests/fixtures/sample_data.py
- **Coverage**: 27% on scripts (90% on generate_heavy_hitters.py)

### Generation Pipeline
- **Script**: scripts/generate_heavy_hitters.py
- **Input**: data/filtered_threads.json
- **Output**: docs/heavy_hitters/*.md (59 files)
- **Features**: Frontmatter generation, navigation links, index creation

## Usage Patterns

### Regenerating Heavy Hitters
```bash
uv run python scripts/generate_heavy_hitters.py
```

### Testing NLP Performance
```bash
uv run python scripts/test_transformer_power.py
```

### Running Tests
```bash
uv run pytest tests/unit/test_text_processing.py
```

## Model Management

### Installation
```bash
# Large model (current)
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl

# Transformer (alternative)
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0-py3-none-any.whl
```

### Fallback Chain
1. Try Large (lg) - best vocabulary
2. Try Transformer (trf) - contextual understanding  
3. Try Medium (md) - basic vectors
4. Use Small (sm) - minimal functionality

## Quality Metrics
- Title extraction: Conceptual phrases vs first sentences
- Tag quality: Domain-specific terms vs generic words
- Semantic similarity: 77.6% for related concepts
- Processing speed: ~10k tokens/second