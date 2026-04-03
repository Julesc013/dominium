Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-6, Υ-7, Υ-8, later checkpoints
Replacement Target: later operator-transaction, downgrade/yank, archive, publication, and trust doctrine may refine consumers and operational procedures without replacing the release-index and resolution semantics
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB1.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/PRESET_AND_TOOLCHAIN_CONSOLIDATION.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/ARTIFACT_NAMING_CHANGELOG_TARGET_POLICY.md`, `docs/release/RELEASE_IDENTITY_CONSTITUTION.md`, `docs/release/RELEASE_INDEX_MODEL.md`, `docs/release/RELEASE_INDEX_RESOLUTION_POLICY.md`, `docs/release/RELEASE_MANIFEST_MODEL.md`, `docs/release/UPDATE_SIM_MODEL_v0_0_0.md`, `repo/release_policy.toml`, `schema/release/release_index.schema`, `schema/release/release_manifest.schema`, `schema/release/release_contract_profile.schema.json`, `release/update_resolver.py`, `release/release_manifest_engine.py`, `data/registries/release_channel_registry.json`, `data/registries/target_matrix_registry.json`, `data/registries/install_profile_registry.json`, `data/registries/component_graph_registry.json`, `data/registries/trust_policy_registry.json`

# Release Index And Resolution Alignment

## A. Purpose And Scope

Release index and resolution alignment exists to freeze one canonical interpretation of how Dominium records release availability and how it lawfully chooses among release candidates.

It solves a specific problem: the repo already contains release identity doctrine, release-index surfaces, resolver policy, update simulation fixtures, target registries, install profiles, trust policy, and manifest rules, but those surfaces can still be misread as if a version string, channel label, filename, or build id alone explains compatibility and selection. Later `Υ` prompts need one constitutional answer to the question "how do identity, compatibility, and selection relate?" before they can safely define operator transactions, downgrade and yank policy, archive continuity, or publication and trust gating.

This document governs:

- what the release index is in Dominium
- what release resolution is in Dominium
- how release identity, release contract profiles, channels and lanes, target descriptors, build identity, and naming policy relate within lookup and selection
- which inputs resolution may lawfully use
- which shortcuts resolution must refuse

It does not govern:

- release-pipeline implementation
- updater or installer algorithm code
- publication workflow
- trust-root operations
- archive layout
- downgrade or operator transaction procedures in full

Those are later `Υ` prompts. This prompt freezes the release-selection semantics they must consume.

## B. Core Definition

A release index is the canonical machine-readable lookup surface that records release-facing availability, identity references, compatibility references, channel or lane placement, target applicability, and later lifecycle state such as deprecation, yank, or supersession.

Release resolution is the lawful process that evaluates indexed candidates against explicit compatibility, target, policy, and governance constraints in order to determine whether a candidate is admissible and, if more than one candidate is admissible, which one should be selected.

They are linked but distinct:

- the release index records governed release facts and references
- release resolution consumes those facts and references under explicit policy

They differ from nearby surfaces:

- version fields describe layered revision labels but do not by themselves resolve compatibility
- a release manifest describes a concrete shipped distribution but is not the whole lookup model
- filenames project metadata but are not release truth
- channel labels classify release lanes but do not replace compatibility checks
- build identity pins exact deterministic artifact provenance but is not semantic compatibility
- target descriptors participate in selection but do not by themselves define full release admissibility

Release index and resolution alignment is a distinct constitutional layer because Dominium needs one auditable place where release lookup and lawful selection semantics are frozen without turning any one nearby field into the whole release-selection story.

## C. Why Alignment Is Necessary

Alignment is necessary because:

- release identity and compatibility reasoning must stay coherent across indices, manifests, registries, and resolver outputs
- update and install consumers must not infer different truths from different fields
- later operator, downgrade, archive, and publication doctrine requires one consistent release-selection substrate
- the repo already distinguishes layered version fields, release contract profiles, exact target descriptors, and build identity; resolution must preserve those distinctions instead of flattening them into "latest wins"
- governance and trust posture must remain explicit instead of being rediscovered from filename conventions or local updater folklore

Without this alignment, later work would drift toward local heuristics, duplicate compatibility semantics in several places, or silently repurpose channel labels and version strings into false compatibility or precedence truth.

## D. Release Index Elements

The constitutional release-index elements are:

### D1. Release Identity Record

An index entry must carry or reference an explicit release identity record, including release-facing identifiers such as release id, release series, product or suite references where relevant, and deterministic fingerprints for the indexed surface.

### D2. Compatibility Envelope Reference

An index entry must carry or reference the release contract profile or its governed equivalent references, including semantic contract binding and the explicit protocol, schema, and format compatibility envelope.

### D3. Channel Or Lane Classification

An index entry may classify a release candidate into a channel or lane context such as `mock`, `alpha`, `beta`, `rc`, `stable`, or later explicit lane classes.

### D4. Target Applicability References

An index entry may carry both:

- target-family references for broad filtering
- exact-target references for machine-facing specificity

These remain distinct.

### D5. Build Identity And Provenance References

An index entry may reference build ids, content hashes, component graph hashes, manifest hashes, install-profile identifiers, and related provenance anchors needed for exact reconstruction and deterministic planning.

### D6. Selection-Relevant Lifecycle State

An index entry may declare state that later selection policy must honor, such as:

- deprecation
- yank posture
- supersession
- availability posture
- publication or governance posture where constitutionally relevant

### D7. Derived Projections

Indices may be mirrored into manifests, filenames, reports, or operator views, but those projections remain downstream of the canonical release index and its upstream compatibility doctrine.

## E. Resolution Inputs

Resolution may lawfully consider:

- release contract profile compatibility
- semantic contract bundle hash alignment
- explicit protocol family and range compatibility
- explicit schema family and range compatibility
- explicit format family and range compatibility
- exact target compatibility descriptors
- target-family filters as broad preselection only
- channel or lane policy
- deprecation, yank, or supersession state
- governance and trust posture
- install-profile or policy preferences when explicitly governed
- deterministic identity anchors such as release id, manifest hash, component graph hash, or build id for exact reconstruction and tie-breaking where constitutionally allowed

Resolution must not overuse or substitute:

- filenames as primary truth
- raw suite version equality as compatibility
- raw product version equality as compatibility
- build identity as a semantic compatibility substitute
- channel shorthand as a replacement for compatibility checks
- target family alone as exact-target resolution

## F. Identity Vs Compatibility Vs Selection

Identity, compatibility, and selection must remain distinct.

Release identity answers:

- which governed release record or artifact set this is

Compatibility answers:

- whether a candidate fits the request, environment, and governed compatibility envelope

Selection answers:

- which admissible compatible candidate should be chosen under explicit policy

These distinctions matter because:

- a release may have a valid identity and still be incompatible
- multiple releases may be compatible and still require policy-based selection
- a channel-preferred candidate may still be refused if the release contract profile or trust posture does not fit
- a build id may help identify the exact candidate chosen, but it does not make the candidate compatible

The key constitutional rule is that lawful resolution first preserves identity and compatibility truth, and only then applies explicit selection policy.

## G. Channel And Lane Policy Relationship

Channel and lane labels influence selection policy, operator intent, and availability posture.

They do not replace compatibility checks.

Channel or lane policy may lawfully:

- limit the candidate set to an allowed lane
- express conservative or experimental operator preference
- coordinate suite-facing release flows
- influence admissibility when policy explicitly requires channel membership

Channel or lane policy must not:

- bypass release contract profile checks
- redefine target compatibility
- transform build identity into compatibility
- override trust or governance posture by shorthand alone

The constitutional rule is that channels and lanes are policy classifiers layered on top of compatibility truth, not substitutes for it.

## H. Target Family Vs Exact Target In Resolution

Target family is a broad grouping aid useful for matrix navigation, lane partitioning, and coarse filtering.

Exact target descriptor is the machine-readable statement of concrete binary meaning, such as:

- target id
- platform id or platform tag
- OS id
- ABI id
- architecture id
- environment or toolchain anchors where constitutionally relevant

Resolution may use both, but must keep them distinct:

- target family may prefilter candidate space
- exact target descriptors determine concrete admissibility

Exact target resolution must not be approximated casually by target family alone. A family label such as `win64` or `linux-x86_64` is not enough to stand in for the whole exact compatibility descriptor when binary meaning or concrete install selection is at stake.

## I. Relationship To Release Contract Profile

Release contract profile is the upstream machine-readable compatibility envelope.

Release index and resolution alignment therefore depends on, and must not replace:

- semantic contract binding
- protocol compatibility
- schema compatibility
- format compatibility
- governance and trust posture
- target-family and exact-target compatibility semantics

The release index may record these truths directly or by reference, but it must remain aligned with profile semantics rather than inventing a second compatibility vocabulary. Resolution consumes profile-governed meaning, not only version strings or manifest fragments.

## J. Relationship To Naming And Manifests

Filenames, bundle labels, changelog prose, and release manifests may project or carry release state, but they are not sole resolution truth.

The governing consequences are:

- filenames are convenient projections and must not become resolver inputs of first resort
- changelog prose may explain selection-relevant state but cannot define machine admissibility
- release manifests describe concrete shipped artifact sets and may carry release-contract-profile references or aligned fields, but they do not replace release-index doctrine
- manifest and naming surfaces must align with this doctrine without becoming a substitute for it

Resolution may inspect manifest or artifact-carried metadata only insofar as that metadata remains subordinate to canonical identity and compatibility fields.

## K. Relationship To Provenance And Archive Continuity

Release index and resolution alignment must preserve exact reconstruction and historical continuity.

Later work on yanks, supersession, downgrade, rollback, archive retention, and operator transactions depends on being able to reconstruct:

- which release identity was selected
- which compatibility envelope admitted it
- which channel or lane policy applied
- which target and install-profile context applied
- which exact build or manifest anchors were chosen
- whether later lifecycle state such as yank or deprecation modified selection

Silent field repurposing is therefore forbidden. The exact meaning of release identity, compatibility, and selection inputs must remain stable and explicit across release history.

## L. Canonical Vs Derived Distinctions

Canonical release-selection surfaces include:

- this doctrine
- the upstream versioning constitution
- the release contract profile doctrine and schema
- canonical release index structures and governed registries
- target, install-profile, trust, and channel registries with intact provenance

Derived or projection surfaces include:

- filenames
- changelog prose
- generated selection summaries
- archive labels
- convenience feeds
- local updater output formatted for humans

Derived artifacts may summarize release-selection outcomes, but they must not silently become resolution law or compatibility truth.

Older planning-number drift and thin root naming convenience remain active cautions. Current authoritative doctrine and active prompt scope outrank stale mirrored numbering or convenience readings of nearby files.

## M. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- latest version string wins
- suite version equality as compatibility
- product version equality as compatibility
- channel label overrides contract-profile checks
- filename parsing as the primary resolver
- build id as compatibility truth
- target family treated as exact target
- release manifest inventing resolution semantics outside constitutional doctrine
- local updater logic repurposing omitted compatibility fields into permissive defaults
- generated summaries or support bundles treated as the source of release-resolution canon

## N. Stability And Evolution

This artifact is `provisional` but canonical for the current `Υ-A` execution band.

Later prompts may refine:

- changelog and change-record consumers
- operator transaction structure
- archive and mirror continuity rules
- downgrade, yank, and supersession procedures
- publication and trust gating

Those later prompts must extend this doctrine rather than replacing it silently.

Updates must remain explicit, auditable, and non-silent. In particular, later work must not:

- collapse identity, compatibility, and selection back together
- repurpose channel or version fields into compatibility or precedence truth
- promote filenames or derived summaries into canonical resolution inputs

Under the active execution chain, this doctrine enables `Υ-6` next and provides a stable substrate for later `Υ-7`, `Υ-8`, and future checkpoint reassessment of the risky `Φ-B` tail.
