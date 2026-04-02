Status: CANONICAL
Last Reviewed: 2026-04-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Φ, Σ, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_SIGMAA1_PHIA2_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`, `specs/reality/SPEC_CAPABILITY_SURFACES.md`, `specs/reality/SPEC_REPRESENTATION_LADDERS.md`, `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`, `specs/reality/SPEC_FORMALIZATION_CHAIN.md`, `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`

# Dominium Domain Service Binding Model

## 1. Purpose and Scope

This document defines the constitutional domain-service binding model for Dominium.
It exists because the completed `Λ` block froze domain law, ownership law, bridge law, capability law, representation law, and formalization law, while `Φ-0` through `Φ-2` froze the runtime kernel, component, and service layers without yet defining how services lawfully attach to semantic domains.

The domain-service binding model governs:

- what a domain-service binding is
- why bindings are a distinct runtime/semantic boundary layer
- what services may bind to and under what conditions
- what services may not redefine through binding
- how ownership review, cross-domain bridge law, capability surfaces, representation ladders, and formalization lineage constrain bindings
- what later `Φ`, `Σ`, `Υ`, and `Ζ` work may rely on once binding law is explicit

This prompt is not:

- a concrete service implementation matrix
- a service orchestration implementation
- state externalization doctrine
- lifecycle machinery doctrine
- module-loader doctrine
- product UX law
- a semantic rewrite of `Λ`

Checkpoint relation:

- the active checkpoint is `post-Λ / post-Σ-A / post-Φ-A1 / post-C-ΣA1ΦA2 / pre-Φ-3`
- `Φ-3` is the first deeper runtime doctrine prompt after checkpoint `C-ΣA1ΦA2`
- older planning artifacts still contain stale `Φ` numbering; this document follows the active checkpoint path and does not normalize legacy numbering drift into authority

## 2. Core Definition

In Dominium, a domain-service binding is a declared, auditable runtime/semantic boundary contract by which a bounded runtime service may support, mediate, observe, validate, externalization support, or coordinate behavior over one or more semantic domains while remaining subordinate to domain contracts, ownership law, bridge law, capability law, representation law, and formalization lineage.

Bindings are a distinct layer because they answer a question that neither domains nor services answer alone:

- domains define semantic truth, lawful Process structure, affordances, observation bindings, interface posture, verification, and scaling expectations
- services define bounded runtime-facing coordination and mediation structures
- bindings define the lawful attachment grammar between those two layers

A domain-service binding is not:

- `domain ownership`
  - domains remain the semantic owners of their truth classes, invariants, and contracts
- `cross-domain bridge law`
  - bridges govern lawful domain-to-domain interaction; bindings consume bridge law when service scope crosses domains
- `the runtime service model`
  - the service model defines service classes and service boundaries; bindings define lawful semantic attachment for service scope
- `the component model`
  - components may realize service internals, but component identity is not the same thing as binding law
- `module loading or module layout`
  - module structure is implementation evidence, not constitutional binding authority
- `product integration`
  - products consume or host services; product convenience does not define binding legality
- `UI, control, or input binding`
  - UI/control bindings map presentation or invocation paths onto lawful surfaces; they do not define the service-domain relationship beneath them

## 3. Why Bindings Are Necessary

Bindings are necessary because domains and services are constitutionally different kinds of things.

- domains are semantic units governed by domain contracts
- services are runtime units governed by kernel, component, and service doctrine
- neither layer may absorb the role of the other

Without an explicit binding layer, the architecture is vulnerable to forbidden shortcuts:

- services silently owning domains because they are the easiest execution path
- runtime convenience redefining semantic scope
- one hidden super-service spanning multiple domains without declared bridge law
- code adjacency or shared modules being treated as semantic authority
- projected or generated artifacts being treated as primary binding targets because they are easier to consume
- product shells normalizing away domain distinctions

Lawful execution therefore requires a declared binding layer.
Hidden binding by convenience is a semantic hazard and a runtime hazard.

## 4. Binding Elements

At the constitutional level, every domain-service binding must be expressible in terms of explicit binding elements.

Each binding may specify:

- `binding identity`
  - a stable binding identifier, summary, and stated scope
- `service side`
  - the service boundary, service class, and runtime responsibility being exercised
- `domain side`
  - the domain or domain family being bound, plus the canonical domain contracts or semantic artifacts that govern it
- `binding class`
  - the class of service-domain relationship being declared
- `binding scope`
  - whether the binding is local to one domain, spans multiple representations of one domain, or crosses domains through bridge law
- `allowed operation or coordination classes`
  - what kinds of service behavior the binding lawfully supports
- `required semantic inputs`
  - the upstream contracts, capability surfaces, observation bindings, representation rules, formalization stages, or bridge declarations the binding depends on
- `required authority and ownership checks`
  - what ownership review outcomes, canonical-vs-projection distinctions, and authority constraints must hold before the binding is lawful
- `bridge dependencies`
  - whether explicit cross-domain bridge law is required and which bridge class or directionality constrains the binding
- `capability-surface implications`
  - which capability surfaces are supported, constrained, or routed through by the binding
- `representation and scaling implications`
  - which representations, summary forms, substitution rules, macro/micro horizons, expansion triggers, or refusal conditions constrain the binding
- `formalization and provenance implications`
  - which standards, blueprints, protocols, institutional forms, lineage records, or validation stages are required
- `canonical versus projected artifact expectations`
  - which roots are semantic owners and which are operational mirrors, registries, or evidence only
- `failure, degradation, refusal, and invalidity conditions`
  - the conditions under which the binding is unavailable, blocked, degraded, unsafe, or invalid
- `verification and observability hooks`
  - what later runtime, validation, or governance work must be able to inspect, test, or audit

Bindings may be specialized later.
They may not skip these categories by implementation convenience.

## 5. Ownership and Authority

Bindings do not erase domain ownership.
They do not promote services into semantic owners.
They do not reassign authority across roots by convenience.

The governing authority rules are:

- services remain subordinate to semantic law
- services may bind only to lawful semantic authority, not to the easiest mirror, cache, projection, or generated echo
- bindings must respect the completed semantic ownership review
- bindings may consume derived registries operationally only when the canonical owner remains explicit and upstream
- bindings may not silently convert a transitional or compatibility facade into the semantic owner
- bindings may not let natural-language phrasing, mirror wording, product wording, or code layout outrank canonical repo doctrine

Services may lawfully bind to:

- canonical domain contracts
- domain-declared observation bindings
- domain-grounded capability surfaces
- domain-declared verification hooks
- domain-declared representation and substitution rules
- domain-relevant formalization artifacts where the domain requires explicit formalization
- explicit cross-domain bridge declarations when the service effect crosses domain boundaries
- machine-readable operational registries only when canonical prose or canonical schema law already establishes their semantic owner

Services may not lawfully bind by default to:

- generated evidence trees under `build/**`, `artifacts/**`, `.xstack_cache/**`, or `run_meta/**`
- validator-facing or projection-facing mirrors as if they were semantic owners
- directory prominence or product-shell locality alone
- shared code paths or import adjacency alone
- stale planning numbering or sequence text as if it overrode active checkpoint law

## 6. Binding Classes

The binding-class taxonomy is constitutional and intentionally broad.
It is not a final instance catalog.

### 6.1 Observation Bindings

These bindings let services support lawful observation, inspection, measurement, audit, or view mediation over a domain.
They must remain downstream of truth and of domain-declared observation bindings.
They must not treat observation summaries as truth structure.

### 6.2 Execution and Coordination Bindings

These bindings let services route or coordinate lawful Process execution over a domain within kernel and service law.
They may host invocation, scheduling, routing, or coordination behavior.
They must not reinterpret what the domain's Processes mean.

### 6.3 Mediation Bindings

These bindings let services mediate access, synchronization, routing, or bounded service-to-domain interaction over lawful domain structure.
They are runtime mediation surfaces, not semantic ownership transfers.

### 6.4 Transformation and Process-Support Bindings

These bindings let services support representation transitions, lawful expansion or collapse, substitution support, or domain-relevant process envelopes.
They must remain representation-aware and invariant-preserving.
They may not hide semantic ascent, descent, or substitution law inside runtime convenience.

### 6.5 Inspection and Validation Bindings

These bindings let services support proof, validation, invariant checking, or compliance-oriented runtime mediation for a domain.
They must remain anchored to domain verification obligations rather than inventing new semantic criteria ad hoc.

### 6.6 Persistence and Replay-Support Bindings

These bindings let services support provenance-preserving save, replay, audit, externalization support, or synchronization support over domain truth.
They do not make persistence or replay surfaces the semantic owners of the domain.
Exact state externalization doctrine remains later `Φ-4` work.

### 6.7 Policy and Compatibility Bindings

These bindings let services support refusal, degradation, compatibility, negotiation, policy mediation, or authority-envelope enforcement over domain-facing operations.
They do not authorize services to redefine capability meaning, schema law, or contract identity.

### 6.8 Bridge-Mediated Bindings

These bindings let services coordinate behavior that lawfully touches more than one domain.
They are valid only when explicit bridge law already exists for the cross-domain effect.
They do not create bridge authority by runtime convenience.

Binding classes are orthogonal to service classes.
One service class may participate in several binding classes, and one binding class may be realized through more than one service class.

## 7. Binding Directionality and Scope

Binding directionality and scope must be explicit.
They must never be inferred from implementation convenience.

Scope categories include:

- `single-domain local`
  - the service binds to one domain contract family only
- `single-domain multi-representation`
  - the service binds to multiple lawful representations of one domain without leaving that domain's ownership
- `bridge-mediated cross-domain`
  - the service affects or coordinates more than one domain and therefore requires explicit bridge law
- `anchor-to-many support`
  - the service attaches to multiple domains through a shared support grammar such as observation, persistence, or interface mediation without owning any of them

Directionality categories include:

- `service-to-domain support`
  - the service depends on domain law to decide what runtime coordination is lawful
- `domain-to-service constraint`
  - domain state, law, or representation horizon constrains what the service may expose or do
- `bidirectional asymmetric`
  - both runtime directions exist, but semantic authority remains upstream and asymmetric
- `bridge-mediated`
  - cross-domain directionality follows the declared bridge directionality, not a service-local assumption

Directionality does not imply shared ownership.
Bidirectionality does not imply that a service may redefine the domain in return.

## 8. Binding Relationship to Capability Surfaces

Bindings may support capability-surface invocation paths.
They may not redefine capability semantics.

The governing rules are:

- capability surfaces remain upstream semantic action law
- a binding may declare how a service supports invocation, routing, refusal propagation, diagnostics, validation, or automation mediation for a capability surface
- a binding may constrain service behavior based on actor classes, preconditions, epistemic scope, authorization, detectability, or usability distinctions already frozen by capability law
- a binding may not reinterpret capability surfaces into UI-only buttons, shell-local verbs, or hidden superpowers
- a binding may not collapse capability existence, detectability, usability, and authorization into one runtime shortcut
- a binding may not let service mediation bypass Process-only mutation or law-gated authority

Services may help realize lawful action.
They may not decide what lawful action means.

## 9. Binding Relationship to Representation Ladders

Bindings may attach to domains at different lawful representation horizons.
They must remain lawful across representation transitions.

This means:

- a service may bind against primitive, recognized, formalized, substituted, macro, or micro representations only when the relevant invariants and horizon conditions are explicit
- a binding must not assume that one currently materialized representation is the only real domain state
- a binding must preserve macro/micro continuity, substitution legality, and expansion or refusal conditions
- a binding may depend on summary forms, but it may not treat summaries as permission to improvise latent truth
- a binding may be representation-local for one horizon while still remaining subordinate to the domain's full ladder law
- if the active representation cannot answer the lawful service question set, the binding must require expansion, preserve uncertainty, degrade explicitly, or refuse explicitly

Bindings therefore inherit ladder discipline.
They may not turn representation convenience into semantic authority.

## 10. Binding Relationship to the Formalization Chain

Some bindings depend directly on formalization lineage.
Others do not.
The dependency must be explicit.

Where a domain requires formalization, a binding may depend on:

- discovery or recognition status
- explicit capture and specification
- validation and testing posture
- standards, protocols, or certification
- institutional adoption
- revision, supersession, or retirement lineage

The governing rules are:

- services must not treat informal guesses as equivalent to formalized structures when the domain requires formality
- services must not grant standard, protocol, blueprint, or institutional status by runtime convenience
- bindings that depend on formalized artifacts must preserve lineage, compatibility posture, provenance, and revision identity
- formalization may stabilize a binding or constrain it, but it does not erase domain distinction
- revision, supersession, deprecation, or local-only status must remain explicit rather than handwaved into one winner

Formalization lineage matters because services may support runtime execution over explicit standards, procedures, and institutions without becoming the author of those forms.

## 11. Binding Relationship to Cross-Domain Bridges

If a service operation crosses domain boundaries, bridge law must be explicit.

The governing rules are:

- a service may not create hidden cross-domain bridges by runtime convenience
- a bridge-mediated binding must declare the participating domains, the relevant bridge class, and the relevant bridge directionality or invariant expectations
- a service may support domain interaction only through ownership-aware and bridge-aware boundaries
- shared code, shared data structures, shared caches, or shared service hosting do not themselves create bridge legality
- bridge-mediated bindings must preserve canonical domain ownership, bridge invariants, representation discipline, capability legality, and provenance
- a bridge-mediated binding should be decomposable into local domain bindings plus the explicit bridge dependency that lawfully couples them

Bridge law remains upstream semantic law.
Binding law tells services how to consume it without replacing it.

## 12. Binding Relationship to Components and Modules

Bindings are not identical to components or modules.

The governing distinctions are:

- components remain bounded runtime-facing functional units
- services may compose, host, route through, or expose components
- bindings define how a service scope lawfully attaches to semantic domain law
- modules remain implementation, packaging, or discovery surfaces
- later loader mechanics remain later `Φ` work

Therefore:

- component identity does not by itself determine binding law
- module layout, import structure, or build targets are evidence only
- bindings may be realized by one component, several components, one module, or many modules without any of those implementation facts becoming constitutional authority
- bindings must be declared from runtime/semantic boundary meaning rather than folder names or shell placement

## 13. Binding Relationship to Products and Interface Surfaces

Products may consume bound services.
Products do not define binding law.

The governing rules are:

- product shells such as client, server, launcher, setup, tools, and appshell may host or consume services through lawful bindings
- product convenience must not normalize away domain distinctions
- product UX wording must not become semantic or binding law
- UI, control, or remote-operation adapters may map onto capability surfaces and service operations, but those adapters are not the same thing as domain-service bindings
- interface adaptation changes the access path, not the owning domain or the legality of the underlying binding

This preserves interface-agnostic reality and prevents shell-local semantics from colonizing runtime law.

## 14. Failure and Invalidity

Bindings may be lawful, degraded, blocked, unsafe, contested, or invalid.
Services must not assume that every binding is always legal or available.

Framework-level failure and invalidity categories include:

- `binding_unavailable`
  - the required binding is absent for the current service or domain scope
- `binding_degraded`
  - the binding remains lawful only in a reduced or explicitly degraded form
- `binding_blocked`
  - the binding is presently blocked by state, authority, compatibility, or activation conditions
- `binding_unsafe`
  - the binding would violate safety, compliance, or hazard constraints
- `under_authorized`
  - the required authority, legitimacy, entitlement, or actor envelope is absent
- `ownership_invalid`
  - the binding targets the wrong semantic owner or ignores ownership review outcomes
- `canonical_target_invalid`
  - the binding treats a projection, mirror, generated artifact, or transitional facade as the semantic owner without explicit higher doctrine
- `bridge_invalid`
  - a cross-domain effect is attempted without lawful bridge support or with the wrong bridge directionality or class
- `capability_surface_misalignment`
  - the binding would reinterpret or bypass capability semantics, preconditions, actor classes, or Process routing
- `representation_scale_mismatch`
  - the active representation horizon is insufficient for lawful service behavior
- `formalization_prerequisite_missing`
  - the binding depends on a formalized artifact, protocol, standard, or institution that does not exist or is not in the required stage
- `provenance_or_lineage_break`
  - the binding would lose required history, identity, revision lineage, or auditability
- `determinism_or_process_violation`
  - the binding would require mutation, ordering, or routing behavior that violates deterministic Process law
- `contested_or_ambiguous_binding`
  - competing interpretations remain explicit and cannot be silently normalized away

Failure, degradation, refusal, and invalidity must remain explicit.
Silent success by convenience is forbidden.

## 15. Verification and Observability

Bindings must be auditable and testable in principle.
Later runtime, governance, validation, and interface systems must be able to reason about them explicitly.

At minimum, later systems should be able to verify:

- service-to-domain attachment references are explicit
- ownership legality and semantic-owner correctness
- canonical-versus-projection adherence
- bridge legality where scope crosses domains
- capability-surface alignment
- representation and scaling consistency
- formalization and provenance prerequisites where relevant
- refusal, degradation, block, and invalidity paths
- traceability back to kernel, component, service, and domain doctrine

Observability consequences include:

- bindings should support service-scoped diagnostics instead of disappearing into one generic orchestrator
- audit surfaces should be able to distinguish semantic-owner errors from runtime-hosting errors
- bridge-mediated bindings should be inspectable as bridge-mediated rather than presented as local service magic
- later registries, validators, task catalogs, MCP exposure surfaces, and safety policy should be able to consume machine-readable binding structure

## 16. Ownership and Anti-Reinvention Cautions

All checkpoint, ownership, and anti-reinvention cautions remain in force for this binding model.

### 16.1 `field/` versus `fields/`

- `fields/` remains the canonical semantic field substrate
- `field/` remains transitional and compatibility-facing
- services may consume `field/` only as an adapter surface, never as the owning semantic field substrate

### 16.2 `schema/` versus `schemas/`

- `schema/` remains canonical semantic contract law
- `schemas/` remains validator-facing or projection-facing
- bindings must follow canonical schema law rather than projection convenience

### 16.3 `packs/` versus `data/packs/`

- `packs/` remains canonical in runtime packaging, activation, compatibility, and distribution scope
- `data/packs/` remains authoritative in authored pack content and declaration scope
- binding law must not flatten authored content meaning, runtime activation, and release identity into one root

### 16.4 Canonical versus projected or generated artifacts

- `specs/reality/**` outranks `data/reality/**` for semantic meaning
- `docs/planning/**` outranks planning JSON for checkpoint and execution interpretation
- generated evidence under `build/**`, `artifacts/**`, `.xstack_cache/**`, and `run_meta/**` remains non-canonical unless stronger doctrine explicitly promotes a specific emitted form

### 16.5 Thin `runtime/` root

- the thin `runtime/` root is not automatically canonical by name
- domain-service binding law must be extracted from the distributed runtime substrate and the semantic constitution, not rebound to one convenience root

### 16.6 Older planning numbering drift

- older planning artifacts still label `Φ-3` differently
- this document follows active checkpoint law rather than stale numbering drift
- later prompts must keep recording that drift explicitly where relevant

### 16.7 Extension over replacement

- this model is extracted from current repo reality and completed doctrine
- it is not a greenfield replacement architecture
- runtime evidence roots such as `app`, `compat`, `control`, `core`, `net`, `process`, `server/runtime`, `server/persistence`, `engine`, and `game` remain extension surfaces
- semantic roots such as `reality`, `worldgen`, `geo`, `materials`, `logic`, `signals`, `system`, `universe`, `epistemics`, `diegetics`, `infrastructure`, and `machines` remain upstream semantic inputs rather than runtime-owned truth

## 17. Anti-Patterns and Forbidden Shapes

The following binding shapes are constitutionally forbidden:

- a service binding directly to a convenient mirror rather than the canonical semantic owner
- a service silently owning domain meaning through runtime mediation
- a binding that crosses domain boundaries without explicit bridge law
- a binding inferred from code adjacency alone
- a binding defined by product UX semantics rather than semantic/runtime law
- a bridge-mediated binding treated as if it were local direct authority
- projected or generated artifacts treated as primary semantic binding targets by default
- a hidden super-service that swallows multiple domains without declared ownership and bridge discipline
- a binding that lets capability surfaces be reinterpreted into shell-local commands or UI-only toggles
- a binding that assumes one representation is the only real domain state
- a binding that grants standard, protocol, or institutional status by runtime convenience
- a binding that silently normalizes ownership-sensitive split roots into one certainty

## 18. Stability and Evolution

This artifact is a provisional but canonical runtime/semantic boundary doctrine.
It is stable enough to govern deeper `Φ` work and downstream `Σ`, `Υ`, and `Ζ` consumption, but it is expected to be refined by explicit doctrine rather than silent code drift.

This artifact enables:

- `Φ-4` to define state externalization boundaries without letting persistence surfaces become semantic owners
- `Φ-5` to define lifecycle transitions without hiding domain ownership or bridge obligations inside service startup or shutdown
- `Σ-3` to freeze task catalog entries against explicit domain-service binding vocabulary
- `Σ-4` to expose MCP and related interfaces against bounded binding law rather than unstable runtime guesses
- `Σ-5` to harden safety policy against explicit binding hazards instead of vague early-`Φ` assumptions
- later `Υ` and `Ζ` work to preserve provenance, compatibility, restart, cutover, and live-ops behavior without redefining semantic ownership

Later work may:

- define machine-readable binding declarations and validators
- map concrete services onto concrete domains using this model
- refine binding-aware state externalization, lifecycle, snapshot, replay, and interface policy
- add domain-specific or service-specific binding specializations that inherit this floor

Later work may not:

- redefine domain ownership, capability meaning, bridge law, or formalization law through runtime binding
- treat services as semantic owners
- promote projections or generated artifacts into binding authority by convenience
- treat product shells or UI wording as binding law
- hide cross-domain coupling inside service implementation details
- silently rewrite this model through code adjacency or implementation drift

Updates must remain explicit, review-aware, and non-silent.

## 19. Direct Constitutional Answers

### 19.1 What is a domain-service binding in Dominium?

A domain-service binding is the declared runtime/semantic boundary contract that states how a bounded runtime service may lawfully support or mediate behavior over a domain while remaining subordinate to the domain's semantic law.

### 19.2 Why is a binding model necessary if domains and services already exist?

Because domains and services solve different architectural problems.
Domains define semantic truth and law.
Services define bounded runtime coordination.
Bindings are the explicit law that stops services from silently becoming domain owners or hidden bridge authorities.

### 19.3 What may services bind to, and under what conditions?

Services may bind to canonical domain contracts, domain-grounded capability surfaces, domain-declared observation and verification bindings, domain representation rules, formalization artifacts where required, and explicit bridge declarations for cross-domain effects.
They may do so only when ownership review, canonical-vs-projection discipline, capability legality, representation discipline, formalization prerequisites, and bridge law all remain satisfied.

### 19.4 What may services not redefine through binding?

Services may not redefine semantic truth, domain ownership, capability meaning, bridge law, representation law, formalization lineage, canonical root ownership, or product-shell semantics through binding.

### 19.5 How do ownership review and cross-domain bridge law constrain bindings?

Ownership review determines which roots are the semantic owners and which are transitional, projected, or generated.
Bindings must target the semantic owners and respect those distinctions.
If the service scope crosses domains, explicit bridge law remains mandatory and the binding must consume that law rather than invent it.

### 19.6 How do bindings interact with capability surfaces, representation ladders, and formalization?

Bindings may support capability invocation and validation paths, but capability surfaces remain upstream semantic action law.
Bindings may attach at different representation horizons, but ladder invariants, substitution rules, and macro/micro continuity remain binding.
Bindings may depend on formalization stages, standards, blueprints, protocols, or institutions where required, but services may not grant those statuses by convenience.

### 19.7 What later prompts does this now enable?

This artifact directly enables `Φ-4`, `Φ-5`, and later `Σ-3` through `Σ-5` to reason about state boundaries, lifecycle, task catalogs, MCP exposure, and safety policy using explicit domain-service binding law instead of unstable placeholder assumptions.
