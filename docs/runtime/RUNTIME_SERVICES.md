Status: CANONICAL
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Φ, Σ, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_SIGMA0_PHIA1_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`, `specs/reality/SPEC_CAPABILITY_SURFACES.md`, `specs/reality/SPEC_REPRESENTATION_LADDERS.md`, `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`, `specs/reality/SPEC_FORMALIZATION_CHAIN.md`, `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`

# Dominium Runtime Services

## 1. Purpose and Scope

This document defines the constitutional runtime service model for Dominium.
It exists so later runtime, governance, task, and operational work can reason about coordinated runtime mediation structures without collapsing the architecture into one generic orchestrator, one product-facing feature layer, or one implicit service graph defined only by code adjacency.

The service model answers a narrower question than the semantic constitution, the runtime kernel model, and the component model.
The completed `Λ` block defines reality, law, representation, formalization, player-desire, ownership, and bridge doctrine.
`Σ-0` defines repository governance and authority discipline.
`Φ-0` defines the runtime kernel as the constitutional execution host.
`Φ-1` defines components as bounded runtime-facing functional units.
This document defines the next layer: the coordinated runtime-facing service structures that may compose, host, mediate, or expose components while remaining subordinate to kernel law and semantic law.

This prompt does not yet define:

- concrete service implementations
- orchestration machinery
- domain-service bindings in detail
- lifecycle machinery
- state externalization
- event-log, snapshot, or replay implementation structure
- module loading behavior

Those remain later prompts.

## 2. Core Definition

In Dominium, a runtime service is a bounded coordinated runtime-facing mediation or hosting structure that composes, coordinates, routes through, or exposes component behavior within kernel law and under upstream semantic and governance constraints.

Services are a distinct layer because they solve a coordination problem that other layers do not:

- the kernel is the constitutional execution host, not the layer that names or organizes every runtime-facing coordination structure
- components are bounded functional units, not the orchestration or mediation structures that combine them
- modules are implementation and discovery surfaces, not the architectural meaning of runtime coordination
- domains are semantic units governed by domain contracts, not runtime mediation structures
- products are consumption and hosting surfaces, not reusable runtime service boundaries
- packs and content are declarative semantic expansion surfaces, not runtime services
- tools are operator-facing or diagnostic consumers, not the canonical service layer
- control-plane and release-plane surfaces govern build, packaging, publication, and trust, not authoritative runtime mediation

Services therefore sit downstream of kernel and component law as the architectural unit of coordinated runtime behavior.

## 3. Service Role in the Architecture

Within the architecture, services are coordinated runtime-facing execution and mediation structures.
They consume kernel law, component law, semantic doctrine, and governance doctrine.
They do not own ontology, law, or canonical repository authority.

Their architectural role is to:

- coordinate bounded runtime behavior across one or more components
- expose declared runtime capabilities within lawful boundaries
- mediate runtime-facing access, routing, synchronization, inspection, persistence support, or policy enforcement
- provide a future carrier for lifecycle, state, observability, replay, and validation refinement
- provide stable runtime boundary vocabulary for later governance mirrors and task mapping

Services are therefore bounded orchestration and hosting layers, not ontological owners.

## 4. Service Responsibilities

At the constitutional level, runtime services are responsible for:

- coordinating bounded runtime behavior within kernel and component law
- exposing declared runtime capabilities within lawful boundaries
- respecting kernel boundaries, component boundaries, and semantic-law inputs
- respecting domain ownership and explicit cross-domain bridge law
- maintaining truth, perceived, and render separation in service behavior
- supporting later observability, validation, lifecycle, replay, and state-externalization refinement
- enabling lawful product consumption without redefining semantics
- supporting explicit refusal, degradation, capability, and compatibility behavior where doctrine requires it

Services may coordinate runtime behavior inside their declared scope.
They may not coordinate by silently inventing new semantic law or authority.

## 5. Service Non-Responsibilities

Services must not own or silently redefine:

- semantic ontology, including Assemblies, Fields, Processes, Law, or domain meaning
- domain ownership truth or domain contract law
- canonical governance law or repository authority ordering
- product-shell semantics, UI meaning, or presentation truth
- release, publication, archive, or trust policy meaning
- implicit cross-domain bridge authority
- arbitrary reinterpretation of capability surfaces
- convenience-based rebinding across canonical, projection, transitional, or quarantined roots

If a service boundary requires new semantics, that meaning must be defined in doctrine first.
Services may host and coordinate lawful runtime behavior.
They may not become semantic owners.

## 6. Service Classes

The service taxonomy is constitutional and intentionally broad.
It is meant to support the live distributed runtime substrate and later refinement without overfitting to one implementation lineage.

### 6.1 Execution Coordination Services

These services coordinate bounded execution-facing runtime behavior such as scheduling, work routing, deterministic progression, or controlled host mediation across runtime units.

Representative evidence roots include:

- `engine/modules/execution`
- `server/runtime`
- `app`
- `core/schedule`

### 6.2 Observation and Inspection Services

These services support lawful observation, inspection, proof, or audit mediation over runtime behavior without becoming truth owners or UI-only abstractions.

Representative evidence roots include:

- `control/view`
- `control/proof`
- `client/observability`
- replay and inspection surfaces in `engine` and `app`

### 6.3 Presentation-Support Services

These services coordinate presentation-adjacent runtime support behavior while remaining subordinate to truth/perceived/render separation.

Representative evidence roots include:

- `app/ui_event_log.c`
- `engine/modules/view`
- `engine/modules/ui`
- `client/presentation`

### 6.4 Control and Integration Services

These services coordinate negotiation, transport, handoff, descriptor exchange, compatibility routing, or other explicit runtime integration behavior.

Representative evidence roots include:

- `compat`
- `control`
- `net`
- `server/net`

### 6.5 Persistence and Replay-Support Services

These services support persistence-facing, replay-facing, or checkpoint-facing runtime mediation without yet defining the later explicit state externalization or snapshot system.

Representative evidence roots include:

- `server/persistence`
- `engine/modules/replay`
- checkpoint and event surfaces in `engine` and `app`

### 6.6 Compatibility and Policy-Support Services

These services coordinate runtime compatibility, refusal, degradation, handshake, negotiation, or runtime policy mediation.

Representative evidence roots include:

- `compat/descriptor`
- `compat/handshake`
- `compat/negotiation`
- `net/policies`

### 6.7 Domain-Support Services

These services support lawful execution, observation, or coordination over specific domain families without erasing domain ownership or explicit bridge law.

Representative evidence roots include:

- `control/planning`
- `process`
- `core`
- `game/core/execution`

### 6.8 Product-Support Services

These services support lawful runtime mediation required by products while remaining distinct from the products themselves.
They exist so product consumption can stay structured without letting one shell’s needs define service law.

Representative evidence roots include:

- `app`
- `server/runtime`
- `server/net`
- `client/interaction`

These classes are not final instance lists or cluster declarations.
They are the constitutional class vocabulary later prompts must refine.

## 7. Service Boundaries

Service boundary discipline is mandatory.
Services exist precisely so later runtime work can avoid hidden super-domains, hidden super-products, or one generic orchestrator that swallows all responsibility.

At the constitutional level:

- services may depend on kernel law, bounded components, canonical semantic contracts, explicit policies, and explicit registries where their scope requires it
- services may expose bounded runtime capabilities, coordination surfaces, diagnostics, compatibility or refusal interfaces, and product-consumable runtime mediation surfaces
- services may coordinate multiple components without erasing component identity
- services may mediate runtime behavior over multiple domains only through explicit ownership- and bridge-aware boundaries

Services must not:

- become hidden semantic or authority owners
- treat product-shell convenience as service identity authority
- bind through ambiguous ownership roots because they are easier to consume
- collapse component, module, domain, and product semantics into one boundary
- behave as if code adjacency proves service unity

Service boundaries matter because later lifecycle, state, loader, replay, and live-ops work need stable units of runtime coordination rather than ad hoc orchestration clusters.

## 8. Service Relationship to Components

Services are not identical to components.

Components remain bounded runtime-facing functional units.
Services may compose, coordinate, host, route through, or expose components, but service law must not collapse component distinctions.

The architectural consequences are:

- a service may involve multiple components
- a service may expose runtime behavior built from component collaboration
- a service may host component attach points or mediation surfaces
- a component does not become a service merely because it is important or widely consumed

## 9. Service Relationship to Modules

Services are not identical to modules.

Modules remain implementation, packaging, or discovery surfaces.
A service may be realized by one module, several modules, or a set of module surfaces distributed across roots.

Therefore:

- module layout is evidence for service extraction, not automatic constitutional truth
- discovery or loader details remain later work
- services must be defined by explicit boundary meaning rather than folder names or build artifacts

## 10. Service Relationship to Domains

Domains remain semantic units governed by domain contracts and the completed `Λ` law.
Services may support execution, observation, interaction, persistence support, or coordination over domain-grounded behavior, but they must not erase domain ownership or invent bridge law.

Domain-support services must therefore remain:

- ownership-aware
- bridge-aware
- representation-aware
- capability-surface-aware
- formalization-aware where standards, policies, or institutional forms matter

Detailed domain-service binding is deferred to later `Φ-3`.

## 11. Service Relationship to Products

Products are not services.
Client, server, launcher, setup, tools, and appshell consume or host services through lawful boundaries, but product convenience must not redefine service semantics.

Services therefore must not:

- be named purely by one product shell’s UX needs
- derive identity only from one consuming product
- let shell-local presentation or interaction concerns redefine their runtime meaning

Products may consume services.
They do not own service law by default.

## 12. Service Relationship to Capability Surfaces

Services may help realize capability-surface invocation paths, but they must not redefine capability surfaces into UI-only, command-only, or shell-only abstractions.

Services must therefore respect:

- actor classes
- preconditions
- law-gated outcomes
- refusal visibility
- domain-grounded substrate

Capability surfaces remain upstream semantic law.
Services only help realize them at runtime.

## 13. Service Relationship to State, Lifecycle, and Replay

Exact state externalization, lifecycle, event/log, and snapshot doctrine remain later work.
Even so, services must be shaped so those later prompts can reason about them explicitly.

At a minimum, service boundaries should remain compatible with later declaration of:

- service activation and quiescence conditions
- attach, detach, and handoff behavior
- explicit lifecycle transitions
- state externalization boundaries
- replay and event/log integration points
- snapshot and checkpoint support boundaries

This is a future-compatibility requirement, not an implementation commitment.

## 14. Service Relationship to Observability and Validation

Services must be diagnosable, auditable, and validation-friendly.
They must support targeted runtime accountability instead of disappearing into one generic orchestrator or one product shell.

Later prompts may define exact mechanisms, but the constitutional expectation is already fixed:

- service boundaries must support targeted validation
- diagnostics must be attributable to service scope
- compatibility, refusal, and degradation issues must be traceable
- service behavior must remain auditable against kernel, component, and semantic inputs

## 15. Ownership and Anti-Reinvention Cautions

All checkpoint, ownership, and anti-reinvention cautions remain in force for the service model.

Service law must remain explicitly cautious about:

- `field/` versus `fields/`, where `fields/` remains the canonical semantic field substrate
- `schema/` versus `schemas/`, where schema law remains canonical and projections remain subordinate
- `packs/` versus `data/packs/`, where packaged activation scope and authored declaration scope are not interchangeable
- generated and mirrored surfaces under `build`, `artifacts`, `.xstack_cache`, and `run_meta`, which remain evidence only
- the thin `runtime/` root, which is not automatically canonical merely because of its name
- older planning artifacts that still contain Φ numbering or order drift and must not override the current checkpoint law

The service model must therefore extend and extract from live repo embodiment rather than imagining a clean-room organization.
Evidence-rich service substrate roots include:

- `control`
- `compat`
- `core`
- `net`
- `process`
- `server/runtime`
- `server/persistence`
- `app`
- `engine`
- `game`

Those roots are evidence for service boundaries.
They are not permission to ignore semantic law, kernel law, component law, or ownership law.

Continuity note:

- older planning artifacts still label `RUNTIME_SERVICES-0` as `Φ-4`
- the current checkpoint path explicitly advances this service doctrine as `Φ-2`
- this artifact follows the current checkpoint law and does not silently normalize the historical numbering drift

## 16. Anti-Patterns and Forbidden Shapes

The following service shapes are constitutionally forbidden:

- a service treated as a semantic owner
- a service treated as a catch-all synonym for component, module, domain, or product
- a service defined purely by product UX or shell convenience
- a service silently owning cross-domain bridge law
- a service created only from code adjacency rather than explicit boundary meaning
- a service bypassing ownership review or canonical-versus-projection distinctions
- a service that lets one generic orchestrator swallow all runtime concerns
- a service that reinterprets capability surfaces into shell-local commands
- a service that derives identity only from build targets, package names, or directory prominence

## 17. Stability and Evolution

This artifact is a provisional but canonical runtime doctrine.
It is stable enough to close the early `Φ-A1` boundary trio and to serve as input to later runtime, governance, and operational work, but it is expected to be refined by explicit doctrine rather than silent code drift.

The immediate downstream consumers are:

- `Σ-1`
- `Σ-2`
- `Φ-3`
- `Φ-4`
- `Φ-5`

Later prompts may extend domain-service binding, lifecycle, state externalization, event/logging, replay, snapshot, and policy behavior, but they must not contradict the service boundary law established here.
Later Υ and Ζ work may also rely on explicit service boundaries when reasoning about release, compatibility, migration, cutover, restart, or live-ops behavior.

## 18. Direct Constitutional Answers

1. A runtime service in Dominium is a bounded coordinated runtime-facing mediation or hosting structure that composes, coordinates, routes through, or exposes component behavior within kernel law.
2. A service is distinct from a component, module, domain, or product because components are bounded functional units, modules implement behavior, domains define semantic law, and products consume services through shell boundaries.
3. A service may coordinate bounded runtime behavior, expose declared runtime capabilities, host component collaboration, and support later lifecycle, observability, replay, persistence, and policy refinement within its declared scope.
4. A service may not own semantic truth, domain ownership, canonical governance law, implicit bridge law, product-shell meaning, or canonical/projection rebinding authority.
5. Services relate to semantic doctrine, kernel law, and component law by consuming upstream semantic contracts, operating within kernel law, and coordinating bounded components without collapsing their distinctions.
6. The relevant ownership cautions remain `field/` versus `fields/`, `schema/` versus `schemas/`, `packs/` versus `data/packs/`, generated evidence roots, the non-canonical status of the thin `runtime/` root, and the older Φ numbering drift that the current checkpoint law overrides locally.
7. This service model now enables `Σ-1`, `Σ-2`, and later `Φ-3..Φ-5` to consume stable runtime service boundaries without inventing them ad hoc.
