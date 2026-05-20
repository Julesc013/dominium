# API-ABI-CANON-01 Validation

Task: `API-ABI-CANON-01`
Result: PASS_WITH_WARNINGS

## ABI Contract Validation

- `python -m py_compile tools/validators/abi/check_public_headers.py`: PASS
- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`: PASS, 375 headers, 0 errors, 2,851 warnings
- `python tools/validators/abi/check_public_headers.py --repo-root . --json`: PASS
- `python tools/validators/abi/check_public_headers.py --repo-root . --fixtures`: PASS, 3 fixture headers, 0 errors
- `python -m json.tool contracts/abi/abi_rule.registry.json`: PASS
- `python -m json.tool contracts/abi/public_header.schema.json`: PASS
- TOML fallback parse for `contracts/abi/c_api.contract.toml`, `contracts/abi/language_boundary.contract.toml`, and `contracts/public_surface/public_surface.contract.toml`: PASS

Python `tomllib` is unavailable on this host, so TOML validation used the
stdlib fallback parser from `tools/validators/abi/check_public_headers.py`.

## Registry And Surface Validation

- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`: PASS, 25 surfaces, 2 stable surfaces
- `python tools/validators/repo/check_public_surface.py --repo-root . --json`: PASS
- `python -m json.tool contracts/public_surface/surface.schema.json`: PASS
- `python -m json.tool contracts/public_surface/surface_kind.registry.json`: PASS
- `python -m json.tool contracts/public_surface/surface_stability.registry.json`: PASS

## AIDE And Repo Validators

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing review-packet warning posture
- `py -3 .aide/scripts/aide_lite.py pack --task "API-ABI-CANON-01"`: PASS
- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: PASS
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: PASS

## Supplemental Validators

- `python scripts/verify_docs_sanity.py --repo-root .`: PASS
- `python scripts/verify_includes_sanity.py --repo-root .`: PASS
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS
- `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT --proof-manifest-out .aide/reports/API-ABI-CANON-01-repox-proof-manifest.json --profile-out .aide/reports/API-ABI-CANON-01-repox-profile.json`: PASS

RepoX initially reported stale `docs/archive/audit/identity_fingerprint.json`
after `docs/architecture/CANON_INDEX.md` gained `docs/architecture/api_abi_canon.md`.
The fingerprint was regenerated with
`python tools/validators/ci/tool_identity_fingerprint.py --repo-root . --output docs/archive/audit/identity_fingerprint.json`,
then RepoX STRICT passed.

## Fast Strict

Command:

```powershell
python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/API-ABI-CANON-01-fast-strict.json --md-out .aide/reports/API-ABI-CANON-01-fast-strict.md
```

Result: PASS.

- elapsed: 337.406 seconds
- commands: 30
- passed: 30
- failed: 0
- smoke CTest: PASS inside fast strict
- CMake configure/build: PASS inside fast strict

First fast-strict attempt failed on `git diff --check` due extra blank lines at
EOF in four markdown files. Those whitespace findings were fixed and
`git diff --check` passed before rerun.

## Git Checks

- `git diff --check`: PASS
- `git status --short --branch`: dirty with intended task files before commit
- `git diff --cached --check`: PASS

## Not Run

- Full CTest was not run. It remains T4 full/release proof and known broad debt,
not a normal fast-strict gate.
