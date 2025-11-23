# Agent Workflow Example: RawDataSource Feature

This document shows a complete example of the issue-first workflow, from initial request to merged code.

---

## The Conversation

### User Request

```
User: I need to track raw data sources - databases, APIs, files, and streams.
      Each source should have a connection string, refresh interval, and sync status.
      I need CRUD operations plus the ability to manually trigger syncs.
```

---

### Phase 1: Agent Creates GitHub Issue

```
Agent: I'll help you create the RawDataSource feature. Before writing any code,
       I need to create a GitHub issue to document the requirements and get your approval.

       Let me create the issue now...
```

**Agent executes:**
```python
from pathlib import Path
from services.orchestrator import Orchestrator

orchestrator = Orchestrator(Path("."))

result = orchestrator.request_feature(
    title="RawDataSource entity and API",
    description="Create entity to store configuration for external data sources (databases, APIs, files, streams) that feed into the platform.",
    user_story="As a data engineer, I want to register and manage data source configurations so that I can set up data ingestion pipelines without DevOps help.",
    acceptance_criteria=[
        "Entity created with all required fields",
        "CRUD API endpoints working",
        "Custom endpoints: sync, test_connection, sync-all",
        "Validation on all fields (name max 100 chars, refresh min 60s)",
        "Unique constraint on name",
        "Connection string marked as sensitive",
        "Tests with 80%+ coverage",
        "API documented in OpenAPI"
    ],
    entity_definition={
        "name": "RawDataSource",
        "layer": "infrastructure",
        "fields": [
            {"name": "id", "type": "uuid", "primary_key": True},
            {"name": "name", "type": "string", "required": True, "max_length": 100},
            {"name": "source_type", "type": "enum", "values": ["database", "api", "file", "stream", "webhook"]},
            {"name": "connection_string", "type": "string", "required": True, "sensitive": True},
            {"name": "schema_definition", "type": "json"},
            {"name": "refresh_interval", "type": "integer", "default": 3600, "min": 60},
            {"name": "is_active", "type": "boolean", "default": True},
            {"name": "last_sync_at", "type": "datetime"},
            {"name": "sync_status", "type": "enum", "values": ["pending", "syncing", "success", "failed"], "default": "pending"},
            {"name": "error_message", "type": "string"},
            {"name": "metadata", "type": "json"},
            {"name": "created_at", "type": "datetime", "auto_now_add": True},
            {"name": "updated_at", "type": "datetime", "auto_now": True}
        ],
        "indexes": [
            {"fields": ["name"], "unique": True},
            {"fields": ["source_type", "is_active"]},
            {"fields": ["sync_status"]}
        ]
    },
    api_endpoints=[
        "GET /raw-data-sources - List with filters (type, status, active) and pagination",
        "GET /raw-data-sources/{id} - Get single source",
        "POST /raw-data-sources - Create new source",
        "PUT /raw-data-sources/{id} - Update source",
        "DELETE /raw-data-sources/{id} - Delete source",
        "POST /raw-data-sources/{id}/sync - Trigger manual sync",
        "POST /raw-data-sources/{id}/test - Test connection",
        "POST /raw-data-sources/sync-all - Sync all active sources"
    ],
    ui_requirements="DataSourceWorkbench with Bento layout: stats panel, data table with filters, detail panel with sync history"
)
```

**Agent response:**
```
✅ Issue #2 created: https://github.com/your-repo/issues/2

I've created the GitHub issue with all the requirements including:
- Entity definition with 13 fields
- 8 API endpoints (5 CRUD + 3 custom)
- Acceptance criteria for testing

Please review the issue:
1. Check if the fields and types are correct
2. Verify the acceptance criteria
3. Add any missing requirements

When you're satisfied, remove the 'needs-review' label and let me know to proceed with implementation.
```

---

### Phase 2: User Reviews and Approves

```
User: I reviewed it, looks good. One change - add a 'tags' field as JSON array
      for categorization. Then let's implement it.
```

**Agent response:**
```
I'll update the issue to add the tags field, then proceed with implementation.

Updating issue #2...
Added: {"name": "tags", "type": "json", "description": "Array of tags for categorization"}

Now implementing issue #2...
```

---

### Phase 3: Agent Implements from Issue

**Agent executes:**
```python
result = orchestrator.implement_issue(2)
```

**Behind the scenes, the orchestrator:**

1. **Verifies issue exists and is approved**
   ```
   ✓ Issue #2 found
   ✓ 'needs-review' label removed
   ✓ Entity definition parsed
   ```

2. **Creates branch**
   ```
   $ git checkout -b feat/issue-2-raw-data-source
   Switched to a new branch 'feat/issue-2-raw-data-source'
   ```

3. **Updates specs**
   ```
   Updating specs/entities.json...
   Added RawDataSource entity with 14 fields
   ```

4. **Generates code**
   ```
   $ make generate
   ⚙️  Generating code from specs...
   ✓ src/domain/models/raw_data_source.py
   ✓ src/app/api/generated/raw_data_source_routes.py
   ✓ tests/test_raw_data_source.py
   ✓ src/app/components/workbenches/DataSourceWorkbench.tsx
   ```

5. **Runs tests**
   ```
   $ make test
   ========================= test session starts =========================
   tests/test_raw_data_source.py::TestRawDataSourceModel::test_create_valid_source PASSED
   tests/test_raw_data_source.py::TestRawDataSourceModel::test_name_max_length PASSED
   tests/test_raw_data_source.py::TestRawDataSourceAPI::test_list_empty PASSED
   tests/test_raw_data_source.py::TestRawDataSourceAPI::test_create_source PASSED
   ... (25 tests)

   ========================= 25 passed in 2.34s ==========================
   Coverage: 87%
   ```

6. **Commits and pushes**
   ```
   $ git add .
   $ git commit -m "feat(RawDataSource): add entity and API (#2)"
   [feat/issue-2-raw-data-source abc1234] feat(RawDataSource): add entity and API (#2)

   $ git push -u origin feat/issue-2-raw-data-source
   ```

7. **Creates PR**
   ```
   $ gh pr create --title "feat: add RawDataSource entity" --body "Closes #2..."
   https://github.com/your-repo/pull/3
   ```

---

### Phase 4: Result

**Agent response:**
```
✅ Implementation complete!

Summary:
- Branch: feat/issue-2-raw-data-source
- Commits: 1 (abc1234)
- Tests: 25 passed, 87% coverage
- PR: https://github.com/your-repo/pull/3

Generated files:
- src/domain/models/raw_data_source.py (Pydantic models)
- src/app/api/generated/raw_data_source_routes.py (FastAPI routes)
- tests/test_raw_data_source.py (pytest tests)
- src/app/components/workbenches/DataSourceWorkbench.tsx (React UI)

The PR is linked to issue #2 and will auto-close it when merged.

CI is running now. Once all checks pass:
- If low-risk: auto-merges
- If needs review: awaits approval

You can test locally with:
  make dev
  # API: http://localhost:8000/docs
  # UI: http://localhost:3000
```

---

## What Happened

```
┌─────────────────────────────────────────────────────────────────────┐
│                        COMPLETE FLOW                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User Request                                                        │
│       ↓                                                              │
│  Agent creates GitHub Issue #2                                       │
│       ↓                                                              │
│  User reviews & approves                                             │
│       ↓                                                              │
│  Agent calls orchestrator.implement_issue(2)                         │
│       ↓                                                              │
│  ┌─────────────────────────────────────┐                            │
│  │ Orchestrator executes:              │                            │
│  │ 1. Parse issue → entity spec        │                            │
│  │ 2. Create branch from issue         │                            │
│  │ 3. Update specs/entities.json       │                            │
│  │ 4. Run generators                   │                            │
│  │ 5. Run tests                        │                            │
│  │ 6. Commit & push                    │                            │
│  │ 7. Create PR linked to issue        │                            │
│  └─────────────────────────────────────┘                            │
│       ↓                                                              │
│  CI runs (quality gates, security, tests)                            │
│       ↓                                                              │
│  PR merged → Issue #2 auto-closed                                    │
│       ↓                                                              │
│  Feature deployed                                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

1. **Issue is the spec** - All requirements documented before coding
2. **Traceability** - Every line of code traces back to an issue
3. **Automation** - Agent handles branch, PR, tests automatically
4. **Quality gates** - Can't merge without tests passing
5. **Single source of truth** - Specs generate everything
6. **No manual editing** - Generated code is protected by hooks
