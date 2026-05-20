# SCHEMA-PROTOCOL-LAW-01 Validation

## Commands Run

Initial sync:

- `git status --short --branch`: clean, `main` aligned with `origin/main`.
- `git remote -v`: origin `https://github.com/Julesc013/dominium.git`.
- `git fetch --all --prune`: PASS.
- `git rev-parse HEAD`: `2635c7d2475b4b015cf2fb3f01b75866f6976343`.
- `git rev-parse origin/main`: `2635c7d2475b4b015cf2fb3f01b75866f6976343`.
- `git merge-base --is-ancestor origin/main HEAD`: PASS.
- `git merge-base --is-ancestor HEAD origin/main`: PASS.

New validator and data:

- `python -m py_compile tools/validators/contracts/check_schema_protocol_evolution.py`: PASS.
- `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --strict`: PASS, 0 errors, 0 warnings.
- `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --json`: PASS.
- `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --fixtures`: PASS, 7 fixtures.
- `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --inventory`: PASS_WITH_WARNINGS, descriptive inventory only, 17,808 files scanned and 2,489 schema/protocol-like files.

Existing governance validators:

- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`: PASS, 33 diagnostic codes, 7 severities, 26 categories.
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`: PASS, 67 surfaces, 2 stable surfaces.
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict`: PASS, 23 artifact kinds, 11 lifecycle states.
- `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`: PASS, 5 commands.
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 5`: FAIL on known existing debt, 16,201 files scanned, 358 violations, 38 warnings.
- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`: PASS, 375 headers, 0 errors, 2,851 warnings.
- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS.
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: PASS.
- `python scripts/verify_docs_sanity.py --repo-root .`: PASS.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS.
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS.

RepoX maintenance:

- `python tools/validators/ci/tool_identity_fingerprint.py --repo-root . --output docs/archive/audit/identity_fingerprint.json`: PASS after CANON_INDEX update.

Fast strict:

- First `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/SCHEMA-PROTOCOL-LAW-01-fast-strict.json --md-out .aide/reports/SCHEMA-PROTOCOL-LAW-01-fast-strict.md`: FAIL at `t0.git_diff_check` due extra blank EOF lines in AIDE packet/status files. Corrected and reran.
- Second run: FAIL at `t1.aide_doctor` because AIDE validate needed rerun after manual task-packet edits. Restored required task packet sections, ran AIDE validate/doctor, and reran.
- Third run: FAIL at `t1.repox_strict` due missing status headers in new markdown docs. Added standard status headers and reran.
- Fourth run: FAIL at `t1.repox_strict` because the new docs used invalid status values for their repo section. Corrected to `Status: DERIVED`, restored generated side effects, and reran.
- Final `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/SCHEMA-PROTOCOL-LAW-01-fast-strict.json --md-out .aide/reports/SCHEMA-PROTOCOL-LAW-01-fast-strict.md`: PASS, 32/32 commands, 331.344 seconds.

Git checks:

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.

Generated side effects:

- Fast strict updated RepoX/migration generated reports during failed and final runs; generated side-effect files were restored from `HEAD` before staging.

## Result

PASS_WITH_WARNINGS. The schema/protocol validator and fast strict normal gate pass.
Dependency-direction strict validation remains a known prior debt signal, not a
hidden schema/protocol pass.

Full CTest was not run; it remains T4 full/release proof.
