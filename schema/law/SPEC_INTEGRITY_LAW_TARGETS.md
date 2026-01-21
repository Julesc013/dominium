# SPEC_INTEGRITY_LAW_TARGETS (OMNI2)

Schema ID: INTEGRITY_LAW_TARGETS
Schema Version: 1.0.0
Status: binding.
Scope: integrity and enforcement law target identifiers.

## Purpose
Define law targets specific to integrity evaluation, refusals, and enforcement.

## Target Identifier Format
Targets use a stable, dot-delimited token:
- DOMAIN.ACTION

Rules:
- DOMAIN and ACTION are uppercase ASCII with underscore separators.
- Targets are stable identifiers; renames require a migration note.

## Integrity Target Registry (Append-Only)
This list is binding and may only expand by appending new entries:
- INTEGRITY.SIGNAL_INGEST
- INTEGRITY.REFUSAL_EMIT
- INTEGRITY.ENFORCEMENT_ACTION
- INTEGRITY.ESCALATION_EVALUATE
- INTEGRITY.ESCALATION_APPLY
- INTEGRITY.ADMIN_OVERRIDE
- INTEGRITY.CAPABILITY_REVOKE
- INTEGRITY.SESSION_QUARANTINE

## Versioning
Changes to this registry MUST bump Schema Version and update governance notes
per `schema/SCHEMA_VERSIONING.md`.
