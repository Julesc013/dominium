Status: PASS_WITH_WARNINGS
Last Reviewed: 2026-05-20
Task: PUBLIC-SURFACE-REGISTRY-01

# Public Surface Registry Validation

## Sync

- `git fetch --all --prune`: PASS
- `git rev-parse HEAD`: `3eb4b7c4f7e230e0384547d94673148003fc2d93`
- `git rev-parse origin/main`: `625f17344f4fc400d810784bd9d49ceacf91ad99`
- `git merge-base --is-ancestor origin/main HEAD`: PASS
- `git merge-base --is-ancestor HEAD origin/main`: FAIL as expected; local main is ahead by FAST-STRICT commits

## Public Surface Validator

- `python -m py_compile tools/validators/repo/check_public_surface.py`: PASS
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`: PASS
- `python tools/validators/repo/check_public_surface.py --repo-root . --json`: PASS
- `python tools/validators/repo/check_public_surface.py --repo-root . --fixture-dir tests/contract/public_surface/fixtures`: PASS
- `python tools/validators/repo/check_public_surface.py --repo-root . --list`: PASS

Validator summary:

- surfaces: 20
- stable surfaces: 2
- kinds: 25
- stability classes: 12
- errors: 0
- warnings: 0

## Parse And Existing Validators

- `python -m json.tool contracts/public_surface/surface.schema.json`: PASS
- `python -m json.tool contracts/public_surface/surface_kind.registry.json`: PASS
- `python -m json.tool contracts/public_surface/surface_stability.registry.json`: PASS
- `python -m json.tool .aide/reports/PUBLIC-SURFACE-REGISTRY-01-results.json`: PASS
- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: PASS
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: PASS
- `python scripts/verify_docs_sanity.py --repo-root .`: PASS
- `python scripts/verify_includes_sanity.py --repo-root .`: PASS
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS

## Fast Strict

Initial fast strict attempts exposed task-caused proof issues that were fixed:

- `t0.changed_toml_parse` needed the Python 3.8 fallback TOML reader to support generic `[[surface]]` array tables.
- AIDE packets needed exact AIDE section headings.
- RepoX required the new architecture doc to have a four-line status header and a DERIVED entry in `docs/architecture/CANON_INDEX.md`.
- RepoX identity fingerprint was refreshed with `tools/validators/ci/tool_identity_fingerprint.py` after the canon index update.

Final command:

```text
python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/PUBLIC-SURFACE-REGISTRY-01-fast-strict.json --md-out .aide/reports/PUBLIC-SURFACE-REGISTRY-01-fast-strict.md
```

Final result:

- status: PASS
- elapsed seconds: 299.828
- commands total: 30
- commands passed: 30
- commands failed: 0

Standalone RepoX command:

```text
python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT --proof-manifest-out .aide/reports/PUBLIC-SURFACE-REGISTRY-01-repox-proof-manifest.json --profile-out .aide/reports/PUBLIC-SURFACE-REGISTRY-01-repox-profile.json
```

Result: PASS.

Final standalone RepoX rerun after status-document updates: PASS.

## Git Hygiene

- `git diff --check`: PASS.

## Not Run

- Full CTest was not run; it remains T4 full/release proof.
