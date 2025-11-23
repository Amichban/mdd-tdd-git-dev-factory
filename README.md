# MDD TDD Git Dev Factory

A **Model-Driven Development** template with **Test-Driven Development** practices and **Git-based** workflow automation.

> **Stop writing code. Start specifying systems.**

## What is This?

A development platform template where:
- **JSON specs are the source of truth** - Define entities, APIs, and UIs in specs
- **Code is generated, not written** - Models, routes, tests auto-generated
- **GitHub is the project manager** - Every change starts with an issue
- **Quality is enforced** - Hooks and CI prevent bad code from merging

## Quick Start

```bash
# 1. Create from template
gh repo create my-project --template your-username/mdd-tdd-git-dev-factory
cd my-project

# 2. Setup
make setup

# 3. Start development
make dev
```

## The Flow

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  IDEA  →  ISSUE  →  SPEC  →  GENERATE  →  TEST  →  DEPLOY   │
│                                                              │
│  "I need      Create       Edit JSON     make        make     │
│   users"     GitHub       specs/       generate    test      │
│              issue     entities.json                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Core Commands

```bash
make setup        # Install everything and setup database
make dev          # Start all services (frontend :3000, backend :8000)
make generate     # Regenerate code from specs
make test         # Run tests (80% coverage required)
make feedback     # Add problems/enhancements to tracker
```

## Architecture

### Spec-First Development

Define your entity in `specs/entities.json`:

```json
{
  "entities": [{
    "name": "User",
    "fields": [
      {"name": "id", "type": "uuid", "primary_key": true},
      {"name": "email", "type": "string", "required": true},
      {"name": "name", "type": "string", "max_length": 100}
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

```python
from services.orchestrator import Orchestrator

orch = Orchestrator(Path("."))

# Step 1: Create issue (REQUIRED before code)
result = orch.request_feature(
    title="User management",
    entity_definition={...},
    acceptance_criteria=[...]
)
# → Creates GitHub issue #42

# Step 2: Implement from approved issue
result = orch.implement_issue(42)
# → Creates branch, generates code, runs tests, creates PR
```

### Enforcement

- **Pre-commit hook** - Validates specs, blocks manual edits to generated code
- **Pre-push hook** - Verifies issue exists, enforces branch naming
- **CI pipeline** - Security scans, tests, coverage, auto-merge

## Tech Stack

- **Backend**: FastAPI, Pydantic, SQLAlchemy, PostgreSQL
- **Frontend**: Next.js, React, TypeScript, TailwindCSS
- **Testing**: Pytest, Jest, 80% coverage minimum
- **DevOps**: Docker, GitHub Actions, Vercel

## Key Files

| File | Purpose |
|------|---------|
| `specs/entities.json` | Entity definitions (source of truth) |
| `specs/workbenches.json` | UI layouts per role |
| `services/orchestrator.py` | Workflow automation |
| `generators/generate_all.py` | Code generation |
| `FEEDBACK.md` | Problems & enhancements tracker |
| `CLAUDE.md` | AI assistant guidance |

## Contributing

1. Run `make feedback` to report issues or suggest enhancements
2. Create a GitHub issue before any code
3. Follow the branch convention: `feat/issue-42-description`
4. Tests must pass with 80%+ coverage

## License

MIT
