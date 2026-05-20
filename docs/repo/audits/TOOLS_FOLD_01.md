Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none

# TOOLS-FOLD-01 Audit

Status: implemented with documented residual validator debt outside the tools fold.

## Starting State

- Branch: `main`
- Starting commit: `231c949b683553258af726da6c12f71512de6fcb`
- Preflight worktree: clean before this task.
- Source of truth: active tracked tree in this checkout.

## Task Scope

Fold broad first-level `tools/` roots into a compact role-based taxonomy:

- `tools/aide/`
- `tools/audit/`
- `tools/build/`
- `tools/codegen/`
- `tools/diagnostics/`
- `tools/domain/`
- `tools/export/`
- `tools/import/`
- `tools/migration/`
- `tools/package/`
- `tools/performance/`
- `tools/release/`
- `tools/repo/`
- `tools/test/`
- `tools/validators/`
- `tools/xstack/`

The task did not start broad docs, AIDE, runtime, schema, content, or feature work.

## Paths Inspected

Inspected active first-level roots under `tools/`, with special attention to:

- broad buckets: `tools/_shared/`, `tools/lib/`, `tools/share/`, `tools/core/`, `tools/tests/`
- app/runtime-like buckets: `tools/appshell/`, `tools/gui/`, `tools/net/`, `tools/server/`, `tools/setup/`, `tools/launcher/`, `tools/engine/`
- validator aliases: `tools/validate/`, `tools/validation/`, `tools/validator/`, `tools/*_validate/`
- codegen aliases: `tools/ui_bind/`, `tools/*_compile/`, `tools/*_gen/`
- user-facing modules: `tools/inspect/`, `tools/launcher_edit/`, `tools/net_inspector/`, `tools/observability/`, `tools/gui/`
- domain roots: `tools/animal/`, `tools/astro/`, `tools/chem/`, `tools/electric/`, `tools/fluid/`, `tools/geology/`, `tools/materials/`, `tools/physics/`, `tools/system/`, `tools/worldgen/`, and related domain roots

Also inspected active references in `.github/`, `apps/`, `contracts/`, `engine/`, `game/`, `release/`, `runtime/`, `scripts/`, `tests/`, `tools/`, and root CMake files.

## Classification Decisions

- Validators and validation probes moved under `tools/validators/<area>/`.
- Code generators moved under `tools/codegen/<area>/`.
- Repo, governance, audit, and migration helpers moved under `tools/repo/`, `tools/audit/`, or `tools/migration/`.
- Build/release/package helpers moved under `tools/build/`, `tools/release/`, or `tools/package/`.
- Noninteractive domain tools moved under `tools/domain/<canonical-domain>/`.
- User-facing editors/viewers/inspectors moved to Workbench modules under `apps/workbench/module/`.
- Test harnesses and smoke helpers moved under `tools/test/<area>/` when they remained tool-owned test machinery.
- Shell/AppShell validation and replay helpers moved to `tools/validators/shell/`; command documentation generation moved to `tools/codegen/shell/`.

## Files And Directories Moved

Representative `git mv` route groups:

- `tools/_shared/` and `tools/tools_host_main.c` -> `tools/build/host/`
- `tools/coredata_compile/` -> `tools/codegen/content/coredata_compile/`
- `tools/coredata_validate/` and `tools/data_validate/` -> `tools/validators/content/`
- `tools/assetc/` and generator roots -> `tools/codegen/`
- `tools/engine/`, `tools/ci/`, `tools/modcheck/`, `tools/security/` -> `tools/validators/`
- `tools/appshell/` -> `tools/validators/shell/`, except command-doc generation -> `tools/codegen/shell/`
- `tools/setup/` -> `tools/package/setup/`
- `tools/launcher/` -> `tools/package/launcher/`
- `tools/pack/`, `tools/modpack/`, `tools/mod_builder/`, `tools/compat/`, `tools/artifactmeta/`, and package distribution helpers -> `tools/package/`
- `tools/meta/`, `tools/governance/`, `tools/control/`, `tools/dev/`, `tools/workspace/`, `tools/models/`, `tools/specs/` -> `tools/repo/`
- `tools/review/` and `tools/coverage/` -> `tools/audit/`
- `tools/convergence/`, `tools/schema_migration/`, and import bridge helpers -> `tools/migration/`
- `tools/worldgen/`, `tools/worldgen_offline/`, `tools/chem/`, `tools/astro/`, `tools/fluid/`, `tools/electric/`, `tools/materials/`, `tools/system/`, and related domain roots -> `tools/domain/`
- `tools/gui/`, `tools/inspect/`, `tools/launcher_edit/`, `tools/net_inspector/`, `tools/observability/` -> `apps/workbench/module/`

Active references were updated in CMake files, C/C++ includes, Python imports, command wrappers, tests, RepoX rulesets, planning path maps, and generated-current architecture registries.

## Retained Tools Roots

Retained first-level tracked `tools/` roots are:

`aide`, `audit`, `build`, `codegen`, `diagnostics`, `domain`, `export`, `import`, `migration`, `package`, `performance`, `release`, `repo`, `test`, `validators`, and `xstack`.

`diagnostics` and `performance` are retained as optional role roots because the contents are noninteractive diagnostic and performance tooling. `domain` is retained for noninteractive domain-specific tooling, not domain implementation.

No active tracked `tools/core`, `tools/lib`, `tools/share`, `tools/gui`, `tools/render`, `tools/net`, `tools/network`, `tools/server`, `tools/setup`, `tools/launcher`, `tools/engine`, `tools/runtime`, `tools/validate`, `tools/validation`, or `tools/validator` roots remain.

## Generated And Historical References

Updated generated-current evidence where active validators consume it:

- architecture bootstrap outputs under `archive/generated/architecture/`, `archive/generated/audit/`, `contracts/registry/architecture/`, and generated audit reports
- Xi6/module-registry evidence where the generator writes active module state

Skipped stale historical/generated prose references when they are evidence snapshots or historical reports, including old references in `docs/archive/audit/TOOL_SURFACE_MAP.md`, duplicate/quarantine reports under `docs/archive/refactor/`, and other superseded audit reports. Migration maps intentionally retain old source paths as old-to-new route aliases.

## Validator Changes

Added `tools/validators/repo/check_tools_taxonomy.py` and CTest coverage for:

- self-test fixtures proving forbidden roots fail
- active tracked tree validation
- exact path reporting with suggested canonical owners

The validator permits only the compact role roots above and finite historical/alias references outside physical active roots.

## Validation Results

Passed:

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate` with pre-existing warnings about a missing review ref and stale repo-map source snapshot hash
- `python tools/validators/repo/check_tools_taxonomy.py --self-test`
- `python tools/validators/repo/check_tools_taxonomy.py --repo-root . --strict`
- focused stale active-reference sweep for forbidden first-level tools roots; remaining hits are route aliases, migration maps, or validator self-test fixtures
- `python tools/audit/review/tool_run_architecture_graph_bootstrap.py --repo-root .` -> complete, module_count `2210`, build_target_count `471`, include_edge_count `40376`, symbol_count `49252`, architecture_fingerprint `a782941867ca278567d339a6dfc7b4301d9c1c1ce99040233326fa852a17cff4`
- `python tools/audit/review/tool_run_xi6.py --repo-root . --write-only` -> blocked with `gate_failures=0`, `single_engine_findings=11`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --subset test_module_registry_deterministic,test_xi5x2_source_pocket_policy_valid`
- `ctest --preset verify -R "dominium_tools_taxonomy|tools_taxonomy|smoke|Smoke" --output-on-failure`
- `cmake --preset verify`
- `cmake --build --preset verify --target ALL_BUILD`

Known residual failures not caused by the tools fold:

- `python scripts/ci/check_repox_rules.py` still fails on broad pre-existing repo/state issues such as missing legacy product registry data, invalid `repo/canon_state.json`, stale doc status headers, missing dist/bin artifacts, worldgen baseline drift, and tool-version hash mismatches. Old physical `tools/` root failures from this task were removed.
- Direct RepoX FAST still reports broad structure and release/build artifact debt outside this fold, plus pre-existing runtime probe findings.
- A broader TestX subset including `test_tick_type_64bit_enforced` still reports the pre-existing mixed-width tick violation at `server/runtime/tick_loop.py`.

## Remaining Follow-Up Work

- Refresh historical/generated audit surfaces if a later docs/archive/audit regeneration task wants old `tools/*` prose snapshots rewritten.
- Resolve unrelated RepoX FAST failures and Xi6 single-engine findings in their own scoped tasks.
- Retire old route aliases in migration helpers only after downstream consumers no longer need source-path mapping evidence.
