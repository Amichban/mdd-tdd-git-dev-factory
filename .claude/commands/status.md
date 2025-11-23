# Show Project Status

Display the current status of the project from GitHub.

## Instructions

Query GitHub to show:
1. Open issues by type (specification, user-story, ontology, etc.)
2. Open pull requests and their CI status
3. Recent commits
4. Current branch and changes
5. Deployment status

## Commands

```bash
# Git status
git status

# Open issues
gh issue list --state open

# Open PRs
gh pr list --state open

# Recent commits
git log --oneline -10

# Check CI status
gh run list --limit 5
```

## Output Format

```
Project Status
==============

Branch: main
Changes: 3 files modified, 1 untracked

Open Issues: 5
- #12 [user-story] US-001: Review pending signal
- #13 [user-story] US-002: Approve signal
- #14 [ontology] Review TradeSignal entity
...

Open PRs: 2
- #15 feat: Add risk_score property - ✅ Checks passing
- #16 fix: Signal strength calculation - ⏳ Running

Recent Deployments:
- dev: ✅ Deployed 2h ago
- staging: ✅ Deployed 1h ago
- prod: ⏳ Awaiting approval
```
