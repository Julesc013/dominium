# DIAGNOSTIC-CODE-REGISTRY-01 Validation

## Commands Run

Initial sync:

- `git status --short --branch`: clean, `main` aligned with `origin/main`.
- `git remote -v`: origin `https://github.com/Julesc013/dominium.git`.
- `git fetch --all --prune`: pass.
- `git rev-parse HEAD`: `3fa25f5e20464e5b31fc138bd0bd704b7c6cd677`.
- `git rev-parse origin/main`: `3fa25f5e20464e5b31fc138bd0bd704b7c6cd677`.
- `git merge-base --is-ancestor origin/main HEAD`: pass.
- `git merge-base --is-ancestor HEAD origin/main`: pass.

New validator and data:

- `python -m py_compile tools/validators/contracts/check_diagnostics_registry.py`: PASS.
- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`: PASS, 14 diagnostic codes, 7 severities, 26 categories, 0 errors, 0 warnings.
- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --json`: PASS, report generation.
- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --fixtures`: PASS.
- JSON parse for created/touched diagnostic, evidence, event, refusal, fixture, and results files: PASS, 14 files.
- JSON parse for fast-strict/results reports: PASS, 2 files.
- JSONL parse for `.aide/ledgers/migration_ledger.jsonl`: PASS, 67 entries.
- TOML fallback parse for `contracts/diagnostics/diagnostic_policy.contract.toml`: PASS through validator fallback because local `tomllib` is unavailable.

Existing governance validators:

- `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`: PASS, 5 commands, 0 errors, 0 warnings.
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`: PASS, 47 surfaces, 2 stable surfaces.
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 5`: FAIL on known existing debt, 16,153 files scanned, 358 violations, 38 warnings.
- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`: PASS, 375 headers, 0 errors, 2,851 warnings.
- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS.
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: PASS.
- `python scripts/verify_docs_sanity.py --repo-root .`: PASS, rerun after evidence doc updates.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS.
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS.

RepoX maintenance:

- `python tools/validators/ci/tool_identity_fingerprint.py --repo-root . --output docs/archive/audit/identity_fingerprint.json`: PASS after CANON_INDEX update.

Fast strict:

- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-fast-strict.json --md-out .aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-fast-strict.md`: PASS, 32/32 commands, 351.282 seconds.

Git checks:

- `git diff --check`: PASS.
- `git diff --cached --check`: pending after staging.

## Result

PASS_WITH_WARNINGS. The diagnostic validator and fast strict normal gate pass.
Dependency-direction strict validation remains a known prior debt signal, not a
hidden diagnostic-registry pass.

Full CTest was not run; it remains T4 full/release proof.

Note: one malformed local JSONL parse one-liner failed before validation because
of shell quoting; the corrected JSONL parse command passed.
