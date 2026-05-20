Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Restructure Repair Status

Latest task: `FOUNDATION-CLOSEOUT-01`.

Result: BLOCKED.

Foundation Lock was verified for presence and validator coverage, but it is not
closed. The dependency-direction strict validator still reports 358 violations
and 38 warnings in required closeout scope.

Next task:
`FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01`

`WORKBENCH-VALIDATION-SLICE-01` is not authorized yet. Broad feature work
remains blocked.

## FOUNDATION-CLOSEOUT-01 Update

FOUNDATION-CLOSEOUT-01 is BLOCKED.

- all required Foundation Lock files for tasks 01 through 15 are present.
- most Foundation validators and fixtures pass.
- active blocker: `tools/validators/repo/check_dependency_directions.py`.
- fast strict was run and produced closeout evidence.
- full CTest remains T4/full-gate debt and is not claimed green.

## MOD-PACK-TRUST-MODEL-01 Update

MOD-PACK-TRUST-MODEL-01 is PASS_WITH_WARNINGS.

- trust law: `contracts/trust/mod_pack_trust.contract.toml`.
- trust level registry: `contracts/trust/trust_level.registry.json`.
- permission kind registry: `contracts/trust/permission_kind.registry.json`.
- trust decision schema: `contracts/trust/trust_decision.schema.json`.
- mod descriptor schema: `contracts/modding/mod_descriptor.schema.json`.
- policies:
  - `contracts/trust/review_policy.contract.toml`.
  - `contracts/trust/sandbox_policy.contract.toml`.
  - `contracts/trust/determinism_impact_policy.contract.toml`.
  - `contracts/trust/native_provider_policy.contract.toml`.
  - `contracts/trust/external_adapter_policy.contract.toml`.
  - `contracts/modding/mod_capability_policy.contract.toml`.
  - `contracts/modding/pack_overlay_policy.contract.toml`.
- validator: `tools/validators/package/check_mod_pack_trust.py`.
- fixtures: `tests/contract/mod_pack_trust/**`.
- trust levels registered: 7.
- permission kinds registered: 22.
- diagnostic codes added: 10 mod/pack trust codes.
- refusal codes added: 9 mod/pack trust refusal codes.
- capabilities added: 9 mod/pack trust capabilities.
- existing pack trust surfaces are inventoried but not migrated.

Next task:
`PORTABILITY-MATRIX-01`

Feature implementation remains blocked until Foundation Lock closes.

## VERSION-DEPRECATION-LAW-01 Update

VERSION-DEPRECATION-LAW-01 is PASS_WITH_WARNINGS.

- versioning law: `contracts/versioning/versioning.contract.toml`.
- lifecycle registry: `contracts/versioning/lifecycle_state.registry.json`.
- schemas:
  - `contracts/versioning/version_compatibility.schema.json`.
  - `contracts/versioning/compatibility_range.schema.json`.
  - `contracts/versioning/deprecation_notice.schema.json`.
  - `contracts/versioning/version_transition.schema.json`.
- policies:
  - `contracts/versioning/deprecation_policy.contract.toml`.
  - `contracts/versioning/retirement_policy.contract.toml`.
  - `contracts/versioning/removal_policy.contract.toml`.
  - `contracts/versioning/surface_lifecycle.contract.toml`.
- validator: `tools/validators/contracts/check_version_deprecation.py`.
- fixtures: `tests/contract/versioning/**`.
- lifecycle states registered: 9.
- diagnostic codes added: 8 version/deprecation codes.
- refusal codes added: 6 version/deprecation refusal codes.
- current version-like surfaces are inventoried but not migrated.

Next task:
`MOD-PACK-TRUST-MODEL-01`

Feature implementation remains blocked until Foundation Lock closes.

## REPLACEMENT-PROTOCOL-01 Update

REPLACEMENT-PROTOCOL-01 is PASS_WITH_WARNINGS.

- replacement law: `contracts/replacement/replacement.contract.toml`.
- replacement packet schema: `contracts/replacement/replacement_packet.schema.json`.
- replacement impact/proof schemas:
  `contracts/replacement/replacement_impact.schema.json` and
  `contracts/replacement/replacement_proof.schema.json`.
- policies:
  - `contracts/replacement/rollback_policy.contract.toml`.
  - `contracts/replacement/conformance_policy.contract.toml`.
  - `contracts/replacement/migration_refusal_policy.contract.toml`.
- validator: `tools/validators/repo/check_replacement_packet.py`.
- fixtures: `tests/contract/replacement/**`.
- replacement kinds registered: 19.
- replacement statuses registered: 10.
- diagnostic codes added: 8 replacement codes.
- refusal codes added: 5 replacement refusal codes.
- inventory: 17,942 tracked files scanned; 1,824 replacement-like historical or
  future-candidate files classified.
- historical refactors are inventoried but not retroactively converted into full
  replacement packets.

Next task:
`VERSION-DEPRECATION-LAW-01`

Feature implementation remains blocked until Foundation Lock closes.

## MODULE-COMPOSITION-LAW-01 Update

MODULE-COMPOSITION-LAW-01 is PASS_WITH_WARNINGS.

- module law: `contracts/module/module_surface.contract.toml`.
- module schema: `contracts/module/module.schema.json`.
- Workbench workspace schema: `contracts/workbench/workspace.schema.json`.
- app descriptor schema: `contracts/app/app_descriptor.schema.json`.
- validators:
  - `tools/validators/contracts/check_module_descriptors.py`.
  - `tools/validators/contracts/check_workbench_workspaces.py`.
  - `tools/validators/contracts/check_app_descriptors.py`.
- fixtures: `tests/contract/module/**`, `tests/contract/workbench/**`, and `tests/contract/app/**`.
- module kinds registered: 12.
- diagnostic codes added: 8 module/workspace/app codes.
- capabilities added: 4 module/workspace/app capabilities.
- inventory: 17,896 tracked files scanned per validator; module, Workbench,
  and app candidates classified.
- current app, Workbench, runtime, pack, and tool systems are inventoried but
  not migrated.

Next task:
`REPLACEMENT-PROTOCOL-01`

Feature implementation remains blocked until Foundation Lock closes.

## PROVIDER-MODEL-01 Update

PROVIDER-MODEL-01 is PASS_WITH_WARNINGS.

- provider law: `contracts/provider/provider.contract.toml`.
- provider registry: `contracts/provider/provider.registry.json`.
- descriptor schema: `contracts/provider/provider_descriptor.schema.json`.
- validator: `tools/validators/contracts/check_provider_model.py`.
- fixtures: `tests/contract/provider/**`.
- provider descriptors registered: 5.
- provider kinds registered: 15.
- lifecycle states registered: 9.
- provider diagnostics and refusal codes added while preserving existing codes.
- capability registry updated with narrow `provided_by` cross-references.
- inventory: 17,865 tracked files scanned; 1,396 provider/backend/service/
  adapter/capability candidates classified.
- current providers and runtime systems are inventoried but not migrated.

Next task:
`MODULE-COMPOSITION-LAW-01`

Feature implementation remains blocked until Foundation Lock closes.

## CAPABILITY-REFUSAL-LAW-01 Update

CAPABILITY-REFUSAL-LAW-01 is PASS_WITH_WARNINGS.

- capability law: `contracts/capability/capability.contract.toml`.
- capability registry: `contracts/capability/capability.registry.json`.
- refusal law: `contracts/refusal/refusal.contract.toml`.
- validator: `tools/validators/contracts/check_capability_refusal.py`.
- fixtures: `tests/contract/capability_refusal/**`.
- capabilities registered: 9.
- refusal codes registered: 13.
- diagnostic codes added: 7 new capability/refusal/provider/platform/fallback
  codes plus the existing missing-capability code.
- inventory: 17,837 tracked files scanned; 1,190 capability/refusal/provider/
  trust candidates classified.
- current providers and runtime systems are inventoried but not migrated.

Next task:
`PROVIDER-MODEL-01`

Feature implementation remains blocked until Foundation Lock closes.

## SCHEMA-PROTOCOL-LAW-01 Update

SCHEMA-PROTOCOL-LAW-01 is PASS_WITH_WARNINGS.

- schema law: `contracts/schema/schema_evolution.contract.toml`.
- protocol law: `contracts/protocol/protocol_evolution.contract.toml`.
- registry law: `contracts/registry/registry_evolution.contract.toml`.
- validator: `tools/validators/contracts/check_schema_protocol_evolution.py`.
- fixtures: `tests/contract/schema_protocol/**`.
- diagnostic codes registered: 11 new schema/protocol/migration/registry codes
  plus the existing unsupported-schema-version code.
- inventory: 17,808 tracked files scanned; 2,489 schema/protocol-like files
  classified.
- existing schemas, protocols, registries, and manifests are inventoried but
  not migrated.

Next task:
`CAPABILITY-REFUSAL-LAW-01`

Feature implementation remains blocked until Foundation Lock closes.

## ARTIFACT-IDENTITY-LAW-01 Update

ARTIFACT-IDENTITY-LAW-01 is PASS_WITH_WARNINGS.

- artifact identity contract: `contracts/artifact/artifact_identity.contract.toml`.
- artifact manifest schema: `contracts/artifact/artifact_manifest.schema.json`.
- validator: `tools/validators/contracts/check_artifact_identity.py`.
- artifact kinds registered: 23.
- lifecycle states registered: 11.
- artifact diagnostics added: 8.
- inventory: 17,782 tracked files scanned; 1,890 artifact-like files classified.
- existing artifacts are inventoried but not migrated.

Next task:
`SCHEMA-PROTOCOL-LAW-01`

Feature implementation remains blocked until Foundation Lock closes.

## DIAGNOSTIC-CODE-REGISTRY-01 Update

DIAGNOSTIC-CODE-REGISTRY-01 is PASS_WITH_WARNINGS.

- diagnostic registry: `contracts/diagnostics/diagnostic_code.registry.json`.
- diagnostic policy: `contracts/diagnostics/diagnostic_policy.contract.toml`.
- validator: `tools/validators/contracts/check_diagnostics_registry.py`.
- diagnostic codes registered: 14 provisional foundational codes.
- severities registered: 7.
- categories registered: 26.
- evidence packet and evidence reference schemas exist under `contracts/evidence/`.
- public surface registry updated with diagnostic/evidence surfaces.

Next task:
`ARTIFACT-IDENTITY-LAW-01`

Feature implementation remains blocked until Foundation Lock closes.

## COMMAND-SURFACE-01 Update

COMMAND-SURFACE-01 is PASS_WITH_WARNINGS.

- command contract: `contracts/command/command_surface.contract.toml`.
- base result schema: `contracts/result/result.schema.json`.
- view/event/refusal/document/evidence schemas and registries exist under
  `contracts/`.
- validator: `tools/validators/contracts/check_command_surface.py`.
- commands registered: 5 provisional foundational validation/test commands.
- refusal codes registered: 5 command-level scaffold codes.
- public surface registry updated with command-surface surfaces.

Next task:
`DIAGNOSTIC-CODE-REGISTRY-01`

Feature implementation remains blocked until Foundation Lock closes.

## DEPENDENCY-DIRECTION-01 Update

DEPENDENCY-DIRECTION-01 is PARTIAL.

- dependency law: `contracts/repo/dependency_directions.contract.toml`.
- schema: `contracts/repo/dependency_direction.schema.json`.
- exception ledger: `contracts/repo/dependency_direction_exceptions.toml`.
- validator: `tools/validators/repo/check_dependency_directions.py`.
- initial scan: 16,104 tracked text/source files across 14 roots.
- violations: 358 high-confidence active dependency-direction violations.
- warnings: 38 unlisted active dependencies.
- active exceptions: 0.
- broad exceptions: none.

Next task:
`COMMAND-SURFACE-01`

Feature implementation remains blocked until Foundation Lock closes.

## LANGUAGE-BASELINE-01 Update

LANGUAGE-BASELINE-01 is PASS_WITH_WARNINGS.

- active mainline C floor: C17.
- active mainline C++ floor: C++17.
- public ABI remains C-compatible.
- language contract: `contracts/build/language_baseline.contract.toml`.
- language validators: `tools/validators/build/check_language_baseline.py` and `tools/validators/build/check_cpp17_forbidden_library_use.py`.
- fast strict: PASS, 32/32 commands, 318.25 seconds.
- warning: 7 legacy projection presets remain outside active mainline with `DOM_LANG_MODE=c89_cpp98`.
- full CTest remains T4 full/release debt and was not rerun.

Next task:
`DEPENDENCY-DIRECTION-01`

Feature implementation remains blocked until Foundation Lock closes.

## API-ABI-CANON-01 Update

API-ABI-CANON-01 is PASS_WITH_WARNINGS.

- C API/ABI canon: `contracts/abi/c_api.contract.toml`.
- Language boundary contract: `contracts/abi/language_boundary.contract.toml`.
- Public-header validator: `python tools/validators/abi/check_public_headers.py --repo-root . --strict`.
- Public header candidates inspected: 375.
- High-confidence violations: 0.
- Warnings: 2,851, retained as provisional ABI debt and stable-promotion blockers.
- No public ABI is frozen by this task.
- Next Foundation Lock task: `DEPENDENCY-DIRECTION-01`.

Feature implementation remains blocked until Foundation Lock closes.

## PUBLIC-SURFACE-REGISTRY-01 Update

PUBLIC-SURFACE-REGISTRY-01 is PASS_WITH_WARNINGS.

- public surface registry: `contracts/public_surface/public_surface.contract.toml`.
- validator: `python tools/validators/repo/check_public_surface.py --repo-root . --strict`.
- initial registry: 20 surfaces, 25 kinds, 12 stability classes.
- stable entries: 2 repo governance contracts with strict validator proof.
- fast strict: PASS, 30/30 commands, 299.828 seconds.
- feature implementation remains blocked until Foundation Lock closes.

Next task:
`API-ABI-CANON-01`

## FAST-STRICT-TEST-TIER-01 Update

FAST-STRICT-TEST-TIER-01 is PASS_WITH_WARNINGS.

- normal gate: `fast_strict` = T0 + T1 + T2.
- command: `python tools/test/run_fast_strict.py --repo-root .`
- latest result: PASS, 30/30 commands, 332.828 seconds.
- full CTest remains T4 full/release debt and was not rerun for this task.
- feature implementation remains blocked until Foundation Lock closes.

Next task:
`PUBLIC-SURFACE-REGISTRY-01`

## Current Green Gates

- AIDE doctor/validate/test/selftest/tools/roots/repo pass.
- Strict layout/root/distribution/component validators pass.
- Focused RepoX passes.
- Smoke CTest passes.
- Fast CTest label passes.
- Semantic lint CTest lanes pass.
- AuditX slow shard passes.
- Native configure and build-only `ALL_BUILD` pass.
- Product boot, portable projection, and internal pilot release validators pass.
- Frozen contract guard passes.
- Override policy tests pass.
- Replay hash invariance passes.

## Current Blockers

- Full CTest is not green.
- Twenty-three formerly bad roots remain under active exceptions.
- Current dry-run router inventory finds 1,765 tracked files under the former bad roots.
- `tools_auditx` no longer blocks the 300 second fast lane after `TEST-PERF-01`; AuditX is split into explicit `audit`/`auditx`/`slow`/`nightly` CTest shards with a 1200 second timeout.
- The tracked `.aide/reports/file-quality-ledger.json` large-file policy remains unresolved.
- The first two repair evidence commits failed AIDE commit-message policy and were not amended; the follow-up commit records the warnings.
- Existing naming conflicts are classified by NAME-00 but not moved or rewritten.

## Next Task

`MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`

DOE-00 is not ready. Feature implementation remains blocked.

## NAME-00 Update

NAME-00 added `contracts/repo/naming.contract.toml`, human naming docs, warning-oriented naming validators, and conflict evidence under `.aide/reports/NAME-00-*`.

The naming canon does not authorize moves. Future MOVE-BULK B-G refinement must use the NAME-00 target grammar and keep planned internal renames as future work only.

NAME-00 redo at `148a9adf95bb678da16784434221c568f7bb96cb` refreshed the current evidence after MOVE-SCRIPT-00:

- naming-law blockers: 0.
- current bad-root dry-run inventory: 1,765 tracked files.
- route candidates: 1,593.
- skipped/deferred files: 172.
- target collisions: 0.

The redo records current answers to the naming-law prompt but still applies no moves, renames, imports, references, shims, maps, or exception retirements.

## TEST-PERF-01 Update

TEST-PERF-01 measured 495 `verify` CTest tests, 57 smoke tests, 57 fast-label tests, and 3 AuditX slow-shard tests.

Current measured lanes:

- focused RepoX: PASS in 128.978 seconds.
- smoke CTest: PASS in 55.829 seconds.
- fast CTest: PASS in 48.821 seconds.
- AuditX shard: PASS in 824.573 seconds.

Full CTest remains governed by the TEST-PERF-01 sharded execution model.

## SEMANTIC-LINTS Update

POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS reproduced and classified 1,104 hardcoded identifier/constant findings:

- `preserve_doctrine_constant`: 213.
- `preserve_fixture_literal`: 582.
- `preserve_protocol_literal`: 264.
- `preserve_schema_literal`: 45.

Current semantic lint lanes:

- `slice0_hardcoded_ids`: PASS in 7.93 seconds.
- `slice1_hardcoded_constants`: PASS in 3.00 seconds.
- combined semantic lint rerun: PASS in 11.01 seconds.

The allowlist is exact-match only and lives at `contracts/repo/semantic_lint_allowlist.json`.

## MOVE-SCRIPT-00 Update

MOVE-SCRIPT-00 added a dry-run-only bad-root router under `tools/migration/`.

Current dry-run evidence:

- bad-root tracked files: 1,765.
- move candidates: 1,593.
- skipped/deferred files: 172.
- target collisions: 0.
- moves applied: 0.
- exceptions retired: 0.

The router consumes the NAME-00 target grammar and emits route candidates, skip/defer reasons, per-root summaries, and B-G batch summaries. It refuses ambiguous targets, collisions, identity-sensitive routes without clear ownership, active Python/import-sensitive packages without rewrite or shim plans, authority-sensitive docs-only routes, normative `specs/reality` material, and forbidden target segments such as `source` and generic `compat`.

## MOVE-ROUTER-01 Update

MOVE-ROUTER-01 replaced the skipped/deferred posture with deterministic
quarantine routing and applied the route table with `git mv`.

- bad-root tracked files before: 1,765.
- bad-root tracked files after: 0.
- semantic moves: 1,694.
- quarantine moves: 71.
- skipped moves: 0.
- target collisions: 0.
- active root exceptions retired: 23.

Current blockers shift from root presence to repair proof:

- old bad-root path references remain.
- imports and CMake/build paths may be stale.
- quarantined files require later owner review before promotion.
- full proof remains blocked until `MOVE-ROUTER-02` repairs references/imports/build/projection surfaces.

Next task:
`MOVE-ROUTER-02 - Repair References, Imports, Build, Projection, and Exceptions After Routing`

## MOVE-ROUTER-02 Update

MOVE-ROUTER-02 is PARTIAL.

- Former bad roots remain empty in tracked source.
- Bad-root absence, strict repo layout, and strict root allowlist validators pass.
- CMake configure passes.
- Integrated fast/smoke tests reached by the build pass: 57/57 passing.
- Broader TestX remains red: 140 of 344 lanes failed.

Remaining blocker classes:

- RepoX ruleset discovery still points at old `repo/repox/rulesets`.
- Registry and pack consumers still expect old `data/` and `packs/` paths.
- Some old import package shapes and source path expectations remain.
- Frozen hashes and generated evidence need reviewed disposition.

Next task:
`MOVE-ROUTER-02R - Finish Registry, Ruleset, Import, and Test Path Repair After Routing`

## CANON-SPINE-NEW Update

CANON-SPINE-NEW is PASS_WITH_WARNINGS.

- Former bad roots remain empty in tracked source.
- Runtime shell, workbench, engine/runtime split, game/domain, contracts,
  content, docs, and tools were routed toward the canonical source spine.
- Strict layout/root/distribution/component validators pass.
- AIDE doctor/validate/test/selftest/tools/roots/repo pass.
- Smoke CTest and focused spine CTest pass.
- Remaining blockers are boundary validation and broad full CTest.

Next task:
`CANON-SPINE-BOUNDARY-01 - Repair Remaining Boundary Imports and Full Proof`

## PORTABILITY-MATRIX-01 Update

PORTABILITY-MATRIX-01 is a Foundation Lock contract task. It adds a provisional
portability matrix and validator, but does not alter the build graph, CMake
presets, CI, providers, renderers, runtime behavior, packages, or release
publication.

Foundation Lock next task: `FOUNDATION-CLOSEOUT-01`.
