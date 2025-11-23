# Feedback Agent Command

Collect and track problems, enhancements, and feedback for the MDD TDD Git Dev Factory template.

## Usage

When invoked, analyze the current state and add appropriate feedback to `FEEDBACK.md`.

## Modes

### 1. Analyze Template (default)
Review the codebase and identify:
- Problems that need fixing
- Potential enhancements
- Areas needing better documentation

### 2. Add Specific Feedback
When user provides specific feedback, add it to the appropriate section.

## Workflow

1. **Read current feedback** - Load `FEEDBACK.md` to see existing items
2. **Analyze or accept input** - Either analyze codebase or take user input
3. **Generate ID** - Next sequential ID for the type (P###, E###, F###)
4. **Format entry** - Use the standard template
5. **Append to file** - Add to appropriate section in `FEEDBACK.md`
6. **Summarize** - Tell user what was added

## Analysis Checklist

When analyzing the template, check for:

### Problems
- [ ] Missing error handling
- [ ] Incomplete validation
- [ ] Security vulnerabilities
- [ ] Performance issues
- [ ] Broken workflows

### Enhancements
- [ ] Missing features for common use cases
- [ ] Integration opportunities
- [ ] Developer experience improvements
- [ ] Scalability improvements
- [ ] Testing gaps

### Feedback
- [ ] Documentation clarity
- [ ] Onboarding experience
- [ ] Error message helpfulness
- [ ] Code organization

## Example

**User:** Add feedback that the pre-commit hook is too slow

**Agent:**
```python
# Read current feedback to get next ID
# Add to FEEDBACK.md:

### [F003] Pre-commit hook performance
- **Date:** 2024-01-15
- **From:** Developer feedback
- **Feedback:** Pre-commit hook takes too long, slowing down development
- **Action:** Consider running only changed file tests, or add --quick mode
- **Status:** Open
```

## Auto-Analysis Mode

When no specific feedback provided, run comprehensive analysis:

```python
# 1. Check generators for missing features
# 2. Review orchestrator error handling
# 3. Analyze spec schemas for completeness
# 4. Check test coverage gaps
# 5. Review security practices
# 6. Evaluate documentation

# Generate report with prioritized items
```
