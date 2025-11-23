# [FEATURE] RawDataSource entity and API

**Issue #2** | Labels: `feature`, `infrastructure`, `api` | Parent: #1

## Summary
Create the RawDataSource entity to store configuration for external data sources. This is the foundation for the data ingestion pipeline.

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

```json
{
  "name": "RawDataSource",
  "layer": "infrastructure",
  "fields": [
    { "name": "id", "type": "uuid", "primary_key": true },
    { "name": "name", "type": "string", "required": true, "max_length": 100, "unique": true },
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
```

## API Endpoints
- [x] `GET /raw-data-sources` - List with filters (type, status, active) and pagination
- [x] `GET /raw-data-sources/{id}` - Get single source
- [x] `POST /raw-data-sources` - Create new source
- [x] `PUT /raw-data-sources/{id}` - Update source
- [x] `DELETE /raw-data-sources/{id}` - Delete source
- [x] `POST /raw-data-sources/{id}/sync` - Trigger manual sync
- [x] `POST /raw-data-sources/{id}/test` - Test connection
- [x] `POST /raw-data-sources/sync-all` - Sync all active sources

## Technical Notes
- Use SQLAlchemy for ORM
- Connection strings should be encrypted at rest (future: integrate with secrets manager)
- Sync and test endpoints emit events to bus for observability
- Indexes optimize common filter patterns

## Definition of Done
1. Spec added to `specs/entities.json`
2. Run `make generate` to create model, routes, tests
3. All tests pass with `make test`
4. API accessible at `/docs`
5. PR created and merged

## Branch
```
feat/issue-2-raw-data-source
```
