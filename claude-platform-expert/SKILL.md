---
name: claude-platform-expert
description: Expert knowledge about Claude Code platform, including MCP (Model Context Protocol), plugins, skills, subagents, hooks, slash commands, headless mode, GitHub Actions integration, configuration system, and all development features. Use this skill when users ask about Claude Code capabilities, how to extend Claude Code, create custom functionality, automate workflows, integrate with CI/CD, or configure Claude Code features.
---

# Claude Platform Expert Skill

This skill provides comprehensive expertise on the Claude Code development platform. When activated, consult the detailed reference documentation in the `docs/` directory.

## Quick Reference

### Core Components
- **MCP (Model Context Protocol)**: Integration with external tools and APIs - See `docs/mcp.md`
- **Plugins**: Custom functionality packages - See `docs/plugins.md`
- **Skills**: Model-invoked capabilities - See `docs/skills.md`
- **Subagents**: Specialized AI assistants - See `docs/subagents.md`
- **Hooks**: Event-driven automation - See `docs/hooks.md`
- **Slash Commands**: Built-in and custom commands - See `docs/slash-commands.md`

### Integration & Deployment
- **Headless Mode**: Programmatic API usage - See `docs/headless-mode.md`
- **GitHub Actions**: CI/CD integration - See `docs/github-actions.md`
- **Configuration**: Settings hierarchy - See `docs/configuration.md`

## Usage Instructions

When users ask questions about Claude Code:

1. **Identify the topic** from the question (MCP, plugins, hooks, etc.)
2. **Reference the appropriate documentation file** in `docs/` directory
3. **Provide specific, actionable guidance** based on the documentation
4. **Include code examples** when relevant
5. **Suggest best practices** for the specific use case

## Common Questions & Where to Look

- "How do I integrate external tools?" → `docs/mcp.md`
- "How do I create custom commands?" → `docs/slash-commands.md` or `docs/plugins.md`
- "How do I automate workflows?" → `docs/hooks.md` or `docs/headless-mode.md`
- "How do I use Claude in CI/CD?" → `docs/github-actions.md` or `docs/headless-mode.md`
- "How do I configure Claude Code?" → `docs/configuration.md`
- "How do I create reusable capabilities?" → `docs/skills.md` or `docs/plugins.md`
- "How do I create specialized agents?" → `docs/subagents.md`

Always read the relevant documentation file before answering to ensure accuracy and completeness.
