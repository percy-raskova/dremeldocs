# Git Workflow Guide for Astradocs

## Quick Setup

Run the setup script to configure Git for this project:
```bash
./setup-git.sh
```

## Daily Workflow

### 1. Starting Work
```bash
# Always start from main
git checkout main
git pull origin main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Making Changes
```bash
# Check status frequently
git st  # alias for status -sb

# Stage changes
git add -p  # Interactive staging (recommended)
# or
git add specific-file.py

# Commit with template
git commit  # Opens editor with template
# or for quick commits
git cm "type: short description"
```

### 3. Commit Message Format

We follow a relaxed conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```bash
git cm "feat(nlp): add semantic similarity scoring"
git cm "fix(tests): update expectations for NLP changes"
git cm "docs: add git workflow guide"
```

### 4. Git Hooks

The project includes helpful git hooks:

**Pre-commit:**
- ✅ Python syntax checking
- ✅ Large file detection (warns >1MB, blocks >10MB)
- ✅ Merge conflict marker detection
- ⚠️ Sensitive information warning (api_key, password, etc.)
- ℹ️ TODO/FIXME counter

**Commit-msg:**
- 💡 Suggests conventional commit format (doesn't enforce)
- ⚠️ Warns about long commit messages (>80 chars)
- ✅ Detects issue references

## Useful Commands

### Aliases
```bash
git st         # Compact status
git co <branch> # Checkout
git br         # List branches
git cm "msg"   # Quick commit
git last       # Show last commit
git visual     # Pretty log graph
git unstage    # Unstage files
```

### Common Tasks
```bash
# Undo last commit (keep changes)
git reset HEAD~1

# Amend last commit
git commit --amend

# Interactive rebase (last 3 commits)
git rebase -i HEAD~3

# Stash changes
git stash
git stash pop

# See what changed
git diff           # Unstaged changes
git diff --staged  # Staged changes
git diff main...   # All changes vs main
```

## File Management

### What's Ignored (.gitignore)
- Python caches (`__pycache__/`, `*.pyc`)
- Virtual environments (`.venv/`)
- Test artifacts (`.coverage`, `htmlcov/`)
- IDE files (`.vscode/`, `.idea/`)
- Environment files (`.env`)
- Temporary files (`*.tmp`, `*.log`)
- Large data files

### Line Ending Consistency (.gitattributes)
- All text files use LF line endings
- Binary files properly marked
- Python/Markdown get special diff handling

### Editor Settings (.editorconfig)
- Python: 4 spaces, max 100 chars
- JSON/YAML: 2 spaces
- Markdown: preserve trailing spaces
- Automatic trimming of trailing whitespace

## Best Practices

1. **Commit Often**: Small, focused commits are better than large ones
2. **Write Good Messages**: Your future self will thank you
3. **Branch for Features**: Keep main clean
4. **Pull Before Push**: Always sync before pushing
5. **Review Before Commit**: Use `git diff --staged` to review

## Troubleshooting

### Pre-commit Hook Fails
```bash
# Bypass hooks if needed (use sparingly!)
git commit --no-verify
```

### Large Files
```bash
# If you accidentally committed a large file
git rm --cached large-file.dat
git commit -m "chore: remove large file"
```

### Merge Conflicts
```bash
# Use rerere (enabled by setup script)
git config rerere.enabled true
# Git will remember how you resolved conflicts
```

## Additional Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

Remember: This is a hobbyist project! The rules are guidelines, not strict requirements. The goal is to make collaboration easier and keep the codebase clean, not to create bureaucracy.