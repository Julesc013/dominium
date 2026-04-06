Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: Codex repo operating contract, AIDE extraction review
Replacement Target: later explicit portable adapter-contract checkpoint or replacement artifact only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`, `docs/xstack/XSTACK_INVENTORY_AND_CLASSIFICATION.md`, `data/xstack/xstack_inventory_and_classification.json`, `docs/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`, `data/xstack/aide_portable_task_contract.json`, `docs/xstack/AIDE_EVIDENCE_AND_REVIEW_CONTRACT.md`, `data/xstack/aide_evidence_and_review_contract.json`, `docs/xstack/AIDE_POLICY_AND_PERMISSION_SHAPE.md`, `data/xstack/aide_policy_and_permission_shape.json`, `docs/xstack/AIDE_CAPABILITY_PROFILE_SHAPE.md`, `data/xstack/aide_capability_profile_shape.json`, `compat/data_format_loader.py`, `compat/handshake/handshake_engine.py`, `compat/shims/tool_shims.py`, `appshell/compat_adapter.py`, `appshell/pack_verifier_adapter.py`, `appshell/ipc/ipc_transport.py`, `appshell/ipc/ipc_client.py`, `tools/tool_surface_adapter.py`, `tools/setup/setup_cli.py`, `tools/import_bridge.py`, `tools/controlx/core/remediation_bridge.py`, `client/render/render_model_adapter.py`, `geo/projection/view_adapters.py`, `validation/validation_engine.py`, `schemas/tool_adapter_output.schema.json`, `templates/adapter_template.md`, `data/reality/cross_domain_bridge_registry.json`, `tools/xstack/testx/tests/test_tool_adapter_offline.py`, `tools/xstack/testx/tests/test_tool_adapter_uses_virtual_paths.py`, `tools/xstack/testx/tests/test_native_adapter_only_calls_command_engine.py`, `tools/xstack/testx/tests/test_shims_emit_deterministic_warnings.py`, `tools/xstack/testx/tests/test_attach_requires_negotiation.py`, `tools/xstack/testx/tests/test_unnegotiated_attach_refused.py`, `tools/xstack/testx/tests/test_tool_incompatibility_refusal.py`

# AIDE Adapter Contract

## A. Purpose and Scope

This artifact freezes the canonical portable adapter contract that later XStack/AIDE prompts may reuse.

It exists because:

- `X-0` froze what XStack means now and what remains outside the current extraction series
- `X-1` classified the live XStack/AIDE-relevant surfaces by portability, maturity, and ownership
- `X-2` froze the portable task unit and its required refusal, evidence, and review hooks
- `X-3` froze the portable evidence and review contract that adapters may emit, consume, or require
- `X-4` froze portable policy and permission shape so adapter use can link to law without becoming an authorization engine
- `X-5` froze the portable capability-profile shape so adapters can declare capability requirements without becoming a runtime resolver
- later AIDE work still needs a smaller and stricter contract for adapter truth itself

This artifact solves a specific narrowing problem:

- the live repo contains real adapter-like implementations, bridge helpers, wrappers, shims, compatibility translators, negotiation helpers, render adapters, and transport boundaries
- later AIDE extraction work needs the portable minimum those surfaces justify
- that portable minimum must be frozen without promoting every wrapper or bridge into a portable adapter and without smuggling in runtime selection, execution, or discovery machinery

This artifact governs:

- what a portable adapter means in the live XStack/AIDE sense
- which fields every canonical portable adapter contract must expose
- which boundaries must remain explicit
- how adapter contracts relate to the prior portable task, evidence/review, policy/permission, and capability-profile contracts
- which parts are portable now versus Dominium-retained now versus deferred until after the playable baseline exists
- which later prompts may treat this artifact as their fact base

This artifact is downstream of `X-0` through `X-5`.
It does not reopen scope, inventory, task, evidence/review, policy/permission, or capability-profile classification.
It narrows those earlier artifacts into portable adapter truth only.

This artifact must preserve current repo reality:

- admissible `Zeta` doctrine and gating work is complete
- the immediate product priority remains the canonical repo-local playable baseline and repo stabilization
- XStack/AIDE work must support clarification, modularization, and contract extraction without competing with the baseline path

This artifact is a contract freeze.
It does not implement an adapter runtime, adapter registry service, daemon, scheduler, compiler, bakeoff framework, or broader AIDE platform.

## B. Current-State Definition of a Portable Adapter

Current definition:

A portable adapter is a canonical declarative contract for a bounded translation or mediation path between one source interface or contract and one target interface or contract, including the adapter's identity, purpose, declared capability requirements and exclusions, linked task or evidence or policy surfaces when applicable, compatibility and stability constraints, explicit refusal and incompatibility semantics, and portability limits, without embedding runtime adapter discovery, runtime selection, execution orchestration, transport ownership, or product-shell command dispatch.

The portable adapter contract is:

- a contract for source-to-target mediation
- a contract for declared compatibility boundaries
- a contract for capability, policy, review, and evidence linkages where the mediation path depends on them
- a contract for explicit refusal, incompatibility, blocked, degraded, and fallback posture

The portable adapter contract is not:

- an adapter implementation
- a runtime adapter resolver or selector
- a daemon or worker contract
- an AppShell command manifest
- an IPC session runtime
- a launcher, setup, or session boot plan
- a general-purpose bridge registry for all cross-domain or reporting links

The portable model must distinguish the following.

### Canonical Adapter Contract

Canonical adapter truth lives in a contract-bearing declaration that identifies the source contract, target contract, required capabilities, exclusions, failure semantics, and portability limits.
It defines what the adapter means, not how a runtime chooses or executes it.

### Adapter Implementation

An adapter implementation is the concrete code that realizes an adapter contract.
Examples in the live repo include `compat/data_format_loader.py`, `appshell/pack_verifier_adapter.py`, `client/render/render_model_adapter.py`, and `geo/projection/view_adapters.py`.
Those implementations are evidence for the contract shape, but their existence does not by itself prove present extraction readiness.

### Wrapper, Shim, and Transitional Surface

A wrapper may invoke or package deeper logic without being the canonical translation contract.
`appshell/compat_adapter.py` is a thin wrapper over product descriptor surfaces, and `tools/tool_surface_adapter.py` emits stable wrapper rows around governed subprocess tools.
`compat/shims/tool_shims.py` is explicitly a deprecation shim surface.
These are real and useful surfaces, but wrapper or shim status must remain explicit instead of being promoted into portable adapter truth by naming convenience.

### Product-Shell Command Surface

Launcher, setup, and AppShell command surfaces may expose adapters or adapter-shaped outputs, but a CLI command is not automatically a portable adapter contract.
For example, `tools/setup/setup_cli.py` uses `bridge_engine_payload` to re-express import and export engine results for command consumers.
That is a shell-facing bridge, not portable adapter law.

### Runtime Service Boundary

Some live surfaces are adapter-shaped but belong to runtime service ownership, not portable adapter truth.
`appshell/ipc/ipc_client.py`, `appshell/ipc/ipc_transport.py`, and `compat/handshake/handshake_engine.py` show negotiated attach, frame, and refusal behavior across local IPC boundaries.
Those files prove useful contract fields such as compatibility mode and refusal posture, but the service boundary itself remains Dominium-retained.

### Portable Adapters Now Versus Dominium-Retained Adapters

Portable now:

- the declaration shape for bounded source-to-target mediation
- the field set for capability, task, evidence/review, and policy linkage
- the explicit refusal, incompatibility, blocked, degraded, and fallback classes
- the rule that adapter existence does not imply permission, runtime availability, or completeness

Dominium-retained now:

- AppShell subprocess tool wrappers
- negotiated IPC attach and loopback transport flows
- render and projected-view adapters tied to Dominium runtime and UI models
- setup and launcher bridge payloads
- import alias bridges and remediation bridges
- validation coverage adapters and deprecation adapter inventories

## C. Portable Adapter Contract Fields

Every canonical portable adapter contract must specify the following fields.

- `adapter_id`
  Stable canonical identifier for the adapter contract itself.
  This identifies the mediation path and must remain stable across derived views and reports.

- `adapter_kind`
  The declared category of mediation the adapter performs.
  Repo-grounded kinds include contract-to-contract translation, format-version mediation, descriptor mediation, projection mediation, or wrapper-bound interface exposure.

- `source_interface`
  The authoritative source interface or source contract the adapter consumes.
  This must point to canonical contract identity or schema identity, not an informal UI label.

- `target_interface`
  The authoritative target interface or target contract the adapter produces or serves.
  This must likewise reference canonical identity rather than derived documentation prose.

- `adapter_purpose`
  A bounded statement of what the adapter translates, mediates, or normalizes.
  This prevents the contract from collapsing into a vague "bridge" claim.

- `capability_requirements`
  Capability classes that must be present for the adapter path to be valid.
  This is a declaration only; runtime capability resolution remains outside this artifact.

- `capability_exclusions`
  Capability classes, modes, or conditions that make the adapter path invalid or unsupported.
  This is required so the contract can model incompatibility explicitly rather than by hidden fallback.

- `task_linkage`
  Optional linkage to portable task kinds or task identifiers when the adapter only matters for certain task families.
  This links the adapter to work intent without turning the adapter contract into a scheduler.

- `evidence_review_linkage`
  Optional linkage to portable evidence or review requirements when the adapter emits evidence, consumes evidence, or requires review before use.
  This includes review gating for degraded or sensitive paths where applicable.

- `policy_permission_linkage`
  Optional linkage to policy or permission shapes when the adapter path is governed by declared access or approval posture.
  This field declares the dependency without making the adapter the policy engine.

- `compatibility_and_stability`
  Canonical compatibility notes, supported ranges, incompatibility boundaries, and stability class.
  This is where the adapter records whether it is stable, transitional, provisional, deprecated, or otherwise bounded.

- `failure_refusal_semantics`
  Declared failure classes the adapter may surface, including unsupported, incompatible, blocked, refused, degraded, ambiguous, or review-gated outcomes.
  These classes must be explicit so downstream systems can reason about them deterministically.

- `fallback_posture`
  Optional declaration of whether any degraded or fallback path exists and what class it belongs to.
  If no fallback is lawful, the contract should say so explicitly rather than imply silent substitution.

- `portability_limits`
  Explicit statement of what parts of the adapter are portable and what parts remain host-specific, product-specific, or runtime-owned.
  This is mandatory because the live repo contains many adapter-shaped surfaces that are not extractable now.

- `version_notes`
  Schema version, contract compatibility version, migration notes, or other explicit version markers for the adapter contract.
  These notes prevent silent reinterpretation when source or target contracts evolve.

## D. Required Boundary Distinctions

The portable adapter contract must preserve the following distinctions.

### Adapter Contract Versus Adapter Implementation

The contract states what mediation path means.
The implementation is the code that carries it out.
Portable extraction may reuse the former before it reuses the latter.

### Adapter Versus Wrapper

A wrapper exposes or packages an implementation for a consumer surface.
`tools/tool_surface_adapter.py` and `appshell/compat_adapter.py` show stable wrappers that are still local to AppShell and tool command surfaces.
A wrapper may embody an adapter path, but wrapper identity is not enough to define portable adapter law.

### Adapter Versus Shim

A shim preserves a legacy entrypoint or compatibility alias while steering callers elsewhere.
`compat/shims/tool_shims.py` is explicit about deterministic deprecation notices and replacement targets.
That is transitional compatibility posture, not portable adapter truth.

### Adapter Versus Runtime Resolver

A contract declares a valid mediation path.
A runtime resolver would choose among candidates, activate one, negotiate runtime state, or load it dynamically.
That resolver work is explicitly deferred.

### Adapter Compatibility Versus Capability Profile

Adapter compatibility states whether a particular source-to-target path is allowed.
Capability profiles declare what capability posture a subject or environment has.
Capability profiles may feed adapter requirements, but they do not replace adapter compatibility law.

### Adapter Permission Versus Adapter Existence

An adapter can exist even when its use is disallowed or review-gated.
Permission lives in the separate policy/permission shape frozen by `X-4`.
Existence does not grant lawful use.

### Canonical Adapter Contract Versus Derived UI and Reporting Summaries

Tool payload schemas, CLI summaries, dashboards, status views, and audit reports may present adapter information.
They may not redefine the canonical source, target, compatibility, or refusal truth of the adapter contract.

## E. Interaction With Prior Portable Contracts

The portable adapter contract links to earlier portable contracts as follows.

### Portable Task Contract

Contract linkage:

- adapters may declare `task_linkage` when a task requires a specific mediation path
- task contracts may point at adapter contracts when source and target interface translation is mandatory for completion

Runtime linkage not frozen here:

- task scheduling
- task-to-adapter selection order
- worker routing or execution orchestration

Deferred runtime work:

- runtime selection between competing adapters for the same task
- queueing or planner behavior based on adapter availability

### Evidence and Review Contract

Contract linkage:

- adapters may declare which evidence they emit, consume, or require
- adapters may declare whether degraded or sensitive paths require review

Runtime linkage not frozen here:

- evidence storage backends
- review workflow execution
- publish/promote/reclassify operations

Deferred runtime work:

- automatic evidence capture pipelines
- review workflow engines tied to adapter execution

### Policy and Permission Shape

Contract linkage:

- adapters may reference policy and permission identities that govern lawful use
- adapters may declare refusal, denial, escalation, or review posture without becoming the policy engine

Runtime linkage not frozen here:

- authorization services
- override execution
- live trust publication or revocation plumbing

Deferred runtime work:

- distributed permission resolution for adapter use
- runtime override procedures

### Capability Profile Shape

Contract linkage:

- adapters may declare capability requirements and exclusions
- capability profiles may establish whether a candidate environment is compatible with the adapter contract

Runtime linkage not frozen here:

- capability probing
- dynamic capability negotiation
- runtime degrade planning

Deferred runtime work:

- adapter resolution against live capability environments
- post-baseline adapter capability negotiation engines

## F. Repo-Grounded Rationale

The portable minimum frozen here is grounded in live repo evidence rather than future platform ambition.

- `compat/data_format_loader.py` is a real contract-to-contract mediator.
  It loads artifacts, applies migration rules, validates output, and emits explicit refusal classes such as missing migration, contract mismatch, and read-only unavailability.
  That directly supports freezing source and target contract identity, compatibility, and refusal semantics.

- `appshell/pack_verifier_adapter.py` is a real AppShell adapter implementation.
  It binds pack verification, trust-policy selection, deterministic output writing, and report shaping together.
  That supports freezing source and target linkage, evidence linkage, and policy linkage while leaving the shell-specific execution flow inside Dominium.

- `appshell/compat_adapter.py` shows a thin wrapper around deeper compat surfaces.
  It proves that adapter naming alone is insufficient and that wrapper layers must remain distinguishable from portable adapter law.

- `tools/tool_surface_adapter.py`, `schemas/tool_adapter_output.schema.json`, `tools/xstack/testx/tests/test_tool_adapter_offline.py`, and `tools/xstack/testx/tests/test_tool_adapter_uses_virtual_paths.py` prove that the repo already uses stable adapter-shaped rows and adapter output payloads.
  They also show why those rows are still local wrappers: they are offline-only, subprocess-bound, command-engine mediated, and virtual-path constrained.

- `compat/shims/tool_shims.py` and `tools/xstack/testx/tests/test_shims_emit_deterministic_warnings.py` prove that the repo distinguishes shims from real adapters.
  Shims carry deprecation identity, replacement targets, and warnings; they should not be silently promoted into portable adapter truth.

- `appshell/ipc/ipc_client.py`, `appshell/ipc/ipc_transport.py`, `compat/handshake/handshake_engine.py`, `tools/xstack/testx/tests/test_attach_requires_negotiation.py`, and `tools/xstack/testx/tests/test_unnegotiated_attach_refused.py` show negotiated runtime boundaries with explicit refusal when attach is attempted without negotiation.
  They justify portable blocked, incompatible, and refused classes while also proving that runtime transport ownership stays in Dominium.

- `tools/xstack/testx/tests/test_tool_incompatibility_refusal.py` proves the repo already surfaces deterministic incompatibility reason codes such as `refusal.tool.incompatible`.
  That is direct evidence that incompatibility must remain a first-class contract class.

- `client/render/render_model_adapter.py` and `geo/projection/view_adapters.py` prove that real model-to-model adapters exist in the repo.
  They are still tied to Dominium-specific truth, perceived, render, and projected-view layers, so they support the shape without proving current portability.

- `tools/setup/setup_cli.py` uses `bridge_engine_payload` to re-express engine outputs as shell-facing results.
  That is evidence for adapter-shaped bridging behavior, but it is a product-shell bridge, not portable adapter law.

- `tools/import_bridge.py`, `tools/controlx/core/remediation_bridge.py`, and `data/reality/cross_domain_bridge_registry.json` prove that bridges are broader than portable adapters.
  The bridge registry explicitly warns that a bridge is not equivalent to a runtime service boundary or shared code path, which reinforces the need for a narrow adapter contract.

- `validation/validation_engine.py` inventories live validation surfaces by `adapter_mode`, `active_adapter`, and `coverage_adapter`.
  That proves the repo already distinguishes active adapters from deprecated or coverage-only ones, which is why X-6 freezes shape and boundary law rather than treating all adapter-labeled surfaces as portable or complete.

- `templates/adapter_template.md` proves the repo already has a documented notion of adapter identity, legacy mapping, refusal behavior, determinism notes, and removal planning.
  X-6 carries forward the portable minimum from that evidence without inheriting the template's transitional repo-local assumptions wholesale.

## G. What Is Portable Now vs Not Portable Now

### Portable Now

The following elements are portable and worth freezing now:

- the canonical declaration that an adapter mediates one named source interface or contract into one named target interface or contract
- stable adapter identity and kind
- bounded purpose for the mediation path
- capability requirements and exclusions
- optional linkage to task, evidence/review, and policy/permission contracts
- explicit compatibility, stability, refusal, incompatibility, blocked, degraded, fallback, and ambiguity posture
- explicit portability limits and version notes
- the rule that adapter existence does not imply runtime availability, lawful use, or implementation completeness

### Dominium-Retained Now

The following remain Dominium-owned and must not be treated as portable adapter runtime now:

- AppShell command surfaces and subprocess tool adapters under `tools/tool_surface_adapter.py`
- tool wrapper output payload execution semantics under `schemas/tool_adapter_output.schema.json`
- `appshell/compat_adapter.py` and other shell-facing wrappers
- `appshell/pack_verifier_adapter.py` execution flow and output writing
- negotiated IPC and attach flows in `appshell/ipc/ipc_client.py`, `appshell/ipc/ipc_transport.py`, and related handshake helpers
- render and view adapters in `client/render/render_model_adapter.py` and `geo/projection/view_adapters.py`
- setup bridge payload translation in `tools/setup/setup_cli.py`
- import alias bridges in `tools/import_bridge.py`
- ControlX remediation bridges in `tools/controlx/core/remediation_bridge.py`
- validation adapter inventories and coverage adapters in `validation/validation_engine.py`
- deprecation shims in `compat/shims/tool_shims.py`

### Deferred Until After the Playable Baseline

The following are explicitly deferred:

- runtime adapter discovery and selection
- dynamic adapter loading or activation
- remote adapter registries or publication
- runtime capability-resolution engines for adapter choice
- queueing, scheduling, or worker routing tied to adapter execution
- bakeoff or compiler systems for adapter comparison or generation
- cross-repo adapter marketplaces or transport-agnostic adapter distribution

## H. Failure, Refusal, Incompatibility, and Fallback Model

Portable adapter contracts must make the following distinctions explicit.

- `unsupported_adapter_path`
  No lawful adapter path exists for the requested source and target combination.
  This is stronger than "not chosen yet"; it means the contract does not define a supported path.

- `incompatible_adapter_path`
  A candidate adapter exists, but capability, source, target, or version constraints do not match.
  `compat/data_format_loader.py` and `test_tool_incompatibility_refusal.py` show that the live repo already treats incompatibility as an explicit class.

- `blocked_adapter_path`
  The adapter is known, but a required precondition is missing.
  Examples include missing negotiation, missing descriptors, missing required artifacts, or other unmet non-policy prerequisites.

- `refused_adapter_path`
  The adapter path is rejected by declared policy, permission, trust, intent, or review posture even though the path is otherwise known.
  Refusal is a lawful outcome, not a generic error bucket.

- `degraded_or_fallback_adapter_path`
  A lower-fidelity or restricted path is allowed, but only when the contract declares it explicitly.
  Read-only or degraded compatibility modes are examples of this class.

- `ambiguous_adapter_selection`
  More than one candidate path exists and no canonical contract rule selects among them.
  This remains a first-class class because selection runtime is deferred.

- `review_gated_adapter_use`
  The adapter path exists but requires review, acknowledgement, approval, or escalation before lawful use.
  This class links directly to the `X-3` evidence and review contract.

These classes must remain reusable and distinct.
They must not be collapsed into a single generic failure or error posture.

## I. Canonical vs Derived Distinctions

Canonical adapter truth is:

- the adapter contract identity
- the source and target contract references
- the declared capability requirements and exclusions
- the declared task, evidence/review, and policy linkage
- the compatibility, refusal, fallback, and portability limits
- the version and stability markers

Derived adapter views include:

- CLI help text
- AppShell status views
- tool adapter payloads
- dashboard or audit summaries
- compatibility reports
- selector views and UI cards

Derived views may summarize canonical adapter truth.
They may not:

- redefine the source or target contract
- widen compatibility or fallback posture
- erase refusal or review requirements
- claim portability because a local wrapper exists
- reinterpret a shim, bridge, or transport surface as portable adapter law

## J. Anti-Patterns and Forbidden Shapes

The following shapes are forbidden for this artifact and later prompts that consume it:

- embedding runtime adapter engine semantics into the portable contract
- treating every wrapper as a portable adapter
- treating every shim or legacy bridge as a portable adapter
- assuming portability from file location or naming
- collapsing capability, permission, and adapter shape into one concept
- treating product-shell command rows as canonical adapter truth
- treating runtime transport, attach, or session flows as portable adapter contracts by default
- using derived payload schemas as proof of extraction readiness
- using X-6 to justify immediate broad adapter implementation or repo-wide renaming

## K. Stability and Evolution

Stability class:

- `stable`

Later prompts enabled by this artifact:

- the Codex repo operating contract prompt next
- later AIDE extraction review over which concrete adapter implementations are portable candidates versus Dominium-retained execution surfaces
- later mapping work that links portable tasks to portable adapters without inventing runtime selection machinery

This artifact must not change silently.
Any material change to adapter identity rules, field set, failure classes, portability boundaries, or prior-contract linkage requires an explicit follow-up artifact rather than drift by implementation convenience.
