# Configuration System

## Settings Files Hierarchy

### User Settings (Global)
- **Location**: `~/.claude/settings.json`
- **Scope**: All projects
- **Use**: Personal preferences

### Project Settings (Shared)
- **Location**: `.claude/settings.json`
- **Scope**: Current project, shared via version control
- **Use**: Team standards

### Local Project Settings (Personal)
- **Location**: `.claude/settings.local.json`
- **Scope**: Current project, personal overrides
- **Use**: Local development preferences (excluded from git)

### Enterprise Policies (System)
- **Location**: System-level `managed-settings.json`
- **Scope**: All users/projects in organization
- **Use**: Organizational security and compliance

## Configuration Precedence (Highest to Lowest)

1. Enterprise managed policies
2. Command-line arguments
3. Local project settings (`.claude/settings.local.json`)
4. Shared project settings (`.claude/settings.json`)
5. User settings (`~/.claude/settings.json`)

## Key Configuration Areas

### Permissions
Control which tools Claude can access:
```json
{
  "permissions": {
    "Bash": "allow",
    "Edit": "ask",
    "Write": "deny",
    "WebFetch": "ask"
  }
}
```

Options: `"allow"`, `"deny"`, `"ask"`

### Environment Variables
```json
{
  "environment": {
    "ANTHROPIC_API_KEY": "sk-ant-...",
    "DEFAULT_MODEL": "claude-sonnet-4-5-20250929",
    "HTTP_PROXY": "http://proxy.company.com:8080"
  }
}
```

### Sandbox Settings
```json
{
  "sandbox": {
    "enabled": true,
    "network_access": false,
    "filesystem_access": "limited"
  }
}
```

Available on macOS/Linux for isolating bash commands

### Tool Configuration
```json
{
  "tools": {
    "Bash": {
      "timeout": 120000,
      "allowedCommands": ["git", "npm", "pytest"]
    },
    "WebFetch": {
      "allowedDomains": ["docs.example.com", "api.example.com"]
    }
  }
}
```

## Complete Configuration Example

```json
{
  "permissions": {
    "Bash": "allow",
    "Read": "allow",
    "Edit": "ask",
    "Write": "ask",
    "WebFetch": "allow"
  },
  "environment": {
    "ANTHROPIC_API_KEY": "sk-ant-...",
    "DEFAULT_MODEL": "claude-sonnet-4-5-20250929",
    "CLAUDE_SANDBOX": "true"
  },
  "sandbox": {
    "enabled": true,
    "network_access": true
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/validate-command.sh"
          }
        ]
      }
    ]
  }
}
```

## Best Practices

### For Personal Use
- Set your preferences in `~/.claude/settings.json`
- Use local project settings for project-specific overrides
- Never commit API keys to version control

### For Teams
- Define team standards in `.claude/settings.json`
- Commit project settings to version control
- Add `.claude/settings.local.json` to `.gitignore`
- Document configuration decisions in README

### For Enterprises
- Use managed policies for security enforcement
- Define allowlist/denylist for tools and domains
- Enable sandbox mode for isolation
- Monitor and audit configuration compliance
- Use environment variables for sensitive data

## Configuration Commands

View current configuration:
```bash
/config
```

Edit settings interactively:
```bash
/settings
```

View effective configuration (after hierarchy resolution):
```bash
claude --show-config
```
