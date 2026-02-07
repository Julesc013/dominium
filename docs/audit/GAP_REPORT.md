Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Gap Report

This report lists blocked, deferred, and immediate next actions from the
current normalization and coverage pass.

## Blocked items (require design/governance decision)

1) Canon conflict on stage/progression vocabulary in runtime-adjacent surfaces
   - Sources:
     - `libs/appcore/command/command_registry.h`
     - `schema/stage.declaration.schema`
     - `schema/pack_manifest.schema`
     - `tools/pack/pack_validate.py`
   - Finding: `STAGE_*` tokens remain in command/schema/tooling surfaces.
   - Impact: conflicts with the current invariant requiring capability/entitlement
     gating without stage/progression encoding.
   - Required: a governance-level reconciliation prompt; do not modify semantics ad hoc.

2) Pack integrity failures
   - Source: `docs/audit/PACK_AUDIT.txt`
   - Current status: `59 packs, 14 failures` (`45 PASS`, `14 FAIL`).
   - Failure classes:
     - missing FAB references (`part/interface/material/instrument/standard/process`)
     - dependency field mismatch (`record.dependencies` vs `depends/dependencies`)
   - Required: scoped pack/schema correction prompts with explicit migration notes.

## Deferred items (tracked, non-blocking for audit-only work)

- Temporary stubs remain (`46` in `docs/audit/STUB_REPORT.json`), mainly
  platform/UI/backend scaffolding.
- TODO/FIXME/PLACEHOLDER marker backlog remains (`49` hits in `docs/audit/INVENTORY.json` summary).
- Test-coverage matrix is structural by naming convention and needs deeper
  capability-to-test semantic mapping.

## Immediate next actions (safe, local, non-breaking)

1) Run a scoped pack-reference remediation pass for the 14 failing packs.
2) Add deterministic lint/report checks for dependency-field canonicalization in pack manifests.
3) Produce a governance reconciliation prompt for stage-token removal/migration to capabilities.
4) Add a stub policy report split by authoritative path vs scaffolding path and wire to RepoX informational output.
