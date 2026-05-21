# SERVICE-CONFORMANCE-LAW-01 Summary

Status: PASS_WITH_WARNINGS

## Summary

Added the service/provider conformance law as contract, schema, registry, fixture, validator, documentation, and evidence surfaces. Services are now modeled as callable semantic runtime capabilities, providers as replaceable implementations, and conformance suites as the proof boundary required before support or replacement claims.

## Changed Files

- `contracts/artifact/artifact_kind.registry.json`
- `contracts/capability/capability.registry.json`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/provider/provider.contract.toml`
- `contracts/provider/provider_conformance.contract.toml`
- `contracts/provider/provider_descriptor.schema.json`
- `contracts/provider/provider.registry.json`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/service/service.contract.toml`
- `contracts/service/service_descriptor.schema.json`
- `contracts/service/service_kind.registry.json`
- `contracts/service/service.registry.json`
- `contracts/conformance/conformance.contract.toml`
- `contracts/conformance/conformance_suite.schema.json`
- `contracts/conformance/conformance_status.registry.json`
- `contracts/conformance/conformance.registry.json`
- `docs/architecture/CANON_INDEX.md`
- `docs/architecture/service_conformance_law.md`
- `docs/architecture/provider_conformance_law.md`
- `docs/development/service_provider_conformance.md`
- `docs/repo/audits/SERVICE_CONFORMANCE_LAW_01.md`
- `tools/validators/contracts/check_service_conformance.py`
- `tests/contract/service/fixtures/valid_service_descriptor.json`
- `tests/contract/service/fixtures/invalid_unknown_capability.json`
- `tests/contract/service/fixtures/invalid_unknown_diagnostic_refusal.json`
- `tests/contract/service/fixtures/invalid_stable_without_conformance.json`
- `tests/contract/conformance/fixtures/valid_conformance_suite.json`
- `tests/contract/conformance/fixtures/valid_planned_no_support_claim.json`
- `tests/contract/conformance/fixtures/valid_provider_with_conformance.json`
- `tests/contract/conformance/fixtures/invalid_unknown_subject.json`
- `tests/contract/conformance/fixtures/invalid_fixture_only_support_claim.json`
- `tests/contract/conformance/fixtures/invalid_provider_service_without_conformance.json`
- `.aide/reports/SERVICE-CONFORMANCE-LAW-01-fast-strict.json`
- `.aide/reports/SERVICE-CONFORMANCE-LAW-01-fast-strict.md`
- `.aide/reports/SERVICE-CONFORMANCE-LAW-01-repox-profile.json`
- `.aide/reports/SERVICE-CONFORMANCE-LAW-01-repox-proof-manifest.json`
- `.aide/reports/SERVICE-CONFORMANCE-LAW-01-summary.md`
- `.aide/reports/SERVICE-CONFORMANCE-LAW-01-validation.json`

## Service Kinds Added

- `command`
- `validation`
- `diagnostics`
- `evidence`
- `package`
- `profile`
- `composition`
- `document`
- `patch`
- `project_graph`
- `render`
- `platform`
- `storage`
- `network`
- `audio`
- `input`
- `module`
- `workbench`
- `replay`

## Conformance Schemas Added

- `contracts/service/service_descriptor.schema.json`
- `contracts/conformance/conformance_suite.schema.json`

## Fixtures Added

- `tests/contract/service/fixtures/valid_service_descriptor.json`
- `tests/contract/service/fixtures/invalid_unknown_capability.json`
- `tests/contract/service/fixtures/invalid_unknown_diagnostic_refusal.json`
- `tests/contract/service/fixtures/invalid_stable_without_conformance.json`
- `tests/contract/conformance/fixtures/valid_conformance_suite.json`
- `tests/contract/conformance/fixtures/valid_planned_no_support_claim.json`
- `tests/contract/conformance/fixtures/valid_provider_with_conformance.json`
- `tests/contract/conformance/fixtures/invalid_unknown_subject.json`
- `tests/contract/conformance/fixtures/invalid_fixture_only_support_claim.json`
- `tests/contract/conformance/fixtures/invalid_provider_service_without_conformance.json`

## Validation

- `python -m py_compile tools/validators/contracts/check_service_conformance.py` -> PASS
- `python tools/validators/contracts/check_service_conformance.py --repo-root . --strict` -> PASS_WITH_WARNINGS
- `python tools/validators/contracts/check_service_conformance.py --repo-root . --json` -> PASS_WITH_WARNINGS
- `python tools/validators/contracts/check_service_conformance.py --repo-root . --fixtures` -> PASS_WITH_WARNINGS
- `python tools/validators/contracts/check_service_conformance.py --repo-root . --inventory` -> PASS_WITH_WARNINGS
- `python tools/validators/contracts/check_provider_model.py --repo-root . --strict` -> PASS
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict` -> PASS
- `python tools/validators/contracts/check_command_surface.py --repo-root . --strict` -> PASS
- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict` -> PASS
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict` -> PASS
- `python tools/validators/repo/check_replacement_packet.py --repo-root . --strict` -> PASS
- `python tools/validators/contracts/check_version_deprecation.py --repo-root . --strict` -> PASS
- `python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict` -> PASS
- `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict` -> PASS
- `python tools/validators/contracts/check_app_descriptors.py --repo-root . --strict` -> PASS
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict` -> PASS
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict` -> PASS_WITH_WARNINGS
- `python tools/validators/check_component_matrices.py --repo-root . --strict` -> PASS_WITH_WARNING
- `python tools/validators/platform/check_portability_matrix.py --repo-root . --strict` -> PASS
- `python scripts/verify_docs_sanity.py --repo-root .` -> PASS
- `python scripts/verify_build_target_boundaries.py --repo-root .` -> PASS
- `python scripts/verify_ui_shell_purity.py --repo-root .` -> PASS
- `python scripts/verify_abi_boundaries.py --repo-root .` -> PASS
- `py -3 .aide/scripts/aide_lite.py doctor` -> PASS
- `py -3 .aide/scripts/aide_lite.py validate` -> PASS_WITH_WARNINGS
- `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT --proof-manifest-out .aide/reports/SERVICE-CONFORMANCE-LAW-01-repox-proof-manifest.json --profile-out .aide/reports/SERVICE-CONFORMANCE-LAW-01-repox-profile.json` -> PASS_WITH_WARNING
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/SERVICE-CONFORMANCE-LAW-01-fast-strict.json --md-out .aide/reports/SERVICE-CONFORMANCE-LAW-01-fast-strict.md` -> PASS
- `git diff --check` -> PASS

## Warnings

- Service/provider runtime dispatch, provider resolver, renderer/platform/storage/network/audio/input/package/profile services, Workbench module runtime, and gameplay behavior remain unimplemented by design.
- Conformance suites are planned or fixture_only except where future runtime proof promotes them; planned and fixture_only do not imply support.
- Service conformance validator strict/json/fixtures/inventory report expected warnings for non-support planned and fixture-only suites.
- Dependency-direction strict passed with 0 violations and known warning debt.
- RepoX strict reports known stale AuditX output warning.
- AIDE Lite validate reports existing review-packet warnings for missing latest verification report and review decision policy refs.
- Component matrix strict uses the fallback TOML parser under the current Python.

## Non-Goals

- No service runtime implementation.
- No provider resolver or runtime loading.
- No renderer, platform, storage, network, audio, input, package, or profile backend implementation.
- No Workbench UI or module runtime implementation.
- No gameplay/domain implementation changes.
- No CMake target changes.

## Next Recommended Task

DOCUMENT-PATCH-TRANSACTION-RUNTIME-01
