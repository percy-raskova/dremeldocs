# Git Setup Configuration - Astradocs

## Configuration Files

### .gitignore
- Comprehensive Python project patterns
- Virtual environments, test artifacts, IDE files
- Project-specific: .zk/, .serena/cache/, work/, archive/
- Large data files and media directories

### .gitattributes
- Line ending normalization (LF for all text)
- Binary file handling
- Language-specific diff settings
- Export-ignore for test/doc directories

### .editorconfig
- Python: 4 spaces, max 100 chars
- JSON/YAML: 2 spaces
- Markdown: preserve trailing spaces
- Cross-editor consistency

### Git Hooks

#### pre-commit
- Python syntax checking
- Large file detection (warn >1MB, block >10MB)
- Merge conflict marker detection
- Sensitive information warning (api_key, password patterns)
- TODO/FIXME counter (informational)

#### commit-msg
- Conventional commit format suggestions (not enforced)
- Line length warnings (>80 chars)
- Issue reference detection
- Non-blocking for hobbyist flexibility

### Templates

#### .gitmessage
Format:
```
type(scope): subject
[body]
[footer]
```
Types: feat, fix, docs, style, refactor, test, chore, perf

### Setup Script (setup-git.sh)
- Configures commit template
- Sets up git aliases:
  - st → status -sb
  - co → checkout
  - br → branch
  - cm → commit -m
  - last → log -1 HEAD
  - visual → log --graph --oneline --decorate --all
- Enables rerere for conflict resolution

## Usage

### Quick Setup
```bash
./setup-git.sh
```

### Daily Workflow
1. Start from main: `git co main && git pull`
2. Create feature branch: `git co -b feature/name`
3. Stage changes: `git add -p` (interactive)
4. Commit: `git commit` (uses template)
5. Quick commit: `git cm "type: description"`

### Best Practices
- Small, focused commits
- Descriptive commit messages
- Feature branches for changes
- Review before committing (`git diff --staged`)

## Philosophy
"Professional enough to keep the project clean, relaxed enough for a hobbyist project"
- Hooks warn but don't block aggressively
- Conventional commits encouraged but not enforced
- Safety checks without bureaucracy