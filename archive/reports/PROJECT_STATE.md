# AstraDocs Project State

*Last updated: 2025-09-21 19:06*

## Project Memory / Session Context

### Core Project Goal
Transform Twitter/X data export from @BmoreOrganized into a curated MkDocs knowledge base, extracting philosophical and political threads to create a permanent, searchable collection of serious intellectual content.

### Archive Statistics
- **Total tweets**: 21,723
- **Liked tweets**: 88,679
- **Followers**: 4,900
- **Following**: 2,005
- **Blocked accounts**: 412
- **Archive size**: 1.9GB
- **Data files**: 83 JavaScript files
- **Archive date**: September 21, 2025

### Current Phase: Initial Setup and Data Structure Analysis
**Status**: In Progress - Infrastructure and analysis phase

### Key Decisions Made
1. **Technology Stack**: Python-based pipeline with MkDocs Material theme
2. **AI Classification**: Using Anthropic/OpenAI for content filtering
3. **Architecture**: Batch processing with checkpoint system for large archive
4. **Content Strategy**: Selective curation focusing on serious philosophical/political content
5. **Thread Preservation**: Maintain original structure and chronology

### Project Structure (Current)
```
/home/percy/projects/astradocs/
├── .venv/                          # Python virtual environment
├── twitter-archives/               # 1.9GB Twitter data export
│   ├── Your archive.html          # Browser-based archive viewer
│   ├── data/                      # 83 JS data files
│   │   ├── tweets.js              # 21,723 tweets (primary data)
│   │   ├── likes.js               # 88,679 liked tweets
│   │   └── [various].js           # Other data categories
│   └── assets/                    # Static viewer assets
├── twitter-pipeline-docs/          # Phase analysis documentation
│   ├── 00-quick-start.md          # Implementation guide
│   ├── 01-data-structure-analysis.md
│   ├── 02-extraction-pipeline.md
│   ├── 03-thread-detection-strategy.md
│   ├── 04-classification-approach.md
│   ├── 05-implementation-plan.md
│   └── 06-technical-specifications.md
├── analyze_twitter_structure.py    # Archive analysis script
├── main.py                        # Entry point (minimal)
├── pyproject.toml                 # Python dependencies
├── twitter-to-mkdocs-project.md   # Comprehensive project specification
├── CLAUDE.md                      # Claude Code instructions
└── PROJECT_STATE.md              # This file (project memory)
```

### Dependencies Status
- **Python**: 3.12+ required
- **Key libraries**: Anthropic, MkDocs Material, ijson, pandas, nltk
- **Environment**: Virtual environment active (.venv)
- **Configuration**: Basic pyproject.toml in place

### Implementation Progress

#### ✅ Completed
1. **Project Structure**: Basic file organization established
2. **Dependencies**: Core Python dependencies defined in pyproject.toml
3. **Archive Analysis**: Structure understanding documented
4. **Pipeline Documentation**: Comprehensive 6-phase analysis completed
5. **Technical Specification**: Detailed architecture and implementation plan

#### 🔄 In Progress
1. **Archive Structure Analysis**: Understanding Twitter export format
2. **Data Extraction Logic**: Parsing JavaScript-wrapped JSON files
3. **Environment Setup**: Python virtual environment configured

#### ⏳ Pending
1. **Core Pipeline Implementation**: Python modules for extraction/classification
2. **Thread Detection**: Algorithm implementation for reconstructing conversations
3. **AI Classification**: Integration with Anthropic/OpenAI for content filtering
4. **MkDocs Configuration**: Site structure and theme setup
5. **Batch Processing**: Memory-efficient processing for large archive
6. **Deployment**: GitHub Pages integration

### Technical Architecture Status

#### Phase 1: Archive Extraction & Parsing
- **Status**: Design complete, implementation pending
- **Approach**: Stream processing with ijson for memory efficiency
- **Challenge**: JavaScript wrapper around JSON data (`window.YTD.tweets.part0 = [...]`)

#### Phase 2: Thread Reconstruction
- **Status**: Strategy documented, implementation pending
- **Approach**: Multi-strategy thread detection (conversation_id, reply chains, temporal clustering)
- **Complexity**: High - critical for content coherence

#### Phase 3: Content Classification
- **Status**: Prompt templates and criteria defined
- **Approach**: AI-powered classification with confidence scoring
- **Integration**: Anthropic Claude API preferred

#### Phase 4: Batch Processing
- **Status**: Memory optimization strategies defined
- **Approach**: Checkpoint system with configurable batch sizes
- **Priority**: Essential for 1.9GB archive processing

#### Phase 5: Tagging & Organization
- **Status**: Taxonomy designed, implementation pending
- **Approach**: Hierarchical tag structure for philosophy/politics
- **Output**: Structured markdown with frontmatter

#### Phase 6: MkDocs Generation
- **Status**: Configuration templates ready
- **Theme**: Material for MkDocs with search and navigation
- **Deployment**: GitHub Pages workflow defined

### Next Session Priorities
1. **Complete archive structure analysis** - Run analyze_twitter_structure.py
2. **Implement core extraction module** - Parse JavaScript-wrapped JSON
3. **Set up basic thread detection** - Start with reply chain following
4. **Create minimal working pipeline** - End-to-end proof of concept

### Quality Standards
- **Content Integrity**: No modification of original tweet text
- **Selective Curation**: Filter casual content, preserve serious discourse
- **Thread Continuity**: Maintain chronological and logical flow
- **Professional Output**: Publication-ready markdown with proper metadata

### Risk Factors
1. **Memory constraints**: 1.9GB archive requires efficient streaming
2. **AI classification costs**: Large volume may require budget management
3. **Thread reconstruction accuracy**: Critical for content quality
4. **Processing time**: 21K+ tweets may require significant computation

### Success Metrics
- **Content preservation**: >95% of serious threads successfully extracted
- **Classification accuracy**: >85% confidence in AI filtering
- **Processing efficiency**: <2GB peak memory usage
- **Output quality**: Professional documentation site ready for publication

### MCP Server Status
- **Serena**: Project memory and semantic understanding - *Initialization attempted*
- **Sequential**: Multi-step reasoning for complex analysis - *Available for pipeline logic*
- **Context7**: Documentation and framework patterns - *Available for MkDocs/Python guidance*
- **Magic**: UI components (not primary for this project)
- **Morphllm**: Bulk pattern-based edits - *Useful for markdown generation*
- **Playwright**: Browser automation (limited relevance)

---

*This document serves as persistent project memory across Claude Code sessions, maintaining context and progress for the Twitter-to-MkDocs transformation pipeline.*