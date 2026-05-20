# CAPABILITY-REFUSAL-LAW-01 Validation

Validation is recorded from the local proof loop for CAPABILITY-REFUSAL-LAW-01.

## Capability/Refusal Validator

PASS:

- `python -m py_compile tools/validators/contracts/check_capability_refusal.py`
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict`
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --json`
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --inventory`

Observed counts:

- capabilities registered: 9
- refusal codes registered: 13
- strict errors: 0
- strict warnings: 0
- fixtures: 8
- inventory files scanned: 17,837
- inventory status: warning

## Cross-Contract Validation

PASS:

- `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --strict`
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict`
- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`
- `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`
- `python tools/validators/check_repo_layout.py --repo-root . --strict`
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`
- `python tools/validators/check_component_matrices.py --repo-root . --strict`
- `python scripts/verify_docs_sanity.py --repo-root .`
- `python scripts/verify_build_target_boundaries.py --repo-root .`
- `python scripts/verify_ui_shell_purity.py --repo-root .`
- `python scripts/verify_abi_boundaries.py --repo-root .`
- `python -m json.tool` over 17 changed JSON files
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`

Expected existing debt:

- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 5`
  reports the known DEPENDENCY-DIRECTION-01 debt: 16,230 files scanned, 358
  violations, and 38 warnings.

PASS fast strict:

- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/CAPABILITY-REFUSAL-LAW-01-fast-strict.json --md-out .aide/reports/CAPABILITY-REFUSAL-LAW-01-fast-strict.md`
- status: PASS
- commands: 32/32
- elapsed: 313.656 seconds

Known warnings reported by fast strict:

- AIDE validate reports review-packet reference warnings in its output.
- Language baseline validator reports 7 legacy projection language-mode
  warnings.
- CMake configure/build emit existing third-party/build warnings.
- Full CTest and other T3/T4 gates remain not run by fast strict policy.
