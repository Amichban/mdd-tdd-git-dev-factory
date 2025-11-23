# Feedback & Enhancement Tracker

This file collects problems, feedback, and enhancement ideas for the MDD TDD Git Dev Factory template.

Use the feedback agent or `make feedback` to add new items.

---

## Problems

<!-- Issues that need to be fixed -->

### [P001] Schema validation incomplete
- **Date:** 2024-01-01
- **Severity:** Medium
- **Description:** Entity schema doesn't validate all field types properly
- **Suggested Fix:** Add comprehensive JSON schema for all field types
- **Status:** Open

### [P002] Generator doesn't handle relationships
- **Date:** 2024-01-01
- **Severity:** High
- **Description:** No support for foreign keys or entity relationships in specs
- **Suggested Fix:** Add `relationships` field to entity schema with `belongs_to`, `has_many`
- **Status:** Open

---

## Enhancements

<!-- New features and improvements -->

### [E001] Add database migration generation
- **Date:** 2024-01-01
- **Priority:** High
- **Description:** Generate Alembic migrations from entity spec changes
- **Benefit:** Automated schema evolution without manual SQL
- **Status:** Open

### [E002] Add GraphQL support
- **Date:** 2024-01-01
- **Priority:** Medium
- **Description:** Option to generate GraphQL schema alongside REST
- **Benefit:** Support for modern API patterns
- **Status:** Open

### [E003] Add real-time sync status via WebSocket
- **Date:** 2024-01-01
- **Priority:** Medium
- **Description:** Push sync status updates to UI instead of polling
- **Benefit:** Better UX, reduced server load
- **Status:** Open

### [E004] Add secrets manager integration
- **Date:** 2024-01-01
- **Priority:** High
- **Description:** Integrate with HashiCorp Vault or AWS Secrets Manager for connection strings
- **Benefit:** Production-ready security
- **Status:** Open

### [E005] Add bulk import/export for specs
- **Date:** 2024-01-01
- **Priority:** Low
- **Description:** Import entities from existing database schema, export to other formats
- **Benefit:** Easier migration from existing projects
- **Status:** Open

---

## Feedback

<!-- General feedback and observations -->

### [F001] Documentation needs examples
- **Date:** 2024-01-01
- **From:** Template users
- **Feedback:** Need more concrete examples of full workflows
- **Action:** Add example project showing complete entity lifecycle
- **Status:** Open

### [F002] Orchestrator error messages unclear
- **Date:** 2024-01-01
- **From:** Agent testing
- **Feedback:** When implement_issue fails, reason not always clear
- **Action:** Add detailed error context and suggested fixes
- **Status:** Open

---

## Template

Use this format when adding new items:

```markdown
### [TYPE###] Title
- **Date:** YYYY-MM-DD
- **Severity/Priority/From:** Value
- **Description:** What is the issue or idea
- **Suggested Fix/Benefit/Action:** How to address it
- **Status:** Open | In Progress | Closed
```

Types: P=Problem, E=Enhancement, F=Feedback
