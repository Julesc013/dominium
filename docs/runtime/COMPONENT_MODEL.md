Status: CANONICAL
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Φ, Σ, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_SIGMA0_PHIA1_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`, `specs/reality/SPEC_CAPABILITY_SURFACES.md`, `specs/reality/SPEC_REPRESENTATION_LADDERS.md`, `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`, `specs/reality/SPEC_FORMALIZATION_CHAIN.md`, `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`

# Dominium Component Model

## 1. Purpose and Scope

This document defines the constitutional component model for Dominium.
It exists so early and later runtime work can reason about bounded runtime-facing functional units without collapsing the architecture into "everything is a service", "everything is a module", or "everything is a product feature".

The component model solves a narrower problem than the semantic constitution and a different problem than the runtime kernel model.
The completed `Λ` block defines reality meaning, domain law, representation law, formalization law, bridge law, and ownership law.
`Σ-0` defines repository governance and authority discipline.
`Φ-0` defines the runtime kernel as the constitutional execution host.
This document defines the next layer: the bounded units that later services, loaders, lifecycle work, task mapping, and runtime governance can reason about explicitly.

This prompt does not yet define:

- the full service model
- the module loader
- concrete component instances
- exact lifecycle state machines
- concrete service or product implementations

Those remain later runtime work.

## 2. Core Definition

In Dominium, a component is a bounded runtime-facing functional unit with explicit identity, declared responsibility scope, declared upstream inputs, and declared boundary expectations, operating inside kernel law and beneath product shells.

Components are a distinct layer because they solve a structural problem that other layers do not:

- the kernel is the constitutional host for lawful execution, not the unit of runtime capability ownership
- services are later orchestration and coordination structures, not the basic bounded unit they compose
- modules are implementation and discovery surfaces, not the architectural meaning of the functionality they realize
- domains are semantic units with contracts and law, not runtime grouping abstractions
- products are consumption and hosting surfaces, not reusable runtime capability units
- packs and content are data- and registry-driven semantic expansion surfaces, not runtime components
- tools and mirrors are operator-facing or derived surfaces, not the canonical runtime unit of responsibility

Components therefore sit between kernel law and later service orchestration as the runtime-capability unit that can be identified, reasoned about, validated, composed, and governed.

## 3. Component Role in the Architecture

Within the architecture, components serve as bounded runtime-facing functional units.
They are part of runtime host structure, not semantic law.

Their architectural role is to:

- expose declared functionality within the kernel boundary
- consume upstream semantic contracts, governance constraints, and runtime policy inputs
- provide a stable unit that later service, loader, lifecycle, validation, and release work can reason about
- support explicit attachment points between runtime execution and product or operator consumption surfaces

Components are therefore runtime-meaningful without becoming semantic owners.
They host and support lawful execution, observation, compatibility, persistence, or coordination behavior, but they do not define what reality means.

## 4. Component Responsibilities

At the constitutional level, components are responsible for:

- exposing declared functionality within kernel law and lawful execution boundaries
- consuming required semantic contracts, policies, compatibility declarations, and runtime constraints explicitly
- preserving declared invariants relevant to their scope
- remaining compatible with truth, perceived, and render separation
- maintaining bounded dependency and exposure surfaces
- supporting explicit capability, compatibility, and identity declaration
- supporting later observability, audit, validation, and lifecycle refinement
- participating in explicit refusal, degradation, and compatibility behavior where required by doctrine

Components may own runtime behavior inside their declared boundary.
They may not own semantic truth outside it.

## 5. Component Non-Responsibilities

Components must not own or silently redefine:

- semantic ontology, including Assemblies, Fields, Processes, Law, or domain meaning
- domain ownership truth or domain contract law
- canonical governance law or repository authority ordering
- product-shell semantics, UI meaning, or presentation truth
- release, publication, archive, or trust policy meaning
- arbitrary cross-domain bridge law
- semantic ownership classification across roots
- convenience-based authority reassignment from canonical to projected, generated, or quarantined surfaces

If a component boundary requires new semantic meaning, that meaning must be added through doctrine first.
Components may host lawful execution and integration.
They may not invent runtime ontology.

## 6. Component Classes

The constitutional component taxonomy is intentionally broad.
It is meant to support current repo embodiment and later refinement without overfitting to one implementation lineage.

### 6.1 Platform Components

Platform components provide bounded runtime-facing adaptation to platform, environment, process-host, or system capability surfaces.
They remain subordinate to kernel law and must not let OS or host convenience redefine truth or authority semantics.

Representative evidence roots include:

- `engine/modules/system`
- `engine/modules/sys`
- `client/adapters`

### 6.2 Execution and Runtime Substrate Components

These components provide bounded execution-facing capabilities that support scheduling, deterministic work execution, state coordination, process execution, or runtime host integrity.

Representative evidence roots include:

- `engine/modules/execution`
- `engine/modules/core`
- `app`
- `core`
- `process`
- `server/runtime`

### 6.3 Observation and Presentation-Support Components

These components support lawful projection, observation, diagnostics, or presentation-adjacent runtime behavior without becoming UI truth owners.

Representative evidence roots include:

- `engine/modules/view`
- `engine/modules/ui`
- `client/presentation`
- `client/observability`
- `control/view`

### 6.4 Control and Integration Components

These components support negotiation, routing, orchestration, transport, integration, or boundary control across lawful runtime layers.

Representative evidence roots include:

- `compat`
- `control`
- `net`
- `libs/contracts`

### 6.5 Domain-Support Components

Domain-support components host or support runtime execution over specific semantic domain families without redefining the domain contracts themselves.

Representative evidence roots include:

- `engine/modules/world`
- `game/core/execution`
- `core/spatial`
- `core/hazards`
- `process/research`

### 6.6 Tooling and Diagnostic Components

These components support inspection, diagnostics, replay, proof, or operator-facing technical observability, but they are not identical to the tools that consume them.

Representative evidence roots include:

- `tools`
- `control/proof`
- `server/persistence`
- replay and observability surfaces in `engine` and `app`

### 6.7 Policy and Compatibility-Support Components

These components support runtime compatibility, negotiation, refusal, policy enforcement, or boundary validation without redefining semantic law or release law.

Representative evidence roots include:

- `compat/descriptor`
- `compat/handshake`
- `compat/negotiation`
- policy and component registries under `data/registries`

These classes are not final instance lists.
They are the constitutional class vocabulary later prompts must refine rather than replace.

## 7. Component Boundaries

Component boundary discipline is mandatory.
Components exist precisely so later runtime work can avoid hidden god-objects and informal coupling.

At the constitutional level:

- components may depend on kernel law and explicit runtime host surfaces
- components may consume canonical semantic contracts, compatibility surfaces, registries, and policy inputs where their scope requires it
- components may expose bounded functionality, diagnostics, attach points, or coordination contracts
- components may rely on modules as implementation surfaces without becoming identical to those modules

Components must not:

- become hidden semantic or authority owners
- depend upward on product-shell convenience as if products were their owners
- treat generated or projected surfaces as canonical owners
- bind through ambiguous ownership roots because they are easier to consume
- collapse domain, service, and product semantics into one boundary

Component boundaries matter because later services, loaders, release work, and live-ops work need a stable unit of runtime responsibility.

## 8. Component Identity and Compatibility

Component identity must be explicit.
A component may not rely on vague naming, folder prominence, build-target coincidence, or product adjacency as its only identity signal.

At minimum, the component model expects later machine-readable component identity to support:

- explicit component identifier
- explicit component class
- explicit stability and compatibility status
- declared upstream kernel and semantic dependencies
- declared runtime boundary scope
- declared attachment or consumption surfaces where relevant

Component identity is not the same as:

- build identity
- product identity
- pack identity
- module filename

Compatibility must also be explicit.
Later CAP-NEG, loader, release, and coexistence work will consume this model and must not guess component compatibility from informal naming.

## 9. Component Relationship to Services

Components are not services.

The service model remains later work.
This document freezes only the constitutional relationship:

- components are bounded runtime units
- services are later orchestration or coordination structures that may compose, host, route through, or expose components
- service meaning must remain downstream of component and kernel law rather than rewriting them

This prompt therefore does not define the service catalog, service clusters, or service lifecycle semantics in detail.

## 10. Component Relationship to Modules

Components are not modules.

Modules are implementation, packaging, discovery, or code-organization surfaces.
A module may implement part of one component, one module may support multiple components, or a component may span multiple modules.

The architectural consequences are:

- module boundaries are evidence for component extraction, not automatic constitutional truth
- code adjacency is not proof of component identity
- later loader or discovery work must consume the component model rather than replacing it

## 11. Component Relationship to Domains

Domains remain semantic units governed by domain contracts and the completed `Λ` law.
Components may support lawful execution, observation, transport, compatibility, or control over domain-grounded behavior, but they must not collapse or redefine domain law.

Domain-support components must therefore remain:

- ownership-aware
- bridge-aware
- representation-aware
- formalization-aware where standards, protocols, or institutional forms matter

Components may host domain-supporting runtime behavior.
They do not become the domain.

## 12. Component Relationship to Products

Products are not components.
Client, server, launcher, setup, tools, and appshell are product or shell surfaces that consume kernel, service, and component structure through lawful boundaries.

Product convenience must not:

- redefine component identity
- redefine component compatibility
- turn components into product-feature labels
- promote shell-specific behavior into component law

Products may host or consume components.
They do not own component semantics by default.

## 13. Component Relationship to Packs and Content

Packs and content are not runtime components.
They remain declarative and registry-driven semantic expansion surfaces under pack law and ownership review.

The component model may later interact with:

- pack-provided capability surfaces
- pack activation policy
- pack compatibility descriptors
- authored content and packaged runtime descriptors

But it must not:

- collapse pack identity into component identity
- treat content packages as runtime components
- flatten `packs/` and `data/packs/` into one interchangeable authority surface

## 14. Component Relationship to Tools, Mirrors, and Adapters

Tools are not components by default.
Mirrors and projections are not canonical component owners.
Adapters may participate in component realization, but adapter status alone does not establish component authority.

This means:

- operator tools may consume or inspect components
- generated or mirrored inventories may describe components
- compatibility facades may route into components

None of those surfaces outrank the canonical component doctrine.

## 15. Component Lifecycle Expectations

Exact lifecycle law is deferred to later prompts.
Even so, components must be modeled in a way that later lifecycle work can reason about explicitly.

At a minimum, component boundaries should remain compatible with later declaration of:

- activation preconditions
- attach and detach expectations
- refusal and degradation behavior
- quiescence and shutdown expectations
- compatibility and migration expectations
- observability and audit state expectations

This is a lifecycle-compatibility requirement, not a lifecycle implementation.

## 16. Observability and Validation

Components must be observable, diagnosable, and auditable in principle.
They must support targeted validation and accountability instead of vanishing into product shells or undifferentiated runtime substrate.

Later prompts may define exact mechanisms, but the constitutional expectation is already fixed:

- component boundaries must support targeted validation
- diagnostics must be attributable to bounded component scopes
- compatibility and refusal issues must be traceable
- component-level invariants must be auditable without redefining semantic law

## 17. Ownership and Anti-Reinvention Cautions

All checkpoint and ownership cautions remain in force for the component model.

Component law must remain explicitly cautious about:

- `field/` versus `fields/`, where `fields/` remains the canonical semantic field substrate
- `schema/` versus `schemas/`, where schema law remains canonical and projections remain subordinate
- `packs/` versus `data/packs/`, where packaged activation scope and authored declaration scope are not interchangeable
- generated and mirrored surfaces under `build`, `artifacts`, `.xstack_cache`, and `run_meta`, which remain evidence only
- the thin `runtime/` root, which is not automatically canonical merely because of its name
- older planning artifacts that still contain sequence or numbering drift and must not override the current checkpoint law

The component model must therefore extend and extract from live repo embodiment rather than imagining a replacement architecture.
Evidence-rich roots include:

- `engine`
- `game`
- `app`
- `compat`
- `control`
- `core`
- `net`
- `process`
- `server/runtime`
- `server/persistence`
- `libs`

Those roots are evidence for component boundaries.
They are not permission to ignore ownership law, semantic law, or kernel law.

## 18. Anti-Patterns and Forbidden Shapes

The following component shapes are constitutionally forbidden:

- a component treated as a hidden semantic owner
- a component treated as a catch-all synonym for service, module, domain, or product
- components defined purely by code adjacency or folder names
- components that bypass cross-domain bridge law or domain contracts
- components that silently bind to ownership-ambiguous roots
- components that collapse truth execution and presentation semantics
- components that derive identity only from build targets or shell placement
- components that let product convenience redefine runtime boundaries
- components that treat pack content as equivalent to component identity

## 19. Stability and Evolution

This artifact is a provisional but canonical runtime doctrine.
It is stable enough to govern the next early runtime prompt and downstream runtime-boundary consumption, but it is expected to be refined by explicit doctrine rather than silent code drift.

The immediate downstream consumers are:

- `Φ-2 — RUNTIME_SERVICES-0`
- `Σ-1`
- `Σ-2`

Later prompts may extend component identity, lifecycle, loader, service, externalization, and policy behavior, but they must not contradict the boundary law established here.
Later Υ and Ζ work may also rely on explicit component identity and compatibility expectations when reasoning about release, migration, cutover, or live-ops behavior.

## 20. Direct Constitutional Answers

1. A component in Dominium is a bounded runtime-facing functional unit with explicit identity, declared boundary, and declared responsibilities operating inside kernel law.
2. A component is distinct from a service, module, domain, or product because services orchestrate components, modules implement them, domains define semantic law, and products consume them.
3. A component may own bounded runtime behavior, explicit interfaces, diagnostics, and compatibility-relevant responsibility within its declared scope.
4. A component may not own semantic truth, domain ownership, governance law, release doctrine, or product-shell semantics.
5. Components relate to semantic doctrine and kernel law by consuming upstream semantic contracts and operating downstream of the kernel's execution host boundaries.
6. The relevant ownership cautions remain `field/` versus `fields/`, `schema/` versus `schemas/`, `packs/` versus `data/packs/`, generated evidence roots, and the non-canonical status of the thin `runtime/` root.
7. This component model now enables `Φ-2`, and gives `Σ-1` and `Σ-2` a stable runtime-boundary unit to mirror and map after early Φ-A1 is complete.
