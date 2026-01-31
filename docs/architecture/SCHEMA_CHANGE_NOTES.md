# SCHEMA_CHANGE_NOTES

Status: binding.
Scope: required migration notes for any schema changes.

Add entries below whenever files under `schema/` change.
Each entry MUST reference the relevant invariant IDs (for example: `INV-SCHEMA-VERSIONED`,
`INV-SCHEMA-UNKNOWN-PRESERVE`, `INV-SCHEMA-NO-SEMANTIC-REUSE`).

Template:
- Date: YYYY-MM-DD
  Schema(s): schema/...
  Change: <short summary>
  Invariants: INV-...
  Migration: <required migration steps or "none">

- Date: 2026-01-31
  Schema(s): schema/knowledge.artifact.schema; schema/skill.profile.schema; schema/education.program.schema
  Change: add KNS0 knowledge, skill, and education contracts
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)

- Date: 2026-01-31
  Schema(s): schema/institution.entity.schema; schema/institution.scope.schema; schema/institution.capability.schema
  Change: add institution entities, jurisdiction scopes, and capability contracts
  Invariants: INV-SCHEMA-VERSIONED; INV-SCHEMA-UNKNOWN-PRESERVE; INV-SCHEMA-NO-SEMANTIC-REUSE; INV-UNITS-ANNOTATED
  Migration: none (new schemas)
