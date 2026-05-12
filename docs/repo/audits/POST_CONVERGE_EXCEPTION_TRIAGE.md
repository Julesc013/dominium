# POST-CONVERGE Exception Triage

## Status

- Task ID: POST-CONVERGE-00
- Source: `contracts/repo/layout_exceptions.toml`
- Active exception count: 37
- Inactive exception count: 0
- Unexcepted strict violation count: 0

## Exception Batches

### Batch 1 - Generated / Output Cleanup

| Exception ID | Path | Kind | Risk | Target | Likely Action | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `xstack_cache_root` | `.xstack_cache` | directory | review | ignored local cache or evidence review | inspect generated evidence, ignore or relocate policy-backed evidence | FAST writes here. Do not delete before provenance review. |
| `artifacts_root` | `artifacts` | directory | review | generated evidence or release/artifact policy exception | classify tracked evidence vs generated residue | Release-adjacent provenance may matter. |
| `build_root` | `build` | directory | low | ignored generated build output | remove/ignore after confirming no tracked source | Likely quick retire. |
| `dist_root` | `dist` | directory | medium | generated distribution output or explicit release exception | inspect for generated package output; preserve intentional release evidence | `dist/` is not source authority. |
| `out_root` | `out` | directory | low | ignored generated build output | remove/ignore after confirming no tracked source | Likely quick retire. |

### Batch 2 - Root Wrapper / Tooling / Governance Cleanup

| Exception ID | Path | Kind | Risk | Target | Likely Action | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `root_init_py` | `__init__.py` | file | medium | remove or allowlist after import review | search import assumptions, then remove or document | Root package marker can affect Python imports. |
| `tool_ui_bind_cmd` | `tool_ui_bind.cmd` | file | low | scripts or tools wrapper review | move wrapper or document allowed root file | Wrapper only if no external command expectation exists. |
| `tool_ui_doc_annotate_cmd` | `tool_ui_doc_annotate.cmd` | file | low | scripts or tools wrapper review | move wrapper or document allowed root file | Wrapper only if no external command expectation exists. |
| `tool_ui_validate_cmd` | `tool_ui_validate.cmd` | file | low | scripts or tools wrapper review | move wrapper or document allowed root file | Wrapper only if no external command expectation exists. |
| `governance_root` | `governance` | directory | review | docs/governance or generated mirror review | split docs/mirrors; preserve AGENTS authority | Must not compete with `AGENTS.md` or canon. |
| `ide_root` | `ide` | directory | review | tools/ide, cmake/ide, docs/ide, or generated projection review | classify projection outputs vs source templates | IDE projection material may be generated. |
| `labs_root` | `labs` | directory | review | archive, tools, docs, or experiment review | classify experiments; archive or document | Experiments are not canonical source roots. |
| `meta_root` | `meta` | directory | review | contracts, tools, docs, game, or archive split | inspect provenance/reference/implementation mix | Likely mixed. |
| `meta_extensions_engine_file` | `meta_extensions_engine.py` | file | review | game, engine, tools, or contracts review | inspect imports and ownership | Root-level engine-like module. |
| `numeric_discipline_file` | `numeric_discipline.py` | file | review | engine, contracts, tools, or docs review | inspect import surface and validator usage | Numeric doctrine can be semantic-sensitive. |
| `performance_root` | `performance` | directory | review | tools/performance or evidence review | split tools vs generated evidence | Avoid promoting benchmark output as source. |
| `validation_root` | `validation` | directory | review | tools, tests, contracts, or docs review | classify validators, fixtures, and reports | No new root validation authority. |

### Batch 3 - Content / Pack / Profile / Bundle Cleanup

| Exception ID | Path | Kind | Risk | Target | Likely Action | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `data_root` | `data` | directory | high | content, contracts, docs, tools, or evidence split | inspect subtrees and split by authority | Contains content, registries, mirrors, planning data, and evidence. |
| `packs_root` | `packs` | directory | high | content/packs plus contracts/packs and release review | preserve pack IDs and compatibility semantics | Do not move wholesale. |
| `profiles_root` | `profiles` | directory | medium | content/profiles or runtime-store projection review | classify authored profiles vs runtime state | Profiles may affect product/runtime identity. |
| `bundles_root` | `bundles` | directory | review | contracts/bundles, content, release, tests, or generated export review | classify source bundle descriptors vs generated exports | Distribution layout is separate from source layout. |
| `modding_root` | `modding` | directory | review | content/modding, contracts, docs, or tools review | split policy, docs, runtime helpers, and content | Current FAST failure touches mod policy code. |
| `models_root` | `models` | directory | review | content/models or generated output review | distinguish authored models from generated artifacts | No generated model authority. |
| `templates_root` | `templates` | directory | review | content/templates, contracts, tools, or generated projection review | classify templates by consumer | Templates may be source inputs or generated projections. |

### Batch 4 - Compat / Lib / Specs / Security / Update Cleanup

| Exception ID | Path | Kind | Risk | Target | Likely Action | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `compat_root` | `compat` | directory | high | contracts/compatibility plus runtime/tools split review | split pure contracts from implementation and shims | Do not move wholesale. |
| `lib_root` | `lib` | directory | review | engine, runtime, external, contracts, or tools review | classify by actual dependencies | Library roots are ambiguous. |
| `libs_root` | `libs` | directory | review | engine, runtime, external, contracts, or tools review | classify by actual dependencies | Library roots are ambiguous. |
| `locks_root` | `locks` | directory | high | contracts/locks, content/store-lock policy, or release lock review | separate lock schemas from concrete lock artifacts | Runtime mutable locks do not belong in contracts. |
| `repo_root` | `repo` | directory | high | contracts/repo, docs/repo, release, or tools split | inspect control-plane authority carefully | Do not add new layout authority here. |
| `safety_root` | `safety` | directory | high | contracts/safety, docs/safety, tools, or runtime policy | protected review required | Safety meaning must not drift. |
| `security_root` | `security` | directory | high | contracts/security, docs/security, release, tools, or runtime policy | protected review required | Trust/security semantics require review. |
| `specs_root` | `specs` | directory | high | contracts/specs, docs/specs, or semantic spec review | protected semantic review required | Reality specs retain established authority. |
| `updates_root` | `updates` | directory | high | release/update, contracts/distribution, or ops transaction review | inspect update identity and trust semantics | Do not change update identity. |

### Batch 5 - Core / Control / Net Ownership Review

| Exception ID | Path | Kind | Risk | Target | Likely Action | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `core_root` | `core` | directory | high | engine, game, runtime, contracts, or tools split review | classify actual source ownership before moving | May include universal primitives. |
| `control_root` | `control` | directory | high | runtime/control, contracts, game, or tools review | inspect process/control semantics | Preserve process-only mutation. |
| `net_root` | `net` | directory | high | runtime/network plus apps/server and contracts review | inspect transport/server/policy split | Preserve runtime and server behavior. |

### Other Exceptions

| Exception ID | Path | Kind | Risk | Target | Likely Action | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `missing_external_root` | `external` | directory | low | `external/` optionality or materialization review | either materialize empty canonical root by policy or mark optional in contract | This is a missing-root exception, not a present sprawl root. |

## Retirement Difficulty

| Category | Exceptions | Notes |
| --- | --- | --- |
| quick_retire | `build_root`, `out_root`, `tool_ui_bind_cmd`, `tool_ui_doc_annotate_cmd`, `tool_ui_validate_cmd` | Likely low-risk after reference/provenance checks. |
| low_risk_cleanup | `xstack_cache_root`, `artifacts_root`, `dist_root`, `missing_external_root`, `ide_root`, `performance_root`, `validation_root` | Needs policy decision or generated/evidence classification before retirement. |
| medium_review | `root_init_py`, `governance_root`, `labs_root`, `meta_root`, `meta_extensions_engine_file`, `numeric_discipline_file`, `profiles_root`, `bundles_root`, `models_root`, `templates_root`, `lib_root`, `libs_root` | Requires ownership/reference inspection but is not necessarily semantic-core. |
| high_risk_review | `data_root`, `packs_root`, `modding_root`, `compat_root`, `locks_root`, `repo_root`, `safety_root`, `security_root`, `specs_root`, `updates_root`, `core_root`, `control_root`, `net_root` | Protected or behavior-sensitive surfaces. |
| blocked | none | No exception is fully blocked, but several require protected review before physical cleanup. |

## Suggested Batch Order

1. Generated/output cleanup.
2. Root wrapper/tooling cleanup.
3. Content/pack/profile/bundle cleanup.
4. Compat/lib/spec/security cleanup.
5. Core/control/net ownership review.

## Risks

- Generated roots may contain provenance, evidence, or intentionally retained audit output.
- `data/`, `packs/`, and `profiles/` may contain identity-sensitive pack/profile content.
- `locks/` may contain deterministic pack/content locks, not only schemas.
- `security/`, `safety/`, and `specs/` require protected review.
- `core/`, `control/`, and `net/` may affect engine, runtime, server, authority, and process-only mutation semantics.

## Acceptance Criteria For Exception Retirement

An exception can be retired only when:

- the path is removed, moved, or explicitly allowed
- target location is correct
- validators pass in audit/json/strict modes
- no unexcepted root violation remains
- build/path references are updated if needed
- no semantic IDs changed
- no product, executable, install, package, virtual-root, or runtime identity changed
