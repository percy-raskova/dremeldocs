# Task Completion Checklist

## When Completing Any Task

### 1. Code Quality Checks
Since no linting/formatting tools are currently configured, manually ensure:
- [ ] Code follows PEP 8 conventions
- [ ] Functions have descriptive docstrings
- [ ] Variable names are clear and follow snake_case
- [ ] No unused imports or variables
- [ ] Error handling is in place for file operations

### 2. Testing (When Available)
Currently no test framework is set up. When implementing:
- [ ] Create unit tests for new functions
- [ ] Test edge cases (empty files, missing data)
- [ ] Verify checkpoint/resume functionality
- [ ] Test with sample Twitter archive data

### 3. Documentation Updates
- [ ] Update relevant markdown files in `/twitter-pipeline-docs/`
- [ ] Add/update docstrings for new functions
- [ ] Update PROJECT_STATE.md with progress
- [ ] Document any new dependencies in pyproject.toml

### 4. Git Workflow
- [ ] Stage changes: `git add .`
- [ ] Review changes: `git diff --staged`
- [ ] Commit with descriptive message
- [ ] Never commit directly to main branch

### 5. Validation Steps
- [ ] Verify code runs without errors
- [ ] Check memory usage with large files
- [ ] Ensure checkpoint files are created
- [ ] Validate output format (markdown, JSON)

## Specific to Twitter Pipeline Tasks

### Data Extraction Tasks
- [ ] Verify JavaScript wrapper is properly removed
- [ ] Check JSON parsing doesn't fail on special characters
- [ ] Ensure all tweet fields are preserved
- [ ] Test with both modern and legacy archive formats

### Thread Detection Tasks  
- [ ] Validate thread continuity
- [ ] Check for orphaned tweets
- [ ] Verify temporal ordering
- [ ] Test self-reply chain detection

### Classification Tasks
- [ ] Review classification confidence scores
- [ ] Spot-check serious vs casual categorization
- [ ] Monitor API rate limits
- [ ] Verify keyword matching logic

### Markdown Generation Tasks
- [ ] Validate frontmatter format
- [ ] Check markdown syntax
- [ ] Ensure proper escaping of special characters
- [ ] Verify file naming conventions

## Performance Considerations
- [ ] Memory usage stays under 2GB for 1.9GB archive
- [ ] Implement streaming for large files
- [ ] Use batch processing where appropriate
- [ ] Add progress indicators with tqdm

## Before Marking Complete
- [ ] Run the full pipeline end-to-end on sample data
- [ ] Document any known limitations
- [ ] Update memory files if project structure changes
- [ ] Ensure reproducible setup instructions