# COMMAND-SURFACE-01 Validation

## Commands Run

Initial sync:

- `git status --short --branch`: clean, `main` aligned with `origin/main`.
- `git remote -v`: origin `https://github.com/Julesc013/dominium.git`.
- `git fetch --all --prune`: pass.
- `git rev-parse HEAD`: `4095831fcbca00ae22f455b973ee75091401980e`.
- `git rev-parse origin/main`: `4095831fcbca00ae22f455b973ee75091401980e`.
- `git merge-base --is-ancestor origin/main HEAD`: pass.
- `git merge-base --is-ancestor HEAD origin/main`: pass.

New validator and data:

- `python -m py_compile tools/validators/contracts/check_command_surface.py`: PASS.
- `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`: PASS, 5 commands, 0 errors, 0 warnings.
- `python tools/validators/contracts/check_command_surface.py --repo-root . --json`: PASS, report generation.
- `python tools/validators/contracts/check_command_surface.py --repo-root . --fixtures`: PASS.
- JSON parse for created command/result/view/event/refusal/document/evidence schemas and fixtures: PASS, 13 files.
- TOML fallback parse for command/view/event contracts and TOML fixtures: PASS, 6 files.

Existing governance validators:

- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`: PASS, 39 surfaces, 2 stable surfaces.
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 5`: FAIL on known existing debt, 16,153 files scanned, 358 violations, 38 warnings.
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

- First fast strict run failed at `t1.repox_strict` because `docs/archive/audit/identity_fingerprint.json` was stale after adding `docs/architecture/command_view_event_refusal.md` to `docs/architecture/CANON_INDEX.md`.
- `python tools/validators/ci/tool_identity_fingerprint.py --repo-root . --output docs/archive/audit/identity_fingerprint.json`: PASS.

Fast strict:

- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/COMMAND-SURFACE-01-fast-strict.json --md-out .aide/reports/COMMAND-SURFACE-01-fast-strict.md`: PASS, 32/32 commands, 309.969 seconds.

Git checks:

- `git diff --check`: PASS before final staging.

## Result

PASS_WITH_WARNINGS. The command-surface validator and fast strict normal gate
pass. Dependency-direction strict validation remains a known prior debt signal,
not a hidden command-surface pass.

Full CTest was not run; it remains T4 full/release proof.
