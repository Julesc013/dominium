Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Gap Report

This report lists blocked, deferred, and immediate next actions from the
current normalization and coverage pass.

## Blocked items (require design/governance decision)

1) Pack integrity failures
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
- `INVENTORY_MACHINE.json` includes transient build/test outputs and should be stabilized
  to reduce churn between runs.

## Immediate next actions (safe, local, non-breaking)

1) Run a scoped pack-reference remediation pass for the 14 failing packs.
2) Add deterministic lint/report checks for dependency-field canonicalization in pack manifests.
3) Split temporary stubs into scaffolding vs authoritative paths and wire an informational RepoX report.
4) Tighten inventory generation filters for transient artifacts (`__pycache__`, test-save outputs, temporary scripts).
