# Plugins System

## What Are Plugins?
Plugins extend Claude Code with custom functionality that can be shared across projects and teams. They enable adding custom commands, agents, hooks, Skills, and MCP servers.

## Plugin Structure
```
.claude-plugin/
├── plugin.json (manifest with metadata)
├── commands/ (custom slash commands)
├── agents/ (specialized agent definitions)
├── skills/ (agent Skills)
├── hooks/ (event handlers)
└── mcp/ (external tool integrations)
```

## Creating a Plugin

### 1. Create Manifest
Create `.claude-plugin/plugin.json`:
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My custom plugin",
  "author": "Your Name"
}
```

### 2. Add Commands
Add commands in `commands/` directory with markdown descriptions

### 3. Build Marketplace
Create `.claude-plugin/marketplace.json` for local testing

### 4. Install Locally
```bash
/plugin install
```

### 5. Test Iteratively
Uninstall and reinstall after changes for testing

## Key Features
- **Discovery**: Browse and install from community marketplaces
- **Team workflows**: Configure automatic plugin installation at repository level
- **Version management**: Use semantic versioning for distribution
- **Local development**: Test with development marketplaces before sharing

## Best Practices
- Version properly using semantic versioning
- Test with development marketplaces before sharing
- Document plugin functionality clearly
- Use appropriate directory structure for organization
