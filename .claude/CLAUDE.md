# Development Platform - Project Rules

## Overview
This is a model-driven development platform where JSON specs are the single source of truth.

## Architecture

### Source of Truth
- `specs/entities.json` - Entity definitions (properties, relationships, actions)
- `specs/algorithms.json` - Calculations and business logic
- `specs/workflows.json` - Process state machines
- `specs/workbenches.json` - UI layouts per persona

### Generated Code
Code in `src/` is generated from specs. Do not edit generated code directly.

### Skills
Four skills guide the development process:
1. **domain-expert** - Idea → Specification
2. **ontology-expert** - Specification → JSON Specs
3. **uiux-specialist** - Specs → Workbench layouts
4. **ai-augmentation** - Human-AI collaboration patterns

## Development Workflow

### 1. GitHub First
Every change must create a GitHub Issue before code:
- Issue tracks the change
- Branch links to issue
- PR closes issue
- This ensures audit trail and coordination

### 2. TDD Required
- Write tests before implementation
- Tests must pass before commit
- Minimum 80% coverage

### 3. Spec Changes
When modifying specs:
1. Validate against JSON Schema
2. Run generators to update code
3. Run tests
4. Create PR

### 4. Automation
The Orchestrator automates:
- Issue/branch/PR creation
- Dependency analysis
- Worktree management
- Code generation
- Testing
- Deployment

## Code Standards

### Naming Conventions
- Entity IDs: `snake_case` (e.g., `trade_signal`)
- Entity names: `PascalCase` (e.g., `TradeSignal`)
- Algorithm IDs: `algo_` prefix (e.g., `algo_signal_strength`)
- Workflow IDs: `workflow_` prefix (e.g., `workflow_signal_review`)

### JSON Specs
- Always include `$schema` reference
- Use semantic versioning
- Include descriptions for all elements
- Define constraints where applicable

### Python Code
- Use type hints
- Follow PEP 8
- Use Pydantic for models
- Use pytest for tests

### TypeScript Code
- Use strict mode
- Define interfaces for all data
- Use React functional components
- Follow ESLint rules

## Security

### Never Commit
- Secrets, API keys, passwords
- .env files with real values
- Credentials of any kind

### Always Use
- Environment variables for secrets
- JSON Schema validation
- Input sanitization
- Type checking

## Commands

### Slash Commands
- `/new-idea` - Start domain expert skill
- `/to-ontology` - Generate JSON specs
- `/design-workbench` - Design UI layout
- `/generate` - Run all generators
- `/status` - Show GitHub project state
- `/deploy` - Trigger deployment

## File Modification Rules

### Editable
- `specs/*.json` - Via Model Editor UI or skills
- `.claude/skills/*.md` - Skill definitions
- `tests/` - Test files
- `services/` - Service implementations

### Generated (Do Not Edit)
- `src/domain/models/` - From entities.json
- `src/app/api/` - From entities.json + workflows.json
- `src/components/` - From workbenches.json

## Testing

### Unit Tests
- Test each algorithm independently
- Test entity validations
- Test action preconditions

### Integration Tests
- Test workflow transitions
- Test API endpoints
- Test database operations

### E2E Tests
- Test complete user journeys
- Test workbench interactions
