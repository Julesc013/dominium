Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: X-2, X-3, AIDE extraction review
Replacement Target: later explicit XStack/AIDE inventory checkpoint or replacement artifact only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`

# XStack Inventory And Classification

## A. Purpose and Scope

This artifact is the authoritative X-1 inventory and classification ledger for the live XStack/AIDE-relevant subset of Dominium.

It exists because `X-0` froze what XStack means now, but later prompts still need a more operational fact base that answers:

- which concrete surfaces actually matter
- which surfaces are reusable versus Dominium-retained
- which surfaces are mature, partial, wrapper-only, or doctrinal
- which surfaces help the playable baseline now
- which surfaces should be deferred until after the baseline exists

This artifact is downstream of `X-0`.
It does not reopen the scope freeze.
It refines the frozen scope into a concrete multi-axis ledger for later contract extraction work.

This artifact must preserve the current repo reality:

- admissible `Ζ` doctrine/gating work is complete
- post-`Ζ` work is reconciliation/consolidation, not more internal `Ζ` expansion
- the immediate product priority remains the canonical repo-local playable baseline and repo stabilization
- XStack/AIDE work must narrow and classify existing surfaces rather than compete with the baseline path

Important current-state limit:

- there is still no repo-local `AIDE` implementation root
- `AIDE` appears here only as an extraction-status label, not as present implementation

## B. Classification Method

### Evidence Sources Used

Classification in this artifact is based on the following evidence types:

- binding canon and governance sources named above
- `X-0` scope-freeze artifacts
- post-`Ζ` closure and ultra audit artifacts
- direct inspection of live implementation roots under `tools/xstack/`, `appshell/`, `tools/validation/`, `validation/`, `tools/launcher/`, `tools/setup/`, `runtime/`, `release/`, `security/`, `server/`, and `client/`
- direct inspection of current entrypoint modules, READMEs, and CLI docstrings
- repo search evidence showing imports, cross-surface references, wrapper patterns, stub language, and generated-evidence roots

### How Maturity Was Judged

Maturity was judged conservatively using live repo evidence:

- `implemented_and_used`
  - the surface has real code and direct usage evidence from imports, audit-run entrypoints, or active orchestration
- `implemented_but_isolated`
  - the surface has real code but limited or example-style usage, or only narrow consumer reach
- `partial_or_incomplete`
  - the surface is real but blocked by known coupling, explicit TODOs, placeholder logic, or incomplete behavior
- `stub_wrapper_or_transitional`
  - the surface is primarily a wrapper, shim, or bridge around another stronger surface, even if it runs
- `doctrinal_or_planning_only`
  - the surface is documentation, catalog, policy, or planning only
- `unknown`
  - reserved for cases where repo evidence is insufficient; not used when stronger evidence exists

### How Portability Was Judged

Portability was judged against the `X-0` freeze, not against aspirations:

- a surface is only `portable_core` when the implementation is structurally generic and reusable without Dominium session/product-shell assumptions
- a surface is not portable merely because it lives under `tools/xstack/`
- a surface is not portable merely because older docs describe portability
- a surface remains Dominium-retained when bundle IDs, pack roots, release/trust behavior, local loopback assumptions, or product-shell wiring are baked in

### How "Used vs Isolated vs Partial vs Doctrinal" Was Judged

This ledger uses the following practical test:

- `used`
  - direct imports, audit-observed entrypoints, or policy wiring point to the surface
- `isolated`
  - the surface exists but is example-only, fixture-only, or not part of the main live command path
- `partial`
  - the surface is active but has coupling bugs, placeholder branches, or explicitly incomplete scope
- `doctrinal`
  - the surface is text or metadata used as guidance/fact base, not as runtime or tool behavior

### What `unclear_or_mixed` Means

`unclear_or_mixed` does not mean "unknown."

It means the surface has multiple real signals that should not be flattened into a single ownership story.
Typical reasons include:

- one part of the surface is generic while another part is repo-bound
- the surface is an integration bridge between XStack and broader Dominium systems
- current code and older docs point in different directions
- the surface is useful now but not cleanly portable or cleanly legacy

## C. Classification Axes

### Role Axis

| Role | Meaning now |
| --- | --- |
| `portable_core` | Narrow deterministic substrate with low direct Dominium/product coupling. |
| `runtime_concern` | Session, boot, SRZ, stage, or authoritative process/session control surfaces. |
| `ops_concern` | Gate, validation, audit, CI, orchestration, and repo-operation surfaces. |
| `dominium_only` | Product-shell, bundle, release, loopback, or repo-control surfaces that should remain in Dominium now. |
| `legacy_or_deprecate` | Older sibling, derived, or transitional surfaces that remain useful evidence but are not the current semantic center. |
| `unclear_or_mixed` | Mixed ownership, bridge, support, or evidence surfaces that should not be flattened into a simple portability claim. |

### Maturity Axis

| Maturity | Meaning now |
| --- | --- |
| `implemented_and_used` | Live code with direct usage evidence. |
| `implemented_but_isolated` | Real code, but example-only or narrowly consumed. |
| `partial_or_incomplete` | Real surface with coupling issues, placeholders, or incomplete behavior. |
| `stub_wrapper_or_transitional` | Wrapper, shim, or transitional surface rather than the strongest implementation layer. |
| `doctrinal_or_planning_only` | Documentation, task, policy, or planning surface only. |
| `unknown` | Evidence insufficient; avoided where stronger evidence exists. |

### Extraction Axis

| Extraction Status | Meaning now |
| --- | --- |
| `plausible_future_aide_extraction_candidate` | Strongest later extraction candidates once baseline and uncoupling work permit it. |
| `maybe_extractable_later` | Reusable shape exists, but current coupling or wrapper status is still too high. |
| `retain_in_dominium` | Keep this surface in Dominium for the current series and baseline period. |
| `defer_until_post_baseline` | Review again later, but do not treat as a current extraction target. |
| `explicitly_not_an_aide_target` | Do not use this surface as the basis for AIDE extraction. |

### Current Usage Status Terms

This ledger also uses a descriptive usage field:

- `wired_to_entrypoints`
- `active_tool_entrypoint`
- `active_product_shell`
- `active_wrapper`
- `baseline_support`
- `transitional_bridge`
- `fact_base_only`
- `fixture_or_generated_evidence`
- `isolated_example`

## D. Concrete Inventory Ledger

### `xinv.core_substrate`

- Name: XStack core planner, scheduler, and artifact substrate
- Repo Paths: `tools/xstack/core/plan.py`, `tools/xstack/core/scheduler.py`, `tools/xstack/core/runners.py`, `tools/xstack/core/runners_base.py`, `tools/xstack/core/impact_graph.py`, `tools/xstack/core/merkle_tree.py`, `tools/xstack/core/artifact_contract.py`, `tools/xstack/core/log.py`, `tools/xstack/core/profiler.py`, `tools/xstack/core/repo_health.py`
- Purpose: Deterministic planning, execution ordering, impact selection, artifact classification, and runner plumbing for XStack profile execution.
- Role: `portable_core`
- Maturity: `implemented_and_used`
- Extraction: `plausible_future_aide_extraction_candidate`
- Current Usage Status: `wired_to_entrypoints`
- Major Dependencies: `scripts/dev/gate.py`, `tools/xstack/run.py`, `tools/xstack/controlx/orchestrator.py`, docs that describe the incremental pipeline
- Evidence Notes: `scripts/dev/gate.py` imports `tools.xstack.core.execution_ledger`, `cache_store`, `plan`, `profiler`, `runners`, and `scheduler`; `docs/governance/XSTACK_INCREMENTAL_MODEL.md` and `docs/XSTACK.md` both name these files as the planner substrate.
- Recommended Treatment: Reuse and freeze the interface shape now; do not rename or extract yet.

### `xinv.compatx_contract_primitives`

- Name: Low-level CompatX contract primitives
- Repo Paths: `tools/xstack/compatx/canonical_json.py`, `tools/xstack/compatx/validator.py`, `tools/xstack/compatx/schema_registry.py`
- Purpose: Canonical JSON hashing, schema loading, and strict instance validation for multiple XStack-adjacent consumers.
- Role: `portable_core`
- Maturity: `implemented_and_used`
- Extraction: `plausible_future_aide_extraction_candidate`
- Current Usage Status: `wired_to_entrypoints`
- Major Dependencies: `validation/validation_engine.py`, `release/*.py`, `security/trust/*.py`, `appshell/**`, `server/server_boot.py`, `client/local_server/local_server_controller.py`
- Evidence Notes: direct imports appear in AppShell, release, security, server, runtime, and client surfaces; these helpers are the broadest reused XStack-adjacent substrate in the repo.
- Recommended Treatment: Treat as the strongest portable-contract candidate, but preserve current repo ownership until later extraction review.

### `xinv.compatx_profile_checks_and_versioning`

- Name: CompatX profile check surface and version routing
- Repo Paths: `tools/xstack/compatx/check.py`, `tools/xstack/compatx/versioning.py`, `tools/xstack/compatx/version_registry.json`, `tools/xstack/compatx/README.md`
- Purpose: Profile-scoped contract checking and schema-version routing on top of the low-level CompatX primitives.
- Role: `unclear_or_mixed`
- Maturity: `partial_or_incomplete`
- Extraction: `maybe_extractable_later`
- Current Usage Status: `active_tool_entrypoint`
- Major Dependencies: `tools/xstack/controlx/orchestrator.py`, `validation/validation_engine.py`, schema registry data
- Evidence Notes: `run_compatx_check()` is used in ControlX and validation; `versioning.py` still routes migrations to `migration_stub()` with refusal code `refuse.compatx.migration_not_implemented`; README explicitly says migration execution is currently a stub.
- Recommended Treatment: Reuse the check surface as evidence and keep the low-level primitives stable; defer any portability claim for migration behavior.

### `xinv.controlx_profile_orchestration`

- Name: Live XStack ControlX orchestration surface
- Repo Paths: `tools/xstack/run.py`, `tools/xstack/controlx/orchestrator.py`, `tools/xstack/controlx/types.py`, `tools/xstack/controlx/utils.py`, `tools/xstack/controlx/README.md`
- Purpose: Drive FAST/STRICT/FULL deterministic profile execution across CompatX, pack validation, registry compile, session smoke, RepoX, AuditX, TestX, PerformX, SecureX, packaging verification, and UI bind checks.
- Role: `ops_concern`
- Maturity: `implemented_and_used`
- Extraction: `maybe_extractable_later`
- Current Usage Status: `active_tool_entrypoint`
- Major Dependencies: nearly every live XStack family plus pack/registry/session subsystems
- Evidence Notes: `tools/xstack/run.py` is the stable XStack entrypoint; `orchestrator.py` imports and coordinates `auditx`, `compatx`, `pack_loader`, `registry_compile`, `performx`, `packagingx`, `repox`, `securex`, `sessionx`, `testx`, and `ui_bind`; audit entrypoints classify `xstack_run` as canonical and runnable now.
- Recommended Treatment: Treat as the live orchestration contract, not as portable core. Freeze semantics and outputs before any future extraction work.

### `xinv.gate_and_review_bridges`

- Name: Repo gate and review bridge scripts that materially consume XStack
- Repo Paths: `scripts/dev/gate.py`, `scripts/ci/check_repox_rules.py`, `tools/review/xi8_common.py`
- Purpose: Bridge repo-wide gate execution, review policies, and CI invariants onto XStack planning, cache, and rule surfaces.
- Role: `ops_concern`
- Maturity: `implemented_and_used`
- Extraction: `defer_until_post_baseline`
- Current Usage Status: `transitional_bridge`
- Major Dependencies: `tools/xstack/core/**`, `tools/xstack/repox/**`, `tools/xstack/sessionx/**`, `tools/xstack/compatx/**`, `tools/xstack/ci/**`
- Evidence Notes: `scripts/dev/gate.py` imports the XStack core planner and cache store; `scripts/ci/check_repox_rules.py` hardcodes many `tools/xstack/*` paths and includes `check_runtime_no_xstack_imports`; `tools/review/xi8_common.py` references `tools/xstack/ci/xstack_ci_entrypoint.py`.
- Recommended Treatment: Keep as XStack-adjacent bridge surfaces. Do not treat these repo scripts as portable AIDE ownership.

### `xinv.session_create_pipeline`

- Name: Session create and pipeline-contract materialization
- Repo Paths: `tools/xstack/session_create.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/pipeline_contract.py`
- Purpose: Create `session_spec.json`, `universe_identity.json`, `universe_state.json`, and pinned contract-bundle artifacts for the repo-local playable path.
- Role: `runtime_concern`
- Maturity: `implemented_and_used`
- Extraction: `retain_in_dominium`
- Current Usage Status: `baseline_support`
- Major Dependencies: `tools/xstack/registry_compile/**`, `tools/xstack/pack_loader/**`, `worldgen.core.pipeline`, `modding`, `universe`, registries under `data/registries/`
- Evidence Notes: the audit ran `python tools/xstack/session_create.py` successfully; `ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md` calls it canonical and part of the shortest path to a baseline session; `creator.py` directly depends on Dominium pack, worldgen, universe, geo, and profile surfaces.
- Recommended Treatment: Reuse now for baseline work. Keep ownership in Dominium.

### `xinv.session_boot_and_runtime_control`

- Name: Session boot, SRZ, runtime, and control machinery
- Repo Paths: `tools/xstack/session_boot.py`, `tools/xstack/session_control.py`, `tools/xstack/session_surface.py`, `tools/xstack/session_script_run.py`, `tools/xstack/session_server.py`, `tools/xstack/srz_status.py`, `tools/xstack/sessionx/runner.py`, `tools/xstack/sessionx/process_runtime.py`, `tools/xstack/sessionx/scheduler.py`, `tools/xstack/sessionx/session_control.py`, `tools/xstack/sessionx/stage_parity.py`, `tools/xstack/sessionx/common.py`, `tools/xstack/sessionx/README.md`
- Purpose: Boot session specs, drive headless/session control flows, run SRZ process execution, and coordinate session stage transitions.
- Role: `runtime_concern`
- Maturity: `partial_or_incomplete`
- Extraction: `retain_in_dominium`
- Current Usage Status: `wired_to_entrypoints`
- Major Dependencies: `net.policies.*`, `modding`, `universe`, `observation`, `render_model`, `reality.ledger`, `performance`, `inspection`, `core.*`, `logistics`, `materials`, many domain/runtime roots
- Evidence Notes: audit marks this family as `partial` and `wired_but_fragile`; `session_boot.py` works only reliably with canonical `saves/<save_id>` layout; `process_runtime.py` directly spans many authoritative runtime and domain modules, proving strong Dominium coupling.
- Recommended Treatment: Stabilize for local baseline flows only. Do not classify as current extraction material.

### `xinv.ui_bind_surface`

- Name: UI bind and descriptor-to-session host boundary
- Repo Paths: `tools/xstack/ui_bind.py`, `tools/xstack/sessionx/ui_host.py`
- Purpose: Validate UI window descriptors and bind them to session-host expectations and entitlements.
- Role: `unclear_or_mixed`
- Maturity: `implemented_and_used`
- Extraction: `maybe_extractable_later`
- Current Usage Status: `active_tool_entrypoint`
- Major Dependencies: `tools/xstack/compatx/validator.py`, `tools/xstack/sessionx/ui_host.py`, `build/registries/ui.registry.json`
- Evidence Notes: audit baselines repeatedly record passing `ui_bind` checks; `ui_bind.py` is a real validator, but it remains coupled to session-host semantics rather than being a purely generic UI contract layer.
- Recommended Treatment: Preserve as a boundary-check surface and revisit later. Do not promote it to portable core now.

### `xinv.testx_harness`

- Name: TestX deterministic harness and suite corpus
- Repo Paths: `tools/xstack/testx/runner.py`, `tools/xstack/testx/tests/**`, `tools/xstack/testx/README.md`, `tools/xstack/testx_all.py`
- Purpose: Run profile-aware deterministic test subsets and larger sweeps over XStack and adjacent runtime/control surfaces.
- Role: `ops_concern`
- Maturity: `implemented_and_used`
- Extraction: `maybe_extractable_later`
- Current Usage Status: `wired_to_entrypoints`
- Major Dependencies: `tools/dev/impact_graph`, `tools/governance/tool_semantic_impact.py`, `tools/xstack/testdata/**`, and many repo surfaces under test
- Evidence Notes: audit classifies `testx_all.py` as canonical and present; `ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md` groups validation, TestX, CTest, and playtest suites as `implemented_and_used`; `testx_all.py` itself is a convenience wrapper on the stronger `testx/runner.py`.
- Recommended Treatment: Reuse to gate baseline assembly. Defer any extraction discussion until the suite mix is better separated from Dominium-specific tests.

### `xinv.auditx_wrapper`

- Name: XStack AuditX wrapper
- Repo Paths: `tools/xstack/auditx/check.py`, `tools/xstack/auditx/README.md`
- Purpose: Run semantic and architecture drift scanning through the XStack profile runner.
- Role: `ops_concern`
- Maturity: `stub_wrapper_or_transitional`
- Extraction: `maybe_extractable_later`
- Current Usage Status: `active_wrapper`
- Major Dependencies: full AuditX implementation under `tools/audit` and `tools/auditx`
- Evidence Notes: `check.py` describes itself as an XStack wrapper for the full AuditX semantic scan pipeline; the wrapper is active, but the owning analyzer stack lives outside `tools/xstack/`.
- Recommended Treatment: Keep as a live wrapper surface. Do not mistake wrapper location for standalone platform ownership.

### `xinv.repox_wrapper`

- Name: XStack RepoX wrapper
- Repo Paths: `tools/xstack/repox/check.py`, `tools/xstack/repox/README.md`
- Purpose: Run deterministic policy and structure checks under XStack profiles.
- Role: `ops_concern`
- Maturity: `stub_wrapper_or_transitional`
- Extraction: `maybe_extractable_later`
- Current Usage Status: `active_wrapper`
- Major Dependencies: `tools/review/xi6_common.py`, `tools/review/xi8_common.py`, repo structure rules, path allowlists
- Evidence Notes: docstring labels it a minimal deterministic RepoX policy scan; scan roots and dependencies are heavily repo-specific; rule docs live under `docs/governance/REPOX_*`.
- Recommended Treatment: Preserve as an operational bridge and defer extraction claims.

### `xinv.securex_minimal`

- Name: SecureX minimal signature-status checks
- Repo Paths: `tools/xstack/securex/check.py`, `tools/xstack/securex/README.md`
- Purpose: Verify pack manifest signature-status metadata during XStack runs.
- Role: `ops_concern`
- Maturity: `implemented_and_used`
- Extraction: `maybe_extractable_later`
- Current Usage Status: `active_tool_entrypoint`
- Major Dependencies: `tools/xstack/pack_loader/loader.py`
- Evidence Notes: code performs real pack iteration and refusal/warn handling; README explicitly brands it as a minimal surface bound to pack signature-status checks.
- Recommended Treatment: Reuse as a narrow operational verifier, but keep it out of current extraction scope.

### `xinv.performx_placeholder`

- Name: PerformX placeholder budget/fidelity checks
- Repo Paths: `tools/xstack/performx/check.py`, `tools/xstack/performx/README.md`
- Purpose: Perform policy- and registry-based budget/fidelity smoke checks during profile runs.
- Role: `ops_concern`
- Maturity: `partial_or_incomplete`
- Extraction: `defer_until_post_baseline`
- Current Usage Status: `active_tool_entrypoint`
- Major Dependencies: `build/registries/*`, `schemas/session_spec.schema.json`, `packs/**`, `docs/contracts/**`
- Evidence Notes: the module docstring says `placeholder checks`; current logic is real but intentionally narrow and depends on build outputs and policy registries.
- Recommended Treatment: Treat as a live placeholder, not as extraction-ready infrastructure.

### `xinv.ci_guardrail_surface`

- Name: Xi-7/Xi-8 XStack CI guardrail surface
- Repo Paths: `tools/xstack/ci/xstack_ci_entrypoint.py`, `tools/xstack/ci/ci_common.py`, `tools/xstack/ci/profiles/*.json`, `docs/xstack/CI_GUARDRAILS.md`, `docs/xstack/ARCH_DRIFT_POLICY.md`, `data/xstack/gate_definitions.json`
- Purpose: Define CI guardrail entrypoints, rule catalogs, profiles, and support documentation for deterministic repo checks.
- Role: `ops_concern`
- Maturity: `implemented_and_used`
- Extraction: `maybe_extractable_later`
- Current Usage Status: `wired_to_entrypoints`
- Major Dependencies: RepoX, AuditX, TestX, docs, CI workflow policy, review helpers
- Evidence Notes: `xstack_ci_entrypoint.py` is a real runner; `data/xstack/gate_definitions.json` records required rules, profiles, and provisional allowances; docs and tests reference the entrypoint repeatedly.
- Recommended Treatment: Treat as live operator policy and CI wiring. It is reusable in shape, but still repo-specific in detail.

### `xinv.pack_registry_compile_pipeline`

- Name: Pack loading, contribution parsing, bundle selection, and registry compile pipeline
- Repo Paths: `tools/xstack/pack_loader/**`, `tools/xstack/pack_contrib/**`, `tools/xstack/registry_compile/**`, `tools/xstack/bundle_list.py`, `tools/xstack/bundle_validate.py`
- Purpose: Discover packs, parse contributions, select bundles, compile registries, and validate lockfile/registry outputs.
- Role: `dominium_only`
- Maturity: `implemented_and_used`
- Extraction: `retain_in_dominium`
- Current Usage Status: `wired_to_entrypoints`
- Major Dependencies: `packs/**`, `profiles/**`, `locks/**`, `build/registries/**`, `modding`, `tools/xstack/cache_store/**`
- Evidence Notes: ControlX orchestrator uses this family directly; `registry_compile/constants.py` bakes in `DEFAULT_BUNDLE_ID = "bundle.base.lab"` and a large Dominium registry vocabulary; README/output contracts are concrete and live.
- Recommended Treatment: Reuse as current repo control-plane/runtime substrate. Do not call it portable now.

### `xinv.packagingx_dist_layout`

- Name: PackagingX dist layout and packaging verification
- Repo Paths: `tools/xstack/packagingx/__init__.py`, `tools/xstack/packagingx/dist_build.py`, `tools/xstack/packagingx/README.md`
- Purpose: Build and validate deterministic dist layouts for launcher/setup/control-plane flows.
- Role: `dominium_only`
- Maturity: `implemented_and_used`
- Extraction: `retain_in_dominium`
- Current Usage Status: `transitional_bridge`
- Major Dependencies: `pack_loader`, `registry_compile`, `session_create`, `sessionx.runner`, `sessionx.script_runner`
- Evidence Notes: `dist_build.py` imports session creation, session boot, intent-script execution, and pack/registry compile helpers; `tools/setup/build.py` imports PackagingX directly.
- Recommended Treatment: Keep in Dominium. PackagingX is useful now, but it is too tied to the current release/dist layout to serve as present AIDE material.

### `xinv.validation_unified_surface`

- Name: Unified validation engine plus legacy adapters
- Repo Paths: `validation/validation_engine.py`, `tools/validation/tool_run_validation.py`, `tools/validation/validate_all_main.cpp`, `tools/validation/validator_common.*`, `tools/validation/validator_reports.*`, `tools/validation/validators_registry.*`
- Purpose: Provide a repo-wide validation entrypoint that aggregates XStack compat checks with broader legacy and product validation surfaces.
- Role: `unclear_or_mixed`
- Maturity: `implemented_and_used`
- Extraction: `retain_in_dominium`
- Current Usage Status: `active_adapter`
- Major Dependencies: many validation suites across compat, audit, install, identity, pack, save, release, and audit roots
- Evidence Notes: the engine imports `tools.xstack.compatx.*` and maps many `legacy.*` surfaces; audit classifies the validation stack as `implemented_and_used`; the live FAST entrypoint exists but the audit did not finish a clean full FAST run, and current local rerun can fail for external file-lock reasons.
- Recommended Treatment: Treat as repo validation infrastructure, not as XStack portable core.

### `xinv.launcher_setup_python_shells`

- Name: Python/AppShell launcher and setup command surfaces
- Repo Paths: `tools/launcher/launch.py`, `tools/launcher/launcher_cli.py`, `tools/setup/setup_cli.py`, `tools/setup/build.py`
- Purpose: Expose the strongest live repo-local shells for packs, profiles, compat status, install/update/trust operations, and local product supervision.
- Role: `dominium_only`
- Maturity: `implemented_and_used`
- Extraction: `retain_in_dominium`
- Current Usage Status: `active_product_shell`
- Major Dependencies: `appshell/**`, `release/**`, `security/trust/**`, `tools/xstack/sessionx/**`, `tools/xstack/packagingx/**`, `tools/xstack/registry_compile/constants.py`
- Evidence Notes: audit identifies `tools/launcher/launch.py` and `tools/setup/setup_cli.py` as canonical repo-local shells; both successfully ran compat-status, profiles list, and packs list.
- Recommended Treatment: Support the playable baseline with these surfaces now. Do not treat them as AIDE candidates.

### `xinv.compiled_launcher_setup_wrappers`

- Name: Compiled launcher and setup wrappers
- Repo Paths: `launcher/`, `setup/`, related generated UI stub files under `tools/launcher/ui/` and `tools/setup/ui/`
- Purpose: Native shells around stronger Python/AppShell flows.
- Role: `dominium_only`
- Maturity: `stub_wrapper_or_transitional`
- Extraction: `explicitly_not_an_aide_target`
- Current Usage Status: `active_wrapper`
- Major Dependencies: wrapper-local UI stubs, AppShell fallback flows, verify binaries
- Evidence Notes: audit marks both compiled shells as `partial` and `wired_but_fragile`; smoke output still reports stub status or limited control hooks; multiple `.h` and `.cpp` files are explicitly labeled as user action stubs.
- Recommended Treatment: Leave these as wrappers for now and keep baseline focus on the stronger Python surfaces.

### `xinv.appshell_shared_command_layer`

- Name: AppShell bootstrap, command, IPC, and supervisor layer
- Repo Paths: `appshell/**`
- Purpose: Shared repo-local command shell, compatibility negotiation, IPC, supervisor, TUI, and mode dispatch infrastructure used by launcher/setup and related product flows.
- Role: `dominium_only`
- Maturity: `implemented_and_used`
- Extraction: `retain_in_dominium`
- Current Usage Status: `active_product_shell`
- Major Dependencies: `compat`, `release`, `validation`, `tools`, `tools/setup/setup_cli.py`, `tools/launcher/launch.py`
- Evidence Notes: audit classifies AppShell as `implemented_and_used`; `bootstrap.py` and `product_bootstrap.py` are real shared infrastructure; however, `rendered_stub.py`, `tui_stub.py`, and several fallback paths prove that parts of AppShell still intentionally preserve stub behavior.
- Recommended Treatment: Keep AppShell Dominium-owned and baseline-relevant. Do not classify it as XStack portable core.

### `xinv.local_baseline_runtime_bridge`

- Name: Local singleplayer and authoritative loopback bridge surfaces
- Repo Paths: `server/server_boot.py`, `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/net/loopback_transport.py`
- Purpose: Materialize the local authoritative loopback flow that the playable baseline will rely on before external transport exists.
- Role: `dominium_only`
- Maturity: `partial_or_incomplete`
- Extraction: `retain_in_dominium`
- Current Usage Status: `baseline_support`
- Major Dependencies: `tools/xstack/sessionx/**`, `tools/xstack/compatx/**`, server/client loopback transport, release/profile inputs
- Evidence Notes: audit marks server boot and loopback transport as real implementation; reuse plan says `client/local_server/local_server_controller.py`, `server/net/loopback_transport.py`, and `runtime/process_spawn.py` should be reused immediately; direct controller invocation produced real handshake/compat payloads, but the public wrapper path remains unclear.
- Recommended Treatment: Reuse and stabilize only as part of the playable baseline path. Do not extract this bridge into AIDE.

### `xinv.release_and_trust_consumers`

- Name: Release and offline trust surfaces that consume XStack contract helpers
- Repo Paths: `release/archive_policy.py`, `release/build_id_engine.py`, `release/component_graph_resolver.py`, `release/release_manifest_engine.py`, `release/update_resolver.py`, `security/trust/trust_verifier.py`, `security/trust/license_capability.py`
- Purpose: Release manifesting, update resolution, archive policy, and trust verification for repo-local release/control-plane flows.
- Role: `dominium_only`
- Maturity: `implemented_and_used`
- Extraction: `retain_in_dominium`
- Current Usage Status: `wired_to_entrypoints`
- Major Dependencies: `tools/xstack/compatx/canonical_json.py`, release registries, trust registries, setup/launcher flows
- Evidence Notes: audit classifies release and security as `implemented_and_used`; these modules import XStack canonical JSON helpers directly, but their role remains release/trust control-plane work inside Dominium.
- Recommended Treatment: Reuse as current release/trust substrate. They are XStack-adjacent consumers, not XStack core.

### `xinv.legacy_controlx`

- Name: Legacy standalone ControlX root
- Repo Paths: `tools/controlx/**`, `tools/controlx/README.md`, `tools/controlx/controlx.py`
- Purpose: Older autonomous prompt/control-plane wrapper with sanitization, queue execution, and run logs.
- Role: `legacy_or_deprecate`
- Maturity: `implemented_but_isolated`
- Extraction: `defer_until_post_baseline`
- Current Usage Status: `transitional_bridge`
- Major Dependencies: `scripts/dev/gate.py`, `tools/controlx/core/**`, release/control-plane docs
- Evidence Notes: code is real and release docs still reference it, but `X-0` froze it as a sibling/transitional surface rather than the current branded XStack center; audit/review docs repeatedly describe it as a planning/review bridge.
- Recommended Treatment: Preserve as a transitional bridge and review later for convergence with `tools/xstack/controlx/`.

### `xinv.legacy_compatx`

- Name: Legacy standalone CompatX root
- Repo Paths: `tools/compatx/**`, `tools/compatx/README.md`, `tools/compatx/compatx.py`
- Purpose: Older compatibility CLI and semantic-contract tooling retained as an adapter bridge.
- Role: `legacy_or_deprecate`
- Maturity: `implemented_but_isolated`
- Extraction: `defer_until_post_baseline`
- Current Usage Status: `transitional_bridge`
- Major Dependencies: `tools/compatx/core/**`, validation inventory, semantic contract helpers
- Evidence Notes: `validation/validation_engine.py` still maps `tools/compatx/compatx.py` as `legacy.compatx_cli`; docs and audits show `tools/compatx/core/semantic_contract_validator.py` remains actively referenced as a bridge helper.
- Recommended Treatment: Keep as a live bridge and fact source until later convergence work explicitly resolves the split with `tools/xstack/compatx/`.

### `xinv.task_policy_and_catalog_docs`

- Name: Current XStack task/policy fact-base docs
- Repo Paths: `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`
- Purpose: Provide current governance/task taxonomy and X-0 scope boundaries for later prompts.
- Role: `unclear_or_mixed`
- Maturity: `doctrinal_or_planning_only`
- Extraction: `explicitly_not_an_aide_target`
- Current Usage Status: `fact_base_only`
- Major Dependencies: canon, AGENTS governance, planning docs
- Evidence Notes: these artifacts are binding or task-facing fact surfaces, not implementation; later prompts should consume them, not infer portability from them.
- Recommended Treatment: Use as the fact base for X-2 and X-3. Do not mistake them for implementation evidence.

### `xinv.legacy_xstack_reference_docs`

- Name: Older XStack governance and portability reference docs
- Repo Paths: `docs/XSTACK.md`, `docs/governance/XSTACK_PORTABILITY.md`, `docs/governance/XSTACK_INCREMENTAL_MODEL.md`, `docs/governance/XSTACK_EXTENSION_MODEL.md`, `docs/governance/XSTACK_PRODUCTION_CRITERIA.md`, `docs/governance/XSTACK_TEMPLATE_CHECKLIST.md`, `docs/governance/XSTACK_SCOPE_TEMPLATE.json`
- Purpose: Historical and derived reference surfaces describing portability, incremental execution, extension hooks, and production criteria.
- Role: `legacy_or_deprecate`
- Maturity: `doctrinal_or_planning_only`
- Extraction: `explicitly_not_an_aide_target`
- Current Usage Status: `fact_base_only`
- Major Dependencies: older governance mirrors and derived docs
- Evidence Notes: several files explicitly say they are only partially aligned; `X-0` already recorded that these docs overstate removability or portability relative to live code; `docs/XSTACK.md` still describes a more idealized gate stack than the live coupling supports.
- Recommended Treatment: Preserve as historical context only. Do not promote them over live implementation evidence or the X-0/X-1 canon.

### `xinv.support_examples_and_evidence_roots`

- Name: XStack support examples, skills, fixtures, cache split, and generated evidence roots
- Repo Paths: `tools/xstack/extensions/example_x/`, `tools/xstack/skills/*.md`, `tools/xstack/testdata/**`, `tools/xstack/cache_store/**`, `tools/xstack/out/**`
- Purpose: Carry example extension hooks, operator skill notes, deterministic fixtures, registry-compile cache helpers, and generated run evidence.
- Role: `unclear_or_mixed`
- Maturity: `implemented_but_isolated`
- Extraction: `explicitly_not_an_aide_target`
- Current Usage Status: `fixture_or_generated_evidence`
- Major Dependencies: `tools/xstack/registry_compile/compiler.py`, `tools/xstack/testx/tests/**`, docs and dist verification rules
- Evidence Notes: `extensions/example_x/extension.py` is a no-op example runner; `skills/*.md` are instruction surfaces; `testdata/**` is actively used by TestX and docs; `tools/xstack/cache_store/**` is a real registry-compile cache distinct from `tools/xstack/core/cache_store.py`; `tools/xstack/out/**` is generated evidence only and already treated by X-0 as non-owning.
- Recommended Treatment: Call these out explicitly so they are not mistaken for portable core or current extraction candidates.

## E. High-Value Reusable XStack Surfaces

The most reusable live surfaces now are:

- `tools/xstack/core/**`
  - Why it matters: this is the strongest deterministic planner/scheduler/artifact substrate currently in the repo
  - Current classification: `portable_core`
  - Extraction posture: plausible later AIDE candidate, but not authorized now
- `tools/xstack/compatx/canonical_json.py`, `validator.py`, and `schema_registry.py`
  - Why it matters: these helpers are already consumed by release, trust, appshell, validation, server, client, and runtime bridge code
  - Current classification: `portable_core`
  - Extraction posture: strongest contract-extraction candidate in the current repo
- `tools/xstack/controlx/**` plus `tools/xstack/run.py`
  - Why it matters: this is the live profile orchestration contract for XStack
  - Current classification: `ops_concern`
  - Extraction posture: maybe later, after baseline and interface freeze
- `tools/xstack/testx/**`
  - Why it matters: this is already the strongest deterministic test harness family inside XStack
  - Current classification: `ops_concern`
  - Extraction posture: maybe later, but currently mixed with Dominium-specific test inventory
- `tools/xstack/ci/**` plus `data/xstack/gate_definitions.json`
  - Why it matters: this is the cleanest current fact source for CI guardrail/profile metadata
  - Current classification: `ops_concern`
  - Extraction posture: maybe later, but still tightly tied to Dominium CI policy

The most reusable surfaces are not the same thing as the most portable-ready surfaces.
Current reuse is strongest in `core` and low-level `compatx`.
Current Dominium retention is still strongest in session/runtime, launcher/setup, AppShell, pack/registry compile, and release/trust glue.

## F. Legacy, Transitional, And Ambiguous Strata

### Legacy or Deprioritized Strata

- `tools/controlx/**`
  - still real, but no longer the semantic center of current XStack
- `tools/compatx/**`
  - still used as a bridge, but not the current branded CompatX center
- older XStack governance reference docs under `docs/XSTACK.md` and `docs/governance/XSTACK_*`
  - useful context, but not authoritative for current portability claims

### Transitional Bridges

- `scripts/dev/gate.py`
  - functionally part of the live control layer, but still repo-script bridge rather than standalone XStack platform code
- `validation/validation_engine.py`
  - active and important, but broader than XStack and explicitly wired to legacy adapters
- `tools/xstack/testx_all.py`
  - live convenience wrapper over the stronger runner
- `tools/xstack/auditx/check.py` and `tools/xstack/repox/check.py`
  - live wrappers over stronger non-`tools/xstack` analyzer and rule implementations

### Mixed Surfaces Needing Later Review

- `tools/xstack/ui_bind.py`
  - operationally useful and audited, but sits between runtime/session semantics and more reusable descriptor validation
- `tools/xstack/cache_store/**` versus `tools/xstack/core/cache_store.py`
  - both are real and used, but they serve different consumers and should not be collapsed by convenience
- `release/**` and `security/trust/**` importing `tools/xstack/compatx/canonical_json.py`
  - strong evidence of shared substrate reuse, but not evidence that release/trust become XStack-owned
- `appshell/**`
  - real product-shell infrastructure, but with intentional stub and fallback modes inside it

### Surfaces That Should Not Be Extracted Prematurely

- `tools/xstack/sessionx/**`
- `tools/xstack/session_boot.py`
- `appshell/**`
- `tools/launcher/launch.py`
- `tools/setup/setup_cli.py`
- `server/server_boot.py`
- `client/local_server/local_server_controller.py`
- `release/**` and `security/trust/**`

These are all too bound to current Dominium product, baseline, release, or runtime behavior to be treated as current AIDE material.

## G. In-Scope Support For The Playable Baseline

### XStack-Related Surfaces That Help The Baseline Now

- `tools/launcher/launch.py` and `tools/setup/setup_cli.py`
  - audit identifies these as canonical repo-local shells
- `appshell/**`
  - shared shell/supervisor/compat infrastructure beneath launcher and setup
- `tools/xstack/session_create.py`
  - shortest current path to a baseline session artifact set
- `tools/xstack/session_boot.py`
  - relevant to the baseline, but only reliable with canonical `saves/<save_id>` layout for now
- `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, and `server/net/loopback_transport.py`
  - strongest evidence-backed local authority bridge
- `tools/validation/tool_run_validation.py` and `tools/xstack/testx_all.py`
  - should gate baseline assembly after boot smoke and loopback stability improve

### Surfaces To Leave Alone For Now

- broad `tools/controlx/**` versus `tools/xstack/controlx/**` convergence
- older portability/governance docs except where future prompts explicitly target them
- broad pack/registry or release/control-plane extraction work
- compiled launcher/setup shell completion work
- `tools/xstack/out/**`, `.xstack_cache/**`, and other generated evidence roots as ownership candidates

The baseline path needs these surfaces to remain legible and stable, not renamed or platformized.

## H. Doctrine vs Implementation vs Extraction Distinction

This artifact makes the following distinctions non-optional:

- doctrinal similarity does not equal extraction readiness
- implementation existence does not equal portability
- current operational usefulness does not equal future AIDE ownership
- a wrapper that runs is still a wrapper
- a generated evidence root that is heavily referenced is still evidence, not an ownership surface
- a current Dominium-retained surface is not low value just because it is not portable

Later prompts must therefore use:

- `X-0` for scope truth
- `X-1` for classified inventory truth
- live code for implementation truth

They must not:

- substitute older portability prose for live repo evidence
- treat AIDE as already present
- claim that every XStack-named file belongs in a future extracted platform

## I. Anti-Patterns and Forbidden Shapes

The following misreadings are forbidden:

- treating every `tools/xstack/**` surface as portable core
- extracting session/runtime control just because it is under `tools/xstack/`
- promoting wrappers and stubs into "core" because they have stable command names
- treating launcher/setup/AppShell shells as current AIDE candidates
- using this inventory to justify immediate broad refactors, moves, or renames
- reading generated evidence roots such as `tools/xstack/out/**` as scope owners
- reading release/trust consumers as proof that XStack already owns the release control plane
- using future AIDE ambitions to compete with canonical playable-baseline work

## J. Stability and Evolution

Stability class: `stable`.

This artifact is intended to be the authoritative classification ledger for the current XStack/AIDE narrowing queue.

Later prompts expected to consume it:

- `X-2` portable contract extraction mapping
- `X-3` Codex/repo-operating contract formalization
- later post-baseline AIDE extraction review

The following changes require explicit follow-up rather than silent drift:

- changing role, maturity, or extraction classification for a ledger entry
- promoting a Dominium-retained surface into a future extraction candidate
- promoting a wrapper/transitional surface into "core"
- claiming current AIDE implementation presence
- changing which surfaces are baseline-supporting versus baseline-distracting

Current fact-base answer:

1. Live XStack/AIDE-relevant surfaces exist primarily under `tools/xstack/**`, with strong adjacent bridges in `scripts/dev/gate.py`, `validation/**`, `tools/launcher/**`, `tools/setup/**`, `appshell/**`, `server/server_boot.py`, `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `release/**`, and `security/trust/**`.
2. The strongest `portable_core` surfaces are `tools/xstack/core/**` and low-level `tools/xstack/compatx/**`.
3. The strongest `runtime_concern` surfaces are `session_create`, `session_boot`, and `tools/xstack/sessionx/**`.
4. The strongest `ops_concern` surfaces are `controlx`, `testx`, `auditx`, `repox`, `securex`, `performx`, and `ci`.
5. The strongest `dominium_only` surfaces are launcher/setup/AppShell, pack/registry compile, packaging, local loopback glue, and release/trust consumers.
6. The strongest `legacy_or_deprecate` surfaces are `tools/controlx/**`, `tools/compatx/**`, and older XStack portability docs.
7. The strongest later extraction fact base is now this artifact plus `X-0`, enabling `X-2` next.
