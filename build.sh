#!/bin/bash
# build.sh - Build site with environment configuration

# Set environment
export ENVIRONMENT=${1:-development}

# Load environment variables
source .env

# Build based on environment
case $ENVIRONMENT in
  development)
    mkdocs serve --config-file mkdocs.yml
    ;;
  staging)
    mkdocs build --config-file mkdocs.yml --site-dir site-staging
    ;;
  production)
    mkdocs build --config-file mkdocs.yml --strict
    ;;
esac
