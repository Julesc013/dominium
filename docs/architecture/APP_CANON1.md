Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Application Layer Canon (APP-CANON1)

This document extends APP-CANON0 without replacing it.

## Capability matrix (explicit)
- Capabilities are declared as data in `schema/app/app_capability.schema`.
- Each application declares required and provided capabilities.
- Missing capabilities cause explicit refusals.

## Failure taxonomy (canonical)
- Failure codes are defined in `schema/app/app_failure_code.schema`.
- Commands document their failure codes; no ad-hoc errors.

## Output format contracts
- All commands support `--format=human` and `--format=json`.
- Machine output follows `schema/app/app_output_envelope.schema`.

## Batch and automation mode
- Non-interactive execution is supported with deterministic exit codes.
- No prompts in batch mode; failures are explicit.

## Instance lineage and provenance
- Instance manifests include immutable lineage fields:
  - parent_instance_id (optional)
  - creation_reason (new | clone | migrate | replay | test)
  - originating_commit
  - originating_tag
  - originating_tool

## Multi-instance and multi-version safety
- Instance isolation is strict; profiles do not cross instances.
- Version mismatches are explicit refusals.
- Lockfile semantics are documented in `docs/ops/INSTANCE_ISOLATION.md`.

## SRZ read-only visibility
- Applications may display SRZ status but never control it.
- SRZ status is read-only and surfaced via contracts.

## Pack and content safety
- Applications refuse implicit downloads.
- Pack provenance, signatures, and compatibility are shown.
- `app_pack_state` includes `pack_origin`, `signature_status`, `compatibility_range`.

## Cross-application consistency
- Command IDs, failure codes, and output envelopes are identical across apps.
- RepoX enforces parity and rejects drift.
