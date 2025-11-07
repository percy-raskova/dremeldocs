# Branch Protection Setup Guide

This guide provides step-by-step instructions for setting up branch protection rules for the DremelDocs repository.

## Overview

Branch protection ensures that:
- Code is reviewed before merging to `main`
- CI builds pass before deployment
- Accidental force pushes are prevented
- Main branch remains stable for production

## Prerequisites

- Repository admin access
- GitHub account with appropriate permissions

## Setting Up Main Branch Protection

### Step 1: Navigate to Branch Protection Settings

1. Go to the repository: `https://github.com/percy-raskova/dremeldocs`
2. Click on **Settings** (top navigation)
3. In the left sidebar, click **Branches**
4. Under "Branch protection rules", click **Add rule** (or **Edit** if a rule exists for `main`)

### Step 2: Configure Branch Name Pattern

- **Branch name pattern**: `main`

This rule will apply only to the `main` branch.

### Step 3: Configure Protection Settings

Enable and configure the following settings:

#### Require a pull request before merging ✅

- **Check**: ✅ Require a pull request before merging
- **Required approvals**: `1`
- **Check**: ✅ Dismiss stale pull request approvals when new commits are pushed
- **Check**: ⬜ Require review from Code Owners (optional - enable if you have CODEOWNERS file)
- **Check**: ⬜ Require approval of the most recent reviewable push

**Why**: Ensures all changes to `main` are reviewed before merging.

#### Require status checks to pass before merging ✅

- **Check**: ✅ Require status checks to pass before merging
- **Check**: ✅ Require branches to be up to date before merging
- **Status checks that are required**:
  - Search for and add: `build`
  - This is the build job from `.github/workflows/deploy.yml`

**Why**: Ensures the build succeeds before allowing merge.

#### Require conversation resolution before merging ✅

- **Check**: ✅ Require conversation resolution before merging

**Why**: Ensures all PR comments and discussions are resolved.

#### Require signed commits (Optional but Recommended)

- **Check**: ✅ Require signed commits

**Why**: Adds extra security by verifying commit author identity.

**Note**: If enabled, all contributors must [set up commit signing](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).

#### Require linear history (Optional)

- **Check**: ⬜ Require linear history

**Why**: Can enforce clean git history, but may complicate workflow. Disabled by default.

#### Require deployments to succeed before merging (Optional)

- **Check**: ⬜ Require deployments to succeed before merging

**Why**: Not needed as deployment happens after merge.

#### Lock branch (Not Recommended)

- **Check**: ⬜ Lock branch

**Why**: Makes branch read-only. Only use for archived branches.

#### Do not allow bypassing the above settings ✅

- **Check**: ✅ Do not allow bypassing the above settings
- **Exception**: ⬜ Restrict who can dismiss pull request reviews (optional)
- **Exception**: ⬜ Restrict who can push to matching branches (optional)

**Important**: Leave unchecked to allow repository administrators to force push in emergencies.

#### Allow force pushes

- **Check**: ⬜ Allow force pushes
- **Who can force push**: Nobody (default)

**Why**: Prevents accidental history rewriting. Admins can still override branch protection if needed.

#### Allow deletions

- **Check**: ⬜ Allow deletions

**Why**: Prevents accidental deletion of the `main` branch.

### Step 4: Save Changes

Click **Create** (or **Save changes** if editing existing rule)

## Setting Up Dev Branch (No Protection)

The `dev` branch should NOT have protection rules to allow flexible development.

### Creating the Dev Branch

```bash
# From main branch
git checkout main
git pull origin main

# Create dev branch
git checkout -b dev

# Push to remote
git push -u origin dev
```

### No Protection Needed

Do not create branch protection rules for `dev`. This allows:
- Direct pushes for quick iterations
- Force pushes if needed for history cleanup
- Flexible development workflow

## Verification

### Test Branch Protection

After setting up, verify protection is working:

1. **Test Direct Push (Should Fail)**
   ```bash
   # Try to push directly to main
   git checkout main
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test: direct push"
   git push origin main
   ```
   **Expected**: Push is rejected with protection rules message

2. **Test PR Workflow (Should Work)**
   ```bash
   # Create feature branch
   git checkout dev
   git checkout -b feature/test
   
   # Make changes
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test: via PR"
   git push -u origin feature/test
   
   # Create PR: feature/test → dev
   # Then create PR: dev → main
   # Request review and approval
   # Merge after approval
   ```
   **Expected**: Works smoothly with protection

3. **Test Build Requirement**
   - Create a PR to `main`
   - Before build completes, try to merge
   **Expected**: Merge button disabled until build passes

## Common Issues and Solutions

### Issue: Can't Push to Main at All

**Symptom**: Even with PR, can't merge to main

**Solution**: Check that status check `build` exists and passes
1. Go to PR
2. Check "Checks" tab
3. Verify `build` job exists and is passing
4. If not, fix the workflow file

### Issue: Status Check Not Required

**Symptom**: Can merge PR even when build fails

**Solution**: 
1. Go to Settings → Branches → Edit rule for `main`
2. Under "Require status checks to pass before merging"
3. Ensure `build` is in the list of required status checks
4. Save changes

### Issue: Admin Can't Force Push in Emergency

**Symptom**: Need to force push for critical fix but can't

**Solution**:
1. Temporarily disable branch protection:
   - Settings → Branches → Edit rule for `main`
   - Uncheck all rules or delete rule
   - Make force push
   - Re-enable protection immediately
   
2. Alternative (Preferred):
   - Ensure "Do not allow bypassing" is NOT checked
   - Admin can override protection when needed
   - Use with caution!

### Issue: Signed Commits Required but Contributors Don't Have Setup

**Symptom**: PRs failing because commits aren't signed

**Solution**:
1. Provide commit signing setup guide to team
2. Or disable "Require signed commits" if not critical
3. Team members setup: https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits

## Best Practices

### For Repository Administrators

1. **Review protection settings quarterly**
   - Ensure rules still match team needs
   - Update required status checks if workflow changes

2. **Document any protection overrides**
   - If you need to bypass protection, document why
   - Create issue tracking the override and restoration

3. **Educate team on workflow**
   - Ensure all contributors understand PR process
   - Provide this documentation to new team members

### For Contributors

1. **Never attempt to bypass protection**
   - Always use PR workflow
   - Request admin help if truly needed

2. **Keep feature branches up to date**
   - Regularly merge/rebase from `dev` or `main`
   - Prevents conflicts and ensures protection rules apply

3. **Fix build failures promptly**
   - Don't try to bypass failing builds
   - Fix the issue or revert the problematic change

## Alternative: GitHub CLI Setup

For automation or scripting, you can use GitHub CLI:

```bash
# Install GitHub CLI if needed
# https://cli.github.com/

# Authenticate
gh auth login

# Create branch protection rule
gh api repos/percy-raskova/dremeldocs/branches/main/protection \
  --method PUT \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field required_pull_request_reviews[dismiss_stale_reviews]=true \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=build \
  --field enforce_admins=false \
  --field required_conversation_resolution[enabled]=true \
  --field allow_force_pushes[enabled]=false \
  --field allow_deletions[enabled]=false
```

## Alternative: Terraform/Infrastructure as Code

For teams using IaC, you can manage branch protection with Terraform:

```hcl
# main.tf
terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 5.0"
    }
  }
}

provider "github" {
  token = var.github_token
  owner = "percy-raskova"
}

resource "github_branch_protection" "main" {
  repository_id = "dremeldocs"
  pattern       = "main"

  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews          = true
  }

  required_status_checks {
    strict   = true
    contexts = ["build"]
  }

  enforce_admins              = false
  require_conversation_resolution = true
  require_signed_commits      = false

  allow_force_pushes {
    enabled = false
  }

  allow_deletions {
    enabled = false
  }
}
```

## Monitoring Protection

### Check Current Settings

Via GitHub UI:
1. Settings → Branches
2. View rule for `main`

Via GitHub CLI:
```bash
gh api repos/percy-raskova/dremeldocs/branches/main/protection
```

Via Git:
```bash
# Test protection by attempting protected action
git push origin main
# If protected, will get error message with details
```

## Summary Checklist

Before completing setup, verify:

- [ ] Main branch protection rule created
- [ ] Require PR before merging: Enabled
- [ ] Required approvals: 1
- [ ] Dismiss stale reviews: Enabled
- [ ] Require status checks: Enabled
- [ ] Required status check `build`: Added
- [ ] Require conversation resolution: Enabled
- [ ] Allow force pushes: Disabled
- [ ] Allow deletions: Disabled
- [ ] Dev branch created (without protection)
- [ ] Team notified of new workflow
- [ ] Documentation updated
- [ ] Tested PR workflow
- [ ] Verified protection works

## Related Documentation

- [CI/CD Pipeline Documentation](CICD_PIPELINE.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Development Workflow](PROJECT_INDEX.md)

---

**Last Updated**: November 2025  
**Maintained By**: DremelDocs Team
