# PROVIDER-MODEL-01 Validation

Validation is recorded from the local proof loop for PROVIDER-MODEL-01.

## Provider Validator

PASS:

- `python -m py_compile tools/validators/contracts/check_provider_model.py`
- `python tools/validators/contracts/check_provider_model.py --repo-root . --strict`
- `python tools/validators/contracts/check_provider_model.py --repo-root . --json`
- `python tools/validators/contracts/check_provider_model.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_provider_model.py --repo-root . --json --inventory`
- `python tools/validators/contracts/check_provider_model.py --repo-root . --list`

Observed counts:

- provider descriptors registered: 5
- provider kinds registered: 15
- provider lifecycle states registered: 9
- strict errors: 0
- strict warnings: 0
- fixtures: 9
- inventory files scanned: 17,865
- inventory candidates classified: 1,396
- inventory status: warning

## Cross-Contract Validation

PASS:

- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict`
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
- `python tools/validators/ci/tool_identity_fingerprint.py --repo-root . --output docs/archive/audit/identity_fingerprint.json`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`

Expected existing debt:

- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 5`
  reports the known DEPENDENCY-DIRECTION-01 debt: 16,258 files scanned, 358
  violations, and 38 warnings.

PASS fast strict:

- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/PROVIDER-MODEL-01-fast-strict.json --md-out .aide/reports/PROVIDER-MODEL-01-fast-strict.md`
- status: PASS
- commands: 32/32
- elapsed: 315.484 seconds

Known warnings expected from the full proof loop:

- Dependency-direction validator exposes existing active dependency debt.
- ABI public-header validator passes with 2,851 provisional stable-promotion warnings.
- Full CTest and other T3/T4 gates are not run by fast strict policy.
