# Trigger Deployment

Trigger the deployment pipeline for the specified environment.

## Arguments

- `$ARGUMENTS` - The environment to deploy to (dev, staging, prod)

## Instructions

Trigger deployment based on environment:

### Development
Auto-deploys on merge to main. To manually trigger:
```bash
gh workflow run deploy.yml -f environment=dev
```

### Staging
Auto-deploys after dev succeeds. To manually trigger:
```bash
gh workflow run deploy.yml -f environment=staging
```

### Production
Requires manual approval. To trigger:
```bash
gh workflow run deploy.yml -f environment=prod
```

Then approve via GitHub UI or:
```bash
gh run list --workflow=deploy.yml
gh run view <run-id> --web  # To approve
```

## Pre-deployment Checks

Before deploying, verify:
1. All tests pass: `pytest tests/ -v`
2. No uncommitted changes: `git status`
3. Branch is up to date: `git pull`
4. CI checks pass: `gh run list --limit 1`

## Output

Report:
- Deployment trigger status
- Link to GitHub Actions run
- Expected completion time
- Approval requirements (for prod)
