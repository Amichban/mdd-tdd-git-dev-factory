# MDD TDD Git Dev Factory

A **Model-Driven Development** template with **Test-Driven Development** practices, **Git-based** workflow automation, and **9-Box Architecture** for enterprise-grade systems.

> **Stop writing code. Start specifying systems.**

## What is This?

A development platform template where:
- **JSON specs are the source of truth** - Define entities, APIs, and UIs in specs
- **Code is generated, not written** - Models, routes, tests auto-generated
- **GitHub is the project manager** - Every change starts with an issue
- **9-Box Architecture** - Every feature fills all 9 boxes with strict contracts
- **Quality is enforced** - Hooks and CI prevent bad code from merging

## Quick Start

```bash
# 1. Create from template
gh repo create my-project --template Amichban/mdd-tdd-git-dev-factory
cd my-project

# 2. Setup
make setup

# 3. Start development
make dev
```

## The 9-Box Architecture

Every feature must be specified across **3 systems** and **9 boxes**:

```
┌─────────────────────────────────────────────────────────────┐
│ REGISTRY (What We Have)                                     │
│ ┌─────────────┬─────────────┬─────────────┐                │
│ │ 1. Entity   │ 2. Task     │ 3. Policy   │                │
│ │ Catalog     │ Library     │ Vault       │                │
│ │ → MCP       │ → Skills    │ → Hooks     │                │
│ └─────────────┴─────────────┴─────────────┘                │
├─────────────────────────────────────────────────────────────┤
│ ENGINE (How It Runs)                                        │
│ ┌─────────────┬─────────────┬─────────────┐                │
│ │ 4. Scheduler│ 5. Workers  │ 6. Broadcast│                │
│ │ → Actions   │ → Headless  │ → PostHooks │                │
│ └─────────────┴─────────────┴─────────────┘                │
├─────────────────────────────────────────────────────────────┤
│ OBSERVER (How It Learns)                                    │
│ ┌─────────────┬─────────────┬─────────────┐                │
│ │ 7. Signal   │ 8. Reasoning│ 9. Command  │                │
│ │ Ingestor    │ Core        │ Center      │                │
│ │ → MCP SSE   │ → Subagents │ → Commands  │                │
│ └─────────────┴─────────────┴─────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### The Three Contracts

| Contract | Purpose | Schema |
|----------|---------|--------|
| **Graph** | Typed business nodes with lineage | `specs/schema/graph.schema.json` |
| **Signal** | Traceable events with correlation IDs | `specs/schema/signal.schema.json` |
| **GenUI** | Safe UI widgets for slash commands | `specs/schema/genui.schema.json` |

### Usage

```bash
# Generate 9-box spec from user story
make architect
# → Enter: "I need to validate data quality before pipeline runs"
# → Output: specs/architecture/data-quality.json

# View business graph
make graph

# Validate architecture specs
make validate-9box
```

## The Complete Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  IDEA → ISSUE → ARCHITECT → SPEC → GENERATE → TEST → DEPLOY      │
│                                                                   │
│  "Data     Create    Run 9-box    Edit       make      make      │
│  quality"  GitHub    architect    specs/    generate   test      │
│            issue     agent        *.json                          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Core Commands

```bash
# Setup
make setup        # Install everything, enable hooks, setup database
make hooks        # Enable git hooks (issue-first, TDD enforcement)

# 9-Box Architecture
make architect    # Generate 9-box spec from user story
make validate-9box # Validate architecture specs
make graph        # Show business graph nodes

# Development
make dev          # Start all services (frontend :3000, backend :8000)
make generate     # Regenerate code from specs
make test         # Run tests (80% coverage required)

# GitHub Workflow
make issue        # Create GitHub issue
make implement    # Implement from issue number

# Utilities
make feedback     # Add problems/enhancements to tracker
```

## Architecture

### Spec-First Development

Define your entity in `specs/entities.json`:

```json
{
  "entities": [{
    "name": "DataSource",
    "fields": [
      {"name": "id", "type": "uuid", "primary_key": true},
      {"name": "name", "type": "string", "required": true},
      {"name": "connection_string", "type": "string"}
    ],
    "api": {
      "endpoints": ["list", "get", "create", "update", "delete"]
    }
  }]
}
```

Run `make generate` and get:
- ✅ Pydantic models with validation
- ✅ FastAPI routes with OpenAPI docs
- ✅ Pytest test suite
- ✅ TypeScript types

### Issue-First Workflow

Git hooks enforce that GitHub issues must exist before code:

```bash
# This will FAIL - no issue reference
git checkout -b my-feature
git commit -m "Add feature"
# ❌ Branch name must reference a GitHub issue

# This will PASS
git checkout -b issue-42-add-data-source
git commit -m "Add data source entity"
# ✅ Branch references issue #42
```

### Orchestrator Automation

```python
from services.orchestrator import Orchestrator

orch = Orchestrator(Path("."))

# Step 1: Create issue (REQUIRED before code)
result = orch.request_feature(
    title="Data quality checks",
    entity_definition={...},
    acceptance_criteria=[...]
)
# → Creates GitHub issue #42

# Step 2: Implement from approved issue
result = orch.implement_issue(42)
# → Creates branch, generates code, runs tests, creates PR
```

### Enforcement

- **Pre-commit hook** - Validates specs, checks issue reference, runs tests
- **Commit-msg hook** - Requires issue reference in commit message
- **CI pipeline** - Security scans, tests, coverage, auto-merge

## 9-Box Mapping to Claude Code

| Box | Description | Claude Code Feature | File Location |
|-----|-------------|---------------------|---------------|
| 1. Entity Catalog | Business entities | MCP Resources | `specs/entities.json` |
| 2. Task Library | Algorithms & skills | Agent Skills | `.claude/skills/` |
| 3. Policy Vault | Rules & policies | Hooks & Config | `.githooks/` |
| 4. Scheduler | Automated triggers | GitHub Actions | `.github/workflows/` |
| 5. Workers | Background processors | Headless Mode | `services/` |
| 6. Broadcaster | Event emitters | PostToolUse Hooks | `.claude/hooks/` |
| 7. Signal Ingestor | Event listeners | MCP SSE | MCP servers |
| 8. Reasoning Core | Decision logic | Subagents | `.claude/agents/` |
| 9. Command Center | User interface | Slash Commands | `.claude/commands/` |

## Tech Stack

- **Backend**: FastAPI, Pydantic, SQLAlchemy, PostgreSQL
- **Frontend**: Next.js, React, TypeScript, TailwindCSS
- **Testing**: Pytest, Jest, 80% coverage minimum
- **DevOps**: Docker, GitHub Actions, Vercel
- **AI**: Claude Code, MCP, Subagents

## Key Files

| File | Purpose |
|------|---------|
| `specs/entities.json` | Entity definitions (source of truth) |
| `specs/workbenches.json` | UI layouts per role |
| `specs/architecture/*.json` | 9-box feature specs |
| `specs/schema/*.json` | Contract schemas (Graph, Signal, GenUI) |
| `.claude/agents/architect.md` | Architect agent for 9-box specs |
| `services/orchestrator.py` | Workflow automation |
| `generators/generate_all.py` | Code generation |
| `CLAUDE.md` | AI assistant guidance |
| `FEEDBACK.md` | Problems & enhancements tracker |

## Contributing

1. Run `make feedback` to report issues or suggest enhancements
2. Create a GitHub issue before any code
3. Use `make architect` to generate 9-box spec
4. Follow the branch convention: `issue-42-description`
5. Tests must pass with 80%+ coverage

## License

MIT
