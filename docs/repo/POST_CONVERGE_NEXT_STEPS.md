Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Post-CONVERGE Next Steps

Status: PROVISIONAL

Phase: POST-CONVERGE

## PORTABILITY-ARCH-POLICY-02 Update

PORTABILITY-ARCH-POLICY-02 is PASS_WITH_WARNINGS.

- native architecture policy is explicit in `contracts/platform/architecture_policy.contract.toml`.
- architecture tiers are registered: `source_native_64`, `constrained_native_32`, `contract_projection`, and `archive_runner`.
- mainline full-native architectures are `x86_64` and `arm64`; `x64` remains a compatibility alias for existing rows.
- 32-bit targets remain constrained/research/projection/archive lanes, not mainline product obligations.
- pointer-width and endian policy are declared and validated.
- architecture policy validator strict/json/fixtures/inventory passes.
- portability matrix, public surface, diagnostics, capability/refusal, provider, artifact, schema/protocol, language, ABI, dependency-direction, AIDE, RepoX, docs, build, UI, and ABI checks pass.
- fast strict passes `33` commands in `296.553` seconds, including CMake configure/build and smoke CTest.
- full CTest remains T4/full-gate debt and was not run.

Next task: `WORKBENCH-VALIDATION-SLICE-01`.

Secondary follow-up if desired: `POINTER-WIDTH-SERIALIZATION-AUDIT-01`.

## FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01 Update

FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01 is PASS.

- dependency-direction strict now passes with `0` violations and `68` warnings.
- the prior closeout blocker was `358` violations and `38` warnings.
- `12` exact provisional dependency-direction exceptions remain, applying to `28` transitional app/runtime tool-adapter import edges.
- newly tracked helper violations found during repair were fixed before final proof.
- fast strict passes `32` commands in `312.147` seconds, including RepoX STRICT, CMake configure/build, and smoke CTest.
- Foundation Lock is ready for `FOUNDATION-CLOSEOUT-02`.
- `WORKBENCH-VALIDATION-SLICE-01` remains pending until closeout passes.

Next task: `FOUNDATION-CLOSEOUT-02`.

## FOUNDATION-CLOSEOUT-02 Update

FOUNDATION-CLOSEOUT-02 is PASS_WITH_WARNINGS.

- dependency-direction strict passes with `0` violations and `68` warnings.
- all Foundation layer validators pass.
- AIDE doctor/validate/test/selftest/tools/roots/repo pass.
- RepoX STRICT passes with the known stale AuditX warning.
- fast strict passes `32` commands in `272.607` seconds, including CMake configure/build and smoke CTest.
- Foundation Lock is closed with warnings.
- `WORKBENCH-VALIDATION-SLICE-01` is authorized as a narrow governed product slice.
- broad feature work remains blocked.
- full CTest remains T4/full-gate debt and was not run.

Recommended next order:

1. `PORTABILITY-ARCH-POLICY-02`
2. `WORKBENCH-VALIDATION-SLICE-01`

## FOUNDATION-CLOSEOUT-01 Update

FOUNDATION-CLOSEOUT-01 is BLOCKED.

- all required Foundation Lock files for tasks 01 through 15 are present.
- most Foundation validators pass in strict and fixture scope.
- blocker: `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict`
  reports 358 violations and 38 warnings.
- narrow product work is not authorized.
- broad feature work remains blocked.
- next repair task: `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01`.

`WORKBENCH-VALIDATION-SLICE-01` remains pending until the dependency-direction
blocker is repaired and Foundation Lock is rerun.

## MOD-PACK-TRUST-MODEL-01 Update

MOD-PACK-TRUST-MODEL-01 adds the provisional mod/pack trust law.

- trust law: `contracts/trust/mod_pack_trust.contract.toml`
- trust registry: `contracts/trust/trust_level.registry.json`
- permission registry: `contracts/trust/permission_kind.registry.json`
- trust decision schema: `contracts/trust/trust_decision.schema.json`
- mod descriptor schema: `contracts/modding/mod_descriptor.schema.json`
- policies:
  - `contracts/trust/review_policy.contract.toml`
  - `contracts/trust/sandbox_policy.contract.toml`
  - `contracts/trust/determinism_impact_policy.contract.toml`
  - `contracts/trust/native_provider_policy.contract.toml`
  - `contracts/trust/external_adapter_policy.contract.toml`
  - `contracts/modding/mod_capability_policy.contract.toml`
  - `contracts/modding/pack_overlay_policy.contract.toml`
- validator:
  - `python tools/validators/package/check_mod_pack_trust.py --repo-root . --strict`
- fixture suite: `tests/contract/mod_pack_trust/**`
- trust levels registered: 7
- permission kinds registered: 22
- next Foundation Lock task: `PORTABILITY-MATRIX-01`

Feature implementation remains blocked until Foundation Lock closes. Runtime
mod loading, sandboxing, native provider loading, dynamic libraries, package
mounting, Workbench UI, gameplay, renderer, native GUI, and product behavior
are not implemented.

## VERSION-DEPRECATION-LAW-01 Update

VERSION-DEPRECATION-LAW-01 adds the provisional versioning, lifecycle,
deprecation, retirement, removal, compatibility, and transition law.

- versioning law: `contracts/versioning/versioning.contract.toml`
- lifecycle registry: `contracts/versioning/lifecycle_state.registry.json`
- compatibility schemas:
  - `contracts/versioning/version_compatibility.schema.json`
  - `contracts/versioning/compatibility_range.schema.json`
- deprecation/transition schemas:
  - `contracts/versioning/deprecation_notice.schema.json`
  - `contracts/versioning/version_transition.schema.json`
- policies:
  - `contracts/versioning/deprecation_policy.contract.toml`
  - `contracts/versioning/retirement_policy.contract.toml`
  - `contracts/versioning/removal_policy.contract.toml`
  - `contracts/versioning/surface_lifecycle.contract.toml`
- validator:
  - `python tools/validators/contracts/check_version_deprecation.py --repo-root . --strict`
- fixture suite: `tests/contract/versioning/**`
- lifecycle states registered: 9
- next Foundation Lock task: `MOD-PACK-TRUST-MODEL-01`

Feature implementation remains blocked until Foundation Lock closes. No active
surface is deprecated, retired, removed, or migrated by this task. Runtime
migration, release promotion, Workbench UI, gameplay, renderer, native GUI, and
product behavior are not implemented.

## REPLACEMENT-PROTOCOL-01 Update

REPLACEMENT-PROTOCOL-01 adds the provisional safe replacement protocol.

- replacement law: `contracts/replacement/replacement.contract.toml`
- replacement packet schema: `contracts/replacement/replacement_packet.schema.json`
- impact/proof schemas: `contracts/replacement/replacement_impact.schema.json`,
  `contracts/replacement/replacement_proof.schema.json`
- policies:
  - `contracts/replacement/rollback_policy.contract.toml`
  - `contracts/replacement/conformance_policy.contract.toml`
  - `contracts/replacement/migration_refusal_policy.contract.toml`
- validator:
  - `python tools/validators/repo/check_replacement_packet.py --repo-root . --strict`
- fixture suite: `tests/contract/replacement/**`
- replacement kinds registered: 19
- replacement statuses registered: 10
- public surfaces after registration: 121
- inventory: 17,942 tracked files scanned; 1,824 replacement-like historical or
  future-candidate files classified descriptively
- next Foundation Lock task: `VERSION-DEPRECATION-LAW-01`

Feature implementation remains blocked until Foundation Lock closes. Actual
replacement, migration runtime, rollback runtime, provider runtime, Workbench UI,
and product behavior are not implemented by this task.

## MODULE-COMPOSITION-LAW-01 Update

MODULE-COMPOSITION-LAW-01 adds the provisional module, Workbench workspace, and app composition law.

- module law: `contracts/module/module_surface.contract.toml`
- module schema: `contracts/module/module.schema.json`
- Workbench workspace schema: `contracts/workbench/workspace.schema.json`
- app descriptor schema: `contracts/app/app_descriptor.schema.json`
- validators:
  - `python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict`
  - `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict`
  - `python tools/validators/contracts/check_app_descriptors.py --repo-root . --strict`
- fixture suites: `tests/contract/module/**`, `tests/contract/workbench/**`, `tests/contract/app/**`
- module kinds registered: 12
- public surfaces after registration: 110
- inventory: 17,896 tracked files scanned per validator; module, Workbench, and app candidates classified descriptively
- next Foundation Lock task: `REPLACEMENT-PROTOCOL-01`

Feature implementation remains blocked until Foundation Lock closes. Runtime
module loading, Workbench UI, App Composer, pack runtime, provider runtime, and
module discovery runtime are not implemented by this task.

## PROVIDER-MODEL-01 Update

PROVIDER-MODEL-01 adds the provisional provider model law.

- contract: `contracts/provider/provider.contract.toml`
- registry: `contracts/provider/provider.registry.json`
- descriptor schema: `contracts/provider/provider_descriptor.schema.json`
- validator: `python tools/validators/contracts/check_provider_model.py --repo-root . --strict`
- fixture suite: `tests/contract/provider/**`
- providers registered: 5
- provider kinds registered: 15
- lifecycle states registered: 9
- inventory: 17,865 tracked files scanned; 1,396 provider/backend/service/adapter/capability candidates classified descriptively
- next Foundation Lock task: `MODULE-COMPOSITION-LAW-01`

Feature implementation remains blocked until Foundation Lock closes. Runtime
provider resolution, dynamic loading, renderer/platform fallback, package/profile
runtime behavior, and Workbench UI are not implemented by this task.

## CAPABILITY-REFUSAL-LAW-01 Update

CAPABILITY-REFUSAL-LAW-01 adds the provisional capability/refusal law.

- contract: `contracts/capability/capability.contract.toml`
- registry: `contracts/capability/capability.registry.json`
- refusal contract: `contracts/refusal/refusal.contract.toml`
- validator: `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict`
- fixture suite: `tests/contract/capability_refusal/**`
- capabilities registered: 9
- refusal codes registered: 13
- inventory: 17,837 tracked files scanned; 1,190 capability/refusal/provider/trust candidates classified descriptively
- next Foundation Lock task: `PROVIDER-MODEL-01`

Feature implementation remains blocked until Foundation Lock closes. Runtime
capability resolution, provider selection, renderer/platform fallback, package
runtime, and Workbench UI are not implemented by this task.

## SCHEMA-PROTOCOL-LAW-01 Update

SCHEMA-PROTOCOL-LAW-01 adds the provisional schema/protocol evolution law.

- schema law: `contracts/schema/schema_evolution.contract.toml`
- protocol law: `contracts/protocol/protocol_evolution.contract.toml`
- registry law: `contracts/registry/registry_evolution.contract.toml`
- canonical serialization: `contracts/serialization/canonical_serialization.contract.toml`
- migration/refusal policy: `contracts/migration/migration_policy.contract.toml`
- validator: `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --strict`
- fixture suite: `tests/contract/schema_protocol/**`
- initial inventory: 17,808 tracked files scanned; 2,489 schema/protocol-like files classified descriptively
- next Foundation Lock task: `CAPABILITY-REFUSAL-LAW-01`

Feature implementation remains blocked until Foundation Lock closes. Existing
schemas, protocols, registries, and manifests are inventoried but not migrated
by this task.

## ARTIFACT-IDENTITY-LAW-01 Update

ARTIFACT-IDENTITY-LAW-01 adds the provisional artifact identity law.

- contract: `contracts/artifact/artifact_identity.contract.toml`
- manifest schema: `contracts/artifact/artifact_manifest.schema.json`
- validator: `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict`
- artifact kinds registered: 23
- lifecycle states registered: 11
- artifact diagnostic codes added: 8
- inventory: 17,782 files scanned, 1,890 artifact-like files classified descriptively
- next Foundation Lock task: `SCHEMA-PROTOCOL-LAW-01`

Feature implementation remains blocked until Foundation Lock closes. Existing
artifacts are inventoried but not migrated by this task.

## DIAGNOSTIC-CODE-REGISTRY-01 Update

DIAGNOSTIC-CODE-REGISTRY-01 adds the provisional diagnostic/evidence registry.

- registry: `contracts/diagnostics/diagnostic_code.registry.json`
- policy: `contracts/diagnostics/diagnostic_policy.contract.toml`
- validator: `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`
- diagnostic codes registered: 14 provisional foundational codes
- severities registered: 7
- categories registered: 26
- evidence packet and evidence reference schemas exist under `contracts/evidence/`
- command/refusal/event surfaces carry narrow diagnostic/evidence alignment
- next Foundation Lock task: `ARTIFACT-IDENTITY-LAW-01`

Feature implementation remains blocked until Foundation Lock closes. Runtime
diagnostic dispatch, Workbench presentation, package behavior, and release
publication remain outside this task.

## COMMAND-SURFACE-01 Update

COMMAND-SURFACE-01 adds the provisional command/result/view/event/refusal/evidence law.

- contract: `contracts/command/command_surface.contract.toml`
- validator: `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`
- commands registered: 5 provisional foundational validation/test commands
- refusal codes registered: 5 command-level refusal scaffold codes
- result/view/event/document/evidence schemas exist under `contracts/*/`
- public surface registry now includes command, result, view, event, refusal, evidence, validator, and fixture surfaces
- Workbench, CLI, TUI, headless, rendered, server/admin, AIDE, and test surfaces are declared projections over registered commands, not separate authorities
- next Foundation Lock task: `DIAGNOSTIC-CODE-REGISTRY-01`

Feature implementation remains blocked until Foundation Lock closes. Runtime
command dispatch, Workbench UI, product behavior, and full diagnostic registry
work remain outside this task.

## DEPENDENCY-DIRECTION-01 Update

DEPENDENCY-DIRECTION-01 adds the provisional repository dependency-direction law.

- contract: `contracts/repo/dependency_directions.contract.toml`
- schema: `contracts/repo/dependency_direction.schema.json`
- exception ledger: `contracts/repo/dependency_direction_exceptions.toml`
- validator: `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict`
- initial scan: 16,104 tracked text/source files scanned across 14 roots
- current strict result: PARTIAL, with 358 high-confidence existing violations and 38 warnings
- violations are recorded as dependency-direction debt, not hidden by broad exceptions
- next Foundation Lock task: `COMMAND-SURFACE-01`

Feature implementation remains blocked until Foundation Lock closes. Full CTest
remains T4 full/release proof and is not required for this governance task.

## LANGUAGE-BASELINE-01 Update

LANGUAGE-BASELINE-01 moves Dominium active mainline governance to C17 + C++17.

- contract: `contracts/build/language_baseline.contract.toml`
- schema: `contracts/build/language_subset.schema.json`
- validators:
  - `python tools/validators/build/check_language_baseline.py --repo-root . --strict`
  - `python tools/validators/build/check_cpp17_forbidden_library_use.py --repo-root . --strict`
- active CMake and verify presets now use C17/C++17
- public ABI remains C-compatible and provisional unless separately promoted
- fast strict: PASS, 32/32 commands, 318.25 seconds
- warning: 7 legacy projection presets still declare `DOM_LANG_MODE=c89_cpp98` outside active mainline
- next Foundation Lock task: `DEPENDENCY-DIRECTION-01`

Feature implementation remains blocked until Foundation Lock closes. Full CTest
remains T4 full/release proof and was not rerun for this task.

## API-ABI-CANON-01 Update

API-ABI-CANON-01 adds the provisional C API/ABI canon:

- contracts: `contracts/abi/c_api.contract.toml` and `contracts/abi/language_boundary.contract.toml`
- rule registry: `contracts/abi/abi_rule.registry.json`
- public header schema: `contracts/abi/public_header.schema.json`
- validator: `python tools/validators/abi/check_public_headers.py --repo-root . --strict`
- public header candidates inspected: 375
- high-confidence violations: 0
- provisional warning findings: 2,851, primarily legacy prefixes, unpromoted ABI struct shape, and C++ declarations in non-frozen headers
- no surface is promoted to frozen ABI by this task
- next Foundation Lock task: `DEPENDENCY-DIRECTION-01`

Feature implementation remains blocked until Foundation Lock closes. Full CTest
remains T4 full/release proof and is not required for this normal-gate task.

## PUBLIC-SURFACE-REGISTRY-01 Update

PUBLIC-SURFACE-REGISTRY-01 adds the initial public surface registry:

- registry: `contracts/public_surface/public_surface.contract.toml`
- validator: `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- initial surfaces: 20
- stable surfaces: 2, limited to strict repo governance contracts
- fast strict: PASS, 30/30 commands, 299.828 seconds
- next Foundation Lock task: `API-ABI-CANON-01`

Feature implementation remains blocked until Foundation Lock closes. No broad
folder work is required by this registry scaffold.

## FAST-STRICT-TEST-TIER-01 Update

FAST-STRICT-TEST-TIER-01 defines the normal development proof gate as
`fast_strict` = T0 + T1 + T2.

- command: `python tools/test/run_fast_strict.py --repo-root .`
- latest result: PASS, 30/30 commands, 332.828 seconds
- full CTest remains T4 full/release debt and is not claimed green
- next Foundation Lock task: `PUBLIC-SURFACE-REGISTRY-01`

## Current Correction After POST-CONVERGE-10E

POST-CONVERGE-00 confirmed that exception retirement and build/runtime proof must precede platform, render, native shell, worldgen, and broad domain expansion.

POST-CONVERGE-06 completed targeted build, FAST, and AIDE diagnostics:

- the AIDE pack Python compatibility blocker is fixed locally
- the original FAST `repox_runner` structural crash is reduced to broader RepoX drift findings
- local `cmake --preset verify` was blocked at that time by the missing Visual Studio 17 2022 generator
- build and CTest proof were pending until a valid verify toolchain or accepted CI lane was available

POST-CONVERGE-07 attempted canonical local runtime proof and is blocked:

- no `client`, `server`, `setup`, or `launcher` binary exists locally
- no full local playtest/session/status/save/load/resume sequence was run
- `python apps/server/server_main.py --help` exits 0 but enters AppShell TUI because the script invocation does not forward CLI args
- `tools/validators/check_local_playtest_path.py` records the current blocked state

POST-CONVERGE-08 attempted product boot matrix proof at the user's request and is partial:

- launcher AppShell help boots through `python tools/package/launcher/launch.py --help`
- client AppShell help boots through `python archive/generated/dist/bin/dominium_client --help`
- server AppShell help boots through `python archive/generated/dist/bin/dominium_server --help`
- the attach-console tool stub help boots through `python tools/validators/shell/product_stub_cli.py --product-id tool.attach_console_stub --help`
- setup remains blocked before help through the Python bridge on local Python 3.8
- `archive/generated/dist/bin/dom` remains blocked because `archive/generated/dist/bin/tool_attach_console_stub` is missing
- no native product binary boot was proven

POST-CONVERGE-09 attempted portable projection/package smoke proof and is partial:

- distribution contracts and portable/package docs are coherent
- package/projection tool help surfaces exist
- a temporary one-file `.dompkg` smoke package was packed and verified under `%TEMP%`, then removed
- no real portable projection root was generated
- required portable manifests and native product binaries remain blocked by the missing build output

POST-CONVERGE-10 added the tuple-driven build contract and machine probe. POST-CONVERGE-10B reprobed after Visual Studio installation:

- build contract files now exist under `contracts/build/`
- local probe output is generated under ignored `.dominium.local/`
- Visual Studio Enterprise 2022 and MSVC v143 are now detected
- generated local preset data now includes `verify.winnt10.x64.msvc143.mt.debug`
- `CMakeUserPresets.json` can be generated as ignored local data so CMake can consume the tuple preset; POST-CONVERGE-10B removed it before final strict layout validation
- CMake selects Windows SDK `10.0.26100.0` and MSVC tools `14.44.35207`
- configure now fails during CMake generation because tests still reference stale pre-convergence root paths:
  - `runtime/projection/rendered/presentation/frame_graph_builder.cpp`
  - `game/law/authority/dom_server_authority.cpp`
- no native product binaries were produced

POST-CONVERGE-10C fixed the stale client/server CMake and test paths:

- `verify.winnt10.x64.msvc143.mt.debug` configure now passes
- `cmake --preset verify` now passes
- tuple and canonical builds produce native product binaries before failing
- build remains red because `tool_ui_bind --check` reports stale generated outputs in `libs/appcore/ui_bind/`
- `ctest --preset verify` was not run because build failed

POST-CONVERGE-10D fixed the UI bind generated-output freshness gate:

- `libs/appcore/ui_bind/**` is now pinned to LF line endings for byte-identical generated-source checks
- `tool_ui_bind --check` passes
- `verify.winnt10.x64.msvc143.mt.debug` configure and build pass
- `cmake --preset verify` and `cmake --build --preset verify` pass
- native product binaries are present under `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/`
- canonical verify binaries for setup/launcher/client/server are present under `out/build/vs2026/verify/bin/`
- CTest remains blocked by tools/auditx failures and timeout

POST-CONVERGE-10E fixed the targeted AuditX/CTest path blockers:

- `tools_refusal_explain` and `tools_coverage_inspect` now pass after direct tool subprocesses resolve the repo root before importing `compat`
- AuditX no longer assumes retired root `schema` as source authority; generated bundle projections now source schemas from `contracts/schema/`
- generated wrapper smoke includes current converged `apps/` and `game/` runtime roots
- missing generated release manifests now surface as deterministic refused verification results instead of uncaught AuditX crashes
- focused AuditX CTest cases pass
- `verify.winnt10.x64.msvc143.mt.debug` configure/build still pass
- `cmake --preset verify` and `cmake --build --preset verify` still pass
- full CTest remains blocked by `invariant_units_present`, `inv_repox_rules`, and local wall-time

POST-CONVERGE-10F remediated and classified the remaining unit/RepoX blockers:

- `invariant_units_present` now passes in the tuple verify CTest lane
- `unit.mass_energy.stub` is declared in `contracts/registry/unit_registry.json`
- the unit validator no longer treats path fragments such as `materials/unit.schema` as unit identifiers
- `inv_repox_rules` still fails with broad RepoX/canonical-evidence drift
- the RepoX CTest wrapper now writes generated proof/profile output to ignored `.dominium.local/ctest/repox/`
- canonical `ctest --preset verify -N` currently discovers 0 tests, while the tuple verify build discovers 493 tests
- full CTest remains blocked by RepoX semantic failures and wall-time/discovery concerns

Current priority order:

1. remediate `inv_repox_rules` broad RepoX/canonical-evidence drift
2. repair or regenerate canonical `verify` CTest discovery so `ctest --preset verify` sees the expected tests
3. partition or classify full CTest wall-time after semantic RepoX failures are resolved
4. decide whether POST-CONVERGE-11 may proceed with build-green/CTest-warning status
5. fix or classify setup Python bridge compatibility and the missing `archive/generated/dist/bin/dom` target
6. fix or classify direct `apps/server/server_main.py` CLI argument forwarding
7. add or prove a real portable projection assembly path that emits required manifests and roots
8. rerun product boot and portable projection proof only after build, product command, and projection blockers are accepted or resolved

Planning references:

- `docs/repo/audits/POST_CONVERGE_00_HEALTH.md`
- `docs/repo/audits/POST_CONVERGE_EXCEPTION_TRIAGE.md`
- `docs/repo/audits/POST_CONVERGE_06_BUILD_FAST_REMEDIATION.md`
- `docs/repo/audits/POST_CONVERGE_07_LOCAL_RUNTIME_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_08_PRODUCT_BOOT_MATRIX_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_09_PORTABLE_PROJECTION_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_10_BUILD_BINARY_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_10E_CTEST_AUDITX_REMEDIATION.md`
- `docs/repo/audits/POST_CONVERGE_10F_UNIT_REPOX_REMEDIATION.md`
- `docs/repo/EXCEPTION_RETIREMENT_QUEUE.md`
- `docs/repo/BUILD_ENVIRONMENT_REMEDIATION.md`
- `docs/repo/BUILD_VERIFICATION_PATHS.md`
- `docs/repo/FAST_GATE_REMEDIATION.md`
- `docs/repo/AIDE_PACK_REMEDIATION.md`
- `docs/runtime/CANONICAL_LOCAL_PLAYTEST.md`
- `docs/release/LOCAL_RUNTIME_PROOF.md`
- `docs/release/PRODUCT_BOOT_PROOF.md`
- `docs/distribution/PORTABLE_PROJECTION_SMOKE_PROOF.md`
- `docs/release/PACKAGE_SMOKE_PROOF.md`
- `docs/release/NATIVE_BINARY_PROOF.md`
- `docs/build/BUILD_CONTRACT.md`

## NAME-00 Naming Canon Update

NAME-00 locks directory, file, language, and ownership naming law before additional broad cleanup.

New naming authority:

- `contracts/repo/naming.contract.toml`
- `docs/repo/directory_naming.md`
- `docs/repo/file_naming.md`
- `docs/repo/no_src_source_policy.md`
- `docs/repo/module_layout.md`
- `docs/repo/language_ownership.md`

Naming validators live under `tools/validators/repo/` and are warning-oriented classifiers for current debt. They do not replace the strict layout/root/distribution/component validators.

Future MOVE-BULK B-G refinement must not route files to `src/`, `source/`, `code/`, `impl/`, `common/`, `shared/`, or `misc` buckets. Planned internal renames such as `runtime/shell/ -> runtime/shell/`, `game/domain/ -> game/domain/`, and `contracts/schema/ -> contracts/schema/` remain future reviewed migrations only.

NAME-00 redo after MOVE-SCRIPT-00 refreshes the current numbers without changing scope:

- HEAD: `148a9adf95bb678da16784434221c568f7bb96cb`.
- naming-law blockers: 0.
- current bad-root tracked files: 1,765.
- route candidates: 1,593.
- skipped/deferred files: 172.
- target collisions: 0.

No files were moved or renamed by the redo. Feature work remains blocked. The current next cleanup task is `MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`.

## TEST-PERF-01 CTest Sharding Update

TEST-PERF-01 establishes the current CTest timing and shard policy after RESTRUCTURE-REPAIR-00 and NAME-00.

Current command lanes:

- focused RepoX: `ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300`
- smoke: `ctest --preset verify -L smoke --output-on-failure --timeout 300`
- fast: `ctest --preset verify -L fast --output-on-failure --timeout 300`
- AuditX: `ctest --preset verify -L audit --output-on-failure --timeout 1200`
- slow/nightly: `ctest --preset verify -L slow --output-on-failure --timeout 1200`

Measured results:

- focused RepoX: PASS in 128.978 seconds.
- smoke: PASS in 55.829 seconds.
- fast: PASS in 48.821 seconds.
- AuditX shard: PASS in 824.573 seconds.

Full CTest remains a promotion lane under the TEST-PERF-01 sharded execution policy.

## POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS Update

POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS resolved the two remaining semantic lint blockers without broad suppressions.

Current semantic lint lanes:

- `slice0_hardcoded_ids`: PASS in 7.93 seconds.
- `slice1_hardcoded_constants`: PASS in 3.00 seconds.
- combined semantic lint rerun: PASS in 11.01 seconds.

Finding disposition:

- `preserve_doctrine_constant`: 213.
- `preserve_fixture_literal`: 582.
- `preserve_protocol_literal`: 264.
- `preserve_schema_literal`: 45.

The allowlist is exact-match only and lives at `contracts/repo/semantic_lint_allowlist.json`.

## MOVE-SCRIPT-00 Bad-Root Router Update

MOVE-SCRIPT-00 generated the deterministic dry-run router needed before re-gating deferred MOVE-BULK B-G cleanup.

Current dry-run routing evidence:

- bad-root tracked files: 1,765.
- route candidates: 1,593.
- skipped/deferred files: 172.
- target collisions: 0.
- moves applied: 0.
- exceptions retired: 0.

Batch summaries:

- B templates/models/modding: 2 route candidates, 4 skipped.
- C content identity: 1,488 route candidates, 26 skipped.
- D authority/policy: 17 route candidates, 33 skipped.
- E active tools: 0 route candidates, 33 skipped.
- F runtime/core/net: 0 route candidates, 54 skipped.
- G libs/ABI: 86 route candidates, 22 skipped.

The next repair/refinement task is `MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`.

## What Can Proceed

The repository is ready for scoped work in these areas:

- targeted CTest/auditx remediation for the existing `verify` preset
- targeted build tuple/probe/preset remediation using `contracts/build/`
- targeted RepoX FAST drift remediation
- targeted command-surface remediation for script-level CLI argument forwarding, after build proof is available
- targeted setup Python compatibility remediation if the Python setup bridge remains a product proof path
- targeted `archive/generated/dist/bin/dom` wrapper remediation or retirement if that wrapper remains a shipped tool surface
- targeted portable projection assembly/manifest generation remediation
- documentation updates that reflect the current validation state
- narrowly scoped AIDE/tooling compatibility fixes

Platform, render, native shell, Universal Reality enforcement, worldgen, domain realism, and public release/package expansion should wait until build proof, product boot proof, and portable projection status are resolved or explicitly accepted.

## What Must Not Happen

- no new root-level domain folders
- no new root-level product folders
- no GUI toolkit owning product semantics
- no renderer owning simulation truth
- no distribution/runtime/install/media roots treated as source roots
- no support claims without component matrix status
- no new machine-readable authority under transitional roots without contract review
- no CONTRACT-00 Universal Reality enforcement until build, product boot, and portable projection blockers are accepted or resolved

## Suggested Sequence

1. Address remaining RepoX FAST/CTest drift findings in a targeted remediation task.
2. Repair or regenerate canonical `verify` CTest discovery.
3. Rerun CTest through `verify.winnt10.x64.msvc143.mt.debug` and the canonical `verify` lane.
4. Run TEST-PERF-00 if semantic failures are clear but full CTest still exceeds local wall-time.
5. Remediate or explicitly classify setup Python bridge compatibility and the missing `archive/generated/dist/bin/dom` target.
6. Add or prove a portable projection assembly path that emits `install.manifest.json`, `semantic_contract_registry.json`, `release.manifest.json`, product binaries, and required portable roots.
7. Rerun strict layout validators, docs/build/UI/ABI checks, FAST, and AIDE pack.
8. Run POST-CONVERGE-11 product boot proof with native binaries after build output exists.
9. Rerun portable projection smoke proof after projection generation is available.
10. Start CONTRACT-00 only after these blockers are resolved or explicitly accepted as warning-only.

## POST-CONVERGE-10J Update - Authority Documentation Status

- Result: PARTIAL.
- Focused RepoX improved from 71 failures / 5 warnings to 60 failures / 5 warnings.
- `INV-DOC-STATUS-HEADER` reduced from 12 to 0 through narrow authority-sensitive metadata repairs.
- Seven architecture documents were added to the DERIVED canon index bucket to avoid introducing canon-index drift after their headers became parseable.
- POST-CONVERGE-11 remains blocked.
- Next recommended task: `POST-CONVERGE-10K - Contract Registry Acceptance Backlog Remediation`.

## Domain Work Rule

Future domain work must use the split model:

- schemas, registries, capabilities, and protocols under `contracts/`
- implementation under `game/domain/`
- authored data and packs under `content/`
- human explanation under `docs/domains/`
- fixtures, determinism, regression, and golden tests under `tests/`

## Matrix Rule

Future platform/render/native/toolchain/package work must update `contracts/release/component_matrix.contract.toml` and relevant `docs/release/*_MATRIX.md` docs when status changes.

Planned, stub, and research rows are not supported implementations.

## POST-CONVERGE-10G Update

POST-CONVERGE-10G reduced focused tuple `inv_repox_rules` from 1844 failures and 5 warnings to 1769 failures and 5 warnings. Safe stale path/root assumptions were fixed for the RepoX top-level root check and retired AppShell root checks. RepoX cache keys now include the rule implementation file, so rule edits invalidate stale group output.

POST-CONVERGE-11 remains blocked. The next recommended task is `POST-CONVERGE-10H - Canonical Documentation Status and Canon Index Remediation`, focused on the `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, and `INV-CANON-NO-HIST-REF` families. Product boot, package proof, portable projection proof, and additional moves remain unauthorized.

## POST-CONVERGE-10H Update

POST-CONVERGE-10H reduced focused tuple `inv_repox_rules` from 1769 failures and 5 warnings to 153 failures and 5 warnings. It repaired 1533 clear DERIVED documentation status/header cases and added 84 missing canonical index entries for documents that already declared `Status: CANONICAL`.

POST-CONVERGE-11 remains blocked. The next recommended task is `POST-CONVERGE-10I - Historical Reference and Archive Citation Remediation`, focused on `INV-CANON-NO-HIST-REF`.

## POST-CONVERGE-10I Update - Historical Reference Remediation

- Result: PARTIAL.
- Focused RepoX improved from 153 failures / 5 warnings to 71 failures / 5 warnings.
- `INV-CANON-NO-HIST-REF` reduced from 81 to 0 by aligning RepoX enforcement to canonical-doc scope and preserving DERIVED quarantine/archive evidence references.
- POST-CONVERGE-11 remains blocked.
- Next recommended task: `POST-CONVERGE-10J - Authority-Sensitive Documentation Status Review`.

## POST-CONVERGE-10K Update - Contract Registry Acceptance

- Result: PARTIAL.
- Focused RepoX actual local state improved from 59 failures / 5 warnings to 51 failures / 5 warnings.
- The prior 10J-reported 60th failure was `INV-LOCKLIST-FROZEN`, which was absent at 10K start because `origin/main` equaled local HEAD.
- `INV-NEW-CONTRACT-REQUIRES-ENTRY` reduced from 9 to 0 by adding four accepted current architecture contract rows to `contracts/registry/semantic_contract_registry.json`.
- POST-CONVERGE-11 remains blocked because focused tuple `inv_repox_rules` still fails on distribution/product proof, retired-domain path policy, tool hash/audit staleness, ruleset mapping, and related families.
- Next recommended task: `POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification`.

## TEST-PERF-00 Update - Tiered Validation

- Result: PASS_WITH_WARNINGS.
- Canonical `verify` CTest discovery was repaired locally by running `cmake --preset verify`; `ctest --preset verify -N` now discovers 493 tests in this checkout.
- CTest label metadata was repaired so `ctest --preset verify -N -L smoke` discovers 57 smoke tests after reconfigure.
- Added `tests/validation_tiers.json`, `scripts/test_tier.py`, `scripts/test_impacted.py`, and `scripts/test_timing_report.py`.
- Full CTest remains the promotion gate, not the default post-change gate.
- Focused RepoX semantic failures remain from POST-CONVERGE-10K, so POST-CONVERGE-11 remains blocked until those failures are resolved or explicitly accepted by a later gate.
- Next recommended semantic task remains `POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification`; next test-performance task is `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline`.

## POST-CONVERGE-10L Update - Distribution/Product Proof Classification

- Result: PARTIAL.
- Focused RepoX baseline from POST-CONVERGE-10K remains 51 failures / 5 warnings after a transient 10K audit status-header failure was repaired.
- `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` remains 7 failures and `INV-NO-ADHOC-MAIN` remains 5 failures.
- All 12 target distribution/product failures were classified as missing portable projection wrapper/proof surfaces under `archive/generated/dist/bin/`.
- No product boot proof, portable projection proof, package proof, release proof, dummy wrapper, or generated artifact was created.
- POST-CONVERGE-11 remains blocked because focused RepoX still has non-proof governance failures outside the product/projection family.
- Next recommended task: `POST-CONVERGE-10M - Retired-Domain Path Policy and Tool Hash Drift Remediation`.

## POST-CONVERGE-10M Update - Retired-Domain Path Policy

- Result: PARTIAL.
- Focused RepoX improved from 51 failures / 5 warnings to 23 failures / 5 warnings.
- Safe stale RepoX rule paths for retired embodiment, geology, worldgen-refinement, universe, and diagnostics roots were updated to exact current locations.
- RepoX group cache file-dependency hashing was repaired so rule edits invalidate stale cached group output.
- Two retired-domain failures remain because `game.domain.embodiment` lazily imports retired `embodiment.*` modules during MW-4 fixture evaluation; fixing that would change product/runtime source behavior and was not authorized by 10M.
- POST-CONVERGE-11 remains blocked because focused RepoX still has non-proof governance failures.
- Next recommended task: `POST-CONVERGE-10N - Tool Hash, Audit Staleness, Ruleset Mapping, and Remaining RepoX Gate Classification`.

## POST-CONVERGE-10N Update - Tool Hash and Audit Staleness

- Result: PARTIAL.
- Focused RepoX improved from 23 failures / 5 warnings to 20 failures / 5 warnings.
- `INV-IDENTITY-FINGERPRINT` reduced from 1 to 0 by refreshing `docs/archive/audit/identity_fingerprint.json` with the canonical generator.
- `INV-TOOL-VERSION-MISMATCH` reduced from 2 to 0 by refreshing `docs/archive/audit/security/INTEGRITY_MANIFEST.json` with the SecureX generator.
- RepoX cached groups now include explicit docs/archive/audit evidence dependencies where they read tracked audit artifacts skipped by Merkle roots.
- `INV-AUDITX-OUTPUT-STALE` and four glossary warnings in generated/historical audit evidence remain warnings.
- POST-CONVERGE-11 remains blocked because focused RepoX still has non-proof governance/source-policy failures.
- Next recommended semantic task: residual RepoX governance/source-policy remediation or an explicit RepoX acceptance gate; TEST-PERF follow-up remains useful for validation speed.

## POST-CONVERGE-10O Update - RepoX Closeout Gate

- Result: PARTIAL.
- Fresh focused RepoX reproduction remains 20 failures / 5 warnings.
- Canonical `ctest --preset verify -N` now discovers 493 tests in this checkout; CTest discovery is not the primary blocker.
- The tuple fallback was not required for POST-CONVERGE-10O because canonical `verify` discovered and ran `inv_repox_rules`.
- POST-CONVERGE-11 remains blocked because the remaining set is not only product/projection proof blockers and not warning-only.
- Real non-proof blockers remain in MW-4 embodiment fixture imports, ruleset mappings, canon supersession, extension registry coverage, worldgen retry-loop policy, and shadow bounded policy.
- Next recommended task: `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`.

## POST-CONVERGE-11 Update - Product Boot Proof Gate

- Result: BLOCKED.
- POST-CONVERGE-11 was attempted only as far as the required RepoX readiness gate.
- Fresh focused RepoX reproduction still reports 20 failures / 5 warnings.
- No accepted-warning ledger exists, so product binaries were not inspected or executed.
- No build, product boot proof, portable projection proof, package proof, or release proof was run.
- POST-CONVERGE-12 is not ready.
- Next recommended task remains `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`.

## POST-CONVERGE-12 Update - Portable Projection Gate

- Result: BLOCKED.
- POST-CONVERGE-12 stopped at the prerequisite product boot readiness gate.
- POST-CONVERGE-11 product boot proof remains blocked and records `ready_for_post_converge_12=false`.
- No projection tooling was executed, no portable projection root was generated, and no native binaries were inspected, copied, refreshed, or executed.
- RELEASE-00 internal pilot release is not ready.
- Next recommended task remains `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`.

## Closeout Remediation Update

- Result: PASS_WITH_WARNINGS.
- Focused RepoX now passes: direct RepoX reports OK, and `ctest --preset verify -R inv_repox_rules --output-on-failure` passes.
- Tracked RepoX proof/profile evidence has zero warnings and zero failures after the closeout refresh.
- Native product command smoke passes for `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe` under `out/build/vs2026/verify/bin/`.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300` passes 57/57.
- Canonical `ctest --preset verify -N` discovers 493 tests, but full promotion verification still needs TEST-PERF follow-up because `cmake --build --preset verify` timed out during verification after producing the binaries.
- Local ignored portable projection generation now completes under `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium`.
- `python tools/validators/check_portable_projection.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium` reports `proof_status: proven`.
- No package, installer, public release, tag, or GitHub release was generated.
- Next recommended release task: `RELEASE-00 - Internal Pilot Release 0`.
- Next recommended validation-speed task: `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline`.

## RELEASE-00 Update - Internal Pilot Release 0

- Result: PASS_WITH_WARNINGS.
- Local ignored internal pilot release staging now completes under `.dominium.local/releases/internal-pilot-0`.
- The staging root contains the portable projection tree, internal pilot manifest, provenance, checksums, proof reports, warning ledger, runbook, and rollback notes.
- `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --json --strict` passes with no blockers and verifies 4718 checksum entries.
- No public release, GitHub release, tag, upload, installer, package publication, source-root move, rename, delete, alias, move map, or salvage map was created.
- Generated release staging remains local ignored proof evidence and was not committed.
- Next recommended task: `DOE-00 - Dominium Operating Environment Doctrine and Boot Spine Plan`.
- Validation-speed follow-up remains `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline`.

## BASELINE-00 Update - Structural Regression Baseline

- Result: PASS_WITH_WARNINGS.
- RELEASE-00 is now frozen as the structural regression baseline for MOVE-FAMILY cleanup waves.
- Baseline HEAD: `0b631fc5f09f3d927a54e8312976b926d111a72e`.
- Release root: `.dominium.local/releases/internal-pilot-0`.
- Projection input: `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium`.
- Generated release, projection, build, and local AIDE outputs remain ignored/local and uncommitted.
- Future move-family work must compare against `docs/repo/STRUCTURAL_REGRESSION_BASELINE.md` and `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`.
- DOE-00 and feature/operating-environment MVP work are deferred until MOVE-FAMILY cleanup and post-restructure proof pass.
- Next recommended task: `MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan`.

## MOVE-FAMILY-00-PLAN Update - First Family Cleanup Planning

- Result: BLOCKED.
- BASELINE-00 task commit used for this plan: `6ed2516ea9570bd54cdd3f1d94ed347f48cf6447`.
- Target roots inspected: `governance/`, `meta/`, `performance/`, `validation/`, and `ide/`.
- Planned moves: 0.
- Deferred files: 36.
- `ide/README.md` was already moved by AIDE-MOVE-01; the remaining target-family material is active Python/tooling surface or machine-readable IDE projection metadata.
- No files were moved, deleted, renamed, or rewritten.
- Apply remains unauthorized and `MOVE-FAMILY-00-GATE` is not ready.
- Next recommended task: `MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES - Define ownership and consumer-safe destinations for active governance/meta/performance/validation modules and IDE projection manifests`.

## MOVE-FAMILY-00B-APPLY Update - IDE Manifest Projection Migration

- Result: PASS_WITH_WARNINGS.
- The three tracked IDE manifest source files moved from `ide/manifests/**` to `contracts/projection/ide/**`.
- Applied reference rewrite groups: 5.
- `git ls-files ide`: empty.
- The empty `ide/` directory tree was removed after verifying it contained no files.
- `ide_root` source-layout exception retired; active layout exception count is now 31.
- Focused RepoX passed after metadata-only status header repairs in three touched planning docs.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration remain not run by scope.
- Next recommended task: `MOVE-FAMILY-00B-PROOF - IDE Root Retirement Proof`.

## MOVE-FAMILY-00B-PROOF Update - IDE Root Retirement Proof

- Result: PASS_WITH_WARNINGS.
- `git ls-files ide`: empty.
- Filesystem `ide/`: absent.
- `ide_root` source-layout exception: retired and accepted by strict validators.
- Tracked replacement files under `contracts/projection/ide/**`: present and JSON parse PASS.
- Active stale references to retired tracked schema/example source paths: none.
- Remaining old-path references are historical, planning, audit, AIDE evidence, root-recycling history, or generated-output references.
- AIDE validation, strict validators, docs/build/UI/ABI checks, focused RepoX, manifest parsing, generated-output ignored/staging checks, and git diff checks passed with known warnings.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration remain not run by scope.
- Next recommended task: `MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan`.

## MOVE-FAMILY-00C-PLAN Update - Active Tool Namespace Planning

- Result: BLOCKED.
- Target roots inspected: `validation/`, `meta/`, `governance/`, and `performance/`.
- Active Python files found: 33.
- Package init files: 14.
- Direct CLI entrypoints under target roots: 0.
- Active Python import files: validation 8, meta 104, governance 9, performance 4.
- Planned move count: 0.
- Shim-required candidate groups: `validation`, `meta.identity`, `meta.stability`, and `governance`.
- semantic/runtime `meta/**` and product/runtime `performance/**` remain preserve-current.
- No moves, deletes, renames, shims, import rewrites, reference rewrites, map applications, or exception retirements occurred.
- Next recommended task: `MOVE-FAMILY-00C-A-PLAN - Validation, Identity, and Stability Shim Contract Plan`.

## MOVE-FAMILY-00C-A-PLAN Update - Validation Shim Contract Planning

- Result: PASS_WITH_WARNINGS.
- Groups planned: `validation`, `meta.identity`, and `meta.stability`.
- Target namespaces: `tools.validators.validation`, `tools.validators.identity`, and `tools.validators.stability`.
- Planned future implementation moves: 7.
- Planned future temporary shim files: 7.
- Apply-phase import rewrites planned: 34.
- Temporary old-import allowlist entries: 10.
- Ready for `MOVE-FAMILY-00C-A-GATE`: true.
- No moves, deletes, renames, shims, import rewrites, reference rewrites, map applications, or exception retirements occurred.
- Next recommended task: `MOVE-FAMILY-00C-A-GATE - Validation, Identity, and Stability Shim Migration Gate`.

## MOVE-BULK-00-PLAN Update - Global Bad-Root Migration Planning

- Result: PASS_WITH_WARNINGS.
- Remaining bad roots inspected: 23.
- Tracked files under remaining bad roots: 1,790.
- Initial gate-ready subset: 309 docs/evidence/archive files in Batch A.
- Deferred until batch gates: 1,481 files.
- Explicit blocked file action: `docs/development/libraries/CMakeLists.txt` until CMake/build-focused ABI gate approval.
- `ide/` remains retired and excluded from remaining bad-root planning.
- No moves, deletes, renames, shims, import rewrites, reference rewrites, move-map applications, salvage-map applications, or exception retirements occurred.
- Feature work remains blocked.
- Next recommended task: `MOVE-BULK-00-GATE - Global Bad-Root Migration Gate`.

## MOVE-BULK-00-GATE Update - Global Bad-Root Migration Gate

- Result: PASS_WITH_WARNINGS.
- Authorized batch: Batch A docs/evidence/archive-only.
- Authorized next task: `MOVE-BULK-01-APPLY-DOCS-ARCHIVE`.
- Authorized planned file count: 309.
- Deferred batches: B, C, D, E, F, and G.
- Blocked batch: H until prior batches apply and prove cleanly.
- No moves, deletes, renames, shims, import rewrites, reference rewrites, map applications, or exception retirements occurred.
- Feature work remains blocked.

## MOVE-BULK-01-APPLY Update - Docs/Archive Safe Subset

- Result: PASS_WITH_WARNINGS.
- Batch A planned files: 309.
- Applied safe-subset moves: 26.
- Skipped files: 283 because exact active/current references remain.
- Reference rewrites applied: 0.
- Layout exceptions retired or narrowed: 0.
- `data/` remains tracked with 1,253 files.
- Tier 0 validation passed with known TOML fallback-parser warnings.
- Feature work remains blocked.
- Next recommended task: next authorized MOVE-BULK apply batch, or Batch A skipped-reference refinement if no later batch is authorized.

<!-- MOVE-BULK-08-CLOSURE -->

## MOVE-BULK-08 Final Exception Closure

MOVE-BULK-08 records a partial closure snapshot rather than a clean final closeout.

- Remaining tracked bad-root files: 1764.
- Roots still tracked: 23.
- Roots retired or empty: ide.
- Exceptions retired or narrowed by closure: 0.
- New shims created by closure: 0.
- Ready for `POST-RESTRUCTURE-00-FULL-PROOF`: no.
- Recommended next task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`, or the next explicit batch gate.

<!-- POST-RESTRUCTURE-00-BLOCKED -->

## POST-RESTRUCTURE-00 Blocked Proof Note

POST-RESTRUCTURE-00 did not run the full proof chain because MOVE-BULK-08 closure says full proof is not ready.

- Remaining former bad-root files: 1764.
- Deferred batches: B-G.
- Blocked batch: H.
- Ready for DOE-00: no.
- Next recommended task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.

## CANON-SPINE-NEW Update

CANON-SPINE-NEW supersedes the remaining second-level source-spine cleanup
prompt chain.

- Result: PASS_WITH_WARNINGS.
- Former bad roots: 0 tracked files.
- Source-spine cleanup: shell/app/appshell/appcore collapsed toward
  `runtime/shell/`; workbench modules moved under `apps/workbench/module/`;
  engine/game/contracts/content/tools/docs duplicate buckets routed toward the
  canonical grammar.
- Passing lanes: AIDE, strict repo/root/distribution/component validators,
  bad-root absence, docs sanity, UI shell purity, ABI boundaries, CMake
  configure, smoke CTest, and focused spine CTest.
- Remaining blockers: build target boundary warnings and broad full CTest.
- Feature implementation authorized: no.
- Next recommended task: `CANON-SPINE-BOUNDARY-01 - Repair Remaining Boundary Imports and Full Proof`.

<!-- MOVE-ROUTER-00 -->

## MOVE-ROUTER-00 Next-Step Update

MOVE-ROUTER-00 changes the active cleanup path from batch micro-planning to a
deterministic route table.

## PORTABILITY-MATRIX-01 Update

PORTABILITY-MATRIX-01 adds the provisional portability matrix scaffold:

- `contracts/platform/**` defines platform floors, architectures, toolchains,
  statuses, runtime/renderer/product/package portability matrices, evidence,
  and refusal policy.
- `tools/validators/platform/check_portability_matrix.py` validates matrix rows,
  fixtures, registry references, and descriptive inventory.
- No CMake presets, CI jobs, build targets, providers, renderers, product modes,
  packages, or release behavior are implemented or promoted by this task.
- Feature work remains blocked pending Foundation Lock closeout.

Next task: `FOUNDATION-CLOSEOUT-01`.

- Naming canon: active.
- Bad-root routing contract: active.
- Dry-run router: `tools/migration/route_bad_roots.py`.
- Bad-root tracked files routed: 1,765 of 1,765.
- Known canonical routes: 1,694.
- Quarantine routes: 71.
- Target collisions: 0.
- Skipped/impossible routes: 0.
- Moves applied: 0.
- Feature work authorized: no.

Next recommended task:
`MOVE-ROUTER-01 - Apply Deterministic Bad-Root Router Safe Subset`.

<!-- MOVE-ROUTER-01 -->

## MOVE-ROUTER-01 Next-Step Update

MOVE-ROUTER-01 applied the deterministic bad-root route table.

- Bad-root tracked files before: 1,765.
- Bad-root tracked files after: 0.
- Semantic moves: 1,694.
- Quarantine moves: 71.
- Skipped moves: 0.
- Target collisions: 0.
- Empty-root exceptions retired: 23.
- Feature work authorized: no.

Next recommended task:
`MOVE-ROUTER-02 - Repair References, Imports, Build, Projection, and Exceptions After Routing`.

<!-- MOVE-ROUTER-02 -->

## MOVE-ROUTER-02 Next-Step Update

MOVE-ROUTER-02 repaired a large first wave of active references and imports but
did not reach final proof.

- Bad-root tracked files: 0.
- Path replacements recorded: 33,316.
- Import replacements recorded: 76.
- Runtime shim packages created: 3.
- CMake configure: PASS.
- Build/TestX: PARTIAL; broader TestX remains red.
- Feature work authorized: no.

Next recommended task:
`MOVE-ROUTER-02R - Finish Registry, Ruleset, Import, and Test Path Repair After Routing`.

<!-- RESTRUCTURE-REPAIR-00 -->

## RESTRUCTURE-REPAIR-00 Repair Update

RESTRUCTURE-REPAIR-00 applied safe structural repairs and reran the strongest feasible proof lanes.

- Result: PARTIAL.
- Passing lanes: AIDE, strict repo/root/distribution/component validators, docs/build/UI/ABI checks, focused RepoX, smoke CTest, native configure, build-only `ALL_BUILD`, product boot, portable projection, and internal pilot.
- Repaired lanes: stale app/client paths, integration metadata path, archive manifest paths, TestX path hygiene fixtures, ops compatibility JSON warning leakage, and doc contract references.
- Remaining blockers: full CTest, root-debt exceptions, frozen hash drift, expired override policy, replay hash mismatches, and AuditX timeouts.
- DOE-00 readiness: no.
- Feature implementation authorized: no.
- Next recommended task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.
