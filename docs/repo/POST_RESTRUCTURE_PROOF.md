Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Post-Restructure Proof

Latest proof state: PARTIAL after `MOVE-SCRIPT-00`, `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS`, `TEST-PERF-01`, NAME-00 naming-law follow-up, Foundation Lock proof tiers, public surface registry, API/ABI canon, LANGUAGE-BASELINE-01, DEPENDENCY-DIRECTION-01, COMMAND-SURFACE-01, DIAGNOSTIC-CODE-REGISTRY-01, ARTIFACT-IDENTITY-LAW-01, SCHEMA-PROTOCOL-LAW-01, CAPABILITY-REFUSAL-LAW-01, PROVIDER-MODEL-01, and MODULE-COMPOSITION-LAW-01.

## MODULE-COMPOSITION-LAW-01 Proof Note

MODULE-COMPOSITION-LAW-01 adds the provisional module/workspace/app composition
law.

- module law: `contracts/module/module_surface.contract.toml`.
- module schema: `contracts/module/module.schema.json`.
- Workbench workspace schema: `contracts/workbench/workspace.schema.json`.
- app descriptor schema: `contracts/app/app_descriptor.schema.json`.
- validators:
  - `python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict`.
  - `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict`.
  - `python tools/validators/contracts/check_app_descriptors.py --repo-root . --strict`.
- fixtures: `tests/contract/module/**`, `tests/contract/workbench/**`, and `tests/contract/app/**`.
- module kinds registered: 12.
- public surface, diagnostics, and capability registries updated with module,
  Workbench, and app surfaces/codes/capabilities.
- runtime module loading, Workbench UI, App Composer, pack runtime, and provider
  runtime are not implemented by this task.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `REPLACEMENT-PROTOCOL-01`.

## PROVIDER-MODEL-01 Proof Note

PROVIDER-MODEL-01 adds the provisional provider model law.

- contract: `contracts/provider/provider.contract.toml`.
- registry: `contracts/provider/provider.registry.json`.
- descriptor schema: `contracts/provider/provider_descriptor.schema.json`.
- selection schemas: `contracts/provider/provider_selection_request.schema.json`
  and `contracts/provider/provider_selection_decision.schema.json`.
- validator: `python tools/validators/contracts/check_provider_model.py --repo-root . --strict`.
- fixtures: `tests/contract/provider/**`.
- provider descriptors registered: 5.
- provider kinds registered: 15.
- lifecycle states registered: 9.
- inventory: 17,865 tracked files scanned; 1,396 provider/backend/service/
  adapter/capability candidates classified descriptively.
- public surface, diagnostics, refusal, and capability registries updated with
  provider surfaces, codes, and cross-references.
- runtime provider resolution, dynamic loading, and renderer/platform fallback
  are not implemented by this task.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `MODULE-COMPOSITION-LAW-01`.

## CAPABILITY-REFUSAL-LAW-01 Proof Note

CAPABILITY-REFUSAL-LAW-01 adds the provisional capability/refusal law.

- contract: `contracts/capability/capability.contract.toml`.
- registry: `contracts/capability/capability.registry.json`.
- refusal policy: `contracts/refusal/refusal.contract.toml`.
- validator: `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict`.
- fixtures: `tests/contract/capability_refusal/**`.
- capabilities registered: 9.
- refusal codes registered: 13.
- inventory: 17,837 tracked files scanned; 1,190 capability/refusal/provider/trust
  candidates classified descriptively.
- public surface, command, and diagnostic registries updated with
  capability/refusal surfaces and codes.
- runtime capability resolution and provider selection are not implemented by
  this task.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `PROVIDER-MODEL-01`.

## SCHEMA-PROTOCOL-LAW-01 Proof Note

SCHEMA-PROTOCOL-LAW-01 adds the provisional schema/protocol/registry evolution
law.

- schema law: `contracts/schema/schema_evolution.contract.toml`.
- protocol law: `contracts/protocol/protocol_evolution.contract.toml`.
- registry law: `contracts/registry/registry_evolution.contract.toml`.
- canonical serialization: `contracts/serialization/canonical_serialization.contract.toml`.
- migration policy: `contracts/migration/migration_policy.contract.toml`.
- validator: `python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --strict`.
- fixtures: `tests/contract/schema_protocol/**`.
- inventory: 17,808 tracked files scanned; 2,489 schema/protocol-like files
  classified descriptively.
- public surface and diagnostic registries updated with schema/protocol
  surfaces/codes.
- existing schemas and registries are not migrated by this task.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `CAPABILITY-REFUSAL-LAW-01`.

## ARTIFACT-IDENTITY-LAW-01 Proof Note

ARTIFACT-IDENTITY-LAW-01 adds the provisional artifact identity law.

- contract: `contracts/artifact/artifact_identity.contract.toml`.
- validator: `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict`.
- artifact kinds registered: 23.
- lifecycle states registered: 11.
- fixtures: `tests/contract/artifact_identity/**`.
- inventory: 17,782 tracked files scanned; 1,890 artifact-like files classified
  descriptively.
- public surface and diagnostic registries updated with artifact surfaces/codes.
- existing artifacts are not migrated by this task.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `SCHEMA-PROTOCOL-LAW-01`.

## DIAGNOSTIC-CODE-REGISTRY-01 Proof Note

DIAGNOSTIC-CODE-REGISTRY-01 adds the provisional diagnostic/evidence registry.

- registry: `contracts/diagnostics/diagnostic_code.registry.json`.
- validator: `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`.
- diagnostic codes registered: 14 provisional foundational codes.
- severities registered: 7.
- categories registered: 26.
- fixtures: `tests/contract/diagnostics/**`.
- public surface registry updated with diagnostics, evidence reference, event
  schema, validator, and fixture surfaces.
- runtime diagnostic dispatch, Workbench presentation, and release publication
  are not implemented by this task.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `ARTIFACT-IDENTITY-LAW-01`.

## COMMAND-SURFACE-01 Proof Note

COMMAND-SURFACE-01 adds the provisional command/result/view/event/refusal/evidence
spine.

- contract: `contracts/command/command_surface.contract.toml`.
- validator: `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`.
- commands registered: 5 provisional foundational validation/test commands.
- refusal codes registered: 5 command-level scaffold codes.
- fixtures: `tests/contract/command_surface/**`.
- public surface registry updated with command, result, view, event, refusal,
  document, evidence, validator, and fixture surfaces.
- runtime dispatch, Workbench UI, product behavior, and the full diagnostic
  registry are not implemented by this task.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `DIAGNOSTIC-CODE-REGISTRY-01`.

## DEPENDENCY-DIRECTION-01 Proof Note

DEPENDENCY-DIRECTION-01 adds the provisional repository dependency-direction law
and validator.

- contract: `contracts/repo/dependency_directions.contract.toml`.
- validator: `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict`.
- initial scan: 16,104 tracked text/source files across 14 roots.
- strict result: PARTIAL because the current repo has 358 high-confidence active
  dependency-direction violations, primarily active Python imports from
  `apps/`, `engine/`, `game/`, and `runtime/` into `tools/`.
- warning result: 38 unlisted active dependencies, including current
  game/runtime cross-dependencies and Workbench content schema includes.
- exceptions active: 0; no broad exception was added to hide the debt.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `COMMAND-SURFACE-01`.

## LANGUAGE-BASELINE-01 Proof Note

LANGUAGE-BASELINE-01 moves the active mainline language floor to C17 + C++17
while keeping public ABI C-compatible.

- contract: `contracts/build/language_baseline.contract.toml`
- validators:
  - `python tools/validators/build/check_language_baseline.py --repo-root . --strict`
  - `python tools/validators/build/check_cpp17_forbidden_library_use.py --repo-root . --strict`
- active CMake and verify presets now use C17/C++17.
- C++17 restricted library validator passes with 1,192 files checked and 0 findings.
- fast strict: PASS, 32/32 commands, 318.25 seconds.
- full CTest remains T4 full/release proof and was not rerun.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `DEPENDENCY-DIRECTION-01`.

## API-ABI-CANON-01 Proof Note

API-ABI-CANON-01 adds provisional public API/ABI law and a public-header
validator.

- contracts: `contracts/abi/c_api.contract.toml` and `contracts/abi/language_boundary.contract.toml`.
- validator: `python tools/validators/abi/check_public_headers.py --repo-root . --strict`.
- fixtures: `tests/contract/public_headers/**`.
- public header candidates inspected: 375.
- high-confidence violations: 0.
- warning findings: 2,851, all blocking stable/frozen promotion until disposition.
- public surface registry updated with ABI canon surfaces and public-header fixture suite.
- no header or symbol is promoted to frozen ABI by this task.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `DEPENDENCY-DIRECTION-01`.

## PUBLIC-SURFACE-REGISTRY-01 Proof Note

PUBLIC-SURFACE-REGISTRY-01 adds a provisional public surface registry and
validator.

- registry: `contracts/public_surface/public_surface.contract.toml`
- validator: `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- initial surfaces: 20.
- stable surfaces: 2, limited to repo layout and root allowlist contracts.
- fast strict: PASS, 30/30 commands, 299.828 seconds.
- unproven headers, schemas, package formats, release surfaces, and Workbench
  modules remain provisional or internal.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `API-ABI-CANON-01`.

## FAST-STRICT-TEST-TIER-01 Proof Note

FAST-STRICT-TEST-TIER-01 adds the normal development gate:

- `fast_strict` = T0 + T1 + T2.
- command: `python tools/test/run_fast_strict.py --repo-root .`
- latest result: PASS, 30/30 commands, 332.828 seconds.
- T3 product/projection proof remains task-dependent.
- T4 full/release proof still owns full CTest and known broad debt.

Feature implementation and DOE-00 remain blocked until Foundation Lock closes.
Next task: `PUBLIC-SURFACE-REGISTRY-01`.

## Passing Proof Surfaces

- AIDE doctor/validate/test/selftest/tools/roots/repo.
- Strict layout/root/distribution/component validators.
- Supplemental docs/build/UI/ABI checks.
- Focused RepoX.
- Smoke CTest.
- Fast CTest label.
- Semantic lint CTest lanes.
- AuditX slow shard.
- Native configure and build-only `ALL_BUILD`.
- Product boot matrix strict smoke.
- Portable projection strict validation.
- Internal pilot release strict validation.
- Frozen contract hash guard.
- Override policy tests.
- Replay hash invariance.

## Remaining Blockers

- Full CTest is not green.
- 23 formerly bad roots remain under active exceptions with 1,765 tracked files in the current `git ls-files` dry-run router inventory.
- MOVE-SCRIPT-00 produced 1,593 route candidates, 172 skipped/deferred files, and 0 target collisions without applying moves.
- AuditX CTest wall-time is now partitioned into explicit `audit`/`auditx`/`slow`/`nightly` shards with 1200 second timeout.
- Large file-quality ledger storage policy remains unresolved.
- Naming conflicts are classified by NAME-00, but no naming migration has been applied.

## Rerun Commands

```powershell
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
py -3 .aide/scripts/aide_lite.py test
py -3 .aide/scripts/aide_lite.py selftest
py -3 .aide/scripts/aide_lite.py tools validate
py -3 .aide/scripts/aide_lite.py roots validate
py -3 .aide/scripts/aide_lite.py repo validate
python tools/validators/check_repo_layout.py --repo-root . --strict
python tools/validators/check_root_allowlist.py --repo-root . --strict
python tools/validators/check_distribution_layout.py --repo-root . --strict
python tools/validators/check_component_matrices.py --repo-root . --strict
python tools/validators/repo/check_no_src_source_dirs.py --repo-root .
python tools/validators/repo/check_path_terms.py --repo-root .
python tools/validators/repo/check_directory_naming.py --repo-root .
python tools/validators/repo/check_file_naming.py --repo-root .
python tools/migration/route_bad_roots.py --repo-root . --dry-run --rules tools/migration/bad_root_routing_rules.json --json-out .aide/reports/MOVE-SCRIPT-00-routing-preview.json --md-out .aide/reports/MOVE-SCRIPT-00-routing-preview.md --skipped-out .aide/reports/MOVE-SCRIPT-00-skipped-ledger.json --root-summary-out .aide/reports/MOVE-SCRIPT-00-root-summary.json --batch-plan-out .aide/reports/MOVE-SCRIPT-00-batch-plan.json --fail-on-collision
ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300
ctest --preset verify -R "slice0_hardcoded_ids|slice1_hardcoded_constants" --output-on-failure --timeout 300
ctest --preset verify -L smoke --output-on-failure --timeout 300
ctest --preset verify -L fast --output-on-failure --timeout 300
ctest --preset verify -L audit --output-on-failure --timeout 1200
ctest --preset verify -L slow --output-on-failure --timeout 1200
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
python tools/validators/check_product_boot_matrix.py --repo-root . --json --strict --run-smoke --timeout 30
python tools/validators/check_portable_projection.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --json --strict
python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --json --strict
```

## Readiness

DOE-00 is not authorized. Feature implementation remains blocked.

Next task: `MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`.

## Semantic Lint Proof Note

POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS reproduced 1,104 hardcoded identifier/constant findings and classified every finding before allowing it. The focused lanes now pass through exact-match allowlist entries keyed by test, file, line, validator message, and source-line hash. No broad suppressions were added.

## NAME-00 Naming Proof Note

NAME-00 locks naming law and produces warning-only conflict evidence. It does not make current excepted bad roots clean, and it does not authorize `runtime/appshell -> runtime/shell`, `game/domains -> game/domain`, or contract-category singularization. Those are planned future migrations requiring reviewed scope.

NAME-00 redo at `148a9adf95bb678da16784434221c568f7bb96cb` refreshes the evidence after MOVE-SCRIPT-00:

- NAME-00 blockers: 0.
- no `src`/`source`/`sources` directory findings: 106 total, 13 warnings, 0 blockers.
- forbidden path-term findings: 1,450 total, 78 warnings, 0 blockers.
- directory naming findings: 418 total, 39 warnings, 0 blockers.
- file naming findings: 5,361 total, 4,307 warnings, 0 blockers.
- language ownership finding classes: 4 warnings, 0 blockers.

The redo did not move, delete, rename, rewrite, shim, retire exceptions, or alter behavior. Feature work and DOE-00 remain blocked.

## MOVE-SCRIPT-00 Routing Proof Note

MOVE-SCRIPT-00 added a deterministic dry-run router and rule file for the 23 former bad roots. It scans tracked files through `git ls-files`, produces sorted route and skipped ledgers, detects target collisions, and emits batch plans for the deferred MOVE-BULK B-G cleanup. The task did not move, delete, rename, rewrite, shim, or retire exceptions.

The router result is `PASS_WITH_WARNINGS`: 1,593 route candidates are available for later gate review, and 172 files remain deferred for import, identity, authority, ABI/build, or naming-risk reasons.

## MOVE-ROUTER-00 Routing Proof Note

MOVE-ROUTER-00 supersedes the MOVE-SCRIPT skipped/deferred posture as the
active routing path. The router now routes every tracked file under former bad
roots: known files to canonical owners and unknown or ambiguous files to
`archive/quarantine/<root>/`.

Current dry-run result:

- Bad-root tracked files: 1,765.
- Routed files: 1,765.
- Known canonical routes: 1,694.
- Quarantine routes: 71.
- Target collisions: 0.
- Skipped/impossible routes: 0.
- Moves, deletes, renames, rewrites, shims, and exception retirements: 0.

Feature work and DOE-00 remain blocked. Next structural task:
`MOVE-ROUTER-01 - Apply Deterministic Bad-Root Router Safe Subset`.

## MOVE-ROUTER-01 Apply Proof Note

MOVE-ROUTER-01 physically moved every tracked file under the configured former
bad roots.

- Bad-root tracked files before: 1,765.
- Bad-root tracked files after: 0.
- Files moved: 1,765.
- Semantic moves: 1,694.
- Quarantine moves: 71.
- Skipped moves: 0.
- Target collisions: 0.
- Active root exceptions retired: 23.

This is not full recovery proof. Reference/import/build repair remains assigned
to `MOVE-ROUTER-02`, and feature work plus DOE-00 remain blocked.

## MOVE-ROUTER-02 Repair Proof Note

MOVE-ROUTER-02 closed as PARTIAL. It repaired the first active path/import/build
layer after MOVE-ROUTER-01 while preserving the routed root cleanup.

- Bad-root tracked files after repair: 0.
- Exact path replacements recorded: 33,316.
- Import replacements recorded: 76.
- Runtime control shim packages created: 3.
- CMake configure: PASS.
- Build: PARTIAL; 57/57 integrated fast/smoke tests passed before broader TestX failed.
- Broader TestX: FAIL, 140 of 344 lanes failed.
- Strict repo/root layout validators: PASS at this boundary.

This is not final proof. Remaining blockers are assigned to
`MOVE-ROUTER-02R - Finish Registry, Ruleset, Import, and Test Path Repair After Routing`.

## CANON-SPINE-NEW Proof Note

CANON-SPINE-NEW completed the structural second-level source-spine cleanup after
MOVE-ROUTER-02.

- Former bad roots remain empty: 0 tracked files.
- Root-level generated/local roots remain untracked.
- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- Strict repo/root/distribution/component validators: PASS.
- Smoke CTest: PASS.
- CMake configure: PASS.
- Boundary validation: not green; remaining warnings are documented in
  `.aide/reports/CANON-SPINE-NEW-blockers.md`.

This is not final green proof. Feature work and DOE-00 remain blocked until the
boundary repair and full proof pass.
