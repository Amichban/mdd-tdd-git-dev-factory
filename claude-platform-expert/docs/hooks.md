# Hooks System

## Overview
Hooks enable automated execution of custom scripts in response to specific events during development sessions. They enforce standards, validate changes, and integrate external tools seamlessly.

## How Hooks Work
Configured in settings files (`~/.claude/settings.json` or `.claude/settings.json`):
- **Exit code-based**: Simple success/failure (0 = success, 2 = blocking error)
- **JSON output control**: Advanced decision-making with structured data via stdout

## Available Hook Types

1. **PreToolUse** - After Claude creates tool parameters but before processing
2. **PostToolUse** - Immediately after successful tool completion
3. **UserPromptSubmit** - When users submit prompts (validation/context injection)
4. **Notification** - When Claude requests permissions or waits for input
5. **Stop** - When main agent finishes responding
6. **SubagentStop** - When subagent tasks complete
7. **SessionStart** - At session initialization for environment setup
8. **SessionEnd** - During session cleanup

## Configuration Structure

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "your-validation-script.sh"
          }
        ]
      }
    ]
  }
}
```

**Matchers**: Case-sensitive patterns supporting regex (e.g., `Edit|Write` or `mcp__.*__write.*`)

## Key Capabilities

- **Tool Input Modification**: PreToolUse hooks can modify parameters using `updatedInput`
- **Context Injection**: UserPromptSubmit and SessionStart add context via stdout or JSON
- **Permission Management**: PreToolUse hooks can "allow," "deny," or "ask" for confirmation
- **Blocking Decisions**: Multiple hook types support preventing actions with custom reasons

## Practical Use Cases
- Validate bash commands before execution
- Enforce coding standards on file writes
- Block sensitive information in prompts
- Add environmental context at session start
- Log completion events for auditing

## Security Warning
⚠️ Hook scripts execute arbitrary shell commands automatically. Users bear full responsibility for validating commands before deployment. Always test hooks thoroughly before production use.

## Best Practices
1. Always test hooks thoroughly in safe environments first
2. Use PreToolUse for validation, PostToolUse for logging
3. Leverage UserPromptSubmit for context injection
4. Keep hook scripts simple and focused
5. Document hook behavior for team members
6. Use exit codes properly (0 = success, 2 = blocking error)
