# AstraDocs Project Documentation

This directory contains documentation for the AstraDocs project - a pipeline for transforming @BmoreOrganized's Twitter archive into a curated MkDocs knowledge base.

## Contents

- `pipeline/` - Original pipeline design and implementation docs
- `setup.md` - Installation and setup instructions
- `workflow.md` - How to use the processing pipeline

## Key Distinction

- `docs/` - Project documentation (you are here)
- `markdown/` - MkDocs content source (the actual website content)
- `site/` - MkDocs HTML output (generated, gitignored)

## Processing Pipeline

1. **Extract**: Stream process 37MB tweets.js file
2. **Filter**: Apply 2-stage local filtering (length + thread detection)
3. **Review**: Manual theme extraction from heavy hitters (500+ words)
4. **Classify**: Apply extracted themes to all threads
5. **Generate**: Create markdown files organized by theme
6. **Publish**: Build and deploy with MkDocs