# Subagents

## What Are Subagents?
Subagents are specialized AI assistants within Claude Code that handle specific task types independently. Each operates in its own context, preventing pollution of the main conversation.

## Key Characteristics
- **Focused expertise**: Each targets specific domains or workflows
- **Independent context**: Separate conversation windows from main thread
- **Customizable tooling**: Individual tool access per subagent
- **System prompt guidance**: Custom instructions shape behavior

## Types of Subagents

### 1. Built-in Subagents
Pre-made agents like the Plan subagent for research

### 2. User-level Subagents
- Location: `~/.claude/agents/`
- Available across all projects
- Personal customization

### 3. Project-level Subagents
- Location: `.claude/agents/`
- Team-specific agents
- Priority over user versions when same name exists

## How They Work
- **Automatic delegation**: When tasks match subagent's purpose
- **Explicit request**: Can be directly invoked
- **Context-aware**: System uses descriptions and context for delegation
- **Efficient problem-solving**: Preserves main conversation focus

## Creating Custom Subagents

Create agent definition files in appropriate directory:

### Agent Definition Structure
```markdown
---
name: my-subagent
description: What this subagent specializes in
allowed-tools: [Bash, Read, Grep, Edit]
---

# Subagent Instructions

Detailed instructions for how this subagent should behave...
```

## Use Cases
- Code review specialists
- Testing automation agents
- Documentation generators
- Security audit agents
- Performance analysis agents
- Migration specialists

## Best Practices
1. Create project-level subagents for team-specific workflows
2. Use clear, specific descriptions for proper delegation
3. Limit tool access appropriately for security
4. Document subagent purpose and capabilities
5. Test subagent behavior in isolated contexts
6. Name subagents descriptively for easy discovery
