# GitHub Actions Integration

## Quick Setup
Use built-in installer:
```bash
/install-github-app
```

## Manual Setup Steps

### 1. Install GitHub App
Visit https://github.com/apps/claude and install the app to your repository

Grant permissions:
- Contents (read/write)
- Issues (read/write)
- Pull Requests (read/write)

### 2. Add API Key
Add your Anthropic API key as a repository secret named `ANTHROPIC_API_KEY`

### 3. Create Workflow File
Copy workflow file into `.github/workflows/claude.yml`

## Usage Modes

### Interactive Mode
Tag `@claude` in PR or issue comments with your request:

```
@claude Please review this PR for security issues and suggest improvements
```

```
@claude Implement the feature described in this issue
```

### Automation Mode
Define `prompt` parameter in workflow for automatic triggers:

```yaml
name: Claude Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: "Review this PR for code quality and suggest improvements"
          claude_args: "--max-turns 5 --model claude-sonnet-4-5-20250929"
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Key Parameters

- `prompt` - Instructions for Claude (what to do)
- `claude_args` - CLI arguments for fine-tuning behavior
  - `--max-turns N` - Limit interaction rounds
  - `--model MODEL_NAME` - Specify model version
  - `--allowedTools "Tool1,Tool2"` - Restrict tools
- `anthropic_api_key` - Your API credentials (use secrets!)

## Common Use Cases

### Automated Code Review
```yaml
on: [pull_request]
# Prompt: "Review code quality, identify bugs, suggest improvements"
```

### Issue to PR
```yaml
on: [issues]
# Prompt: "Implement the feature described in this issue and create a PR"
```

### Bug Fix from Error Reports
```yaml
on: [issues]
# Prompt: "Analyze the bug report and create a fix"
```

### Documentation Updates
```yaml
on: [push]
# Prompt: "Update documentation to reflect code changes"
```

### Security Scanning
```yaml
on: [pull_request]
# Prompt: "Scan for security vulnerabilities and suggest fixes"
```

## Leveraging CLAUDE.md

Create `.claude/CLAUDE.md` or `CLAUDE.md` in your repository root to define:
- Coding standards
- Architecture patterns
- Testing requirements
- Documentation expectations

Claude will automatically follow these guidelines when working in GitHub Actions.

Example `CLAUDE.md`:
```markdown
# Project Guidelines for Claude

## Code Style
- Use TypeScript with strict mode
- Follow ESLint configuration
- Prefer functional components in React

## Testing
- Write unit tests for all new functions
- Maintain >80% code coverage
- Use Jest for testing

## Documentation
- Add JSDoc comments for public APIs
- Update README.md for new features
- Include examples in documentation
```

## Best Practices
1. Use repository secrets for API keys (never hardcode)
2. Set appropriate `--max-turns` to control execution time
3. Leverage `CLAUDE.md` for consistent project standards
4. Use specific prompts for better results
5. Monitor usage and costs through GitHub Actions logs
6. Test workflows in draft PRs first
7. Use branch protection rules to control when Claude can commit
