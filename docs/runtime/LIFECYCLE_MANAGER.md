Status: CANONICAL
Last Reviewed: 2026-04-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Σ, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/FOUNDATION_READINESS_REPORT.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_SIGMAA1_PHIA2_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`, `specs/reality/SPEC_REPRESENTATION_LADDERS.md`, `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`, `specs/reality/SPEC_FORMALIZATION_CHAIN.md`, `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`

# Dominium Lifecycle Manager Model

## 1. Purpose and Scope

This document defines the constitutional lifecycle manager model for Dominium.
It exists because the completed `Λ` block froze semantic truth, sparse materialization, domain law, ownership law, bridge law, representation law, and formalization law, while `Φ-0` through `Φ-4` froze the kernel, component, service, domain-service binding, and state externalization layers without yet defining the lawful transition grammar for runtime-hosted structures over time.

The lifecycle manager model governs:

- what lifecycle management means in Dominium
- why lifecycle management is a distinct runtime law layer
- which runtime subjects may have lifecycle states or transitions
- which lifecycle states and transitions are constitutionally meaningful
- what lifecycle transitions must preserve across availability, quiescence, suspension, degradation, stop, retirement, and later handoff or replacement
- what later `Σ`, `Υ`, and `Ζ` work may rely on once explicit lifecycle law exists

This prompt is not:

- OS process supervision
- a scheduler implementation
- a hot-reload implementation
- a restartless update implementation
- a migration engine
- a live-ops control system
- a release rollout policy rewrite
- a semantic or governance rewrite

Checkpoint relation:

- the active execution path is `post-Λ / post-Σ-A / post-Φ-A2(binding + state law) / pre-Φ-5`
- `Φ-5` is the third deeper runtime doctrine prompt after `Φ-3` and `Φ-4`
- older planning artifacts may still retain stale numbering drift, but this document follows active checkpoint law rather than legacy sequence text

## 2. Core Definition

In Dominium, lifecycle management is the constitutional discipline that determines how bounded runtime subjects are declared, initialized, made available, activated, quiesced, suspended, resumed, degraded, stopped, retired, recovered, or later replaced without letting runtime transition convenience redefine truth, ownership, bridge legality, representation continuity, or state obligations.

Lifecycle management is a distinct layer because it answers questions that execution, persistence, and products do not answer by themselves:

- execution explains what a runtime subject does while it is running
- state externalization explains what must survive runtime locality
- bindings explain how services attach lawfully to domains
- lifecycle law explains how runtime subjects may change operational posture over time without unlawful semantic side effects

Lifecycle management is not:

- `OS process management`
  - process boundaries are implementation evidence, not the full constitutional lifecycle model
- `runtime execution alone`
  - execution does not by itself define when transition is lawful
- `persistence alone`
  - persistence is one continuity tool, not the lifecycle law
- `state externalization alone`
  - externalization constrains lifecycle, but it does not replace lifecycle transition law
- `product or session UX flow`
  - user-visible flow is not the same thing as runtime lifecycle legality
- `release rollout or control-plane operations`
  - release and control planes consume lifecycle law later; they do not define it here
- `live-ops or hot-swap implementations`
  - those are downstream consumers of lifecycle law

## 3. Why Lifecycle Law Is Necessary

Runtime subjects change posture over time.
They become available, active, blocked, degraded, quiescent, suspended, stopped, or retired.
Those changes matter because they alter availability, mutability envelopes, actor access, observability posture, replaceability, and continuity expectations.

Without explicit lifecycle law, the architecture is vulnerable to forbidden shortcuts:

- restart or reload treated as truth reset
- suspension treated as if the suspended subject has become semantically nonexistent
- degraded or blocked runtime posture silently reported as full lawful availability
- handoff or replacement silently bypassing ownership, bridge, or state rules
- product shell behavior redefining lifecycle truth because it is the currently visible flow

Lifecycle law is therefore necessary to keep runtime availability downstream of semantic law.
Lifecycle convenience must never redefine truth, ownership, or bridge legality.

## 4. Lifecycle Subjects

Lifecycle law applies to runtime subjects, not to semantic domains themselves.
The taxonomy is constitutional and intentionally general.

### 4.1 Kernel-Adjacent Runtime Structures

These are execution-hosting or execution-coordinating structures adjacent to kernel law.
They may expose activation, refusal, degradation, replay, checkpoint, and verification attach points.

### 4.2 Bounded Components

These are bounded runtime-facing functional units frozen by the component model.
They must remain lifecycle-addressable without being collapsed into modules, products, or domains.

### 4.3 Coordinated Services

These are bounded runtime coordination or mediation structures frozen by the service model.
They may have lifecycle posture because availability, quiescence, handoff, and degradation materially affect lawful runtime support.

### 4.4 Domain-Support Runtime Structures

These are runtime subjects whose purpose is to support lawful execution, validation, mediation, or observation over domain-grounded behavior without becoming domain owners.

### 4.5 Observation and Presentation Support Structures

These are runtime subjects that support observation, explanation, rendering, view synthesis, presentation, or diagnostics.
They may be lifecycle-managed, but their lifecycle does not redefine truth existence.

### 4.6 Control and Integration Structures

These are runtime subjects that coordinate negotiation, transport, routing, handoff, compatibility, or control-plane-adjacent mediation while remaining subordinate to semantic and lifecycle law.

### 4.7 Later Module Realizations

Later module realizations may embody lifecycle-managed subjects, but module layout alone does not define lifecycle identity.
Modules remain implementation evidence, not the constitutional lifecycle owner.

## 5. Lifecycle States

Lifecycle states describe runtime posture.
They do not describe ontology.
A subject may change lifecycle state without altering whether authoritative truth exists upstream.

The constitutional lifecycle state taxonomy is:

- `declared`
  - the subject is recognized and identified as a lawful runtime subject, but is not yet initialized
- `initialized`
  - prerequisites, identity, and lawful setup have been satisfied enough for runtime use to become possible
- `available`
  - the subject is ready for lawful activation or consumption under current constraints
- `active`
  - the subject is presently participating in lawful runtime work
- `quiescent`
  - the subject is not actively advancing work and is in a transition-safe or observation-safe posture
- `suspended`
  - the subject is temporarily halted from active progression while preserving explicitly required continuity conditions
- `degraded`
  - the subject remains lawful only under reduced, narrowed, or fallback behavior that must remain explicit
- `blocked`
  - the subject cannot lawfully activate or continue because constraints, authority, state, or dependencies forbid it
- `stopped`
  - the subject is no longer running or available for active work, but is not yet retired as a recognized runtime subject
- `retired`
  - the subject is intentionally withdrawn from future lawful activation within its current identity
- `failed`
  - the subject has entered an invalid or failed operational posture requiring explicit refusal, recovery, or retirement handling

State names may be refined later, but these distinctions may not be collapsed silently.

## 6. Lifecycle Transitions

Lifecycle transitions are lawful posture changes between lifecycle states.
They are constitutional transition classes, not implementation-specific procedures.

The transition taxonomy is:

- `declare`
  - establish the subject as a recognized lifecycle participant with explicit identity and boundary scope
- `initialize`
  - move from declared or stopped posture into a prepared runtime posture subject to prerequisites
- `make_available`
  - expose the initialized subject for lawful activation or bounded consumption
- `activate`
  - enter active runtime participation under current constraints
- `quiesce`
  - move from active or degraded posture into a transition-safe, pause-safe, or handoff-safe posture
- `suspend`
  - halt active progression temporarily while preserving required continuity and externalization conditions
- `resume`
  - return from suspended or quiescent posture into available or active posture only when legality is re-established
- `degrade`
  - narrow lawful operation explicitly under reduced capability, fidelity, throughput, or scope
- `recover`
  - restore a degraded, blocked, or failed subject into a lawful state only when the reasons for invalidity are resolved
- `block`
  - prevent activation or continued operation because prerequisites, authority, dependencies, or legality conditions are absent
- `stop`
  - end runtime participation without implying semantic erasure
- `retire`
  - explicitly end future lawful activation for the current subject identity
- `replace_or_handoff`
  - a later refinement target for continuity-preserving transfer or substitution that remains constrained by state, ownership, bridge, and provenance law

Lifecycle transitions are lawful only when the target posture, state handling, authority envelope, and continuity conditions are explicit.

## 7. Lifecycle and Truth

Lifecycle transitions must not redefine semantic truth.

The governing rules are:

- runtime availability does not equal truth existence
- active versus suspended posture does not erase authoritative truth
- stopped or failed runtime posture does not imply that the domain or the truth it owns has ceased to exist
- lifecycle transitions may change runtime access, throughput, or mutability posture, but they may not change semantic ontology by convenience
- truth continuity remains primary even when runtime subjects are unavailable

Availability is not ontology.
Lifecycle law is therefore downstream of truth law rather than a replacement for it.

## 8. Lifecycle and State Externalization

Lifecycle transitions must respect state externalization law.
No lifecycle transition is lawful if it traps authoritative or continuity-relevant state in an impermissible transient form.

The governing rules are:

- lifecycle legality depends on the correct distinction between authoritative truth state, lawful derived runtime-managed state, transient execution state, projection state, presentation state, provenance state, and binding or lifecycle support state
- quiesce, suspend, stop, replace, and handoff transitions must preserve any state that state law requires to remain externalizable or externalized
- transient execution state may be dropped only when state law permits it
- authoritative truth state may not be stranded inside a service, component, or product merely because a transition occurred
- degraded, failed, or blocked posture does not suspend externalization obligations

Lifecycle law therefore consumes state law rather than inventing its own hidden exceptions.

## 9. Lifecycle and Ownership

Lifecycle transitions must not silently alter semantic ownership.

- services, components, products, and control shells do not gain authority merely by being the currently active runtime subject
- currently active posture does not promote runtime locality into semantic ownership
- lifecycle transitions may not silently rebind authority from canonical roots to mirrors, caches, generated artifacts, or transitional facades
- ownership review remains binding during initialization, activation, suspension, replacement, stop, and retirement alike
- canonical versus projected or generated distinctions remain binding for lifecycle-managed surfaces

Lifecycle is therefore an operational posture grammar, not an ownership transfer grammar.

## 10. Lifecycle and Bridges

If lifecycle transitions affect cross-domain operations, bridge law remains binding.

The governing rules are:

- suspension, degradation, replacement, handoff, or recovery may not silently bypass cross-domain bridge legality
- a lifecycle transition affecting a bridge-mediated service or runtime subject must preserve participating-domain identity and the declared bridge invariants
- blocked or degraded bridge conditions may constrain lifecycle possibilities, including lawful activation, resume, replacement, or recovery
- shared runtime hosting, shared caches, or shared orchestration do not create bridge authority by convenience

Lifecycle transitions must therefore remain bridge-aware wherever their effects are bridge-mediated.

## 11. Lifecycle and Representation and Continuity

Lifecycle transitions must preserve representation-ladder invariants and lawful continuity where relevant.

The governing rules are:

- macro and micro continuity must remain lawful across suspend, resume, degrade, stop, recover, and later replace or handoff transitions
- lifecycle transitions must not fabricate arbitrary teleports, unexplained disappearances, or hidden replacements in represented reality
- if the active representation cannot support continuity claims, the system must expand, degrade explicitly, refuse explicitly, or preserve uncertainty explicitly
- representation-local runtime posture does not authorize semantic discontinuity
- continuity is a constitutional requirement, not a cosmetic presentation detail

Lifecycle law therefore inherits the representation discipline already frozen by `Λ`.

## 12. Lifecycle and Capability Surfaces

Lifecycle posture may affect capability availability.
It may not redefine capability semantics.

The governing rules are:

- lifecycle states may determine whether a capability surface is currently available, degraded, blocked, or refused
- lifecycle transitions may alter actor access posture or operational readiness
- capability semantics, actor classes, preconditions, and lawful outcomes remain upstream semantic law
- degraded or blocked lifecycle posture must remain visible rather than masquerading as full lawful invocation
- lifecycle convenience may not convert unavailable runtime posture into silent hidden capability removal or silent capability reinterpretation

Capability law remains upstream.
Lifecycle law only governs posture for runtime realization.

## 13. Lifecycle and Products

Products and shells may observe or consume lifecycle-managed structures.
They do not define lifecycle law.

The governing rules are:

- product UX, session flow, launcher flow, or operator flow must not redefine runtime lifecycle semantics
- product-visible availability is evidence of one access path, not proof of lifecycle legality in itself
- product convenience must not hide degraded, blocked, suspended, or failed lifecycle posture from runtime and governance doctrine
- user-facing session boundaries and runtime lifecycle boundaries may interact, but they are not interchangeable concepts

This preserves the distinction between product flow and runtime law.

## 14. Lifecycle and Future Live-Ops, Replacement, and Handoff Work

This prompt does not implement supervisors, hot-reload, restartless replacement, migration orchestration, or distributed authority transfer.
It defines the lifecycle law those later systems must consume.

The dependency rules are:

- later hot-swap or replacement work must preserve truth continuity, state externalization, ownership boundaries, bridge legality, and provenance continuity
- later restart and cutover work must distinguish stop, suspend, quiesce, retire, and replace semantics rather than treating them as one generic restart
- later migration work must remain downstream of lifecycle law and state law rather than improvising continuity contracts
- later distributed handoff work must preserve explicit authority envelopes and must not invent authority transfer by operational convenience
- later live-ops work must inherit lifecycle legality rather than overriding it under deployment pressure

Later `Ζ` work therefore depends on this lifecycle model instead of replacing it.

## 15. Lifecycle Invalidity and Failure

Lifecycle states and transitions may be invalid, unsafe, contested, or under-authorized.
Failures and degraded posture must remain explicit.

Framework-level invalidity and failure categories include:

- `lifecycle_unavailable`
  - the subject or required lifecycle transition surface does not currently exist for lawful use
- `initialization_invalid`
  - required setup, identity, compatibility, authority, or prerequisites were not satisfied
- `activation_blocked`
  - the subject cannot lawfully become active because dependencies, policy, or authority conditions are absent
- `quiescence_incomplete`
  - the subject cannot lawfully quiesce because required continuity or state-preservation obligations remain unresolved
- `suspension_illegal`
  - the subject cannot be suspended lawfully without violating truth, state, or bridge constraints
- `resume_invalid`
  - the subject cannot lawfully resume because the prior suspension or current prerequisites are invalid
- `degraded_only`
  - the subject may continue only in an explicitly degraded posture
- `recovery_blocked`
  - recovery is not presently lawful because failure causes or authority constraints remain unresolved
- `state_externalization_violation`
  - the transition would trap or lose required authoritative or continuity-relevant state
- `ownership_invalid`
  - the transition would rebind lifecycle meaning or authority to the wrong owner
- `bridge_invalid`
  - the transition would violate cross-domain bridge law
- `representation_continuity_break`
  - the transition would break representation or continuity invariants
- `formalization_or_provenance_break`
  - the transition would lose required lineage, revision posture, or formalized continuity
- `under_authorized_transition`
  - the subject exists, but the requested lifecycle transition is not lawful under the present authority envelope
- `contested_or_ambiguous_lifecycle`
  - competing lifecycle interpretations remain explicit and cannot be normalized away silently

Degraded operation must remain visibly degraded.
Recovery must remain constrained by explicit legality, not optimism.

## 16. Verification and Auditability

Lifecycle behavior must be auditable and testable in principle.
Later runtime, governance, interface, and live-ops systems must be able to reason about lifecycle posture explicitly.

At minimum, later systems should be able to verify:

- subject identity and subject class
- current lifecycle state and the transition path that produced it
- whether a transition preserved state-class obligations from the state externalization model
- whether ownership remained canonical and explicit during transition
- whether bridge legality was preserved where lifecycle effects cross domains
- whether degraded, blocked, suspended, stopped, failed, and active postures are explicitly distinguishable
- whether continuity and representation invariants were preserved
- whether recovery, replacement, or handoff claims remain lawful and attributable

Auditability requires more than a binary up or down flag.
Later diagnostics must be able to distinguish lifecycle failures from semantic-owner failures, bridge failures, continuity failures, and state-externalization failures.

## 17. Ownership and Anti-Reinvention Cautions

All checkpoint, ownership, and anti-reinvention cautions remain in force for lifecycle law.

### 17.1 `field/` versus `fields/`

- `fields/` remains the canonical semantic field substrate
- `field/` remains transitional and compatibility-facing
- lifecycle law may consume `field/` only as an adapter surface, never as the semantic owner

### 17.2 `schema/` versus `schemas/`

- `schema/` remains canonical contract law
- `schemas/` remains projection or validator-facing
- lifecycle legality must follow canonical schema law rather than mirror convenience

### 17.3 `packs/` versus `data/packs/`

- `packs/` remains canonical in runtime packaging, activation, compatibility, and distribution scope
- `data/packs/` remains authoritative in authored content and declaration scope
- lifecycle law must not flatten packaged activation, authored content identity, and release semantics into one root

### 17.4 Canonical versus projected or generated artifacts

- `specs/reality/**` outranks `data/reality/**` for semantic meaning
- `docs/planning/**` outranks planning JSON for checkpoint interpretation
- generated evidence under `build/**`, `artifacts/**`, `.xstack_cache/**`, and `run_meta/**` remains evidence only unless stronger doctrine explicitly promotes a specific form

### 17.5 Thin `runtime/` root

- the thin `runtime/` root is not automatically canonical by name
- lifecycle law must be extracted from the distributed runtime substrate and doctrine rather than rebound to one convenience root

### 17.6 Older planning numbering drift

- older planning artifacts still encode stale `Σ` and `Φ` numbering
- this document follows current checkpoint law rather than stale numbering drift
- later prompts must keep recording that drift explicitly where relevant

### 17.7 Extension over replacement

- this model is extracted from current repo reality and completed doctrine
- it does not authorize a greenfield lifecycle super-manager
- evidence-rich runtime surfaces remain `app`, `compat`, `control`, `core`, `net`, `process`, `server/runtime`, `server/persistence`, `engine`, and `game`
- semantic roots remain upstream inputs rather than runtime-owned truth

## 18. Anti-Patterns and Forbidden Shapes

The following lifecycle shapes are constitutionally forbidden:

- a service restart treated as a truth reset
- a suspended subject treated as semantically nonexistent
- a lifecycle transition that traps authoritative truth in transient execution state
- UI, launcher, or session flow used as lifecycle law
- replacement or handoff that bypasses ownership review or bridge law
- degraded posture silently treated as full lawful operation
- lifecycle semantics defined purely by one runtime implementation path
- lifecycle convenience used to promote projections, mirrors, or generated artifacts into canonical authority
- active runtime posture treated as permission to own semantic meaning
- stop, suspend, quiesce, retire, and replace semantics collapsed into one generic restart label

## 19. Stability and Evolution

This artifact is `provisional` and canonical.
It freezes the lifecycle floor for post-`Φ-4` deeper runtime doctrine without claiming that later orchestration and live-ops machinery is already implemented.

The governing evolution rules are:

- later prompts may refine lifecycle machinery explicitly, but they may not weaken semantic-law primacy, state law, ownership review, bridge law, representation continuity, or provenance continuity
- `Σ-3` may rely on this model for lifecycle-aware task classification
- `Σ-4` may rely on this model for exposing lifecycle-sensitive MCP and interface surfaces without ambiguous runtime guesses
- `Σ-5` may rely on this model for refusal, escalation, and safety logic around blocked, degraded, suspended, failed, replace, or handoff requests
- later `Υ` and `Ζ` work may rely on this model for restart, cutover, migration, replacement, rollback, canary, replay, and live-ops assumptions
- updates must remain explicit, reviewable, and non-silent

This document therefore answers the mandatory lifecycle questions for the current checkpoint:

- lifecycle management in Dominium is the law governing runtime posture changes over time for bounded runtime subjects
- it is necessary because runtime transition convenience must remain subordinate to truth, state, ownership, bridge, and continuity law
- runtime subjects with lifecycle posture include kernel-adjacent structures, components, services, domain-support structures, observation and presentation support structures, control and integration structures, and later module realizations
- lifecycle states and transitions exist constitutionally as explicit posture categories rather than as one implementation's process model
- lifecycle transitions remain lawful only when they preserve truth continuity, state externalization rules, ownership boundaries, bridge legality, representation continuity, and provenance where relevant
- this model now enables `Σ-3`, `Σ-4`, `Σ-5`, and later `Υ` and `Ζ` work to consume explicit lifecycle law instead of inventing it ad hoc
