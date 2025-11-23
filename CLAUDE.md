# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Concept

This is a **model-driven development platform** where JSON specifications are the single source of truth. Code is generated from specs, never hand-written for generated portions.

**The flow:** Issue → Spec → Generate → Test → Deploy

## Essential Commands

```bash
make setup        # Full setup: install deps, build containers, run migrations
make dev          # Start all services (frontend :3000, backend :8000, db :5432)
make generate     # Regenerate code from specs (models, routes, tests)
make test         # Run pytest with coverage (80% minimum required)
make lint         # Lint Python (ruff) and TypeScript (eslint)
make validate     # Validate specs against JSON schema
```

## Architecture

### Spec-First Code Generation

Specs in `specs/` drive all generated code:

- **`specs/entities.json`** → Generates Pydantic models (`src/domain/models/`) + FastAPI routes (`src/app/api/generated/`) + tests
- **`specs/workbenches.json`** → Generates UI components per persona/role
- **`specs/algorithms.json`** → Generates function stubs with observability hooks

**Never edit files in `src/domain/models/` or `src/app/api/generated/` directly.** Edit specs and run `make generate`.

### Issue-First Workflow

The orchestrator (`services/orchestrator.py`) enforces that GitHub issues must exist before code:

```python
from pathlib import Path
from services.orchestrator import Orchestrator

orch = Orchestrator(Path("."))

# Step 1: Create issue (REQUIRED)
result = orch.request_feature(
    title="Feature name",
    description="What it does",
    user_story="As a...",
    acceptance_criteria=["..."],
    entity_definition={"name": "EntityName", "fields": [...]}
)

# Step 2: Implement from approved issue
result = orch.implement_issue(issue_number=42)
```

`implement_issue()` automatically: creates branch → updates specs → generates code → runs tests → creates PR.

### Core Services

| Service | Purpose |
|---------|---------|
| `services/orchestrator.py` | Workflow automation, issue-first enforcement |
| `services/github_bridge.py` | GitHub API (issues, PRs, branches, worktrees) |
| `services/dependency_graph.py` | Entity dependencies, conflict detection, risk assessment |
| `services/events.py` | Algorithm observability (decision/result events) |

### Event Bus Observability

Algorithms emit events for explainability:

```python
from services.events import decision, result

is_valid = decision(
    correlation_id=correlation_id,
    node_id="algo.name",
    step="validate",
    condition=value > 0,
    reason=f"Value is {value}",
    impact="Proceed" if value > 0 else "Skip"
)
```

Events: `job_started`, `decision_evaluated`, `result_computed`, `job_completed`, `job_failed`

## Conventions

### Branch Naming
```
type/issue-NUMBER-description
```
Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

Example: `feat/issue-42-add-user-roles`

### Entity Naming
- Spec ID: `snake_case` (e.g., `raw_data_source`)
- Class: `PascalCase` (e.g., `RawDataSource`)
- Table: `snake_case_plural` (e.g., `raw_data_sources`)

## Enforcement Hooks

### Pre-commit (`.githooks/pre-commit`)
- Validates specs against JSON schema
- Blocks manual edits to generated files (unless spec also changed)
- Runs tests (must pass)

### Pre-push (`.githooks/pre-push`)
- Enforces branch naming convention
- Verifies GitHub issue exists
- Runs full test suite

Enable hooks: `git config core.hooksPath .githooks`

## Docker Services

```bash
make dev  # Starts all services
```

- **frontend**: Next.js on :3000
- **backend**: FastAPI on :8000
- **db**: PostgreSQL on :5432
- **redis**: Event bus on :6379

## Key Patterns

1. **Spec changes only** - Modify `specs/*.json`, never generated code
2. **Issue before code** - Every feature starts with a GitHub issue
3. **Orchestrator handles workflow** - Branch, generate, test, PR automated
4. **Observability built-in** - Algorithms emit decision events to event bus
5. **Pre-commit validates** - Can't commit invalid specs or failing tests

## CI Pipeline

`.github/workflows/ci.yml` enforces:
- Spec validation and consistency check
- Security scanning (TruffleHog, Trivy)
- Tests with 80% coverage minimum
- Issue linking verification
- Auto-merge for low-risk changes with passing tests

## Project Rules

### Skills
Four skills guide the development process:
1. **domain-expert** - Idea → Specification
2. **ontology-expert** - Specification → JSON Specs
3. **uiux-specialist** - Specs → Workbench layouts
4. **ai-augmentation** - Human-AI collaboration patterns

### Code Standards

#### Python Code
- Use type hints
- Follow PEP 8
- Use Pydantic for models
- Use pytest for tests

#### TypeScript Code
- Use strict mode
- Define interfaces for all data
- Use React functional components
- Follow ESLint rules

### Security

#### Never Commit
- Secrets, API keys, passwords
- .env files with real values
- Credentials of any kind

#### Always Use
- Environment variables for secrets
- JSON Schema validation
- Input sanitization
- Type checking

### Slash Commands
- `/new-idea` - Start domain expert skill
- `/to-ontology` - Generate JSON specs
- `/design-workbench` - Design UI layout
- `/generate` - Run all generators
- `/status` - Show GitHub project state
- `/deploy` - Trigger deployment

### File Modification Rules

#### Editable
- `specs/*.json` - Via Model Editor UI or skills
- `.claude/skills/*.md` - Skill definitions
- `tests/` - Test files
- `services/` - Service implementations

#### Generated (Do Not Edit)
- `src/domain/models/` - From entities.json
- `src/app/api/` - From entities.json + workflows.json
- `src/components/` - From workbenches.json

### Testing

#### Unit Tests
- Test each algorithm independently
- Test entity validations
- Test action preconditions

#### Integration Tests
- Test workflow transitions
- Test API endpoints
- Test database operations

#### E2E Tests
- Test complete user journeys
- Test workbench interactions

## 9-Box Platform Architecture

Every feature must be specified across all 9 boxes in 3 systems.

### System 1: Registry (What We Have)
| Box | Claude Code Feature | Maps To |
|-----|---------------------|---------|
| 1. Entity Catalog | MCP Resources | `specs/entities.json`, MCP servers |
| 2. Task Library | Agent Skills | `.claude/skills/`, `specs/algorithms.json` |
| 3. Policy Vault | Hooks & Config | `.githooks/`, `.claude/hooks/` |

### System 2: Engine (How It Runs)
| Box | Claude Code Feature | Maps To |
|-----|---------------------|---------|
| 4. Scheduler | GitHub Actions | `.github/workflows/` |
| 5. Workers | Headless Mode | `services/`, `claude -p "..."` |
| 6. Broadcaster | PostToolUse Hooks | `.claude/hooks/post-*.sh` |

### System 3: Observer (How It Learns)
| Box | Claude Code Feature | Maps To |
|-----|---------------------|---------|
| 7. Signal Ingestor | MCP Event Bus | MCP SSE streams |
| 8. Reasoning Core | Subagents | `.claude/agents/` |
| 9. Command Center | Slash Commands | `.claude/commands/` |

### The Three Contracts

#### Contract 1: Graph (Registry)
Typed business graph nodes with lineage.

#### Contract 2: Signal (Observer)
Traceable telemetry events with correlation IDs.

#### Contract 3: GenUI (Interaction)
Safe UI widget configurations for slash commands.

### Usage

```bash
claude @architect "I need to add data quality checks"
```

Output: `specs/architecture/feature-name.json`
