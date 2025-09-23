#!/bin/bash
# Install SpaCy model after uv sync

echo "Installing SpaCy en_core_web_lg model..."
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl

if [ $? -eq 0 ]; then
    echo "✅ SpaCy model installed successfully!"
else
    echo "❌ Failed to install SpaCy model"
    exit 1
fi