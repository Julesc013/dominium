Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-4, Υ-5, Υ-6, Υ-7, Υ-8, later checkpoints
Replacement Target: later release-index, artifact-naming, archive, operator-transaction, and publication/trust doctrine may refine consumers and operational procedures without replacing the profile semantics
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB1.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/PRESET_AND_TOOLCHAIN_CONSOLIDATION.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_IDENTITY_CONSTITUTION.md`, `docs/release/RELEASE_INDEX_MODEL.md`, `docs/release/RELEASE_INDEX_RESOLUTION_POLICY.md`, `docs/release/RELEASE_MANIFEST_MODEL.md`, `docs/release/ARTIFACT_NAMING_RULES.md`, `docs/release/UPDATE_SIM_MODEL_v0_0_0.md`, `repo/release_policy.toml`, `data/governance/governance_profile.json`, `data/registries/governance_mode_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/release_channel_registry.json`, `data/registries/component_graph_registry.json`, `data/registries/install_profile_registry.json`, `data/registries/target_matrix_registry.json`, `data/registries/toolchain_matrix_registry.json`, `schema/SCHEMA_VERSIONING.md`, `schema/release/build_id.schema`, `schema/release/release_index.schema`, `schema/release/release_manifest.schema`, `schema/identity/artifact_identity.schema`, `schema/meta/universal_identity_block.schema`, `governance/governance_profile.py`, `release/build_id_engine.py`, `release/update_resolver.py`, `release/release_manifest_engine.py`

# Release Contract Profile

## A. Purpose And Scope

Release contract profile exists to freeze the canonical machine-readable compatibility envelope for Dominium releases after the layered field model established by `Υ-2`.

It solves a specific problem: the repo already has explicit fields for semantic contract pins, protocol ranges, governance posture, trust policy, component graph anchors, platform tags, build identity, and release identifiers, but those truths are still spread across release indices, manifests, registries, and resolver code. Later `Υ` work needs one governed envelope that composes those truths without letting any single field impersonate the whole compatibility story.

This document governs:

- what a release contract profile is
- which truths it binds together explicitly
- which truths must remain separate even while being composed
- how later release-manifest, release-index, naming, archive, operator-transaction, and publication/trust work must consume the profile

It does not govern:

- release-pipeline execution
- update-resolution implementation details
- artifact naming syntax
- changelog structure
- archive layout
- publication or trust operational rollout

Those are later `Υ` prompts. This prompt freezes the compatibility envelope they must use.

## B. Core Definition

A release contract profile is the canonical machine-readable compatibility envelope for a governed release surface.

It is the place where Dominium explicitly composes:

- semantic meaning compatibility
- protocol compatibility
- schema compatibility
- format compatibility
- governance and trust posture
- release and component graph anchors
- target compatibility specificity
- lane and channel context

The profile is distinct because it answers a different question than any single field answers alone:

- suite version answers "which curated suite snapshot is this?"
- product version answers "which product lineage revision is this?"
- protocol, schema, and format fields answer "which compatibility lanes exist for this layer?"
- build identity answers "which deterministic build instance is this?"
- release manifest answers "what concrete artifacts are shipped here?"
- filenames answer "how is this artifact projected for humans or packaging?"
- target family labels answer "which broad target grouping is this near?"

The release contract profile answers:

- "what explicit compatibility envelope governs admission, selection, and interpretation of this release surface?"

## C. Why The Profile Is Necessary

The profile is necessary because:

- compatibility must remain explicit and machine-readable
- layered truths must remain separate but composable
- later release-index and resolver work needs one coherent compatibility envelope instead of ad hoc field bundles
- release manifests need a canonical compatibility reference instead of locally invented fragments
- operator, archive, and downgrade work later needs exact compatibility reconstruction, not version-string folklore

Humans can read suite or product versions, but machines must evaluate explicit compatibility structures. The release contract profile is the constitutional place where those structures are composed without being collapsed.

## D. Profile Fields

The release contract profile binds the following field classes.

### D1. Profile Identity And Metadata

The profile declares its own identity and profile metadata, including:

- `profile_kind`
- `schema_version`
- `profile_id`
- `stability_class_id`
- `deterministic_fingerprint`

These fields identify the profile artifact itself. They do not replace the compatibility fields the profile carries.

### D2. Semantic Contract Binding

The profile must carry explicit semantic contract binding through the semantic contract bundle hash.

### D3. Protocol Compatibility

The profile must carry machine-readable protocol family and range data.

### D4. Schema Compatibility

The profile must carry machine-readable schema family and range data.

### D5. Format Compatibility

The profile must carry machine-readable format family and range data.

### D6. Governance And Trust Binding

The profile must carry governance and trust posture identifiers, including governance mode, governance profile hash, and trust policy identity.

### D7. Release And Build Anchors

The profile may anchor itself to:

- build graph model identity
- preset/toolchain model identity where useful
- component graph hash
- release series
- release identity
- install profile identities
- build identity anchors when a concrete build set is pinned

These anchors support reproducibility, provenance, and exact control-plane interpretation without converting build identity into semantic compatibility.

### D8. Target Compatibility Envelope

The profile may reference both:

- target families for broad grouping
- exact target descriptors for machine-facing specificity

These remain distinct. Family grouping is not enough for exact binary meaning.

### D9. Lane And Channel Context

The profile may declare explicit lane and channel context where constitutionally relevant, such as release channels or lane classes. This context informs interpretation, but it does not replace compatibility facts.

## E. Semantic Contract Binding

Semantic contract bundle hash belongs in the profile because semantic meaning compatibility cannot be inferred from suite version, product version, or build identity.

This field binds the release surface to explicit semantic meaning and CAP-NEG discipline. If the semantic contract bundle hash is absent, mismatched, or silently repurposed, the compatibility envelope is incomplete.

The profile therefore treats semantic contract binding as mandatory because:

- it pins meaning compatibility directly
- it prevents local release surfaces from inventing semantic equivalence by convenience
- it keeps semantic law upstream of release tooling

## F. Protocol, Schema, And Format Compatibility

Protocol, schema, and format compatibility remain explicit and separate inside the profile because they govern different truths.

Protocol compatibility answers whether negotiated or wire-level interaction can proceed.

Schema compatibility answers whether structured artifact or contract shapes can be accepted, transformed, or refused lawfully.

Format compatibility answers whether persisted or transferred payload layouts can be read, migrated, or rejected lawfully.

The profile composes these fields. It does not replace them. It must therefore preserve their explicit identity as separate compatibility layers rather than collapsing them into one generic version string.

## G. Governance And Trust Binding

Governance and trust posture belongs in the release contract profile because release compatibility is not only a question of bytes and versions. It is also a question of which governance bundle and trust posture the release was authored, resolved, and archived under.

The profile therefore binds:

- governance mode identity
- governance profile hash
- trust policy identity

This does not mean the profile authorizes publication or trust rollout. It means later consumers must not detach governance and trust posture from the compatibility envelope and then try to rediscover them from filenames, channels, or local policy guesses.

Publication, signer rotation, and trust-root operations remain later doctrine. The profile only ensures that the release surface can declare the governance and trust posture it expects consumers to evaluate.

## H. Build And Release Identity Anchors

Build and release anchors matter because a lawful release contract profile must be reconnectable to the concrete release substrate that emitted it.

The profile may therefore reference:

- build graph model identity from `Υ-0`
- preset/toolchain consolidation identity from `Υ-1`
- component graph hash
- install profile identities
- release series
- release identity
- build identity anchors when pinned to a concrete build set

These anchors serve provenance and reconstruction. They do not redefine semantic compatibility. In particular:

- build identity may be referenced, but it is not the profile
- release identity may be referenced, but it is not the profile
- component graph hash may be referenced, but it does not replace semantic contract pinning or target specificity

## I. Target Family Vs Exact Target Binding

Target family and exact target remain distinct inside the profile.

Target family is broad grouping useful for matrix navigation, policy grouping, and human comprehension.

Exact target descriptor is the machine-readable statement of concrete binary meaning. It may include:

- target matrix target id
- platform tag
- OS identity
- ABI identity
- architecture identity
- platform identity
- toolchain or environment anchors where relevant

The profile may reference both, but it must not let target family stand in for exact target specificity. When exact compatibility is claimed, machine-facing exact target descriptors must be explicit.

## J. What The Profile Must Not Do

The release contract profile must not:

- replace the versioning constitution
- overload suite version into compatibility meaning
- overload product version into compatibility meaning
- overload build identity into semantic compatibility
- use filenames as compatibility truth
- collapse release identity into product version
- treat target family shorthand as exact target compatibility
- infer omitted compatibility facts by convenience
- become a giant opaque metadata blob with no field semantics

It is a composition layer, not a semantic trash bin.

## K. Relationship To Release Manifest And Release Index

Release manifests later consume this profile as the canonical compatibility envelope for the concrete artifacts they describe.

Release index and resolution work later consume this profile as the canonical compatibility envelope for deterministic selection, refusal, and rollback planning.

This prompt does not implement those flows. It defines the envelope they must reference instead of inventing local compatibility fragments or reusing whichever manifest fields happened to be nearby.

## L. Relationship To Provenance And Archive Continuity

The release contract profile supports provenance and archive continuity because it makes compatibility reconstructable.

Later archive, rollback, downgrade, yank, and operator transaction doctrine needs to know:

- which semantic contract bundle governed the release
- which protocol, schema, and format ranges were declared
- which governance and trust posture applied
- which component graph and target envelope were in force

Explicit profiles make those questions auditable. Silent field repurposing makes them unreconstructable.

## M. Validation And Auditability

Later systems should be able to verify:

- all required profile fields are present
- hash and identifier fields are typed and non-empty
- protocol, schema, and format ranges are explicit
- semantic contract binding is present and aligned with governed release surfaces
- governance and trust posture references are explicit
- target compatibility includes exact descriptors when exact compatibility is claimed
- the profile remains compatible with the versioning constitution
- derived filenames or generated manifests did not redefine canonical profile meaning

This prompt freezes the structure that later audit tooling and resolution logic must validate.

## N. Canonical Vs Derived Distinctions And Ownership Cautions

Release contract profiles are canonical compatibility artifacts.

Generated summaries, release notes, filenames, projected tags, manifest views, dist bundle layouts, and other derived surfaces are projections.

Derived surfaces may expose profile data, but they must not silently become the source of truth for the profile.

This prompt also carries forward the active caution set:

- `schema/` remains canonical over `schemas/`
- `docs/release/` doctrine outranks generated release outputs
- `field/` and `fields/` remain ownership-sensitive
- `packs/` and `data/packs/` remain ownership-sensitive
- old planning-numbering drift does not override the active checkpoint chain

Release contract profile law must therefore be extracted from authored doctrine, schemas, registries, and committed release/control-plane code that already exists in the repo. It must not be rebound to whichever generated output is easiest for one tool to read.

## O. Anti-Patterns / Forbidden Shapes

The following shapes are forbidden:

- suite version used as the release contract profile
- product version used as the release contract profile
- build id used as the release contract profile
- filename used as the release contract profile
- target family used as the only exact compatibility descriptor
- local manifest fields inventing compatibility facts outside the canonical profile
- omitted semantic contract hash treated as acceptable by convenience
- generated release summaries silently redefining canonical profile semantics

## P. Stability And Evolution

This artifact is `CANONICAL` and `provisional`.

It is stable enough for later `Υ` prompts to consume directly, but it remains provisional because later prompts still need to freeze:

- release-index alignment
- artifact and target naming policy
- changelog policy
- release-pipeline and archive doctrine
- operator transaction law
- publication and trust gating

Any update to the release contract profile must remain explicit, reviewed, and non-silent. Later prompts may refine how the envelope is consumed, but they may not dissolve it back into version strings, filenames, or ad hoc manifest fragments.
