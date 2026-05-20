# PORTABILITY-MATRIX-01 Validation

Status: PASS_WITH_WARNINGS

## Direct Portability Proof

- PASS: `python -m py_compile tools/validators/platform/check_portability_matrix.py`
- PASS: `python tools/validators/platform/check_portability_matrix.py --repo-root . --strict`
- PASS: `python tools/validators/platform/check_portability_matrix.py --repo-root . --json`
- PASS: `python tools/validators/platform/check_portability_matrix.py --repo-root . --fixtures`
- PASS: `python tools/validators/platform/check_portability_matrix.py --repo-root . --inventory`
- PASS: JSON parse for 21 touched platform/fixture/registry files.
- PASS: TOML parse for 3 touched TOML files using `py -3`.

## Cross-Law Validators

- PASS: `python tools/validators/package/check_mod_pack_trust.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_version_deprecation.py --repo-root . --strict`
- PASS: `python tools/validators/repo/check_replacement_packet.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_app_descriptors.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_provider_model.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`
- PASS: `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`
- PASS: `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- WARN: `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict` reports known existing debt: 358 violations and 38 warnings.
- PASS_WITH_WARNINGS: `python tools/validators/abi/check_public_headers.py --repo-root . --strict` passes with 2851 ABI stable-promotion warnings.

## Repo And Supplemental Validators

- PASS: `python tools/validators/check_repo_layout.py --repo-root . --strict`
- PASS: `python tools/validators/check_root_allowlist.py --repo-root . --strict`
- PASS: `python tools/validators/check_distribution_layout.py --repo-root . --strict`
- PASS: `python tools/validators/check_component_matrices.py --repo-root . --strict`
- PASS: `python scripts/verify_docs_sanity.py --repo-root .`
- PASS: `python scripts/verify_build_target_boundaries.py --repo-root .`
- PASS: `python scripts/verify_ui_shell_purity.py --repo-root .`
- PASS: `python scripts/verify_abi_boundaries.py --repo-root .`
- PASS: `python tools/validators/ci/tool_identity_fingerprint.py --repo-root . --output docs/archive/audit/identity_fingerprint.json`
- PASS: `py -3 .aide/scripts/aide_lite.py validate` after latest task/review packet update.

## Fast Strict

- PASS: `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/PORTABILITY-MATRIX-01-fast-strict.json --md-out .aide/reports/PORTABILITY-MATRIX-01-fast-strict.md`
- Fast strict result: PASS.
- Commands: 32.
- Elapsed seconds: 312.297.

## Git Checks

- PASS: `git status --short --branch` inspected.
- PASS: `git diff --check` passed during fast strict and final pre-stage rerun.
- NOT RUN: `git diff --cached --check` before final staging; run during commit preparation.

## Notes

The first fast strict attempt failed Repox canon-index validation because new canonical docs were not listed in `docs/architecture/CANON_INDEX.md`. The index was updated, the identity fingerprint was refreshed, and fast strict passed on rerun.
