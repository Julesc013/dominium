# MODULE-COMPOSITION-LAW-01 Validation

Validation is recorded from the local proof loop for MODULE-COMPOSITION-LAW-01.

## Module, Workbench, And App Validators

PASS:

- `python -m py_compile tools/validators/contracts/check_module_descriptors.py tools/validators/contracts/check_workbench_workspaces.py tools/validators/contracts/check_app_descriptors.py`
- `python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict`
- `python tools/validators/contracts/check_module_descriptors.py --repo-root . --json`
- `python tools/validators/contracts/check_module_descriptors.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_module_descriptors.py --repo-root . --json --inventory`
- `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict`
- `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --json`
- `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --json --inventory`
- `python tools/validators/contracts/check_app_descriptors.py --repo-root . --strict`
- `python tools/validators/contracts/check_app_descriptors.py --repo-root . --json`
- `python tools/validators/contracts/check_app_descriptors.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_app_descriptors.py --repo-root . --json --inventory`

Observed counts:

- module kinds registered: 12
- module fixtures: 6
- Workbench fixtures: 5
- app fixtures: 4
- module inventory candidates: 1,208
- Workbench inventory candidates: 194
- app inventory candidates: 882

## Cross-Contract Validation

PASS:

- `python tools/validators/contracts/check_provider_model.py --repo-root . --strict`
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict`
- `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --strict`
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict`
- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`
- `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`
- `python tools/validators/ci/tool_identity_fingerprint.py --repo-root . --output docs/archive/audit/identity_fingerprint.json`

Expected existing debt:

- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 5`
  reports existing dependency-direction debt: 16,289 files scanned, 358
  violations, and 38 warnings.

PASS fast strict:

- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/MODULE-COMPOSITION-LAW-01-fast-strict.json --md-out .aide/reports/MODULE-COMPOSITION-LAW-01-fast-strict.md`
- status: PASS
- commands: 32/32
- elapsed: 315.25 seconds

Known warnings expected from the full proof loop:

- Dependency-direction validator exposes existing active dependency debt.
- ABI public-header validator passes with provisional stable-promotion warnings.
- Full CTest and other T3/T4 gates are not run by fast strict policy.
