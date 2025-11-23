# Headless Mode

## Core Concept
Run Claude Code programmatically without interactive UI for automation and script integration.

## Basic Usage

```bash
claude -p "Stage my changes and write a set of commits for them" \
  --allowedTools "Bash,Read" \
  --permission-mode acceptEdits
```

## Key Configuration Options

- `--output-format` - Choose: `text` (default), `json`, or `stream-json`
- `--resume SESSION_ID` - Resume previous conversations
- `--continue` - Continue most recent conversation
- `--allowedTools` - Specify which tools Claude can use
- `--append-system-prompt` - Add custom instructions
- `--permission-mode` - Control permission behavior (acceptEdits, acceptAll, etc.)

## Multi-Turn Conversations

### Continue Most Recent Conversation
```bash
claude --continue "Now refactor this for better performance"
```

### Resume Specific Conversation
```bash
claude --resume SESSION_ID "Update the tests"
```

## Output Formats

### Text Output (Default)
Simple text response for human reading

### JSON Output
```json
{
  "type": "result",
  "total_cost_usd": 0.003,
  "result": "The response text...",
  "session_id": "abc123"
}
```

### Streaming JSON
Emits messages as received for real-time processing

## Practical Integration Examples

### Security Audit Script
```bash
#!/bin/bash
claude -p "Review PR #${PR_NUMBER} for security vulnerabilities" \
  --output-format json \
  --allowedTools "Bash,Read,Grep" \
  | jq -r '.result'
```

### SRE Incident Response
```bash
claude -p "Analyze these logs and suggest fixes: $(cat error.log)" \
  --output-format json \
  --allowedTools "Bash,Read,WebFetch"
```

### Document Review Workflow
```bash
claude -p "Check documentation for completeness @docs/" \
  --output-format text \
  --allowedTools "Read,Glob"
```

### CI/CD Automation
```bash
# In your CI pipeline
claude -p "Run tests, fix failures, and create a summary" \
  --permission-mode acceptEdits \
  --output-format json \
  --allowedTools "Bash,Read,Edit"
```

## Best Practices
1. Use `--output-format json` for programmatic parsing and integration
2. Specify `--allowedTools` explicitly for security
3. Use `--permission-mode` appropriately for automation level
4. Leverage `--continue` for multi-step workflows
5. Parse JSON output with tools like `jq` for scripting
6. Set appropriate timeouts for long-running tasks
7. Log session IDs for debugging and audit trails
