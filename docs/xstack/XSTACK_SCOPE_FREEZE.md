Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: X-1, X-2, X-3, AIDE extraction review
Replacement Target: later explicit XStack/AIDE scope checkpoint or replacement artifact only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`

# XStack Scope Freeze

## A. Purpose and Scope

This artifact freezes what XStack means in the live Dominium repo now.

It exists so later XStack/AIDE prompts can inventory, classify, and extract contracts without:

- smuggling in future platform ambitions
- treating stale portability prose as live repo truth
- broadening into product work that competes with the playable-baseline path
- collapsing doctrine, implementation, and extraction into one concept

It governs:

- the current repo-grounded definition of XStack
- the boundary between branded XStack, XStack-adjacent tooling, and broader Dominium product/runtime surfaces
- what the XStack/AIDE series may do now
- what must remain in Dominium for now
- what must be documented now and deferred until after the playable baseline exists

This artifact is downstream of completed admissible `Ζ` closure and must preserve:

- `admissible Ζ doctrine program complete = yes`
- `further Ζ prompt required = no`
- post-`Ζ` mode = `frontier reconciliation and consolidation first`
- current product priority = repo-local playable baseline and repo stabilization

This artifact is a scope-freeze and extraction-prep baseline.
It is not an AIDE implementation plan and it does not authorize work that competes with the playable-baseline path.

## B. Current-State Definition of XStack

Current definition:

XStack is the live repo-native deterministic tooling and control layer centered on `tools/xstack/`, plus its immediate support docs/data, used today for gate orchestration, validation families, session artifact materialization/control, pack and registry tooling, CI guardrails, and related operator surfaces.

What is branded or named XStack now:

- `tools/xstack/**`
- `docs/xstack/**`
- `data/xstack/**`
- explicit XStack governance/task docs under `docs/agents/` and `docs/governance/`

What is functionally part of the live XStack control/tooling layer now:

- `scripts/dev/gate.py`, which imports `tools.xstack.core.*`
- repo-local validation surfaces that consume XStack contracts, especially `validation/validation_engine.py` and `tools/validation/tool_run_validation.py`
- product-shell and session-adjacent surfaces that directly import XStack helpers, including `appshell/**`, `server/server_boot.py`, and `client/local_server/local_server_controller.py`

What resembles XStack concerns but is not the same as current XStack scope:

- sibling roots such as `tools/controlx/**` and `tools/compatx/**`
- broad runtime/domain roots such as `engine/**`, `game/**`, `geo/**`, `logic/**`, `materials/**`, and `worldgen/**`
- launcher/setup compiled shells and other product wrappers that consume XStack-adjacent flows but are not themselves XStack

What is better understood as future AIDE material rather than current XStack:

- any standalone, repo-independent extraction of XStack contracts into a new platform identity
- any AIDE runtime, daemon, compiler, adapter ecosystem, or service layer
- any portability claim that requires XStack to be cleanly separable from Dominium today

Repo-grounded caution:

- `tools/xstack/run.py`, `tools/xstack/controlx/orchestrator.py`, `tools/xstack/session_create.py`, `tools/xstack/sessionx/**`, `tools/xstack/testx/**`, and `tools/xstack/ci/**` prove that XStack is live implementation, not just prose
- `validation/validation_engine.py` and `appshell/**` import XStack helpers directly
- a repo search over `engine/`, `game/`, `client/`, and `server/` finds live `tools.xstack` references, especially `compatx` helpers and `sessionx` helpers
- `docs/governance/XSTACK_PORTABILITY.md` still describes a removability discipline that the live repo does not currently satisfy as a universal fact
- a repo search for `AIDE` or `aide` returns no current repo-local AIDE implementation root

So XStack today is real, important, and already wired into the repo, but it is not yet a clean standalone platform.

## C. Scope Buckets

| Bucket | Meaning now | Inclusion criteria |
| --- | --- | --- |
| `portable_core` | Narrow deterministic substrate that already exposes generic planner, runner, hashing, or schema-contract behavior with limited direct product knowledge. | The surface is structurally generic, reused across multiple XStack families, and can be described without Dominium session/startup assumptions. |
| `runtime_concern` | XStack-branded code that directly creates, boots, stages, controls, or mutates sessions or authoritative session-adjacent state. | The surface works with `SessionSpec`, universe artifacts, SRZ, stage parity, observation/render adaptation, or authoritative process/session control. |
| `ops_concern` | Operator, CI, gate, audit, validation, and repo-execution surfaces. | The surface exists to run the repo, gate changes, emit evidence, or coordinate verification rather than to provide product gameplay. |
| `dominium_specific_concern` | Surfaces tied to Dominium product shells, bundle/lock/profile assumptions, loopback authority, or repo-local control-plane details. | The surface bakes in Dominium paths, bundle IDs, registry outputs, release/trust wiring, or product-shell assumptions that are not proven portable. |
| `legacy_transitional` | Older sibling roots, wrappers, or docs that remain useful evidence but are not the current XStack semantic center. | The surface predates current `tools/xstack/**` canon, is marked as wrapper or transitional by audit evidence, or overclaims portability/removability relative to live code. |
| `deferred_to_later_aide_extraction` | Plausible future extraction candidates that may be mapped now but must not be platformized now. | The surface shows reusable structure, but extracting it now would compete with baseline assembly or would still require convergence/uncoupling work. |
| `explicitly_outside_current_scope` | Work this series must not perform now. | The surface is product/runtime expansion, non-loopback multiplayer, broad renaming, or a not-yet-present AIDE implementation. |

## D. Concrete Repo-Grounded Scope Ledger

The ledger below uses a dominant current-role bucket.
A path may appear again in Section H as a later extraction candidate without changing its current bucket.

### `portable_core`

| Paths | Why this bucket fits now |
| --- | --- |
| `tools/xstack/core/` | `plan.py`, `scheduler.py`, `runners.py`, and `artifact_contract.py` implement a generic deterministic planner, runner, cache, and artifact-classification substrate with limited direct product knowledge. |
| `tools/xstack/compatx/canonical_json.py` | Pure canonical JSON serialization and hashing helper; widely reused but not itself a gameplay or product-shell surface. |
| `tools/xstack/compatx/validator.py` | Strict schema validator for canonical contracts; reusable contract substrate rather than a product runtime. |
| `tools/xstack/compatx/schema_registry.py` | Generic schema discovery and version-registry loading helper; repo-relative today, but structurally a contract-layer primitive. |

### `runtime_concern`

| Paths | Why this bucket fits now |
| --- | --- |
| `tools/xstack/sessionx/` | `creator.py`, `runner.py`, `scheduler.py`, `process_runtime.py`, `pipeline_contract.py`, `ui_host.py`, and related modules are the XStack-branded session lifecycle and authoritative process/session machinery. |
| `tools/xstack/session_create.py` | Creates `session_spec.json`, `universe_identity.json`, `universe_state.json`, and `universe_contract_bundle.json`; this is session materialization, not just generic tooling. |
| `tools/xstack/session_boot.py` | Boots SessionSpec artifacts and is audited as a real but fragile runtime/session path. |
| `tools/xstack/session_control.py` and `tools/xstack/session_surface.py` | Stage, abort, resume, compact, and CLI/TUI/GUI parity wrappers are session-control surfaces. |
| `tools/xstack/session_script_run.py`, `tools/xstack/session_server.py`, and `tools/xstack/srz_status.py` | Scripted SRZ and session/server status handling are runtime/session operations. |
| `tools/xstack/ui_bind.py` | Validates `ui.registry` descriptors against `sessionx.ui_host` expectations and session gating, so it belongs with session/runtime support rather than pure ops. |

### `ops_concern`

| Paths | Why this bucket fits now |
| --- | --- |
| `tools/xstack/run.py` | Stable FAST/STRICT/FULL XStack entrypoint for deterministic profile runs. |
| `tools/xstack/controlx/` | `orchestrator.py` coordinates pack, bundle, compile, audit, test, session, and UI checks as repo operations. |
| `tools/xstack/testx/` and `tools/xstack/testx_all.py` | Deterministic test harness and large suite selection are validation/evidence operations. |
| `tools/xstack/auditx/`, `tools/xstack/repox/`, `tools/xstack/securex/`, and `tools/xstack/performx/` | Audit, static checks, trust checks, and profile/budget checks are operator-facing gate families. |
| `tools/xstack/ci/`, `data/xstack/gate_definitions.json`, `docs/xstack/CI_GUARDRAILS.md`, and `docs/xstack/ARCH_DRIFT_POLICY.md` | These surfaces define and drive CI/guardrail policy rather than gameplay or product runtime. |
| `scripts/dev/gate.py` | Imports `tools.xstack.core.*` and functionally participates in the live XStack control layer even though it does not live under `tools/xstack/`. |
| `validation/validation_engine.py` and `tools/validation/tool_run_validation.py` | Repo-local unified validation surface that consumes XStack compatx contracts and emits audit/validation evidence. |
| `tools/xstack/compatx/check.py` | Profile-driven CompatX check surface is an operational contract-check entrypoint rather than a low-level primitive. |

### `dominium_specific_concern`

| Paths | Why this bucket fits now |
| --- | --- |
| `tools/xstack/registry_compile/` | Uses default bundle IDs such as `bundle.base.lab` and emits a large Dominium registry set; current structure is tied to Dominium bundle and registry vocabulary. |
| `tools/xstack/pack_loader/` and `tools/xstack/pack_contrib/` | Assume Dominium pack roots, manifest names, and contribution vocabulary. |
| `tools/xstack/packagingx/` | Dist layout and packaging helpers are tied to Dominium packaging and release structure. |
| `appshell/` | Product bootstrap, supervisor, IPC, compatibility, and virtual-path logic import XStack helpers but remain product-shell integration. |
| `server/server_boot.py` | Directly imports `tools.xstack.sessionx.*` and pack/session helpers; server boot remains Dominium-owned even when it uses XStack helpers. |
| `client/local_server/local_server_controller.py` | Loopback local-singleplayer controller is baseline gameplay glue, not current AIDE extraction material. |
| `profiles/bundles/bundle.mvp_default.json`, `locks/pack_lock.mvp_default.json`, and `data/session_templates/session.mvp_default.json` | Live baseline content/config pair and session template called out by the audit as the near-term playable slice. |

### `legacy_transitional`

| Paths | Why this bucket fits now |
| --- | --- |
| `tools/controlx/` | Older autonomous control-plane wrapper outside `tools/xstack/`; still useful evidence, but not the current branded XStack root. |
| `tools/compatx/` | Older compatibility CLI/core; `validation/validation_engine.py` maps it as legacy or adapter surface rather than the current XStack canon. |
| `tools/validation/validate_all_main.cpp`, `tools/validation/validator_common.*`, `tools/validation/validator_reports.*`, and `tools/validation/validators_registry.*` | Explicitly represented by the unified validation engine as legacy coverage adapters or deprecated aggregate validator surfaces. |
| `tools/mvp/runtime_entry.py` | Audit marks this as a transitional wrapper rather than the dependable canonical playtest bootstrap. |
| `docs/XSTACK.md` | Useful reference, but still describes an older gate-centric model and does not cleanly reflect current live coupling. |
| `docs/governance/XSTACK_PORTABILITY.md`, `docs/governance/XSTACK_INCREMENTAL_MODEL.md`, `docs/governance/XSTACK_EXTENSION_MODEL.md`, `docs/governance/XSTACK_PRODUCTION_CRITERIA.md`, `docs/governance/XSTACK_TEMPLATE_CHECKLIST.md`, and `docs/governance/XSTACK_SCOPE_TEMPLATE.json` | Derived portability/removability guidance; several files say they are only partially aligned, and live imports show stronger coupling than the docs claim. |

### `deferred_to_later_aide_extraction`

| Paths | Why this bucket fits now |
| --- | --- |
| `tools/xstack/core/` and `tools/xstack/compatx/` | Strongest reusable contract substrate, but extracting it now would still require uncoupling discipline and would compete with baseline assembly. |
| `tools/xstack/testx/`, `tools/xstack/auditx/`, `tools/xstack/repox/`, `tools/xstack/securex/`, `tools/xstack/performx/`, and `tools/xstack/ci/` | Coherent tool families that may later support AIDE-style extraction, but current scope is documentation, mapping, and contract freezing only. |
| `docs/xstack/` and `data/xstack/` | Useful support surfaces for later extracted policy/catalog packaging, but docs/data do not justify a standalone platform by themselves. |
| `tools/controlx/` | Plausible later convergence target after scope is frozen, but still a sibling/transitional surface now. |

### `explicitly_outside_current_scope`

| Paths | Why this bucket fits now |
| --- | --- |
| `aide/`, `tools/aide/`, and `apps/aide/` | No such repo roots exist; a full AIDE implementation is not present and is not authorized by this series. |
| `engine/`, `game/`, `geo/`, `worldgen/`, `logic/`, `materials/`, `signals/`, and `reality/` as broad implementation targets | These roots may be read as evidence, but XStack/AIDE work may not broaden into general product/runtime implementation work here. |
| `net/transport/tcp_stub.py` and `net/transport/udp_stub.py` | Audit explicitly says non-loopback multiplayer transport is not part of the near-term playable baseline. |
| `launcher/` and `setup/` native GUI/TUI completion work | Audit explicitly says compiled launcher/setup shells should stay wrappers for now. |
| `legacy/`, `quarantine/`, and `attic/` broad convergence/rename work | Audit explicitly says to retire or ignore broad convergence work during playable-baseline assembly. |

## E. In Scope for the Current XStack/AIDE Series

This series is allowed to do the following now:

- freeze the current repo-grounded meaning of XStack
- inventory and classify branded XStack surfaces and the adjacent sibling roots that materially interact with them
- identify conservative portable-contract candidates without claiming full portability
- define the boundary between current XStack, Dominium-owned product/runtime surfaces, and later AIDE candidates
- extract documentation-level or machine-readable contract maps for later prompts
- define a repo-operating contract for later agent/Codex work over XStack/AIDE surfaces
- map what should remain in Dominium versus what may later be reviewed for extraction
- produce scope, inventory, classification, and extraction-mapping artifacts that do not alter runtime/product behavior

## F. Out of Scope for the Current XStack/AIDE Series

This series must not do the following now:

- implement a full AIDE runtime
- implement an AIDE daemon
- implement a compiler, adapter runtime, or bakeoff framework
- perform broad repo renaming for its own sake
- move `tools/xstack/**` or adjacent roots just to make the tree look cleaner
- broaden into non-XStack/AIDE product work
- implement multiplayer transport beyond the current loopback baseline
- replace launcher/setup/product shells instead of documenting the stronger live repo-local paths
- treat portability docs as proof that the live repo is already uncoupled
- reopen blocked or future-only post-`Ζ` frontier work

## G. Relationship to Dominium

### XStack and the Repo Control Plane

XStack currently sits inside Dominium's control-plane and tooling layer.
It provides live gate, validation, session-tooling, pack/registry, CI, and evidence surfaces.
It does not replace the repo's broader control plane.

### XStack and Product Shells

The strongest repo-local operator shells today remain Dominium-owned:

- `tools/launcher/launch.py`
- `tools/setup/setup_cli.py`
- `appshell/**`

XStack is beneath or beside these shells, not above them as a separate platform.

### XStack and Runtime/Session/Playtest Assembly

Session materialization and session control live partly inside XStack, but the playable-baseline path remains Dominium work:

- default bundle, lock, and session template are Dominium baseline assets
- loopback local authority and attach flow are Dominium-owned baseline glue
- AppShell supervision and compatibility negotiation are Dominium product-shell behavior

So the XStack/AIDE series may document and narrow these surfaces now, but it may not compete with baseline assembly or claim them as extracted platform ownership.

### XStack and Post-`Ζ` Frontier Work

Post-`Ζ` closure is already complete as admissible doctrine.
This XStack/AIDE series is not a new `Ζ` family and does not reopen blocked live-ops realization.
Its role is narrowing, classification, and contract extraction prep only.

### What Must Remain in Dominium for Now

The following remain Dominium-owned for now:

- `tools/xstack/sessionx/**` and session CLI wrappers
- `appshell/**`
- `server/server_boot.py`
- `client/local_server/local_server_controller.py`
- baseline bundle/lock/template assets
- release/trust/control-plane glue used by launcher/setup and baseline startup

## H. Relationship to Later AIDE Extraction

### Plausible Future AIDE Extraction Targets

The strongest plausible later AIDE candidates are:

- `tools/xstack/core/`
- low-level `tools/xstack/compatx/` contract helpers
- `tools/xstack/testx/`, `tools/xstack/auditx/`, `tools/xstack/repox/`, `tools/xstack/securex/`, `tools/xstack/performx/`, and `tools/xstack/ci/`
- support policy/catalog surfaces under `docs/xstack/` and `data/xstack/`

These may later support extraction because they already act like coherent operator/tool families.
They are still deferred now.

### Definitely Dominium-Specific for Now

The following are definitely Dominium-specific for now:

- `tools/xstack/sessionx/**`
- `appshell/**`
- `server/server_boot.py`
- `client/local_server/local_server_controller.py`
- `profiles/bundles/bundle.mvp_default.json`
- `locks/pack_lock.mvp_default.json`
- `data/session_templates/session.mvp_default.json`

These are too bound to current baseline assembly, product-shell behavior, or Dominium runtime semantics to be treated as current AIDE material.

### Ambiguous or Mixed Surfaces Requiring Later Review

The following remain mixed and need later review rather than immediate extraction:

- `tools/xstack/registry_compile/`
- `tools/xstack/pack_loader/`
- `tools/xstack/pack_contrib/`
- `tools/xstack/packagingx/`
- `validation/validation_engine.py`
- `tools/controlx/`
- `tools/xstack/ui_bind.py`

These surfaces show reusable patterns, but they also carry strong Dominium vocabulary, bundle assumptions, validation aggregation, or product-shell coupling.

### Document Now, Defer Until After the Playable Baseline Exists

The following should be documented now and deferred until after the playable baseline exists:

- convergence between `tools/controlx/` and `tools/xstack/controlx/`
- any cleanup intended to make `sessionx` more separable from Dominium runtime semantics
- any portability/removability repair work needed to reconcile live imports with older portability docs
- any extraction packaging, publishable AIDE layout, or repo-independent distribution story

## I. Doctrine vs Implementation vs Extraction Distinction

The following distinctions are binding for this series:

- doctrinal similarity does not equal extraction readiness
- implementation existence does not equal portability
- current utility inside Dominium does not equal future AIDE ownership
- a path living under `tools/xstack/` does not automatically make it portable core
- a derived portability document does not outrank live implementation evidence
- generated or cached outputs such as `.xstack_cache/**`, `tools/xstack/out/**`, `build/**`, and `artifacts/**` are evidence only, not scope owners

## J. Anti-Patterns and Forbidden Shapes

The following shapes are forbidden:

- treating all tooling as XStack
- treating all XStack as portable
- treating all session/runtime work touched by XStack as future AIDE
- using future AIDE ambitions to justify present repo churn
- renaming roots before semantics are frozen
- using derived portability/removability prose to override live repo coupling
- competing with canonical playable-baseline work
- silently promoting adjacent sibling roots into canonical XStack ownership
- flattening doctrine, implementation, and extraction into one umbrella concept

## K. Stability and Evolution

Stability class:

- `stable`

This artifact is intended to be consumed by later prompts that perform:

- XStack inventory and finer classification
- portable-contract extraction mapping
- repo-operating contract freezing for agent/Codex work on XStack/AIDE surfaces
- later post-baseline review of mixed extraction candidates

This artifact must not change silently.
Any later change requires:

- explicit follow-up scope checkpoint or explicit replacement artifact
- repo-grounded evidence for the reclassification
- preservation of playable-baseline non-interference
- explicit separation between current Dominium ownership and later extraction ambition
