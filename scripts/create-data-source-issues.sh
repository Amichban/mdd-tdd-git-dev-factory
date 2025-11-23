#!/bin/bash
#
# Create GitHub Issues for Data Ingestion Epic
#
# This script creates the Epic and child issues for the RawDataSource feature.
# Run this BEFORE any code development begins.
#
# Prerequisites:
# - GitHub CLI (gh) installed and authenticated
# - Repository exists on GitHub
#
# Usage: ./scripts/create-data-source-issues.sh

set -e

echo "📝 Creating GitHub Issues for Data Ingestion Epic..."
echo ""

# Check gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "   Install: https://cli.github.com/"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "   Run: gh auth login"
    exit 1
fi

# Get repo info
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null || echo "")
if [ -z "$REPO" ]; then
    echo "❌ Not in a GitHub repository"
    echo "   Initialize with: gh repo create"
    exit 1
fi

echo "Repository: $REPO"
echo ""

# ============================================
# Create Epic
# ============================================
echo "Creating Epic: Data Ingestion Pipeline..."

EPIC_BODY=$(cat <<'EOF'
## Epic Summary
Build a complete data ingestion system that allows data engineers to configure, monitor, and manage external data sources feeding into the platform.

## Business Value
- Enable self-service data source configuration without DevOps involvement
- Provide visibility into sync status and failures
- Support multiple source types (databases, APIs, files, streams)
- Ensure data lineage tracking from source to consumption

## User Stories
- As a **data engineer**, I want to register a new data source so that I can start ingesting data
- As a **data engineer**, I want to see sync status so that I know if ingestion is working
- As a **data engineer**, I want to manually trigger syncs so that I can refresh data on demand
- As a **data engineer**, I want to define schemas so that data is validated on ingestion

## Child Issues
<!-- Will be updated with issue numbers -->
- [ ] RawDataSource entity and API
- [ ] DataSourceWorkbench UI
- [ ] Sync engine with connectors
- [ ] Schema validation on ingestion
- [ ] Alerting for failed syncs

## Acceptance Criteria
- [ ] Can create data sources via API and UI
- [ ] Supports: database, api, file, stream, webhook types
- [ ] Sync status visible in real-time
- [ ] Failed syncs trigger alerts
- [ ] All actions logged for audit
- [ ] 80%+ test coverage

## Out of Scope
- Data transformation (separate epic)
- Data quality rules (separate epic)
- Historical sync replay
EOF
)

EPIC_NUMBER=$(gh issue create \
    --title "[EPIC] Data Ingestion Pipeline" \
    --body "$EPIC_BODY" \
    --label "epic" \
    | grep -oE '[0-9]+$')

echo "✅ Epic created: #$EPIC_NUMBER"

# ============================================
# Create Feature Issue: RawDataSource
# ============================================
echo "Creating Feature: RawDataSource entity and API..."

FEATURE_BODY=$(cat <<EOF
## Summary
Create the RawDataSource entity to store configuration for external data sources. This is the foundation for the data ingestion pipeline.

Parent Epic: #$EPIC_NUMBER

## User Story
As a **data engineer**, I want to register and manage data source configurations so that I can set up data ingestion pipelines without DevOps help.

## Acceptance Criteria
- [ ] Entity created with all required fields
- [ ] CRUD API endpoints working
- [ ] Custom endpoints: sync, test_connection, sync-all
- [ ] Validation on all fields
- [ ] Unique constraint on name
- [ ] Indexes for common queries
- [ ] Connection string marked as sensitive
- [ ] API documented in OpenAPI
- [ ] Tests with 80%+ coverage

## Entity Definition
\`\`\`json
{
  "name": "RawDataSource",
  "layer": "infrastructure",
  "fields": [
    { "name": "id", "type": "uuid", "primary_key": true },
    { "name": "name", "type": "string", "required": true, "max_length": 100 },
    { "name": "source_type", "type": "enum", "values": ["database", "api", "file", "stream", "webhook"] },
    { "name": "connection_string", "type": "string", "sensitive": true },
    { "name": "schema_definition", "type": "json" },
    { "name": "refresh_interval", "type": "integer", "default": 3600, "min": 60 },
    { "name": "is_active", "type": "boolean", "default": true },
    { "name": "last_sync_at", "type": "datetime" },
    { "name": "sync_status", "type": "enum", "values": ["pending", "syncing", "success", "failed"] },
    { "name": "error_message", "type": "string" },
    { "name": "metadata", "type": "json" },
    { "name": "created_at", "type": "datetime", "auto_now_add": true },
    { "name": "updated_at", "type": "datetime", "auto_now": true }
  ],
  "indexes": [
    { "fields": ["name"], "unique": true },
    { "fields": ["source_type", "is_active"] },
    { "fields": ["sync_status"] }
  ]
}
\`\`\`

## API Endpoints
- [ ] \`GET /raw-data-sources\` - List with filters and pagination
- [ ] \`GET /raw-data-sources/{id}\` - Get single source
- [ ] \`POST /raw-data-sources\` - Create new source
- [ ] \`PUT /raw-data-sources/{id}\` - Update source
- [ ] \`DELETE /raw-data-sources/{id}\` - Delete source
- [ ] \`POST /raw-data-sources/{id}/sync\` - Trigger manual sync
- [ ] \`POST /raw-data-sources/{id}/test\` - Test connection
- [ ] \`POST /raw-data-sources/sync-all\` - Sync all active sources

## Definition of Done
1. Spec added to \`specs/entities.json\`
2. Run \`make generate\`
3. All tests pass with \`make test\`
4. PR created and merged
EOF
)

FEATURE_NUMBER=$(gh issue create \
    --title "[FEATURE] RawDataSource entity and API" \
    --body "$FEATURE_BODY" \
    --label "feature,infrastructure,entity" \
    | grep -oE '[0-9]+$')

echo "✅ Feature created: #$FEATURE_NUMBER"

# ============================================
# Create Feature Issue: DataSourceWorkbench
# ============================================
echo "Creating Feature: DataSourceWorkbench UI..."

UI_BODY=$(cat <<EOF
## Summary
Create the DataSourceWorkbench UI component for managing raw data sources using the Bento layout pattern.

Parent Epic: #$EPIC_NUMBER
Depends on: #$FEATURE_NUMBER

## User Story
As a **data engineer**, I want a dedicated workbench UI so that I can manage data sources efficiently without switching between multiple screens.

## Acceptance Criteria
- [ ] Bento layout with 3 zones (Pulse, Canvas, Co-Pilot)
- [ ] Stats cards showing active sources and failed syncs
- [ ] Data table with filtering, search, and pagination
- [ ] Detail panel showing source configuration
- [ ] Sync and Test buttons functional
- [ ] Keyboard shortcuts (n=create, r=refresh, /=search)
- [ ] Real-time status updates
- [ ] Responsive design

## UI Layout
\`\`\`
┌──────────┬─────────────────────────────┬────────────────┐
│  PULSE   │         CANVAS              │   CO-PILOT     │
│  (20%)   │         (50%)               │    (30%)       │
├──────────┼─────────────────────────────┼────────────────┤
│ Stats    │  Data Table                 │ Detail Panel   │
│ Activity │  - Search & Filters         │ - Config       │
│ Feed     │  - Sortable columns         │ - Schema       │
│          │  - Row actions              │ - Status       │
│          │  - Pagination               │ - Sync History │
└──────────┴─────────────────────────────┴────────────────┘
\`\`\`

## Definition of Done
1. Spec added to \`specs/workbenches.json\`
2. Component generated in \`src/app/components/workbenches/\`
3. Connected to API endpoints
4. All tests pass
5. PR created and merged
EOF
)

UI_NUMBER=$(gh issue create \
    --title "[FEATURE] DataSourceWorkbench UI" \
    --body "$UI_BODY" \
    --label "feature,ui,workbench" \
    | grep -oE '[0-9]+$')

echo "✅ Feature created: #$UI_NUMBER"

# ============================================
# Update Epic with child issues
# ============================================
echo ""
echo "Updating Epic with child issue references..."

gh issue edit "$EPIC_NUMBER" --body "$(gh issue view $EPIC_NUMBER --json body -q '.body' | sed "s/- \[ \] RawDataSource entity and API/- [ ] #$FEATURE_NUMBER - RawDataSource entity and API/" | sed "s/- \[ \] DataSourceWorkbench UI/- [ ] #$UI_NUMBER - DataSourceWorkbench UI/")"

echo ""
echo "============================================"
echo "✅ All issues created successfully!"
echo "============================================"
echo ""
echo "Epic:     #$EPIC_NUMBER - Data Ingestion Pipeline"
echo "Feature:  #$FEATURE_NUMBER - RawDataSource entity and API"
echo "Feature:  #$UI_NUMBER - DataSourceWorkbench UI"
echo ""
echo "Next steps:"
echo "  1. Review issues and refine requirements"
echo "  2. Remove 'needs-review' label when ready"
echo "  3. Implement with: python -c \"from services.orchestrator import *; o = Orchestrator(Path('.')); o.implement_issue($FEATURE_NUMBER)\""
echo ""
echo "Or manually:"
echo "  git checkout -b feat/issue-$FEATURE_NUMBER-raw-data-source"
echo "  # Edit specs/entities.json"
echo "  make generate && make test"
echo "  git add . && git commit -m 'feat: add RawDataSource entity (#$FEATURE_NUMBER)'"
echo "  git push && gh pr create"
EOF
