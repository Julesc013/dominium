Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0, `docs/canon/glossary_v1.md` v1.0.0, `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md` v1.0.0, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md` v1.0.0, `specs/reality/SPEC_CAPABILITY_SURFACES.md` v1.0.0, `specs/reality/SPEC_REPRESENTATION_LADDERS.md` v1.0.0, `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md` v1.0.0, `specs/reality/SPEC_FORMALIZATION_CHAIN.md` v1.0.0, `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md` v1.0.0, and `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md` v1.0.0.
Stability: stable
Future Series: Σ, Φ, Υ, Ζ
Replacement Target: later domain bridge specifications, governance/task constitutions, and runtime/service boundary extractions must instantiate this framework rather than replace it

# Dominium Cross-Domain Bridge Framework v1

## A. Purpose And Scope

This document defines the constitutional cross-domain bridge framework for Dominium after `Λ-0` through `Λ-5.5`.

It exists because Dominium is not made of isolated semantic silos.
The project already embodies matter, field, geo, worldgen, logistics, protocol, provenance, institution, observation, and collapse/expansion surfaces across roots such as:

- `materials/construction/construction_engine.py`
- `materials/blueprint_engine.py`
- `materials/provenance/event_stream_index.py`
- `worldgen/earth/hydrology_engine.py`
- `signals/institutions/standards_engine.py`
- `logic/protocol/protocol_engine.py`
- `geo/lens/lens_engine.py`
- `system/system_expand_engine.py`
- `system/system_collapse_engine.py`

Those surfaces imply cross-domain interaction, but code adjacency is not constitutional bridge law.
Dominium needs one explicit bridge framework that defines how domains interact without:

- hidden coupling
- ownership leakage
- silent projection drift
- runtime-first guesswork
- one giant undifferentiated super-domain

This framework governs:

- what a cross-domain bridge is
- what elements a lawful bridge must declare
- what invariants and ownership boundaries a bridge must preserve
- how bridges interact with capability surfaces, representation ladders, formalization, and semantic ownership review
- what later governance, runtime, release, and live-ops work may assume about inter-domain coupling

This framework does not yet define:

- every individual bridge instance for every domain pair
- runtime bridge engines or execution services
- every persistence or networking contract
- every later governance/task wrapper that consumes bridge law
- physical convergence of roots reviewed in `Λ-5.5`

This framework inherits from `Λ-0` through `Λ-5.5`.
It does not create a parallel ontology.

## B. Core Definition

A cross-domain bridge is a declared lawful coupling by which one domain family may affect, constrain, inform, formalize, or mediate another domain family while preserving:

- domain ownership
- declared invariants
- lawful Process boundaries
- representation and scaling continuity
- provenance and bridge lineage

A bridge is distinct from:

- `domain ownership`:
  ownership says which domain or artifact root owns semantic meaning
- `capability surfaces`:
  capability surfaces expose lawful action over substrate, while bridges define how domains relate underneath those surfaces
- `semantic ascent and descent`:
  ascent and descent describe lawful movement between semantic levels, while bridges describe lawful coupling across distinct domain families
- `formalization chain`:
  formalization explains how designs, methods, and institutions become reusable, while bridges explain how domains interact once or while that formalization exists
- `runtime service boundaries`:
  runtime boundaries are later implementation consequences, not the source of bridge meaning
- `module imports or shared code`:
  code adjacency is evidence of interaction, not constitutional authority to declare a bridge

Bridges are needed as a distinct layer because Dominium must support lawful interaction across physical, biological, economic, institutional, infrastructural, observational, and persistence domains without letting any one layer quietly redefine the others.

Resolved ambiguity:

- domain interaction cannot be left implicit
- shared code or convenience does not create semantic bridge authority
- bridges do not erase domain ownership
- canonical versus projected distinctions still matter across bridges

## C. Why Bridges Are Necessary

Domains exist to preserve coherent ownership and local law.
That does not mean they live in isolation.

Dominium requires explicit bridges because:

- matter affects biology
- terrain and geology affect logistics, extraction, and settlement
- agents act through knowledge, economy, and institutions
- infrastructure changes politics, maintenance, and strategic reach
- persistence and interface layers touch every meaningful domain without becoming their owner

If those relations remain implicit, later systems will tend to infer semantics from:

- shared code paths
- shared storage shapes
- convenience wrappers
- runtime service decomposition
- presentation needs

That would violate the semantic and ownership discipline already frozen by `Λ-0` through `Λ-5.5`.

Therefore bridge law must come first.
Runtime, governance, tooling, release, and live-ops layers consume bridge law later.
They do not invent it retroactively.

## D. Bridge Elements

At the framework level, every lawful bridge family or bridge instance must be able to declare the following elements.

- `source_domain_family`:
  the domain family from which the bridge originates or whose state/meaning is being coupled outward
- `target_domain_family`:
  the domain family being affected, constrained, interpreted, or mediated
- `bridge_subject`:
  the class of interaction such as metabolism, extraction, jurisdiction, standards transfer, audit, or persistence anchoring
- `directionality`:
  whether the bridge is symmetric, directional, asymmetrically bidirectional, institutionally mediated, or an anchor-to-many relation
- `preserved_invariants`:
  identity, conservation, jurisdiction, topology, lineage, safety, or other invariant families that must survive the bridge
- `ownership_requirements`:
  how the bridge respects canonical domain contracts and avoids promoting projections into semantic owners
- `capability_surface_implications`:
  which capability surface classes the bridge enables, constrains, or conditions
- `representation_and_scaling_notes`:
  how bridge legality survives macro/micro transitions, substitution, collapse, and expansion
- `formalization_dependencies`:
  whether the bridge depends on standards, blueprints, procedures, institutions, or other formalization stages
- `failure_and_invalidity_conditions`:
  how the bridge may be blocked, degraded, unsafe, contested, or invalid
- `verification_hooks`:
  what later systems should be able to audit or test about the bridge

Bridge law may be declared at more than one granularity later:

- framework family
- domain-family pair
- institutional or standards-mediated bridge
- specific bridge instance

But all later declarations inherit this structure rather than inventing their own bridge grammar ad hoc.

## E. Ownership And Authority

Bridges connect domains.
They do not dissolve them.

The ownership rules are:

- every bridge must bind to the canonical semantic owner for each participating domain within declared scope
- a bridge may be expressed through projected or machine-readable artifacts, but those artifacts do not become the semantic owner
- bridges may not silently transfer semantic authority from one domain to another
- bridges may not quietly promote validator, packaged, or generated surfaces into domain owners
- bridge declarations that touch a quarantined family must preserve the exact caution recorded by `Λ-5.5`

This has direct consequences for known ownership-sensitive roots.

- `fields/` is the field substrate owner, while `field/` remains a transitional compatibility facade
- `schema/` owns semantic contract law, while `schemas/` remains validator-facing projection law
- `specs/reality/` owns normative semantic meaning, while `data/reality/` remains an operational registry mirror
- `docs/planning/` owns planning meaning, while `data/planning/` remains an operational planning mirror
- `packs/` and `data/packs/` remain a scoped-ownership and residual-quarantine family rather than a single-root truth

Accordingly:

- bridges may refer to projections for tooling, validation, packaging, or exposure
- bridges may not treat those projections as the semantic owner
- bridges that touch the `packs/` versus `data/packs/` family must preserve authored-versus-packaged scope instead of inventing a fake global winner

## F. Invariants And Preservation

Every bridge must preserve declared invariant classes.
Later domain bridge instances must refine the exact list, but the framework-level invariant families include:

- `identity_and_provenance`:
  the coupled thing keeps its identity anchors and causal lineage
- `conservation_relevant_quantities`:
  mass, stock, flow, counts, energy, and similar bounded quantities are not magically created or lost
- `topology_and_connectivity`:
  routes, containment, adjacency, and network relationships remain lawful
- `authority_and_jurisdiction`:
  permissions, obligations, legal authority, and institutional competence remain explicit
- `historical_lineage`:
  bridge effects do not erase the history of what happened or why
- `institutional_continuity`:
  standards, offices, memberships, and governance meanings remain traceable
- `capability_legality`:
  lawful action opportunities remain consistent with substrate, authority, and Process
- `safety_and_compliance`:
  hazard, refusal, containment, and compliance requirements remain explicit
- `epistemic_traceability`:
  what is known, measured, inferred, or uncertain through the bridge remains inspectable

A bridge is unlawful if it requires invariant loss that has not been explicitly declared and justified by the participating domain contracts.

## G. Bridge Directionality

Directionality must be explicit.
It must never be inferred from implementation convenience.

The framework recognizes the following directionality patterns.

- `symmetric`:
  both domains lawfully constrain one another in the same declared way
- `directional`:
  one domain lawfully influences or constrains another more directly than the reverse
- `bidirectional_asymmetric`:
  both directions exist, but each direction preserves different invariants, authority rules, or failure semantics
- `mediated`:
  the bridge only becomes lawful through standards, institutions, logistics, protocol, or other formalization structures
- `anchor_to_many`:
  an anchor domain such as interface or persistence lawfully touches many domains through one common bridge grammar without owning them

Later bridge instances must declare which of these applies.
They may not assume reversibility, reciprocity, or universal access by default.

## H. Bridge Classes

Cross-domain bridges are not all the same kind.
The framework uses the following constitutional bridge classes.

### H.1 Causal / Physical Bridges

These bridges carry material, energetic, environmental, or process-level consequences across domains.

Typical examples:

- matter affecting biology
- geology constraining extraction
- hydrology affecting settlement or agriculture
- pollution affecting health or compliance

### H.2 Observational / Epistemic Bridges

These bridges govern how one domain becomes knowable, measurable, interpretable, or auditable through another.

Typical examples:

- agents observing world state
- instrumentation revealing machine or environmental conditions
- governance acting on inspection evidence

### H.3 Economic / Logistical Bridges

These bridges govern how resources, goods, obligations, routes, labor, and throughput connect domains.

Typical examples:

- matter entering valuation and exchange
- transport constraining industry
- settlements depending on logistics

### H.4 Institutional / Governance Bridges

These bridges govern law, office, legitimacy, jurisdiction, compliance, coordination, and policy effects across domains.

Typical examples:

- knowledge informing governance
- infrastructure and territory changing political authority
- organizations governing labor, access, and standards

### H.5 Infrastructure / Network Bridges

These bridges govern connectivity, services, routes, communication, utilities, and distributed support structures.

Typical examples:

- transport interacting with settlements
- utilities affecting industry and habitation
- routing and network state affecting strategic possibilities

### H.6 Interface / Embodiment Bridges

These bridges govern how embodied users, planners, NPCs, AI agents, and future interfaces lawfully access domain structure without redefining it.

Typical examples:

- embodied action over machine surfaces
- abstract planning over logistics and institutions
- future adapters over the same underlying domain law

### H.7 Persistence / Provenance Bridges

These bridges govern how domain truth is preserved, replayed, audited, synchronized, or lineage-bound across persistence-oriented surfaces.

Typical examples:

- event or provenance records anchoring material or institutional change
- replay and save boundaries preserving domain identity
- networking or synchronization consuming domain truth without rewriting it

### H.8 Formalization / Standards Bridges

These bridges govern how explicit knowledge, standards, blueprints, methods, and educational forms travel between domains.

Typical examples:

- knowledge enabling industry
- standards reshaping infrastructure or safety
- educational or legal form spreading technical practice

### H.9 Safety / Compliance Bridges

These bridges govern hazard, refusal, containment, inspection, certification, and legal or institutional constraint across domains.

Typical examples:

- pollution and health
- machine safety and governance
- infrastructure risk and political oversight

## I. Representative Required Bridge Families

The following bridge families are constitutionally important.
They are recognized here at the framework level even though their full domain-specific instances remain later work.

### I.1 Matter ↔ Biology

This family is required because metabolism, exposure, nutrition, toxicity, shelter materiality, and medical or environmental constraint all depend on lawful interaction between material and biological domains.

Bridge implications:

- preserve conservation-relevant quantities, safety constraints, and provenance
- keep biology from being treated as presentation-only matter animation
- keep material use from bypassing biological constraint or harm law

### I.2 Matter ↔ Economy

This family is required because resources, goods, scarcity, value, storage, and exchange all depend on how material substrate becomes economically meaningful.

Bridge implications:

- preserve quantity, provenance, ownership, and compatibility commitments
- distinguish material existence from price, contract, or accounting projection
- allow economic meaning to arise lawfully without erasing material truth

### I.3 Geology ↔ Economy

This family is required because terrain, strata, extraction conditions, water, topology, and hazard all shape economic availability, cost, transport, and settlement behavior.

Bridge implications:

- preserve topology, jurisdiction, extraction rights, and depletion lineage
- keep resource economics bound to lawful geological or hydrological conditions
- prevent abstract economy layers from inventing extractive abundance detached from substrate

### I.4 Biology ↔ Culture

This family is required because diet, health, reproduction, kinship, labor habit, disease, care, ritual, and identity all involve lawful interplay between biological and cultural structures.

Bridge implications:

- preserve identity, epistemic caution, and institutional continuity
- avoid reducing culture to biology or biology to pure symbolism
- allow lawful social meaning to attach without hidden determinism claims

### I.5 Agents ↔ Knowledge

This family is required because agents discover, record, teach, infer, forget, inspect, and act under epistemic constraint.

Bridge implications:

- preserve epistemic scope, provenance, and observation lineage
- keep knowledge from becoming omniscient world access
- make lawful ignorance, uncertainty, and institutional learning first-class

### I.6 Agents ↔ Economy

This family is required because actors labor, exchange, own, reserve, command, contract, and consume within economic structures.

Bridge implications:

- preserve authority, accountability, obligation, and scarcity
- prevent planning or automation layers from granting impossible economic powers
- support lawful delegation and refusal rather than invisible command magic

### I.7 Knowledge ↔ Industry

This family is required because industrial capability depends on designs, measurements, standards, training, repeatability, and process stabilization.

Bridge implications:

- preserve formalization lineage, validation, compatibility, and institutional continuity
- keep industrialization from collapsing into recipe-only progression
- allow knowledge to change production lawfully through standards and blueprints

### I.8 Knowledge ↔ Governance

This family is required because law, administration, compliance, inspection, policy, and institutional legitimacy depend on records, evidence, doctrine, and knowledge circulation.

Bridge implications:

- preserve provenance, authority, certification, and contestability
- keep governance from treating rumor or presentation as equivalent to verified knowledge
- keep knowledge systems from silently becoming sovereign law without formal adoption

### I.9 Infrastructure ↔ Politics

This family is required because routes, power, water, ports, utilities, communication, and maintenance priorities shape jurisdiction, strategy, membership, and legitimacy.

Bridge implications:

- preserve topology, service obligations, jurisdiction, and access rights
- keep infrastructure from being modeled as politically neutral when it changes authority and social power
- keep politics from inventing network behavior detached from actual infrastructure state

### I.10 Interface ↔ All Domains

This family is required because every embodied, abstract, AI, operator, or future-interface access path must remain a lawful adapter over domain truth rather than a separate ontology.

Bridge implications:

- preserve canonical domain ownership
- preserve truth / perceived / render separation
- ensure interface change does not change bridge legality or domain meaning

### I.11 Persistence ↔ All Domains

This family is required because every domain must preserve provenance, replay, save, audit, and synchronization meaning without letting persistence surfaces become substitute ontology owners.

Bridge implications:

- preserve identity, lineage, legality, and canonical ownership across record, save, replay, and synchronization paths
- prevent event logs, save formats, or network payloads from redefining domain meaning
- keep distributed or live-operation futures subordinate to semantic bridge law

## J. Capability-Surface Implications

Bridges may expose, constrain, or mediate capability surfaces across domains.
That does not mean a bridge is itself a capability surface.

The constitutional rules are:

- a bridge may declare that capability surfaces in one domain depend on state or legitimacy in another
- a bridge may constrain lawful invocation, visibility, or authorization conditions across domains
- a bridge may explain why one actor class can plan or inspect across domains while another cannot
- a bridge may not create hidden superpowers
- a bridge may not let capability surfaces bypass Process-only mutation or law-gated authority

Examples:

- an economic bridge may constrain whether a fabrication capability is usable because materials or entitlements are absent
- an institutional bridge may determine whether a planning or command surface is lawful
- an observational bridge may determine whether an inspection surface reveals enough to act safely

## K. Representation And Scaling Implications

Bridge legality must survive lawful representation changes.

That means:

- a bridge cannot disappear semantically just because one participating domain is summarized macroscopically
- a bridge cannot become more permissive merely because detail is collapsed
- expansion back into micro detail must preserve bridge lineage, ownership, and preserved invariants
- substitution and capsules may express a bridge differently, but may not rewrite what the bridge means
- bridge verification may be approximate at one scale and precise at another, but the governing bridge law remains the same

This matters because Dominium must support:

- local embodied action
- regional planning
- industrial and institutional scaling
- civilization-scale simulation
- future distributed or persistent operations

without letting cross-domain meaning drift between scales.

## L. Formalization Implications

Some bridges depend directly on formalization.

Examples:

- knowledge ↔ industry may require blueprints, validation, standards, and training
- knowledge ↔ governance may require recordkeeping, doctrine, procedure, and institutional adoption
- infrastructure ↔ politics may require charters, jurisdictions, compliance regimes, and maintenance obligations
- agents ↔ economy may require explicit contracts, accounting standards, or labor-role structures

Formalization may stabilize a bridge, make it portable, or make it institutionally legitimate.
But formalization does not erase domain distinction.

Therefore:

- bridge law may depend on formalization stages
- bridge legality may change when a standard, institution, or protocol is absent
- formalization does not authorize silent substitution or ownership reassignment

## M. Failure And Invalidity

Bridges may be lawful, degraded, blocked, unsafe, contested, or invalid.
Success is never automatic.

Framework-level failure and invalidity categories include:

- `ownership_misbinding`:
  the bridge binds to the wrong semantic owner or ignores a canonical-versus-projection distinction
- `invariant_violation`:
  the bridge would require identity, conservation, topology, lineage, or authority loss
- `directionality_violation`:
  the bridge is used as though reversible or symmetric when it is not
- `authority_or_jurisdiction_refusal`:
  a bridge is blocked because authority, legitimacy, or jurisdiction is absent
- `missing_formalization_prerequisite`:
  the bridge depends on standards, procedures, records, or institutions that do not yet exist
- `representation_scale_mismatch`:
  the bridge cannot currently be used lawfully at the active representation horizon
- `capability_surface_illegality`:
  a claimed action would bypass lawful capability or Process boundaries
- `contested_or_conflicting_bridge_law`:
  competing or unresolved interpretations remain explicit rather than hidden
- `provenance_or_persistence_break`:
  the bridge would lose lineage or auditability
- `unsafe_bridge_state`:
  hazard, compliance, or reliability constraints are violated

Later domains and runtime systems must model these failure semantics explicitly.
They must not assume bridge success by default.

## N. Verification

Cross-domain bridges must be auditable and testable.
Later systems should be able to verify at minimum:

- domain ownership consistency
- canonical-versus-projection adherence
- invariant preservation
- declared directionality legality
- bridge-class compatibility
- capability-surface legality
- macro/micro continuity
- formalization prerequisite satisfaction where relevant
- explicit failure, refusal, degradation, or contestability paths

Verification is not only a runtime concern.
Bridge declarations, task systems, governance surfaces, and provenance work all need machine-checkable bridge structure.

## O. Anti-Patterns And Forbidden Shapes

- implicit coupling justified only by convenience or shared code path
- a `god bridge` that erases domain boundaries and makes every domain depend on one hidden super-layer
- bridge rules hidden only in runtime logic
- bridges that silently redefine domain ownership or ontology
- bridges that treat projected or generated artifacts as canonical owners
- bridges that allow impossible actions or flows absent lawful substrate
- bridge declarations that ignore directionality
- bridge declarations that ignore representation or scaling constraints
- bridge declarations that bypass standards, institutions, or authority where those are required
- bridge declarations that flatten quarantined ownership families into certainty

## P. Stability And Evolution

This artifact is `stable` for the current semantic constitution block.

Later work may:

- define domain-specific bridge instances
- refine bridge invariants for specific domain pairs
- author machine-readable bridge declarations, validators, and service mappings
- use this framework to extract runtime/service boundaries and governance/task surfaces

Later work may not:

- redefine bridge law from runtime adjacency
- erase domain ownership through bridge declarations
- collapse canonical-versus-projected distinctions
- silently weaken residual quarantine from `Λ-5.5`

Future bridge families may be added lawfully if they:

- inherit this framework
- declare ownership and invariant discipline explicitly
- remain compatible with the universal reality framework, domain contract template, capability surfaces, representation ladders, formalization chain, player-desire acceptance map, and semantic ownership review

## Cross-References

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`
- `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`
- `specs/reality/SPEC_CAPABILITY_SURFACES.md`
- `specs/reality/SPEC_REPRESENTATION_LADDERS.md`
- `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`
- `specs/reality/SPEC_FORMALIZATION_CHAIN.md`
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
