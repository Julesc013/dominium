# SPEC_LAW_TARGETS (EXEC0c)

Schema ID: LAW_TARGETS
Schema Version: 1.2.0
Status: binding.
Scope: canonical law target identifiers.

## Purpose
Define typed law targets that tasks and commands must declare. Targets are
schema-defined and versioned; ad hoc identifiers are forbidden.

## Target Identifier Format
Targets use a stable, dot-delimited token:
- DOMAIN.ACTION

Rules:
- DOMAIN and ACTION are uppercase ASCII with underscore separators.
- Targets are stable identifiers; renames require a migration note.

## Canonical Target Registry (Initial)
This list is binding for EXEC0c and may expand over time:
- LIFE.BIRTH
- LIFE.DEATH
- CIV.PRODUCTION
- WAR.ENGAGEMENT
- ECON.MARKET_CLEAR
- ECON.TRANSFER
- UI.PROJECTION
- NET.CLIENT_ADMISSION
- TOOL.ADMIN_ACTION
- EXEC.DERIVED_TASK
- EXEC.AUTH_TASK
- EXEC.BACKEND_SELECT
- EXEC.MULTITHREAD_ENABLE
- EXEC.SIMD_ENABLE
- EXEC.GPU_DERIVED_ENABLE
- EXEC.BUDGET_PROFILE_SELECT
- NET.UNAUTHENTICATED_PLAYERS
- NET.MODIFIED_CLIENTS
- TOOL.ADMIN_ACTIONS
- UI.DEBUG_OVERLAYS
- AUTH.CAPABILITY_GRANT
- AUTH.CAPABILITY_DENY
- AUTH.CAPABILITY_OVERRIDE
- AUTH.OMNIPOTENT_ACTION
- AUTH.LAW_MODIFY
- AUTH.ARCHIVAL_OVERRIDE

## Declaration Rules
- AUTHORITATIVE TaskNode entries MUST declare non-empty law_targets.
- DERIVED/PRESENTATION tasks MUST declare law_targets when they emit
  information or perform gated actions (e.g., UI.PROJECTION, EXEC.DERIVED_TASK).

## Versioning
Changes to this registry MUST bump Schema Version and update governance notes
per `schema/SCHEMA_VERSIONING.md`.
