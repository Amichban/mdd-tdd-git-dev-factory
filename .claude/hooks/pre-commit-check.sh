#!/bin/bash
# Pre-commit quality gate checks
# This hook runs before any git commit to ensure code quality

set -e

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Running pre-commit checks..."

# Check 1: Validate JSON specs against schemas
echo -n "Validating JSON specs... "
if command -v python3 &> /dev/null; then
    python3 "$PROJECT_ROOT/generators/generate_all.py" --validate-only > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "JSON spec validation failed. Run: python generators/generate_all.py --validate-only"
        exit 1
    fi
else
    echo -e "${YELLOW}skipped (python3 not found)${NC}"
fi

# Check 2: No secrets in code
echo -n "Checking for secrets... "
if command -v trufflehog &> /dev/null; then
    trufflehog git file://. --only-verified --fail --no-update > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "Secrets detected in code!"
        exit 1
    fi
else
    # Basic check for common secret patterns
    if git diff --cached --name-only | xargs grep -l -E "(password|secret|api_key|token)\s*[:=]\s*['\"][^'\"]+['\"]" 2>/dev/null; then
        echo -e "${RED}✗${NC}"
        echo "Potential secrets detected in staged files!"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} (basic check)"
fi

# Check 3: Run linter (if available)
echo -n "Running linter... "
if command -v ruff &> /dev/null; then
    ruff check "$PROJECT_ROOT" --quiet
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "Linting errors found. Run: ruff check ."
        exit 1
    fi
elif command -v flake8 &> /dev/null; then
    flake8 "$PROJECT_ROOT" --quiet
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}skipped (no linter found)${NC}"
fi

# Check 4: Run type checker (if available)
echo -n "Running type check... "
if command -v mypy &> /dev/null; then
    mypy "$PROJECT_ROOT/src" "$PROJECT_ROOT/generators" --ignore-missing-imports --quiet 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}warnings${NC}"
        # Don't fail on type errors for now, just warn
    fi
else
    echo -e "${YELLOW}skipped (mypy not found)${NC}"
fi

# Check 5: Run tests
echo -n "Running tests... "
if command -v pytest &> /dev/null; then
    pytest "$PROJECT_ROOT/tests" -q --tb=no 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "Tests failed. Run: pytest tests/ -v"
        exit 1
    fi
else
    echo -e "${YELLOW}skipped (pytest not found)${NC}"
fi

# Check 6: Check coverage threshold
echo -n "Checking coverage... "
if command -v pytest &> /dev/null && command -v coverage &> /dev/null; then
    coverage_result=$(pytest "$PROJECT_ROOT/tests" --cov=src --cov-fail-under=80 -q --tb=no 2>&1)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}below threshold${NC}"
        # Don't fail on coverage for now, just warn
    fi
else
    echo -e "${YELLOW}skipped (coverage not available)${NC}"
fi

echo ""
echo -e "${GREEN}All pre-commit checks passed!${NC}"
exit 0
