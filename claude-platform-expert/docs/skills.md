# Agent Skills

## What Are Skills?
Agent Skills are modular capabilities that extend Claude's functionality. They package expertise into discoverable capabilities consisting of a `SKILL.md` file with instructions plus optional supporting files.

**Key Distinction**: Skills are **model-invoked**—Claude autonomously decides when to use them based on request and Skill description. This differs from slash commands which require explicit user activation.

## Creating Custom Skills

### Three Locations
1. **Personal Skills** (`~/.claude/skills/`) - Available across all projects
2. **Project Skills** (`.claude/skills/`) - Shared with team via git
3. **Plugin Skills** - Bundled with installed plugins

## Structure

Each Skill requires `SKILL.md` with YAML frontmatter:
```yaml
---
name: my-skill-name
description: Explains what the Skill does and when Claude should use it (max 1024 chars)
---
```

### Naming Rules
- Lowercase, alphanumeric with hyphens
- Max 64 characters
- Example: `claude-platform-expert`

## Skill Organization Best Practice

**Keep SKILL.md concise** - Use it as an index/guide that references detailed documentation:
- Create a `docs/` subdirectory for detailed reference materials
- SKILL.md should explain WHEN to use the skill and WHERE to find information
- Supporting files can include: documentation, examples, scripts, templates

Example structure:
```
.claude/skills/my-skill/
├── SKILL.md (concise guide with references)
├── docs/
│   ├── topic-1.md
│   ├── topic-2.md
│   └── examples.md
└── scripts/
    └── helper.sh
```

## Advanced Features
- **Tool Restrictions**: Use `allowed-tools` field to limit which capabilities Claude can use when Skill is active
- **Supporting Files**: Add reference documentation, examples, scripts, and templates alongside SKILL.md
- **Discovery**: Description field is critical—include specific triggers and use cases

## Best Practices
1. Write clear descriptions with specific triggers so Claude knows when to activate
2. Keep SKILL.md as a concise index that references detailed docs
3. Include specific use cases in the description
4. Organize detailed documentation in separate files
5. Use tool restrictions when appropriate for security
