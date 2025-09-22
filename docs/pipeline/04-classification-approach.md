# AI Classification Approach

## Classification Goals

Separate serious philosophical/political content from casual posts, memes, and "shitposting" while preserving the integrity of theoretical discourse.

## Classification Pipeline

### Step 1: Pre-filtering Rules

```python
class PreFilter:
    """Rule-based pre-filtering before AI classification"""
    
    def __init__(self):
        # Keywords that strongly suggest serious content
        self.philosophical_markers = [
            'epistemology', 'ontology', 'metaphysics', 'phenomenology',
            'dialectic', 'praxis', 'hermeneutics', 'existential',
            'categorical imperative', 'being', 'consciousness'
        ]
        
        self.political_markers = [
            'political economy', 'capitalism', 'socialism', 'neoliberal',
            'hegemony', 'ideology', 'labor', 'class', 'material conditions',
            'means of production', 'imperialism', 'sovereignty'
        ]
        
        # Patterns that suggest casual content
        self.casual_markers = [
            'lol', 'lmao', 'wtf', 'based', 'cringe', 
            '😂', '💀', '🤣',  # Emoji patterns
            'ratio', 'L + ratio', 'touch grass'
        ]
        
        # Minimum requirements
        self.min_thread_length = 3  # tweets
        self.min_word_count = 100  # words total
        
    def pre_classify(self, thread: List[Dict]) -> Dict[str, Any]:
        """Initial classification based on rules"""
        
        full_text = ' '.join([t['text'] for t in thread])
        word_count = len(full_text.split())
        
        # Check for philosophical/political markers
        philosophical_score = sum(
            1 for marker in self.philosophical_markers 
            if marker.lower() in full_text.lower()
        )
        
        political_score = sum(
            1 for marker in self.political_markers 
            if marker.lower() in full_text.lower()
        )
        
        casual_score = sum(
            1 for marker in self.casual_markers 
            if marker in full_text
        )
        
        # Initial classification
        likely_serious = (
            (philosophical_score > 0 or political_score > 0) and
            casual_score < 3 and
            word_count >= self.min_word_count
        )
        
        return {
            'likely_serious': likely_serious,
            'philosophical_score': philosophical_score,
            'political_score': political_score,
            'casual_score': casual_score,
            'word_count': word_count,
            'confidence': 'high' if philosophical_score + political_score > 3 else 'low'
        }
```

### Step 2: AI Classification Prompts

```python
class AIClassifier:
    def __init__(self, api_key: str, model: str = "claude-3-opus"):
        self.api_key = api_key
        self.model = model
        
    def create_classification_prompt(self, thread: List[Dict]) -> str:
        """Create prompt for AI classification"""
        
        # Concatenate thread text
        thread_text = '\n---\n'.join([
            f"Tweet {i+1}: {tweet['text']}" 
            for i, tweet in enumerate(thread)
        ])
        
        prompt = f"""Analyze this Twitter thread to determine if it contains serious philosophical, political, or theoretical content.

Thread:
{thread_text}

Classification criteria:
1. SERIOUS content includes:
   - Philosophical arguments or explorations
   - Political theory or analysis  
   - Social criticism with substantive argumentation
   - Theoretical discussions of any academic field
   - Historical analysis with interpretive framework
   - Essays or long-form thoughts on complex topics

2. CASUAL content includes:
   - Jokes, memes, shitposts
   - Personal anecdotes without broader analysis
   - Simple observations without theoretical framework
   - Reactions to current events without deep analysis
   - Social interactions and replies

3. Edge cases:
   - Satirical political commentary: Include if substantive argument underneath
   - Pop culture analysis: Include if using philosophical/theoretical framework
   - Mixed threads: Include if majority is serious content

Respond with JSON:
{{
    "classification": "serious" or "casual",
    "confidence": 0.0 to 1.0,
    "primary_domain": "philosophy" or "politics" or "theory" or "other" or null,
    "key_concepts": ["list", "of", "main", "concepts"],
    "reasoning": "Brief explanation of classification decision"
}}

Remember: When uncertain, err on the side of inclusion (classify as serious)."""
        
        return prompt
    
    async def classify_thread(self, thread: List[Dict]) -> Dict[str, Any]:
        """Send thread to AI for classification"""
        import aiohttp
        import json
        
        prompt = self.create_classification_prompt(thread)
        
        # Example for Claude API
        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 500,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            ) as response:
                result = await response.json()
                
        # Parse AI response
        try:
            classification = json.loads(result['content'][0]['text'])
            return classification
        except:
            # Fallback if parsing fails
            return {
                "classification": "serious",  # Default to inclusion
                "confidence": 0.5,
                "reasoning": "Failed to parse AI response"
            }
```

### Step 3: Batch Processing with Rate Limiting

```python
import asyncio
from typing import List, Dict
import time

class BatchClassifier:
    def __init__(self, classifier: AIClassifier, rate_limit: int = 10):
        self.classifier = classifier
        self.rate_limit = rate_limit  # requests per minute
        self.last_request_time = 0
        
    async def classify_batch(self, threads: List[List[Dict]]) -> List[Dict]:
        """Classify multiple threads with rate limiting"""
        
        classifications = []
        
        for i, thread in enumerate(threads):
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Pre-filter
            pre_filter = PreFilter()
            pre_result = pre_filter.pre_classify(thread)
            
            # Skip obvious cases
            if pre_result['confidence'] == 'high':
                if pre_result['likely_serious']:
                    classification = {
                        'classification': 'serious',
                        'confidence': 0.9,
                        'method': 'pre_filter',
                        'reasoning': 'High confidence from keyword analysis'
                    }
                else:
                    classification = {
                        'classification': 'casual',
                        'confidence': 0.9,
                        'method': 'pre_filter',
                        'reasoning': 'Too short or too casual'
                    }
            else:
                # Need AI classification
                classification = await self.classifier.classify_thread(thread)
                classification['method'] = 'ai'
            
            # Add pre-filter scores to classification
            classification['pre_filter_scores'] = pre_result
            classifications.append(classification)
            
            # Progress logging
            if i % 10 == 0:
                print(f"Classified {i}/{len(threads)} threads")
        
        return classifications
    
    async def _enforce_rate_limit(self):
        """Ensure we don't exceed rate limit"""
        min_interval = 60.0 / self.rate_limit
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        self.last_request_time = time.time()
```

### Step 4: Tag Generation

```python
class TagGenerator:
    def __init__(self):
        self.tag_taxonomy = {
            'philosophy': {
                'metaphysics': ['ontology', 'being', 'existence', 'reality'],
                'epistemology': ['knowledge', 'truth', 'belief', 'skepticism'],
                'ethics': ['moral', 'virtue', 'duty', 'consequentialism'],
                'aesthetics': ['beauty', 'art', 'sublime', 'taste'],
                'logic': ['reasoning', 'argument', 'fallacy', 'proof']
            },
            'politics': {
                'theory': ['democracy', 'anarchism', 'marxism', 'liberalism'],
                'economy': ['capitalism', 'socialism', 'labor', 'class'],
                'power': ['authority', 'sovereignty', 'hegemony', 'resistance'],
                'justice': ['equality', 'rights', 'freedom', 'oppression']
            },
            'interdisciplinary': [
                'critical-theory',
                'political-economy', 
                'philosophy-of-mind',
                'social-philosophy'
            ]
        }
    
    def generate_tags(self, thread: List[Dict], classification: Dict) -> List[str]:
        """Generate tags based on content analysis"""
        
        full_text = ' '.join([t['text'] for t in thread]).lower()
        tags = []
        
        # Primary domain tag
        if classification.get('primary_domain'):
            tags.append(classification['primary_domain'])
        
        # Check taxonomy
        for category, subcategories in self.tag_taxonomy.items():
            if isinstance(subcategories, dict):
                for subtag, keywords in subcategories.items():
                    if any(keyword in full_text for keyword in keywords):
                        tags.append(f"{category}-{subtag}")
            else:
                # Interdisciplinary tags
                for tag in subcategories:
                    if tag.replace('-', ' ') in full_text:
                        tags.append(tag)
        
        # Add concept tags from AI classification
        if 'key_concepts' in classification:
            for concept in classification['key_concepts'][:3]:  # Limit to 3
                if concept.lower() not in tags:
                    tags.append(concept.lower().replace(' ', '-'))
        
        # Limit total tags
        return tags[:5]
```

## Complete Classification Pipeline

```python
class ClassificationPipeline:
    def __init__(self, api_key: str):
        self.pre_filter = PreFilter()
        self.ai_classifier = AIClassifier(api_key)
        self.batch_classifier = BatchClassifier(self.ai_classifier)
        self.tag_generator = TagGenerator()
        
    async def process_threads(self, threads: List[List[Dict]]) -> Dict[str, Any]:
        """Complete classification pipeline"""
        
        print(f"Starting classification of {len(threads)} threads")
        
        # Classify all threads
        classifications = await self.batch_classifier.classify_batch(threads)
        
        # Process results
        serious_threads = []
        casual_threads = []
        
        for thread, classification in zip(threads, classifications):
            # Generate tags for serious content
            if classification['classification'] == 'serious':
                tags = self.tag_generator.generate_tags(thread, classification)
                
                thread_data = {
                    'thread': thread,
                    'classification': classification,
                    'tags': tags,
                    'word_count': sum(len(t['text'].split()) for t in thread),
                    'tweet_count': len(thread)
                }
                serious_threads.append(thread_data)
            else:
                casual_threads.append(thread)
        
        # Generate statistics
        stats = {
            'total_threads': len(threads),
            'serious_threads': len(serious_threads),
            'casual_threads': len(casual_threads),
            'classification_methods': {
                'pre_filter': sum(1 for c in classifications if c.get('method') == 'pre_filter'),
                'ai': sum(1 for c in classifications if c.get('method') == 'ai')
            },
            'average_confidence': sum(c['confidence'] for c in classifications) / len(classifications),
            'tag_distribution': self._calculate_tag_distribution(serious_threads)
        }
        
        return {
            'serious_threads': serious_threads,
            'casual_threads': casual_threads,
            'statistics': stats
        }
    
    def _calculate_tag_distribution(self, threads: List[Dict]) -> Dict[str, int]:
        """Count tag frequency"""
        from collections import Counter
        
        all_tags = []
        for thread in threads:
            all_tags.extend(thread['tags'])
        
        return dict(Counter(all_tags))
```

## Configuration File

```yaml
# classification_config.yaml
classification:
  # Pre-filter settings
  pre_filter:
    min_thread_length: 3
    min_word_count: 100
    confidence_threshold: 0.7
    
  # AI settings
  ai:
    model: "claude-3-opus"  # or "gpt-4"
    temperature: 0.3  # Lower = more consistent
    max_tokens: 500
    rate_limit: 10  # requests per minute
    
  # Classification thresholds
  thresholds:
    inclusion_confidence: 0.5  # Include if confidence >= this
    high_confidence: 0.8
    
  # Tag settings
  tagging:
    max_tags_per_thread: 5
    min_tag_frequency: 2  # Minimum occurrences to keep tag
    
  # Edge case handling
  edge_cases:
    include_mixed_threads: true
    mixed_thread_serious_threshold: 0.6  # 60% serious content
    include_satirical: true
    include_theoretical_popculture: true
```

## Quality Assurance

```python
class ClassificationValidator:
    """Validate classification quality"""
    
    def sample_for_review(self, classified_threads: List[Dict], sample_size: int = 20):
        """Select sample for manual review"""
        import random
        
        # Get range of confidence scores
        low_confidence = [t for t in classified_threads if t['classification']['confidence'] < 0.6]
        high_confidence = [t for t in classified_threads if t['classification']['confidence'] > 0.8]
        
        sample = {
            'low_confidence_sample': random.sample(low_confidence, min(10, len(low_confidence))),
            'high_confidence_sample': random.sample(high_confidence, min(10, len(high_confidence))),
            'total_reviewed': min(sample_size, len(classified_threads))
        }
        
        return sample
```

This classification approach balances automation with accuracy, using rule-based pre-filtering for obvious cases and AI for nuanced decisions.
