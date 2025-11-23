#!/bin/bash
#
# Setup GitHub Branch Protection Rules
#
# This script configures branch protection rules for the main branch
# to enforce the model-driven workflow.
#
# Prerequisites:
# - GitHub CLI (gh) installed and authenticated
# - Admin access to the repository
#
# Usage: ./scripts/setup-branch-protection.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔒 Setting up GitHub Branch Protection..."

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "   Install: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI is not authenticated${NC}"
    echo "   Run: gh auth login"
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null)

if [ -z "$REPO" ]; then
    echo -e "${RED}❌ Not in a GitHub repository${NC}"
    exit 1
fi

echo "Repository: $REPO"
echo ""

# Branch protection configuration
BRANCH="main"

echo "Configuring protection for branch: $BRANCH"
echo ""

# Apply branch protection rules using GitHub API
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/$REPO/branches/$BRANCH/protection" \
  -f required_status_checks='{"strict":true,"contexts":["Quality Gates","Build","Verify Issue Linked"]}' \
  -f enforce_admins=false \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":0}' \
  -f restrictions=null \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  -F block_creations=false \
  -F required_conversation_resolution=true \
  -F lock_branch=false \
  -F allow_fork_syncing=true

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Branch protection configured successfully!${NC}"
    echo ""
    echo "Protected branch: $BRANCH"
    echo ""
    echo "Rules applied:"
    echo "  ✓ Require pull request before merging"
    echo "  ✓ Dismiss stale reviews when new commits pushed"
    echo "  ✓ Require status checks to pass:"
    echo "      - Quality Gates (tests, linting, spec validation)"
    echo "      - Build (Docker image)"
    echo "      - Verify Issue Linked (branch naming, issue exists)"
    echo "  ✓ Require branches to be up to date"
    echo "  ✓ Require conversation resolution"
    echo "  ✓ Block force pushes"
    echo "  ✓ Block branch deletion"
    echo ""
    echo -e "${YELLOW}Note: To require approving reviews, run:${NC}"
    echo "  gh api --method PUT /repos/$REPO/branches/$BRANCH/protection \\"
    echo "    -f required_pull_request_reviews='{\"required_approving_review_count\":1}'"
else
    echo ""
    echo -e "${RED}❌ Failed to configure branch protection${NC}"
    echo "   Check that you have admin access to the repository"
    exit 1
fi
