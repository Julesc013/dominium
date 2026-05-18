Status: PASS_WITH_WARNINGS
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-00

# MOVE-ROUTER-00 Validation

## Router

- `python tools/migration/route_bad_roots.py --repo-root . --dry-run --include-quarantine --fail-on-collision --json-out .aide/reports/MOVE-ROUTER-00-dry-run.json --md-out .aide/reports/MOVE-ROUTER-00-dry-run.md --route-table-out .aide/reports/MOVE-ROUTER-00-route-table.json --skipped-out .aide/reports/MOVE-ROUTER-00-skipped-or-quarantined.md`: PASS.
- Bad-root tracked files: 1,765.
- Routed files: 1,765.
- Known canonical routes: 1,694.
- Quarantine routes: 71.
- Target collisions: 0.
- Skipped/impossible routes: 0.

## New Validators

- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .`: PASS_WITH_WARNINGS, 106 findings, 0 blockers.
- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root . --json`: PASS_WITH_WARNINGS, 106 findings, 0 blockers.
- `python tools/validators/repo/check_forbidden_root_names.py --repo-root .`: PASS_WITH_WARNINGS, 1,460 findings, 0 blockers.
- `python tools/validators/repo/check_forbidden_root_names.py --repo-root . --json`: PASS_WITH_WARNINGS, 1,460 findings, 0 blockers.
- `python tools/validators/repo/check_bad_root_absence.py --repo-root .`: PASS_WITH_WARNINGS, 1,765 tracked files in 23 nonempty former bad roots; all nonempty bad roots have active exceptions.
- `python tools/validators/repo/check_bad_root_absence.py --repo-root . --json`: PASS_WITH_WARNINGS.

## AIDE

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing warning-only review-packet review-ref diagnostic.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS.

## Existing Strict Validators

- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS.
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: PASS.

The strict validators still report expected fallback TOML parser warnings under
Python 3.8, but strict results pass.

## Supplemental Checks

- `python scripts/verify_docs_sanity.py --repo-root .`: PASS.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS.
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS.

## Parse And Syntax

- `python -m py_compile tools/migration/route_bad_roots.py tools/validators/repo/check_no_src_source_dirs.py tools/validators/repo/check_forbidden_root_names.py tools/validators/repo/check_bad_root_absence.py`: PASS.
- JSON parse for `contracts/repo/bad_root_routing.schema.json`, `.aide/reports/MOVE-ROUTER-00-dry-run.json`, and `.aide/reports/MOVE-ROUTER-00-route-table.json`: PASS.
- Routing TOML contract parse through `route_bad_roots.load_contract`: PASS, 24 bad roots and 17 canonical roots.

## Not Run

- Full CTest: not in scope.
- Full eval: not in scope.
- CMake configure/build: not required; no build metadata was changed.
- Product binaries, projection generation, package generation, release generation: not in scope.
