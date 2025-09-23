#!/bin/bash
# Git configuration setup for astradocs project

echo "🔧 Setting up Git configuration for astradocs..."

# Set up commit message template (local to this repo)
git config --local commit.template .gitmessage
echo "✅ Commit message template configured"

# Optional: Set up some useful aliases (local to this repo)
git config --local alias.st "status -sb"
git config --local alias.co "checkout"
git config --local alias.br "branch"
git config --local alias.cm "commit -m"
git config --local alias.last "log -1 HEAD"
git config --local alias.unstage "reset HEAD --"
git config --local alias.visual "log --graph --oneline --decorate --all"
echo "✅ Helpful Git aliases configured"

# Set default branch name to 'main' (local)
git config --local init.defaultBranch main

# Enable rerere (reuse recorded resolution) for merge conflicts
git config --local rerere.enabled true

echo ""
echo "📝 Git configuration complete! Quick reference:"
echo ""
echo "Aliases configured:"
echo "  git st     → status (short format)"
echo "  git co     → checkout"
echo "  git br     → branch"
echo "  git cm     → commit -m"
echo "  git last   → show last commit"
echo "  git visual → visual log graph"
echo ""
echo "Hooks installed:"
echo "  pre-commit  → Python syntax, large files, secrets check"
echo "  commit-msg  → Conventional commit format suggestions"
echo ""
echo "To use the commit template, just run 'git commit' without -m"
echo ""