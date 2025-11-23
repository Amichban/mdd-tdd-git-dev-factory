# Slash Commands

## What Are Slash Commands?
Slash commands are directives that control Claude's behavior during interactive sessions. They invoke predefined prompts or built-in functionality with `/` prefix.

## Built-in Commands

### Session Management
- `/clear` - Reset conversation history
- `/rewind` - Undo recent changes

### Configuration
- `/config` - Configure settings
- `/model` - Switch AI models
- `/settings` - View/edit settings

### Information
- `/help` - Get help
- `/status` - Check status
- `/cost` - View usage costs
- `/usage` - View usage statistics

### Authentication
- `/login` - Authenticate
- `/logout` - Sign out

### Development
- `/review` - Code review
- `/sandbox` - Isolated execution

### Utilities
- `/init` - Project setup
- `/mcp` - Manage MCP connections
- `/doctor` - Diagnose issues

## Custom Slash Commands

Create personalized commands with Markdown files:

### Project-level (shared with team)
- Location: `.claude/commands/`
- Appear as "(project)" in `/help`

### Personal-level (available across all projects)
- Location: `~/.claude/commands/`
- Appear as "(user)" in `/help`

## Custom Command Features

### Arguments
- `$ARGUMENTS` - All parameters
- `$1`, `$2` - Positional arguments

### Bash Execution
Prefix with `!` to run shell scripts and include output

### File References
Use `@` to include file contents

### Namespacing
Organize in subdirectories for structure

### Frontmatter
```yaml
---
description: What this command does
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Edit]
---
```

## Example Custom Command

File: `.claude/commands/deploy.md`
```markdown
---
description: Deploy application to production
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read]
---

Deploy the application to $1 environment.

Steps:
1. Run tests
2. Build production bundle
3. Deploy to $1
4. Verify deployment

!./scripts/deploy.sh $1
```

## Best Practices
- Use descriptive command names
- Document command behavior in frontmatter description
- Leverage arguments for flexibility
- Organize related commands in subdirectories
- Use appropriate tool restrictions for security
