# DEPENDENCY-DIRECTION-01 Validation

## Commands Run

Initial sync:

- `git status --short --branch`: clean, `main` ahead of `origin/main` by one local README commit at task start.
- `git remote -v`: origin `https://github.com/Julesc013/dominium.git`.
- `git fetch --all --prune`: pass.
- `git rev-parse HEAD`: `5ee3d5b92e56ed16dd3c205fb453245851a054cb`.
- `git rev-parse origin/main`: `ed7427c96b9857ab5b93b0fab127a16d436d83ae`.
- `git merge-base --is-ancestor origin/main HEAD`: pass.
- `git merge-base --is-ancestor HEAD origin/main`: fail, expected local-ahead state.

New validator and data:

- `python -m py_compile tools/validators/repo/check_dependency_directions.py`: pass.
- JSON parse for dependency-direction schema and fixtures: pass, 5 files.
- TOML parse for dependency-direction contract and exceptions: pass.
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --list-rules`: pass.
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 25`: fail, expected current debt.
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --json`: pass as report generation; status field is `fail`.

Existing governance validators:

- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`: pass, 30 surfaces.
- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`: pass, 375 headers, 0 errors, 2,851 warnings.
- `python tools/validators/check_repo_layout.py --repo-root . --strict`: pass.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: pass.
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: pass.
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: pass.
- `python scripts/verify_docs_sanity.py --repo-root .`: pass.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: pass.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: pass.
- `python scripts/verify_abi_boundaries.py --repo-root .`: pass.

Fast strict:

- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/DEPENDENCY-DIRECTION-01-fast-strict.json --md-out .aide/reports/DEPENDENCY-DIRECTION-01-fast-strict.md`: pass, 32/32 commands, 334.907 seconds.

RepoX maintenance:

- Added `docs/architecture/dependency_direction_law.md` to `docs/architecture/CANON_INDEX.md`.
- Regenerated `docs/archive/audit/identity_fingerprint.json`.
- Focused RepoX strict rerun passed.

Git checks:

- `git diff --check`: pass before staging.
- `git diff --cached --check`: pending after staging.

Focused final reruns:

- `py -3 .aide/scripts/aide_lite.py validate`: pass, with existing review-reference warnings.
- `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT ...`: pass after CANON_INDEX and identity fingerprint maintenance.
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`: pass, 30 surfaces.

## Result

PARTIAL. The task deliverables exist and fast strict passes, but the new
dependency-direction validator correctly fails strict mode on current existing
dependency-direction debt: 358 violations and 38 warnings.

Full CTest was not run; it remains T4 full/release proof.
