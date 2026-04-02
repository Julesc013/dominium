Status: CANONICAL
Last Reviewed: 2026-04-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Φ, Σ, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/FOUNDATION_READINESS_REPORT.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_SIGMAA1_PHIA2_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`, `specs/reality/SPEC_REPRESENTATION_LADDERS.md`, `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`, `specs/reality/SPEC_FORMALIZATION_CHAIN.md`, `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`

# Dominium State Externalization Model

## 1. Purpose and Scope

This document defines the constitutional state externalization model for Dominium.
It exists because the completed `Λ` block froze total truth, sparse materialization, domain law, ownership law, representation law, formalization law, and bridge law, while `Φ-0` through `Φ-3` froze the runtime kernel, component, service, and domain-service binding layers without yet defining what runtime-relevant state must remain externalized or externalizable.

The state externalization model governs:

- what state externalization means in Dominium
- why state externalization is a distinct runtime/state boundary layer
- what kinds of state exist and which must remain externalized or externalizable
- what runtime layers may host transient state versus what they may not own authoritatively
- how ownership review, bridge law, representation ladders, formalization lineage, and runtime binding law constrain state handling
- what later `Φ`, `Σ`, `Υ`, and `Ζ` work may rely on once explicit state law exists

This prompt is not:

- a save or load implementation
- a snapshot implementation
- a replay-log implementation
- a migration engine
- a live-ops handoff implementation
- a storage-technology choice
- a doctrine rewrite of `Λ`, `Σ`, or release law

Checkpoint relation:

- the active execution path is `post-Λ / post-Σ-A / post-Φ-A2(binding model) / pre-Φ-4`
- `Φ-4` is the second deeper runtime doctrine prompt after `Φ-3`
- older planning artifacts may still retain stale numbering drift; this document follows active checkpoint law rather than legacy sequence text

## 2. Core Definition

In Dominium, state externalization is the declared constitutional discipline that determines which runtime-relevant state must remain outside transient hosting convenience, which state must remain externalizable even when not presently emitted, and how state may be exposed, transferred, persisted, replayed, reconstructed, audited, or handed off without reassigning semantic ownership or silently changing meaning.

State externalization is a distinct layer because it answers questions that domains, services, bindings, and storage technologies do not answer by themselves:

- domains define semantic truth classes, invariants, Processes, affordances, and ownership
- runtime layers host, coordinate, or expose state under law
- bindings define how services lawfully attach to domains
- state externalization defines what must survive runtime locality without becoming trapped inside it

State externalization is not:

- `truth itself`
  - truth remains the semantic reality owned by domain law
- `runtime execution context`
  - execution context may host state, but it does not define what must survive that context
- `caches`
  - caches are only one non-authoritative class of state
- `projected or generated artifacts`
  - projections and generated outputs may carry state evidence but do not become state authority by convenience
- `persistence formats or storage technologies`
  - format choice is downstream implementation detail
- `save files`
  - save files are one possible externalized artifact, not the law
- `snapshots`
  - snapshots are downstream consumers of state law
- `replay logs`
  - replay logs are downstream consumers of state law
- `product or UI state`
  - product-local state is not automatically authoritative semantic state

## 3. Why Externalization Is Necessary

State externalization is necessary because truth must not become trapped in transient runtime containers.

Without explicit externalization law, the architecture is vulnerable to forbidden shortcuts:

- services owning hidden irreplaceable truth because they happen to be where execution passes through
- products or UIs becoming de facto homes of authority because they materialize the current view
- caches, projections, or checkpoint helpers being promoted into truth by convenience
- replay, snapshot, migration, or handoff semantics being improvised later without a lawful state model
- domain-service bindings hiding ownership transitions that should remain explicit

Externalization is therefore required for:

- auditability
- continuity across process boundaries and runtime restarts
- lawful replay and deterministic verification
- replaceability of runtime containers and products
- correctness under sparse materialization
- explicit refusal, degradation, and invalidity instead of hidden fallback magic

## 4. State Classes

The state taxonomy is constitutional and intentionally general.
It defines state classes, not every concrete state store or file.

### 4.1 Authoritative Truth State

This is the domain-owned semantic state that participates directly in authoritative truth.
It includes domain commitments, authoritative facts, Process-relevant truth carriers, and any state whose meaning is governed by domain contracts rather than by runtime convenience.

Authoritative truth state remains domain-owned even when hosted, transformed, observed, persisted, replayed, or externally represented.

### 4.2 Lawful Derived Runtime-Managed State

This is runtime-managed state that is lawfully derived from authoritative truth, lawful inputs, or deterministic Process progression and is needed to support execution, mediation, validation, or coordination.

It may be essential for runtime continuity, but it is not the semantic owner of truth.
If it cannot be treated as purely transient, it must remain externalizable or reconstructable under explicit law.

### 4.3 Transient Execution State

This is in-flight, activation-local, quiescence-local, or step-local state used for bounded execution.
Examples include ephemeral work queues, temporary handles, reductions, scratch buffers, and non-authoritative runtime bookkeeping.

Transient execution state is lawful only when it is explicitly transient and not the sole home of irreplaceable semantic commitments.

### 4.4 Cache and Projection State

This is memoized, indexed, summarized, generated, mirrored, compatibility-facing, or projection-facing state that exists to accelerate access, support inspection, or adapt one surface to another.

Cache and projection state is explicitly non-authoritative.
It may be useful, but it may not silently become canonical truth or override the owning semantic root.

### 4.5 Observation and Presentation State

This is perceived, observed, rendered, UI-facing, control-facing, or operator-facing state derived from authoritative or lawful runtime-managed state for display, reporting, explanation, or interaction.

Observation and presentation state may be externalized as evidence, views, diagnostics, or operator artifacts.
It does not redefine truth.

### 4.6 Control-Plane and Operator-Visible State

This is runtime status, refusal posture, compatibility posture, health, diagnostics, negotiation state, activation posture, or other operator-visible control information.

It may be crucial for operations and audit, but it does not become semantic truth merely because it is visible to operators.

### 4.7 Provenance and Lineage Support State

This is state that preserves identity, revision posture, deterministic hashes, audit trails, refusal evidence, lineage anchors, or formalization support required to explain how authoritative or runtime-managed state came to be.

It is not a substitute for truth itself, but it is required whenever lineage, accountability, or proof obligations apply.

### 4.8 Binding and Lifecycle Support State

This is state that supports lawful activation, quiescence, attach, detach, handoff, replay-anchor attachment, or service-domain binding continuity.

It must remain subordinate to binding law and state law.
It does not authorize a service, product, or runtime shell to become a hidden truth owner.

## 5. Externalization Requirements

State classes have different constitutional requirements.
Those requirements must be explicit rather than inferred from implementation habit.

The core requirement categories are:

- `must be externalizable`
  - the state must be expressible outside one transient runtime container without semantic loss beyond declared lawful limits
- `must be externalized when crossing persistence, replay, snapshot, migration, handoff, audit, or proof boundaries`
  - if the system relies on the state beyond one live transient execution scope, the state must be emitted lawfully
- `must be reconstructable`
  - if a state class is not directly externalized, later systems must be able to reconstruct it lawfully from authoritative externalized state plus declared rules
- `explicitly transient`
  - the state is permitted to remain local only when its non-authoritative and temporary nature is explicit
- `explicitly non-authoritative`
  - the state may inform runtime behavior or operators, but it must not redefine domain truth

The class-level rules are:

- authoritative truth state must be externalizable
- authoritative truth state must not exist only as hidden service-local, component-local, or product-local memory
- authoritative truth state must be externalized whenever persistence, replay, snapshot, migration, cross-process handoff, or audit proof depends on it
- lawful derived runtime-managed state must be externalizable or deterministically reconstructable from authoritative state and declared laws
- transient execution state may remain local only when it is explicitly transient and losing it does not erase authoritative commitments
- cache and projection state must remain reconstructable, discardable, and explicitly non-authoritative
- observation and presentation state may be externalized as evidence or views, but only as non-authoritative derivatives
- control-plane and operator-visible state must remain externalizable where audit, refusal, degradation, or continuity obligations depend on it
- provenance and lineage support state must be externalized whenever identity, revision posture, auditability, or formalization lineage is required
- binding and lifecycle support state must remain externalizable whenever lifecycle continuity, handoff legality, or binding legality depends on it

Externalization therefore does not mean "persist everything all the time."
It means the architecture must know what cannot be trapped inside convenience state.

## 6. State Ownership

Domains own semantic truth according to domain law.
Runtime layers may host, transform, expose, validate, route, or externalize state under law, but they do not become semantic owners by doing so.

The governing ownership rules are:

- domains remain the owners of authoritative truth state
- kernel, components, services, bindings, products, and tools may host state under law but may not silently become owners of authoritative truth
- ownership review remains binding for state surfaces just as it remains binding for semantic and binding surfaces
- canonical versus projected or generated distinctions remain binding for state artifacts
- runtime convenience may not reassign authority across roots
- no service, component, product, cache, or projection may become the sole irreplaceable home of authoritative truth

State externalization therefore preserves semantic ownership while making runtime continuity lawful.

## 7. State and Kernel, Component, Service, and Binding Layers

The completed runtime stack remains valid.
State externalization does not replace it; it constrains how each runtime layer may host and expose state.

- the kernel may host authoritative execution, deterministic progression, coordination hooks, and externalization attach points, but the kernel is not the semantic owner of truth
- components may host bounded functional state, temporary execution state, and lawful derived runtime-managed state inside their scope, but they may not hide authoritative truth as private component-local fact
- services may host coordination state, mediation state, compatibility state, and bounded runtime-managed state, but they may not own hidden authoritative truth or silently absorb domain meaning
- bindings define how service-hosted or service-mediated state remains attached to lawful domain authority and to bridge law where scope crosses domains
- products may host input state, view state, session state, and presentation state, but they may not redefine truth or become truth homes by convenience

Binding law matters here because cross-domain or multi-layer state interactions must remain bridge-aware, ownership-aware, and canonical-target-aware.
State externalization may not be used to hide a binding violation inside a persistence helper or product shell.

## 8. State and Truth, Perceived, and Render Separation

Truth state remains distinct from perceived state and rendered state.
State externalization must preserve that separation.

- authoritative truth state is not the same thing as perceived observations of truth
- perceived or observed state is not the same thing as rendered or presented state
- observation and presentation state may be externalized for diagnostics, audit, user interfaces, or operator workflows, but those externalized forms remain downstream of truth
- runtime systems must not treat the currently visible, currently cached, or currently rendered state as permission to redefine authoritative semantic state

Externalization must therefore preserve the constitution's truth/perceived/render split instead of collapsing it into "whatever was on screen" or "whatever the service last held."

## 9. State and Representation Ladders

State may participate in multiple lawful representations.
State externalization must remain representation-aware.

The governing rules are:

- externalized state must preserve ladder invariants and lineage rather than pretending one materialized form is the whole reality
- macro and micro state transitions must not silently fabricate, erase, or reinterpret protected meaning
- summary forms may be externalized lawfully, but they must not be treated as permission to improvise latent detail as though it were already authoritative truth
- substituted or collapsed forms remain lawful only under declared substitution and expansion rules
- if the active representation cannot answer the required lawful question set, the system must expand, refuse, degrade explicitly, or preserve uncertainty explicitly
- state externalization must not normalize sparse materialization into partial-truth doctrine

State law therefore inherits representation-ladder discipline.
Externalized state is still representation-bound, lineage-bound, and scope-bound.

## 10. State and Formalization and Provenance

Some state semantics depend on explicit formalization lineage, standards, protocols, institutional records, revision posture, or other provenance-bearing structures.
State externalization must preserve that lineage whenever it matters.

The governing rules are:

- externalized state must preserve identity, revision posture, provenance, and supersession lineage where those are part of the state's lawful meaning
- formalized artifacts, standards, protocols, and institutional records may constrain what counts as valid externalized state
- revision, migration, or supersession must not silently erase lineage
- services and products must not treat informal guesses as equivalent to formalized structures where the domain requires formality
- provenance support state may be distinct from authoritative truth state, but it remains required whenever proof, audit, compatibility, or institutional continuity depends on it

Later release, migration, provenance, and live-ops work must consume this requirement rather than inventing lineage rules ad hoc.

## 11. State and Bridges

Cross-domain state interactions must respect bridge law.
State externalization may not hide cross-domain coupling or ownership transitions.

The governing rules are:

- if authoritative or runtime-managed state crosses domain boundaries, the relevant bridge law must already exist
- no service, persistence helper, cache, replay surface, or product shell may create hidden cross-domain state authority by convenience
- bridge-mediated state flows must preserve participating-domain identity, domain ownership, bridge invariants, and representation discipline
- externalized state that spans more than one domain must remain decomposable into local domain meaning plus explicit bridge-mediated relationship meaning
- bindings remain bridge-aware when service-domain interaction carries state across domain boundaries

Cross-domain state law is therefore never "just storage."
It remains semantic bridge law consumed through runtime/state discipline.

## 12. State and Lifecycle, Replay, Persistence, Snapshot, and Migration Work

This prompt does not implement persistence, replay, snapshot, migration, lifecycle, or live-ops systems.
It defines the state law those later systems must consume.

The dependency rules are:

- lifecycle work must distinguish what state may be dropped at quiescence from what must remain externalizable for lawful resume or handoff
- replay work must distinguish authoritative truth state, lawful derived runtime-managed state, and presentation evidence instead of collapsing them together
- snapshot work must follow state-class and externalization rules rather than inventing snapshot scope by convenience
- migration work must preserve identity, compatibility posture, provenance, and ownership distinctions rather than silently rewriting truth
- live-ops handoff or cutover work must preserve bridge legality, lineage, and externalization requirements under real deployment pressure

Later `Φ-5` and later `Υ` and `Ζ` work are therefore enabled by this state model, not authorized to replace it.

## 13. State Invalidity and Failure

Not all state is always lawful for authoritative use.
Invalidity, degradation, and refusal conditions must remain explicit.

Framework-level failure and invalidity categories include:

- `state_unavailable`
  - required state is absent for the current lawful scope
- `state_stale`
  - the state exists but no longer satisfies freshness, continuity, or revision requirements
- `state_incomplete`
  - required portions of lawful state are missing
- `projected_only_state`
  - only a projection, mirror, or generated derivative is present and canonical authoritative use is therefore invalid
- `transient_only_state`
  - the state exists only inside a transient runtime container when externalization or reconstructability is required
- `ownership_invalid`
  - the state is bound to the wrong semantic owner or ignores ownership review outcomes
- `bridge_invalid`
  - the state crosses domain boundaries without lawful bridge support
- `representation_invalid`
  - the current representation horizon cannot lawfully support the required use
- `formalization_or_provenance_invalid`
  - identity, lineage, standard, protocol, or revision posture requirements are not satisfied
- `determinism_or_process_invalid`
  - the state cannot be used lawfully without violating Process-only mutation, replay equivalence, or deterministic ordering
- `unsafe_or_under_authorized`
  - the state may exist but may not be used under the present authority or safety envelope

Systems must not silently upgrade projected, transient, stale, or incomplete state into authoritative truth.

## 14. Verification and Auditability

State externalization must be auditable and testable in principle.
Later runtime, governance, interface, and release systems must be able to reason about state classes and externalization posture explicitly.

At minimum, later systems should be able to verify:

- whether a state surface is authoritative truth, lawful derived runtime-managed state, transient execution state, projection or cache state, or presentation state
- whether ownership remains consistent with domain law and ownership review
- whether cross-domain state handling is lawful under bridge doctrine
- whether representation and scaling rules were preserved
- whether provenance and formalization requirements were preserved where relevant
- whether reconstructability claims are true
- whether transient state was kept within explicitly transient boundaries
- whether products, services, or caches have attempted to become hidden truth owners

Auditability requires attribution.
Later diagnostics must be able to distinguish semantic-owner faults, bridge faults, representation faults, runtime-hosting faults, and projection-only faults rather than reporting one generic persistence failure.

## 15. Ownership and Anti-Reinvention Cautions

All checkpoint, ownership, and anti-reinvention cautions remain in force for state law.

### 15.1 `field/` versus `fields/`

- `fields/` remains the canonical semantic field substrate
- `field/` remains a transitional compatibility facade
- state externalization may not treat `field/` as the semantic owner merely because it is easier for runtime consumption

### 15.2 `schema/` versus `schemas/`

- `schema/` remains canonical semantic contract law
- `schemas/` remains validator-facing or projection-facing
- externalized state meaning must remain pinned to canonical schema law rather than to validation convenience

### 15.3 `packs/` versus `data/packs/`

- `packs/` remains canonical for runtime packaging, activation, compatibility, and distribution-descriptor scope
- `data/packs/` remains authoritative for authored pack content and declaration scope
- state law must not flatten authored content meaning, activation state, and distribution identity into one root by convenience

### 15.4 Canonical versus projected or generated artifacts

- canonical semantic and planning artifacts outrank projections, mirrors, and generated evidence
- generated outputs under `build/**`, `artifacts/**`, `.xstack_cache/**`, and `run_meta/**` remain evidence only unless stronger doctrine promotes them
- projected or generated state must not be treated as canonical merely because it is already materialized

### 15.5 Thin `runtime/` root caution

- a thin `runtime/` root name does not automatically establish state authority
- runtime-local presence is evidence of hosting, not proof of semantic ownership

### 15.6 Older planning numbering drift

- stale sequence text in older planning artifacts does not override active checkpoint law
- state law must be extracted from current doctrine and repo reality rather than reinvented greenfield to match legacy numbering habits

## 16. Anti-Patterns and Forbidden Shapes

The following shapes are forbidden unless stronger doctrine explicitly authorizes them, which this prompt does not do:

- service-local hidden truth state treated as the only real authoritative state
- product or UI state treated as authoritative truth because it is the most visible materialization
- cache, projection, mirror, or generated state silently promoted to canonical authority
- replay, snapshot, migration, or save semantics invented without reference to explicit state law
- cross-domain state coupling hidden inside convenience runtime code, persistence helpers, or product shells
- state externalization defined by one storage technology rather than by constitutional law
- state continuity depending on undocumented transient memory that cannot be lawfully externalized or reconstructed
- binding or lifecycle support state treated as permission to transfer domain ownership into services
- sparse materialization misread as permission to externalize only the currently rendered slice and discard the rest of lawful truth

## 17. Stability and Evolution

This artifact is `provisional` and canonical.
It freezes the first constitutional runtime/state model after `Φ-3` without claiming that the later implementation machinery is complete.

The governing evolution rules are:

- later prompts may refine this model explicitly, but they may not silently weaken semantic-law primacy, ownership review, bridge law, provenance law, or canonical-versus-projected distinctions
- `Φ-5` may rely on this model for lifecycle transitions, attach and detach legality, quiescence, handoff, and continuity boundaries
- `Σ-3` through `Σ-5` may rely on this model for task classification, MCP and interface exposure boundaries, and safety-policy refusal logic
- later `Υ` and `Ζ` work may rely on this model for replay, restart, cutover, publication, provenance, archive, and live-ops assumptions
- updates must remain explicit, reviewable, and non-silent

This document therefore answers the mandatory runtime/state questions for the current checkpoint:

- state externalization is the law that keeps authoritative and continuity-relevant state from becoming trapped inside transient runtime locality
- it is necessary because domains, services, bindings, and products do not by themselves define what state must survive lawful continuity
- runtime layers may host transient or derived state under law, but they may not own hidden authoritative truth
- ownership review, bridge law, representation ladders, and provenance constrain state just as they constrain domains and bindings
- later `Φ-5`, `Σ-3`, `Σ-4`, `Σ-5`, `Υ`, and `Ζ` work are now authorized to consume explicit state law rather than inventing it ad hoc
