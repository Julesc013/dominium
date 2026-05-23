Status: DERIVED
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Result: PASS_WITH_WARNINGS
Date: 2026-05-23
Baseline Commit: af6f9a90f4985fd3061407076956420e4fd3ff3c
Task: STRUCTURE-RESIDUAL-CLEANUP-01
Scope: report bundle integrity, residual taxonomy classification, and structure guardrails

# STRUCTURE-RESIDUAL-CLEANUP-01

## Summary

The live repo is newer than the stale structure snapshot that cited
`6e0dd93f263815667135bbf94b445c44cff6f733`. The current baseline for this
pass is `af6f9a90f4985fd3061407076956420e4fd3ff3c`.

This pass does not perform broad source moves. It fixes the proof problem by
hardening the tracked-only structure report pipeline, then classifies the
remaining residual taxonomy issues with validator evidence and named follow-up
tasks.

## Files Inspected

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/structure_report_integrity.md`
- `docs/repo/audits/CANON_STRUCTURE_FINALIZE_NOW_01.md`
- `docs/repo/audits/CANON_STRUCTURE_RESIDUALS_LOOP_01.md`
- `contracts/package/packs/README.md`
- `tools/validators/repo/check_canonical_structure.py`
- `tools/validators/repo/check_content_layout.py`
- `tools/validators/repo/check_structure_report_integrity.py`
- tracked paths under `contracts/package/packs/`, `content/packs/`,
  `runtime/`, `engine/`, `.aide/`, and `tests/`

## Files Changed

- `docs/repo/structure_report_integrity.md`
- `docs/repo/structure_residual_classification.md`
- `docs/repo/audits/STRUCTURE_RESIDUAL_CLEANUP_01.md`
- `tools/validators/repo/README.md`
- `tools/validators/repo/check_structure_report_integrity.py`
- `tools/validators/repo/check_structure_residuals.py`

## What Changed

- Added strict manifest field checks for structure bundles, including `run_id`.
- Added metadata consistency checks across `dir_tree.json`, `dir_tree.txt`, and
  `dirfiles_run.log`.
- Added zip member integrity checks against manifest hashes.
- Added `--write-bundle` support for producing a fresh local tracked-only
  structure bundle under `.dominium.local/<task-id>/`.
- Added a residual classifier for pack authority, pack-local `content/`
  payload layout, runtime/engine residual taxonomy, schema breadth, AIDE
  state-like roots, missing projection/workbench surfaces, and tests taxonomy.

## Current Classification

- `contracts/package/packs/` is contract-only and currently contains only its
  direct README note.
- `contracts/diagnostic/` is the canonical diagnostic contract root;
  `contracts/diagnostics/` remains retired.
- `content/packs/**/content/` is classified as legacy pack payload layout, not
  contract authority.
- `runtime/project_graph`, `runtime/ui/client`, `runtime/ui/control/domui`, and
  `runtime/include/domino/ui/dui` have accepted ownership evidence.
- `engine/compatibility`, `archive/legacy/runtime/compatx`, `engine/foundation`,
  `engine/serialization`, `runtime/serialization`, `engine/session`, and
  `runtime/session` remain classified residuals pending
  `RUNTIME-RESIDUAL-TAXONOMY-01`.
- `contracts/schema/runtime/engine/` owns the former `contracts/schema/engine/`
  schemas.
- `contracts/schema/repo/meta/` owns the former `contracts/schema/meta/`
  schemas.
- `contracts/schema/` remains broad and is deferred to
  `SCHEMA-CANON-RESIDUAL-02`.
- tracked `.aide/` state-like roots are classified as AIDE control-plane,
  fixture, policy, or evidence roots; mutable local state remains outside
  tracked `.aide/`.
- missing `runtime/projection/cli`, `runtime/projection/headless`,
  `runtime/projection/native`, and `apps/workbench/shell` are deferred
  warnings, not reasons to create empty placeholders.

## Validation

- `py -3 .aide/scripts/aide_lite.py doctor` - PASS
- `py -3 .aide/scripts/aide_lite.py validate` - PASS
- `py -3 .aide/scripts/aide_lite.py pack --task "STRUCTURE-RESIDUAL-CLEANUP-01"` - PASS
- `py -3 -m tools.aide.validate` - unavailable (`No module named tools.aide.validate`)
- `py -3 -m tools.aide.doctor` - unavailable (`No module named tools.aide.doctor`)
- `py -3 -m py_compile tools/validators/repo/check_structure_report_integrity.py tools/validators/repo/check_structure_residuals.py` - PASS
- `py -3 tools/validators/repo/check_structure_report_integrity.py --repo-root . --json` - PASS
- `py -3 tools/validators/repo/check_structure_report_integrity.py --repo-root . --write-bundle .dominium.local/structure-residual-cleanup-01 --strict --json` - PASS
- `py -3 tools/validators/repo/check_structure_residuals.py --repo-root . --json --max-findings 120` - PASS_WITH_WARNINGS
- `py -3 tools/validators/repo/check_canonical_structure.py --repo-root . --json --max-findings 80` - PASS_WITH_WARNINGS
- `py -3 tools/validators/repo/check_content_layout.py --repo-root . --strict` - PASS
- `git diff --check` - PASS

## Warnings Preserved

- full CTest remains a full/release gate, not run in this pass;
- schema taxonomy breadth remains deferred to `SCHEMA-CANON-RESIDUAL-02`;
- pack-local payload layout remains deferred to `PACK-INTERNAL-LAYOUT-CANON-01`;
- runtime/engine residual taxonomy remains deferred to
  `RUNTIME-RESIDUAL-TAXONOMY-01`;
- AIDE state classification remains deferred to `AIDE-STATE-CLASSIFICATION-01`;
- Workbench shell and projection mode roots remain deferred until their owning
  implementation or conformance tasks exist;
- tests taxonomy remains warning-only and not a feature/release proof.

## Non-Goals Preserved

- no product/runtime behavior change;
- no source-tree moves;
- no automatic branch, merge, scheduler, or promotion automation;
- no Workbench shell implementation;
- no package/replay/client implementation changes;
- no full CTest or broad build.

## Next Tasks

- `STRUCTURE-REPORT-INTEGRITY-02` can now use the hardened validator/generator
  if a retained proof bundle is required.
- `SCHEMA-CANON-RESIDUAL-02`
- `PACK-AUTHORITY-FINAL-CHECK-02`
- `PACK-INTERNAL-LAYOUT-CANON-01`
- `RUNTIME-RESIDUAL-TAXONOMY-01`
- `AIDE-STATE-CLASSIFICATION-01`
- `AIDE-CAPABILITY-REALITY-LEDGER-01`
- `PRESENTATION-CONTRACT-01`
- `PROJECTION-CONFORMANCE-01`
- `POINTER-WIDTH-SERIALIZATION-AUDIT-01`
