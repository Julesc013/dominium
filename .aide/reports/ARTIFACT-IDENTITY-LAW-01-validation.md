# ARTIFACT-IDENTITY-LAW-01 Validation

## Commands Run

Initial sync:

- `git status --short --branch`: clean, `main` aligned with `origin/main`.
- `git remote -v`: origin `https://github.com/Julesc013/dominium.git`.
- `git fetch --all --prune`: pass.
- `git rev-parse HEAD`: `de5b38964a74e56d658bddac791f14b236dd65c0`.
- `git rev-parse origin/main`: `de5b38964a74e56d658bddac791f14b236dd65c0`.
- `git merge-base --is-ancestor origin/main HEAD`: pass.
- `git merge-base --is-ancestor HEAD origin/main`: pass.

New validator and data:

- `python -m py_compile tools/validators/contracts/check_artifact_identity.py`: PASS.
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict`: PASS, 23 artifact kinds, 11 lifecycle states, 0 errors, 0 warnings.
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --json`: PASS, report generation.
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --fixtures`: PASS.
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --inventory`: PASS_WITH_WARNINGS, descriptive inventory only, 17,782 files scanned and 1,890 artifact-like files.
- JSON parse for created/touched artifact, diagnostics, evidence, fixture, and results files: PASS, 14 files.
- JSON parse for fast-strict/results reports: PASS, 2 files.
- JSONL parse for `.aide/ledgers/migration_ledger.jsonl`: PASS, 68 entries.
- TOML fallback parse for artifact contracts: PASS through validator fallback because local `tomllib` is unavailable.

Existing governance validators:

- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`: PASS, 22 diagnostic codes, 7 severities, 26 categories.
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`: PASS, 57 surfaces, 2 stable surfaces.
- `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`: PASS, 5 commands, 0 errors, 0 warnings.
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 5`: FAIL on known existing debt, 16,175 files scanned, 358 violations, 38 warnings.
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

- First `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/ARTIFACT-IDENTITY-LAW-01-fast-strict.json --md-out .aide/reports/ARTIFACT-IDENTITY-LAW-01-fast-strict.md`: FAIL at `t1.repox_strict`, because `docs/architecture/artifact_identity_law.md` was inserted in the older CANONICAL section of `docs/architecture/CANON_INDEX.md`.
- Corrected the CANON_INDEX placement to the derived Foundation Lock architecture section and refreshed `docs/archive/audit/identity_fingerprint.json`.
- Final `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/ARTIFACT-IDENTITY-LAW-01-fast-strict.json --md-out .aide/reports/ARTIFACT-IDENTITY-LAW-01-fast-strict.md`: PASS, 32/32 commands, 321.578 seconds.

Git checks:

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.

## Result

PASS_WITH_WARNINGS. The artifact validator and fast strict normal gate pass.
Dependency-direction strict validation remains a known prior debt signal, not a
hidden artifact-identity pass.

Full CTest was not run; it remains T4 full/release proof.

Note: the first cached diff check found trailing blank lines at EOF in new
artifact files; a mechanical whitespace cleanup was applied and the cached check
then passed.
