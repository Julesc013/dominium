Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: X-9 closure audit, post-baseline extraction checkpoints
Replacement Target: later explicit XStack/AIDE extraction-review checkpoint or approved spinout checkpoint only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `data/audit/ultra_repo_audit_system_inventory.json`, `data/audit/ultra_repo_audit_reuse_plan.json`, `data/audit/ultra_repo_audit_product_assembly_plan.json`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`, `docs/xstack/XSTACK_INVENTORY_AND_CLASSIFICATION.md`, `data/xstack/xstack_inventory_and_classification.json`, `docs/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`, `data/xstack/aide_portable_task_contract.json`, `docs/xstack/AIDE_EVIDENCE_AND_REVIEW_CONTRACT.md`, `data/xstack/aide_evidence_and_review_contract.json`, `docs/xstack/AIDE_POLICY_AND_PERMISSION_SHAPE.md`, `data/xstack/aide_policy_and_permission_shape.json`, `docs/xstack/AIDE_CAPABILITY_PROFILE_SHAPE.md`, `data/xstack/aide_capability_profile_shape.json`, `docs/xstack/AIDE_ADAPTER_CONTRACT.md`, `data/xstack/aide_adapter_contract.json`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`, `data/xstack/codex_repo_operating_contract.json`, `tools/xstack/compatx/README.md`, `tools/xstack/controlx/README.md`, `tools/xstack/sessionx/README.md`, `tools/xstack/testx/README.md`, `tools/xstack/compatx/versioning.py`, `tools/xstack/compatx/profile_checks.py`, `tools/xstack/controlx/orchestrator.py`, `tools/xstack/securex/check.py`, `tools/xstack/sessionx/runner.py`, `tools/xstack/testx/runner.py`, `appshell/compat_adapter.py`, `appshell/pack_verifier_adapter.py`, `tools/tool_surface_adapter.py`, `tools/import_bridge.py`, `tools/controlx/core/remediation_bridge.py`, `validation/validation_engine.py`, `tools/compatx/compatx.py`, `tools/controlx/controlx.py`, `tools/xstack/auditx/check.py`, `tools/xstack/repox/check.py`, `tools/xstack/performx/check.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `release/release_manifest_engine.py`, `release/update_resolver.py`, `security/trust/trust_verifier.py`

# XStack To AIDE Extraction Map

## A. Purpose And Scope

This artifact freezes the canonical XStack-to-AIDE extraction map for the live Dominium repository.

It exists because the earlier X-series artifacts already froze:

- what XStack means now
- which live surfaces are portable core, ops, runtime, Dominium-only, legacy, or mixed
- which task, evidence/review, policy/permission, capability-profile, and adapter shapes are portable now
- which repo-operating constraints keep the playable-baseline work honest

What was still missing was the boundary map that answers:

- which live surfaces are the strongest future AIDE extraction candidates
- which surfaces must remain in Dominium
- which surfaces should stay behind a wrapper or bridge instead of moving
- which surfaces should be deprecated rather than spun out
- which extractions must wait until after the playable baseline is real
- what order later post-baseline extraction work should follow

This artifact is baseline-first.
It does not authorize immediate code movement, repo migration, or a new AIDE runtime.

It must preserve current repo reality:

- admissible `Zeta` doctrine and gating work is complete
- the next broader program after `Zeta` is reconciliation and consolidation, not further internal `Zeta`
- the immediate product priority remains the canonical repo-local playable baseline
- XStack/AIDE work must continue to narrow, classify, and map boundaries without competing with the baseline path

## B. Extraction Framing

Extraction here means a later, post-baseline, evidence-backed separation of genuinely reusable XStack substrate into an AIDE-owned contract or code package without weakening Dominium’s current playable-baseline path.

This map distinguishes:

- document-first extraction readiness
  - frozen portable contracts and clearly reusable semantics that can be promoted into an AIDE fact base before any code moves
- later code extraction candidacy
  - live code that may eventually move or be mirrored into AIDE after baseline, stabilization, and bridge work
- wrapping versus moving
  - keep Dominium product/runtime/control-plane code in place, but later let extracted portable cores talk through explicit adapters or wrappers
- retaining in Dominium
  - keep the implementation in this repo because it is product-critical, runtime-critical, baseline-critical, or deeply tied to Dominium ownership
- deprecating rather than extracting
  - do not spin the surface out; later convergence or retirement should reduce it instead
- deferred extraction until after baseline
  - extraction may be reviewed later, but only after the playable baseline exists and the current startup/session path is stabilized

Extraction readiness is therefore not a binary.
It is a staged boundary judgment.

## C. Extraction Decision Classes

| Decision Class | Meaning now |
| --- | --- |
| `extract_later_as_portable_core` | Strongest future AIDE candidate. The extracted center is already document-first or code-light enough to justify later portable-core promotion after baseline. |
| `extract_later_with_wrapper_bridge` | A reusable kernel may later move, but only if Dominium keeps product/runtime/control-plane adapters, wrappers, or provider bridges behind. |
| `retain_in_dominium` | Keep the surface in Dominium. AIDE may consume the surrounding contract shapes, but this implementation stays repo-owned for the foreseeable future. |
| `deprecate_or_retire` | Do not spin this out. Prefer later convergence, retirement, or historical retention over extraction. |
| `defer_until_after_baseline` | Too baseline-critical, incomplete, or unstable to map beyond "review later." No extraction work should begin before the playable baseline exists. |
| `mixed_needs_later_review` | Surface contains real reusable and repo-bound portions at the same time. Keep visible, but do not force a clean extraction story yet. |

## D. Concrete Extraction Ledger

### `xmap.portable_contract_freezes`

- Name: Frozen portable AIDE contract artifacts
- Repo Paths: `docs/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`, `data/xstack/aide_portable_task_contract.json`, `docs/xstack/AIDE_EVIDENCE_AND_REVIEW_CONTRACT.md`, `data/xstack/aide_evidence_and_review_contract.json`, `docs/xstack/AIDE_POLICY_AND_PERMISSION_SHAPE.md`, `data/xstack/aide_policy_and_permission_shape.json`, `docs/xstack/AIDE_CAPABILITY_PROFILE_SHAPE.md`, `data/xstack/aide_capability_profile_shape.json`, `docs/xstack/AIDE_ADAPTER_CONTRACT.md`, `data/xstack/aide_adapter_contract.json`
- Current role / maturity summary: portable-contract freezes; implemented as canonical docs and machine-readable mirrors only
- Extraction decision: `extract_later_as_portable_core`
- Rationale: these artifacts already freeze the portable task, evidence/review, policy/permission, capability-profile, and adapter shapes without embedding runtime machinery
- What would be extracted later: the contract pack itself, later schemas generated from it, and any portable validator/checker layer that enforces the frozen fields
- What would remain behind: repo-local operating guidance, Dominium startup rules, and product/runtime ownership
- Shim or bridge required: contract-to-schema packager; contract-to-validator adapter; optional bridge from AIDE contracts back into Dominium tooling
- Extraction prerequisites: playable baseline exists; closure audit accepts the frozen contracts as stable; schema/export packaging is defined explicitly
- Unsafe to extract now because: no standalone AIDE package exists yet, and immediate value still comes from using these contracts inside Dominium

### `xmap.core_substrate`

- Name: XStack core planner, scheduler, runner, and artifact substrate
- Repo Paths: `tools/xstack/core/`
- Current role / maturity summary: `portable_core / implemented_and_used / wired_to_entrypoints`
- Extraction decision: `extract_later_as_portable_core`
- Rationale: this is the strongest live generic planner/runner substrate, and `scripts/dev/gate.py` plus `tools/xstack/run.py` already consume it as shared execution logic
- What would be extracted later: planner, scheduler, runner, impact, artifact-contract, Merkle, and profiler substrate with portable naming
- What would remain behind: Dominium gate scripts, repo-specific step catalogs, and repo-local report/output conventions
- Shim or bridge required: profile-name mapping; artifact-class mapping; Dominium gate-step adapter
- Extraction prerequisites: playable baseline exists; ControlX step taxonomy is stabilized; output/report path ownership is explicit
- Unsafe to extract now because: it is still wired into live repo gating and baseline assembly work, and pulling it early would create avoidable operator churn

### `xmap.compatx_contract_primitives`

- Name: Low-level CompatX canonicalization and validation primitives
- Repo Paths: `tools/xstack/compatx/canonical_json.py`, `tools/xstack/compatx/validator.py`, `tools/xstack/compatx/schema_registry.py`
- Current role / maturity summary: `portable_core / implemented_and_used / wired_to_entrypoints`
- Extraction decision: `extract_later_as_portable_core`
- Rationale: these helpers are the broadest reused XStack-adjacent substrate, with direct imports in `runtime/process_spawn.py`, `client/local_server/local_server_controller.py`, `server/net/loopback_transport.py`, `release/*.py`, `security/trust/*.py`, `validation/validation_engine.py`, and AppShell surfaces
- What would be extracted later: canonical JSON text/hash helpers, strict instance validation, and schema discovery/loading helpers
- What would remain behind: Dominium schema trees, specific schema registries, repo-relative defaults, and product-specific refusal vocabulary
- Shim or bridge required: schema-root adapter for `schema/` versus `schemas/`; registry source adapter; refusal-code mapping layer where needed
- Extraction prerequisites: playable baseline exists; ownership-sensitive schema split remains explicit; contract export packaging is approved
- Unsafe to extract now because: many baseline-critical surfaces currently import these helpers directly, and the repo still owns the schema source landscape

### `xmap.compatx_profile_and_version_checks`

- Name: CompatX profile checks and version-routing layer
- Repo Paths: `tools/xstack/compatx/check.py`, `tools/xstack/compatx/profile_checks.py`, `tools/xstack/compatx/versioning.py`, `tools/xstack/compatx/version_registry.json`, `tools/xstack/compatx/README.md`
- Current role / maturity summary: `mixed / partial_or_incomplete / active_tool_entrypoint`
- Extraction decision: `extract_later_with_wrapper_bridge`
- Rationale: the low-level contract primitives are reusable, but this layer is still tied to repo docs, repo schemas, version registries, and a migration path that currently stops at `migration_stub(...)` with `refuse.compatx.migration_not_implemented`
- What would be extracted later: generic version-resolution semantics, profile-check runner shape, and portable mismatch/refusal reporting
- What would remain behind: Dominium doc-link tables, version registry contents, schema policy registries, and repo-local migration tool invocation
- Shim or bridge required: schema name mapping; version-registry provider; migration-route adapter; doc-link provider
- Extraction prerequisites: migration story is no longer stub-only; policy ownership is explicit; schema/export adapter exists
- Unsafe to extract now because: the layer still encodes repo-specific schema/doc expectations and incomplete migration behavior

### `xmap.controlx_profile_orchestration`

- Name: XStack ControlX orchestration surface
- Repo Paths: `tools/xstack/run.py`, `tools/xstack/controlx/`
- Current role / maturity summary: `ops_concern / implemented_and_used / active_tool_entrypoint`
- Extraction decision: `extract_later_with_wrapper_bridge`
- Rationale: `tools/xstack/controlx/orchestrator.py` is a real orchestration surface, but it currently imports AuditX, CompatX, PerformX, PackagingX, registry compile, SessionX boot/create, TestX, and UI bind directly
- What would be extracted later: orchestration step model, run-context semantics, and profile-to-step contract
- What would remain behind: Dominium step implementations for pack loading, bundle selection, registry compile, session boot/create, UI checks, and repo-local audit/report emission
- Shim or bridge required: step-provider adapter; profile mapping; task-contract adapter; report-path adapter
- Extraction prerequisites: playable baseline exists; session/runtime surfaces are stabilized; Dominium step providers are cleanly declared
- Unsafe to extract now because: ControlX currently coordinates many baseline-critical Dominium surfaces and would destabilize the shortest playtest path if moved early

### `xmap.gate_and_review_bridges`

- Name: Repo gate and review bridge scripts that consume XStack
- Repo Paths: `scripts/dev/gate.py`, `scripts/ci/check_repox_rules.py`, `tools/review/xi8_common.py`
- Current role / maturity summary: `ops_concern / implemented_and_used / transitional_bridge`
- Extraction decision: `defer_until_after_baseline`
- Rationale: these are repo bridges between XStack semantics and Dominium review/gate flows, not portable core
- What would be extracted later: nothing by default; at most later mapping hooks that let extracted cores feed repo-owned review/gate wrappers
- What would remain behind: the gate scripts, review bundles, Xi-series review helpers, and repo policy enforcement
- Shim or bridge required: if later needed, task/evidence/review adapters from extracted AIDE cores back into Dominium gate flows
- Extraction prerequisites: playable baseline exists; X-9 closure audit confirms the retained gate posture; repo review surfaces are normalized
- Unsafe to extract now because: these bridges are part of the repo’s live operational discipline and are not a separate platform surface

### `xmap.session_create_pipeline`

- Name: Session create and pipeline-contract materialization
- Repo Paths: `tools/xstack/session_create.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/pipeline_contract.py`
- Current role / maturity summary: `runtime_concern / implemented_and_used / baseline_support`
- Extraction decision: `retain_in_dominium`
- Rationale: this surface is called out by the audit as part of the shortest playable-baseline path and bakes in Dominium bundle, lock, session-template, and save-root assumptions
- What would be extracted later: only document-first contract semantics already frozen elsewhere, not the current create/materialize implementation
- What would remain behind: SessionSpec materialization, universe artifact writing, bundle/lock/template defaults, and repo-local save tree semantics
- Shim or bridge required: any future exposure should go through profile/bundle mapping adapters, not code movement
- Extraction prerequisites: none for current planning because the implementation is retained
- Unsafe to extract now because: it directly supports the baseline session path and is still coupled to Dominium profile and save ownership

### `xmap.session_boot_runtime_control`

- Name: Session boot, SRZ, runtime, and control machinery
- Repo Paths: `tools/xstack/session_boot.py`, `tools/xstack/session_control.py`, `tools/xstack/session_surface.py`, `tools/xstack/session_script_run.py`, `tools/xstack/session_server.py`, `tools/xstack/srz_status.py`, `tools/xstack/sessionx/runner.py`, `tools/xstack/sessionx/process_runtime.py`, `tools/xstack/sessionx/scheduler.py`, `tools/xstack/sessionx/server_gate.py`, `tools/xstack/sessionx/ui_host.py`, `tools/xstack/sessionx/render_model.py`
- Current role / maturity summary: `runtime_concern / partial_or_incomplete / wired_to_entrypoints`
- Extraction decision: `defer_until_after_baseline`
- Rationale: this cluster is deep runtime/session machinery, and `tools/xstack/sessionx/runner.py` still hardcodes `save_dir = os.path.join(repo_root, "saves", save_id)` while `session_boot.py` explicitly documents `saves/<save_id>/session_spec.json`
- What would be extracted later: not the current code path; at most later review of narrow reusable contracts already frozen by X-2 through X-6
- What would remain behind: boot flow, SRZ/runtime execution, stage control, session server, UI host, render model, and all local authority/runtime coupling
- Shim or bridge required: save-root adapter; runtime bootstrap wrapper; session/runtime provider layer; law/profile provider bridge
- Extraction prerequisites: playable baseline exists; save-root coupling is fixed; canonical startup path is stable; runtime ownership review is explicit
- Unsafe to extract now because: it is both baseline-critical and still fragile

### `xmap.ui_bind_and_session_host_boundary`

- Name: UI bind checker and session-host boundary
- Repo Paths: `tools/xstack/ui_bind.py`, `tools/xstack/sessionx/ui_host.py`
- Current role / maturity summary: `mixed / implemented_and_used / active_tool_entrypoint`
- Extraction decision: `mixed_needs_later_review`
- Rationale: the descriptor-validation side looks portable, but the checked host surface is still part of SessionX runtime/session control
- What would be extracted later: possibly descriptor-validation rules and UI-bind contract checking only
- What would remain behind: session-host behavior, action dispatch, selector wiring, and Dominium UI registry semantics
- Shim or bridge required: UI registry adapter; session-host provider bridge
- Extraction prerequisites: UI registry semantics stabilized; session host separated cleanly from runtime control
- Unsafe to extract now because: the surface still straddles portable descriptor law and Dominium runtime implementation

### `xmap.testx_harness`

- Name: TestX deterministic harness and suite corpus
- Repo Paths: `tools/xstack/testx/`, `tools/xstack/testx_all.py`
- Current role / maturity summary: `ops_concern / implemented_and_used / wired_to_entrypoints`
- Extraction decision: `extract_later_with_wrapper_bridge`
- Rationale: the runner itself is reusable, but `tools/xstack/testx/runner.py` still depends on repo diff detection, semantic-impact helpers, the live suite corpus, and `.xstack_cache/xstack_testx`
- What would be extracted later: runner semantics, profile selection, sharding, deterministic subset selection, and cache contract shape
- What would remain behind: the Dominium test corpus, repo diff base refs, impact-graph generation, and report/output path policy
- Shim or bridge required: suite registry adapter; changed-files provider; cache-root adapter; repo-specific impact-graph bridge
- Extraction prerequisites: playable baseline exists; suite taxonomy and impact coverage are stable; report/output contract is explicit
- Unsafe to extract now because: the harness is a live baseline gate and still tightly coupled to this repo’s test corpus and Git layout

### `xmap.auditx_and_repox_wrappers`

- Name: XStack AuditX and RepoX wrapper entrypoints
- Repo Paths: `tools/xstack/auditx/check.py`, `tools/xstack/repox/check.py`
- Current role / maturity summary: `ops_concern / wrapper_or_transitional / active_wrapper`
- Extraction decision: `deprecate_or_retire`
- Rationale: these are wrapper CLIs over repo-specific audit and review scans; `auditx/check.py` explicitly calls itself a wrapper and reads `docs/audit/auditx/FINDINGS.json`, while `repox/check.py` hardcodes repo scan roots and review helpers
- What would be extracted later: not these wrappers; only underlying contract or rule shapes if separately justified
- What would remain behind: the wrapper CLIs, repo policy scan rules, and audit/report destinations
- Shim or bridge required: none for extraction because the wrappers themselves are not the future portable core
- Extraction prerequisites: if later desired, portable rule schemas would need to be separated first
- Unsafe to extract now because: wrapper behavior is not proof of portable ownership

### `xmap.securex_minimal`

- Name: SecureX minimal signature-status checks
- Repo Paths: `tools/xstack/securex/check.py`, `tools/xstack/securex/README.md`
- Current role / maturity summary: `ops_concern / implemented_and_used / active_tool_entrypoint`
- Extraction decision: `extract_later_with_wrapper_bridge`
- Rationale: the check surface is small and coherent, but it depends on Dominium pack loading, signature-status vocabulary, and trust policy resolution
- What would be extracted later: narrow verifier semantics for signature-status classification and refusal/warning posture
- What would remain behind: trust policy registries, pack enumeration, release/install integration, and Dominium trust plumbing
- Shim or bridge required: trust-policy provider; artifact enumeration adapter; pack metadata adapter
- Extraction prerequisites: portable policy/permission linkage remains stable; trust-root provider boundary is explicit
- Unsafe to extract now because: current behavior is still a Dominium trust and pack check, not a standalone policy engine

### `xmap.performx_placeholder`

- Name: PerformX placeholder budget and fidelity checks
- Repo Paths: `tools/xstack/performx/check.py`
- Current role / maturity summary: `ops_concern / partial_or_incomplete / active_tool_entrypoint`
- Extraction decision: `deprecate_or_retire`
- Rationale: the file describes itself as a placeholder, reads build registries opportunistically, and emits warnings rather than a mature portable contract engine
- What would be extracted later: none by default; later capability/policy evaluators should derive from the frozen X-4 and X-5 contracts instead
- What would remain behind: current placeholder behavior until later Dominium cleanup or replacement
- Shim or bridge required: none
- Extraction prerequisites: a real capability/policy evaluator would have to exist first
- Unsafe to extract now because: placeholder status is not extraction readiness

### `xmap.ci_guardrail_surface`

- Name: Xi-7 and Xi-8 CI guardrail surface
- Repo Paths: `tools/xstack/ci/`, `docs/xstack/CI_GUARDRAILS.md`, `docs/xstack/ARCH_DRIFT_POLICY.md`, `data/xstack/gate_definitions.json`
- Current role / maturity summary: `ops_concern / implemented_and_used / wired_to_entrypoints`
- Extraction decision: `mixed_needs_later_review`
- Rationale: the rule metadata is useful, but `tools/xstack/ci/ci_common.py` is deeply tied to Xi-series repo policy, GitHub workflow shape, audit report paths, and repo-local refusal categories
- What would be extracted later: maybe guardrail rule schemas, profile shapes, and CI-result contract helpers
- What would remain behind: repo-specific workflow wiring, drift policy rules, and audit/report output locations
- Shim or bridge required: CI provider adapter; report sink adapter; repo policy rule adapter
- Extraction prerequisites: closure audit confirms stable guardrail semantics; repo-specific rule IDs are separated from portable rule shapes
- Unsafe to extract now because: the current surface is still part of Dominium’s repo policy spine

### `xmap.validation_unified_surface`

- Name: Unified validation engine plus legacy adapters
- Repo Paths: `validation/validation_engine.py`, `tools/validation/tool_run_validation.py`, `tools/validation/validate_all_main.cpp`, `tools/validation/validator_common.*`, `tools/validation/validator_reports.*`, `tools/validation/validators_registry.*`
- Current role / maturity summary: `mixed / implemented_and_used / active_adapter`
- Extraction decision: `mixed_needs_later_review`
- Rationale: the validation engine is real and valuable, but it writes repo-local audit outputs, consumes many Dominium validators, and explicitly embeds a long `LEGACY_VALIDATION_SURFACE_SPECS` bridge table
- What would be extracted later: perhaps a narrow contract-checker kernel and report schema helpers
- What would remain behind: repo suite registry, audit report destinations, legacy adapter routing, release/install/save validators, and repo-local validation policy
- Shim or bridge required: suite-registry adapter; report-path adapter; validator provider bridge; output sink adapter
- Extraction prerequisites: baseline exists; legacy adapters are reduced or clearly ring-fenced; portable checker core is explicitly separated
- Unsafe to extract now because: it is current repo validation infrastructure, not a clean portable core

### `xmap.pack_and_distribution_pipeline`

- Name: Pack loading, contribution parsing, registry compile, and packaging pipeline
- Repo Paths: `tools/xstack/pack_loader/**`, `tools/xstack/pack_contrib/**`, `tools/xstack/registry_compile/**`, `tools/xstack/packagingx/**`, `tools/xstack/bundle_list.py`, `tools/xstack/bundle_validate.py`
- Current role / maturity summary: `dominium_only / implemented_and_used / wired_to_entrypoints`
- Extraction decision: `retain_in_dominium`
- Rationale: `tools/xstack/registry_compile/compiler.py` writes Dominium registry outputs and lockfiles, calls SessionX null-boot artifact helpers, and operates over live Dominium packs, bundles, release, and dist layout semantics
- What would be extracted later: at most contract adapters around the frozen capability/policy/adapter shapes, not the current compile/packaging implementation
- What would remain behind: pack loading, contribution parsing, registry compile, lockfile generation, dist layout build/validation, and Dominium pack/bundle vocabulary
- Shim or bridge required: future extracted cores would consume this through bundle/pack/profile adapters, not code movement
- Extraction prerequisites: none for current planning because the implementation remains Dominium-owned
- Unsafe to extract now because: it is core control-plane and baseline support substrate for the live repo

### `xmap.operator_shell_and_appshell_surfaces`

- Name: Python launcher/setup shells and shared AppShell command layer
- Repo Paths: `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `appshell/**`
- Current role / maturity summary: `dominium_only / implemented_and_used / active_product_shell`
- Extraction decision: `retain_in_dominium`
- Rationale: the audit identifies these as the strongest repo-local operator shells for the playable baseline, and they encode repo-root, dist, profile, pack, trust, supervision, and product-command assumptions
- What would be extracted later: not the shells themselves; only the portable contract shapes that the shells consume
- What would remain behind: launcher/setup operator commands, AppShell bootstrap, command dispatch, IPC, supervisor, and product-shell affordances
- Shim or bridge required: if later extracted cores need access, Dominium-owned operator wrappers should remain the integration boundary
- Extraction prerequisites: none for current planning because these shells are baseline-critical Dominium surfaces
- Unsafe to extract now because: baseline assembly explicitly depends on them as the canonical repo-local shells

### `xmap.appshell_and_tool_bridge_helpers`

- Name: AppShell and tool-level bridge helpers
- Repo Paths: `appshell/compat_adapter.py`, `appshell/pack_verifier_adapter.py`, `tools/tool_surface_adapter.py`, `tools/import_bridge.py`, `tools/controlx/core/remediation_bridge.py`
- Current role / maturity summary: `mixed / implemented_and_used / transitional_bridge`
- Extraction decision: `retain_in_dominium`
- Rationale: these files are bridge hosts, not portable cores; they bind Dominium release, trust, packs, audit artifacts, and old import topology into current operator flows
- What would be extracted later: only the abstract adapter or bridge contracts already frozen by X-3 through X-6
- What would remain behind: descriptor emission, pack verification wrapping, tool-surface command catalogs, import aliasing, and remediation artifact linking
- Shim or bridge required: these files are themselves the kind of bridge layer later extractions will need
- Extraction prerequisites: none for current planning; later AIDE cores can target them as retained boundaries
- Unsafe to extract now because: moving bridge code defeats the purpose of using Dominium-owned wrappers to protect baseline-critical behavior

### `xmap.local_baseline_runtime_bridge`

- Name: Local singleplayer and authoritative loopback bridge
- Repo Paths: `server/server_boot.py`, `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/net/loopback_transport.py`
- Current role / maturity summary: `dominium_only / partial_or_incomplete / baseline_support`
- Extraction decision: `retain_in_dominium`
- Rationale: the audit calls this the strongest evidence-backed local authority path, and it is directly coupled to repo-local server boot, process spawn, loopback negotiation, and the current playable-baseline target
- What would be extracted later: not this code path; later extracted portable cores would integrate through it
- What would remain behind: server boot, loopback transport, local attach/start logic, process spawn, and all local authority/runtime behavior
- Shim or bridge required: future adapters from extracted task/evidence/policy/capability layers into Dominium runtime control
- Extraction prerequisites: none for current planning because this remains baseline-critical Dominium runtime glue
- Unsafe to extract now because: it is part of the current baseline runtime direction and still partially fragile

### `xmap.release_and_trust_consumers`

- Name: Release, update, and offline trust surfaces that consume XStack helpers
- Repo Paths: `release/archive_policy.py`, `release/build_id_engine.py`, `release/component_graph_resolver.py`, `release/release_manifest_engine.py`, `release/update_resolver.py`, `security/trust/trust_verifier.py`, `security/trust/license_capability.py`
- Current role / maturity summary: `dominium_only / implemented_and_used / wired_to_entrypoints`
- Extraction decision: `retain_in_dominium`
- Rationale: these surfaces import CompatX helpers, but they are still Dominium release/trust control-plane implementations tied to repo policy, install, dist, and publication semantics
- What would be extracted later: only portable contract checking or hashing primitives already handled elsewhere
- What would remain behind: release manifests, update resolution, trust verification, license capability logic, and all repo publication/trust ownership
- Shim or bridge required: if later needed, trust-policy and release-manifest provider adapters
- Extraction prerequisites: none for current planning because these are protected Dominium control-plane surfaces
- Unsafe to extract now because: release and trust meaning is review-sensitive and explicitly protected

### `xmap.legacy_controlx_and_compatx_roots`

- Name: Legacy standalone ControlX and CompatX roots
- Repo Paths: `tools/controlx/**`, `tools/compatx/**`
- Current role / maturity summary: `legacy / implemented_but_isolated / transitional_bridge`
- Extraction decision: `deprecate_or_retire`
- Rationale: these are older sibling roots that still provide bridge value, but the current semantic center for the XStack/AIDE series lives under `tools/xstack/**`
- What would be extracted later: not these roots; if anything, later work would converge or retire them while preserving any still-needed bridge behavior
- What would remain behind: any temporary bridge or archaeology value until explicit convergence work is approved
- Shim or bridge required: staged migration rules and compatibility aliases if future cleanup touches their consumers
- Extraction prerequisites: post-baseline convergence task explicitly approved
- Unsafe to extract now because: spinning out legacy siblings would freeze the wrong ownership center

### `xmap.legacy_reference_docs_and_repo_contract`

- Name: Older XStack reference docs and repo-specific operating contract surfaces
- Repo Paths: `docs/XSTACK.md`, `docs/governance/XSTACK_PORTABILITY.md`, `docs/governance/XSTACK_INCREMENTAL_MODEL.md`, `docs/governance/XSTACK_EXTENSION_MODEL.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`, `data/xstack/codex_repo_operating_contract.json`
- Current role / maturity summary: older docs are `legacy`; the repo operating contract is `repo-specific governance`
- Extraction decision: `retain_in_dominium`
- Rationale: the older docs are historical context only, and the Codex repo operating contract is intentionally specific to this repo’s build, validation, playtest, and directory-authority rules
- What would be extracted later: not these documents as-is; later AIDE may derive generic operating guidance elsewhere, but this repo contract remains Dominium-owned
- What would remain behind: the historical XStack reference set and the repo-local Codex operating contract
- Shim or bridge required: none
- Extraction prerequisites: none
- Unsafe to extract now because: these artifacts either describe superseded local context or intentionally govern this repo only

## E. Definite Dominium-Retained Surfaces

The following surfaces should remain in Dominium for now:

- `tools/xstack/session_create.py` and `tools/xstack/sessionx/creator.py`
  - baseline session materialization and default bundle/lock/template semantics
- `tools/xstack/session_boot.py` and the broader `tools/xstack/sessionx/**` runtime/control path
  - boot, SRZ, stage control, UI host, render model, and runtime coupling remain repo-owned
- `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, and `appshell/**`
  - canonical operator shells and product-shell control surfaces for the playable baseline
- `server/server_boot.py`, `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, and `server/net/loopback_transport.py`
  - strongest current loopback authority/runtime path and therefore baseline-critical
- `tools/xstack/pack_loader/**`, `tools/xstack/pack_contrib/**`, `tools/xstack/registry_compile/**`, and `tools/xstack/packagingx/**`
  - Dominium pack, bundle, registry, lockfile, dist, and release semantics
- `release/**` and `security/trust/**` consumers of XStack helpers
  - protected release/trust/control-plane meaning
- `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md` and `data/xstack/codex_repo_operating_contract.json`
  - repo-local operating law, not portable AIDE truth

## F. Likely Later AIDE Candidates

The strongest later AIDE candidates are:

- the frozen portable contract artifacts under `docs/xstack/AIDE_*.md` and `data/xstack/aide_*.json`
  - document-first portable core already exists
- `tools/xstack/core/**`
  - strongest reusable planner/runner substrate
- `tools/xstack/compatx/canonical_json.py`, `validator.py`, and `schema_registry.py`
  - broadest reused contract primitives across XStack-adjacent consumers
- a later wrapped subset of `tools/xstack/compatx/check.py`, `profile_checks.py`, and `versioning.py`
  - only after migration and schema-provider boundaries are explicit
- a later wrapped subset of `tools/xstack/testx/**`
  - runner semantics and sharding/cache posture are reusable, but the suite corpus stays Dominium-owned
- a later wrapped subset of `tools/xstack/controlx/**` and `tools/xstack/securex/check.py`
  - only after the baseline exists and provider boundaries are explicit

## G. Mixed / Deferred / Unsafe-To-Extract Surfaces

The following surfaces are intentionally not clean targets yet:

- `tools/xstack/controlx/**`
  - reusable orchestration shape exists, but the live implementation still drives many Dominium-specific steps
- `tools/xstack/compatx/check.py`, `profile_checks.py`, `versioning.py`
  - mixed portable and repo-specific schema/doc/version behavior, plus migration stubs
- `tools/xstack/ui_bind.py` plus `tools/xstack/sessionx/ui_host.py`
  - portable descriptor rules mixed with Dominium runtime/session host behavior
- `validation/validation_engine.py` and `tools/validation/**`
  - valuable infrastructure, but deeply tied to repo suites, legacy adapters, and report outputs
- `tools/xstack/ci/**` plus `data/xstack/gate_definitions.json`
  - portable-looking rule metadata mixed with Xi-specific repo CI policy
- gate/review bridges such as `scripts/dev/gate.py`
  - repo bridge, not platform core
- `tools/xstack/sessionx/**`
  - baseline-critical and still carrying save-root coupling and startup fragility

## H. Bridge And Shim Requirements

Later extraction will require explicit retained bridge layers rather than direct code moves.

### H1. Schema and contract adapters

- schema-root adapter to handle `schema/` law versus `schemas/` validator projection
- registry-source adapter for Dominium schema/version/policy registries
- contract packager that turns frozen AIDE docs/data into explicit machine-checkable exports

### H2. Profile, bundle, and pack mapping

- profile mapping from portable capability/task/policy vocabulary to Dominium bundle IDs such as `profile.bundle.mvp_default`
- pack-lock and registry provider adapters so extracted cores do not own Dominium pack roots
- staged migration rules for any later convergence around `tools/xstack/registry_compile/**`

### H3. Validation and test adapters

- suite-registry adapter for `validation/validation_engine.py`
- changed-files and impact-graph provider bridge for `tools/xstack/testx/runner.py`
- report sink/path adapters so extracted cores do not write directly into `docs/audit/**` and `data/audit/**`

### H4. Trust and release adapters

- trust-policy provider for `tools/xstack/securex/check.py`
- release/trust consumer adapters so extracted helpers do not absorb Dominium publication policy

### H5. Operator and runtime wrappers

- AppShell/operator wrappers remain in Dominium
- startup/session/runtime integration should keep using retained bridges such as `appshell/compat_adapter.py`, `appshell/pack_verifier_adapter.py`, `tools/tool_surface_adapter.py`, `tools/import_bridge.py`, and `tools/controlx/core/remediation_bridge.py`
- any future extracted portable core should talk through these boundaries instead of displacing them

## I. Extraction Order After The Baseline Exists

No code extraction should begin before the playable baseline is real, repeatable, and no longer blocked by the canonical startup/session/save-root issues.

Recommended staged order after that:

1. Document-first portable core promotion
   - promote the frozen AIDE task, evidence/review, policy/permission, capability-profile, and adapter contracts into a standalone AIDE contract pack
   - include this extraction map as the boundary ledger, not as an implementation plan

2. Low-level portable substrate extraction
   - extract `tools/xstack/core/**`
   - extract low-level CompatX primitives: canonical JSON, validator, schema registry helpers
   - keep Dominium schema/provider adapters behind

3. Checker and harness extraction with retained bridges
   - review a narrow wrapped subset of CompatX profile/version checks
   - review a narrow wrapped subset of TestX runner semantics
   - review narrow SecureX verifier semantics
   - do not move Dominium suites, registries, trust policy, or report sinks

4. Orchestration-layer extraction with explicit provider wrappers
   - only after the earlier stages are stable, review whether ControlX profile/orchestration semantics can move behind Dominium step-provider adapters
   - keep session/runtime, AppShell, pack compile, and product/operator shells in Dominium

5. Optional late mixed-surface review
   - only then review CI guardrail schemas, UI bind descriptor validation, or validation checker kernels
   - treat runtime/session/AppShell/release/trust surfaces as retained unless a later explicit checkpoint authorizes more

Deprecated or retired surfaces are not a stage:

- `tools/xstack/auditx/check.py`
- `tools/xstack/repox/check.py`
- `tools/xstack/performx/check.py`
- `tools/controlx/**`
- `tools/compatx/**`

Those should be reduced, converged, or retained as local history/bridges rather than spun out into AIDE.

## J. Doctrine Vs Implementation Vs Extraction Distinction

The following distinctions remain binding:

- doctrinal similarity does not equal extraction readiness
  - a surface may sound generic while still being tightly tied to Dominium runtime, packs, or review flow
- implementation existence does not equal portability
  - running code is evidence of value, not proof that it belongs in AIDE
- extraction mapping does not equal immediate extraction execution
  - this artifact authorizes later review and sequencing only
- wrapper existence does not equal platform ownership
  - bridge hosts often prove the opposite: they are exactly the retained Dominium seam

## K. Anti-Patterns / Forbidden Shapes

The following moves are forbidden under this extraction map:

- extracting baseline-critical surfaces now
- moving mixed surfaces because they sound generic
- treating wrapper code as portable core by default
- using this map to justify immediate repo churn, broad renames, or code moves
- claiming a separate AIDE runtime is ready now
- collapsing document-first contract freezes, code extraction candidacy, and runtime implementation into one story
- treating the current repo operating contract as AIDE policy

## L. Stability And Evolution

Stability class:

- stable until an explicit post-baseline extraction checkpoint or closure audit replaces it

This artifact enables:

- the final XStack/AIDE closure audit next
- later post-baseline extraction checkpoints that need a conservative boundary map
- future implementation prompts that need to know what to retain, wrap, defer, or retire before any code movement is proposed

This artifact must not change silently when:

- a surface changes decision class
- a retained Dominium surface is proposed as a later AIDE core
- the post-baseline extraction order changes materially
- a new bridge/shim prerequisite appears that changes extraction safety

Any such change requires an explicit follow-up artifact rather than silent drift.
