# AIDE-GATE-00 Structure-to-Root Recycling Readiness Gate

## Status

- Task ID: AIDE-GATE-00
- Gate result: PASS_WITH_WARNINGS
- HEAD: `f2bd322e7403cc076f29a512868516119d4becad`
- origin/main: `b4342d70dfdda7903d61ed78113ab0125184dfc7`

## Purpose

This gate verifies the AIDE structure/control plane is ready to support root recycling inventory work.

## Decision

PASS_WITH_WARNINGS. Structure outputs, tool recycling evidence, wrapper surfaces, root framework schemas, and no-apply controls are present.

## Known Warnings

- AIDE repo validate still reports advisory unknown file classifications.
- Full eval, full CTest, build, package, and release generation were not run.

## Authorization

AIDE-ROOT inventory tasks may proceed. Move/apply tasks remain unauthorized.

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
