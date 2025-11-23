# Implement Feature Command

This command guides the agent through the issue-first workflow for implementing a new feature.

## Workflow

When a user requests a new feature, follow this exact sequence:

### Phase 1: Requirements Gathering

1. **Understand the request** - Ask clarifying questions if needed
2. **Identify the entity** - What data needs to be stored?
3. **Define the fields** - What properties does it have?
4. **Identify the API needs** - What operations are needed?
5. **Understand the UI needs** - How will users interact with it?

### Phase 2: Create GitHub Issue (REQUIRED FIRST)

**IMPORTANT: Never write code before creating the issue.**

Use the orchestrator to create the issue:

```python
from pathlib import Path
from services.orchestrator import Orchestrator

orchestrator = Orchestrator(Path("."))

result = orchestrator.request_feature(
    title="Feature title",
    description="What this feature does",
    user_story="As a [role], I want [feature] so that [benefit]",
    acceptance_criteria=[
        "Criterion 1",
        "Criterion 2",
        "Tests pass with 80% coverage"
    ],
    entity_definition={
        "name": "EntityName",
        "layer": "domain|infrastructure|operational",
        "fields": [
            {"name": "id", "type": "uuid", "primary_key": True},
            # ... other fields
        ]
    },
    api_endpoints=[
        "GET /entities - List all",
        "POST /entities - Create",
        # ... other endpoints
    ],
    ui_requirements="Description of UI needs"
)

print(f"Issue created: {result.issue_url}")
print("Review the issue and remove 'needs-review' label when ready")
```

### Phase 3: Wait for Approval

Tell the user:
- The issue has been created
- They should review and refine it
- Remove 'needs-review' label when ready to implement

### Phase 4: Implement from Issue

Once approved, implement:

```python
result = orchestrator.implement_issue(issue_number)
print(result.message)
if result.pr_url:
    print(f"PR created: {result.pr_url}")
```

This will:
1. Create branch `feat/issue-{number}-{entity}`
2. Update specs/entities.json
3. Run `make generate`
4. Run `make test`
5. Create PR linked to issue

## Example Conversation

**User:** I need to track raw data sources for our ingestion pipeline

**Agent:** I'll help you create the RawDataSource feature. Let me first create a GitHub issue to document the requirements.

*[Creates issue with entity definition, acceptance criteria, etc.]*

Issue #42 created: https://github.com/repo/issues/42

Please review the issue and:
1. Refine any requirements
2. Approve by removing the 'needs-review' label
3. Let me know when ready to implement

**User:** Looks good, let's implement it

**Agent:** Implementing issue #42...

*[Runs orchestrator.implement_issue(42)]*

✅ Implementation complete!
- Branch: feat/issue-42-raw-data-source
- Tests: 25 passed, 87% coverage
- PR: https://github.com/repo/pull/43

The PR is ready for review and will auto-merge once approved.

## Key Principles

1. **Issue First** - Always create the GitHub issue before any code
2. **Single Source of Truth** - The issue contains the spec
3. **Traceability** - Branch → Commits → PR → Issue
4. **Automation** - Let the orchestrator handle branch/PR creation
5. **Quality Gates** - Tests must pass before PR
