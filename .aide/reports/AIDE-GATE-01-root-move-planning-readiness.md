# AIDE-GATE-01 Root Inventory to Move-Planning Readiness Gate

## Status

- Task ID: AIDE-GATE-01
- Gate result: PASS_WITH_WARNINGS
- Branch: main
- HEAD: `f2bd322e7403cc076f29a512868516119d4becad`
- origin/main: `b4342d70dfdda7903d61ed78113ab0125184dfc7`

## Purpose

This gate verifies AIDE-ROOT-00 through AIDE-ROOT-06 evidence before any move-wave planning begins.

## Root Framework Outputs

Root recycling schemas, docs, index, runbook, and no-apply tools are present.

## Inventory Wave Outputs

AIDE-ROOT-01 through AIDE-ROOT-05 inventory waves are present with classifications, reference scans, sensitivity scans, and draft salvage maps.

## Reconciliation Outputs

AIDE-ROOT-06 reconciliation, move-wave candidates, first-move recommendation, and draft move-wave plan are present.

## First Move Candidate

- Selected: yes
- Root/subtree: `ide` / ide/README.md and ide/manifests projection docs/examples
- Risk: low
- apply_allowed: false
- approval_status: not_approved

## No-Apply Invariants

- moves applied: no
- deletes applied: no
- renames applied: no
- references rewritten: no
- active aliases introduced: no
- exceptions retired: no
- product/source/runtime/build behavior changed: no

## Known Warnings

- Draft candidate has high reference complexity and requires AIDE-MOVE-01-PLAN review.
- AIDE repo validate advisory unknown classifications remain.
- Full eval, full CTest, build, package, and release generation were not run.

## Gate Decision

PASS_WITH_WARNINGS. `AIDE-MOVE-01-PLAN` may proceed. Move/apply tasks remain unauthorized.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `python -m py_compile tools/aide/root_recycling_common.py tools/aide/inventory_root.py tools/aide/classify_files.py tools/aide/generate_salvage_map.py tools/aide/check_salvage_map.py tools/aide/scan_references.py tools/aide/check_no_raw_root_references.py tools/aide/scan_identity_markers.py tools/aide/scan_authority_markers.py tools/aide/scan_semantic_markers.py tools/aide/scan_abi_build_markers.py tools/aide/reconcile_root_inventories.py tools/aide/select_move_wave.py` | PASS | root recycling tools compile |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS | ignored untracked local roots are excluded |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS | ignored untracked local roots are excluded |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | strict validator passed |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | strict validator passed |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | build boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE test passed |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS_WITH_WARNINGS | unknown file classifications remain advisory |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | latest commit check passed |
| `git diff --check` | PASS_WITH_WARNINGS | CRLF warnings only |
| `git diff --cached --check` | PASS | no staged changes |
