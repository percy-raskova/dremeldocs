# AstraDocs Project Overview

## Purpose
Transform a Twitter/X archive (from @BmoreOrganized) into a curated MkDocs-powered knowledge base, extracting philosophical and political threads to create a permanent, searchable collection of serious intellectual content.

## Tech Stack
- **Language**: Python 3.12
- **Framework**: MkDocs with Material theme
- **Key Libraries**: 
  - Data Processing: pandas, ijson, python-dateutil
  - AI Classification: anthropic, openai, tiktoken
  - Documentation: mkdocs, mkdocs-material, pymdown-extensions
  - Utilities: click, loguru, tqdm, pyyaml
- **Deployment**: GitHub Pages

## Project Type
Data transformation pipeline that:
1. Extracts tweets from Twitter archive (JavaScript-wrapped JSON)
2. Reconstructs threads from reply chains
3. Classifies content as serious/casual using AI
4. Generates markdown documentation
5. Builds static site with MkDocs

## Archive Statistics
- Total tweets: 21,723
- Archive size: 1.9GB
- Data files: 83 JavaScript files
- Primary data source: twitter-archives/data/tweets.js