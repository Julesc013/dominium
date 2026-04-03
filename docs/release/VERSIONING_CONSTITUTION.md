Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-3, Υ-4, Υ-5, Υ-6, Υ-7, Υ-8, later checkpoints
Replacement Target: later release-contract, artifact-naming, release-index, archive, publication, and operator-transaction doctrine may refine field-specific procedures without replacing the layered versioning model
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB1.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/PRESET_AND_TOOLCHAIN_CONSOLIDATION.md`, `docs/release/RELEASE_IDENTITY_CONSTITUTION.md`, `docs/release/RELEASE_INDEX_MODEL.md`, `docs/release/RELEASE_INDEX_RESOLUTION_POLICY.md`, `docs/release/RELEASE_MANIFEST_MODEL.md`, `docs/release/ARTIFACT_NAMING_RULES.md`, `docs/release/UPDATE_SIM_MODEL_v0_0_0.md`, `repo/release_policy.toml`, `schema/SCHEMA_VERSIONING.md`, `schema/release/build_id.schema`, `schema/identity/artifact_identity.schema`, `schema/release/artifact_identity.schema`, `release/build_id_engine.py`, `release/release_manifest_engine.py`, `release/update_resolver.py`, `data/registries/component_graph_registry.json`, `data/registries/toolchain_matrix_registry.json`, `VERSION_SUITE`, `VERSION_CLIENT`, `VERSION_SERVER`, `VERSION_GAME`, `VERSION_TOOLS`, `VERSION_LAUNCHER`, `VERSION_SETUP`, `VERSION_ENGINE`

# Versioning Constitution

## A. Purpose And Scope

Versioning constitution exists to freeze one explicit layered model for version labels, compatibility fields, immutable identities, release identifiers, and target descriptors across Dominium.

It solves a specific problem: the repo already contains release identity docs, resolver policy, manifest rules, schemas, build identity code, update feeds, and product version files, but those surfaces can still be misread as if one version string or one filename explains everything. Later `Υ` prompts need one constitutional answer to the question "which truth belongs in which field?" before they can safely refine release contracts, artifact naming, release indices, archives, operator transactions, or publication doctrine.

This document governs:

- what "version" means in Dominium
- which version-like and identity-like fields exist
- what each field is for
- what must not be overloaded into one string or one filename
- how layered versioning relates to build graph lock, preset/toolchain consolidation, release identity, and release-index work

It does not govern:

- the final release contract profile shape
- release-index resolution mechanics in detail
- artifact naming syntax in detail
- archive or publication flow behavior
- release pipeline implementation

Those are later `Υ` prompts. This prompt freezes the field semantics they must consume.

## B. Core Doctrine

The constitutional versioning rules are:

- different truths require different fields
- version is not identity
- compatibility is not a marketing or suite-facing version label
- filenames project metadata and do not define it
- build identity is immutable provenance and reproducibility evidence, not semantic precedence
- target family is a broad compatibility grouping, not an exact binary descriptor
- release-control-plane identifiers must remain explicit instead of being hidden inside overloaded version strings

This is a distinct constitutional layer because Dominium already carries suite labels, per-product versions, protocol and schema surfaces, semantic contract pins, deterministic build IDs, release IDs, artifact identities, and target-matrix metadata. Without a constitution, those layers drift into folklore and local tool interpretation.

## C. Version And Identity Classes

The main field classes are:

### C1. Suite Version

A human-facing curated snapshot identifier for a coordinated suite state.

### C2. Product Version

A product-scoped evolution label for one product line such as client, server, engine, launcher, setup, tools, or game.

### C3. Protocol Version Or Range

A machine-readable compatibility surface for negotiated wire or inter-process behavior.

### C4. Schema Version

A machine-readable contract-structure version governed by schema law and migration or refusal rules.

### C5. Format Version

A machine-readable persisted-layout or payload-layout version for save, manifest, bundle, feed, or archive structures.

### C6. Semantic Contract Bundle Hash

A machine-readable pin for semantic meaning compatibility and contract-bundle identity.

### C7. Build Identity

A deterministic build instance identity such as `build_id`, derived from canonical deterministic inputs.

### C8. Artifact Identity And Content Hash

Immutable artifact-level identity surfaces, including stable artifact identifiers and content-addressed hashes.

### C9. Release Contract Profile

A later explicit machine-readable compatibility envelope that binds together the fields required for release admission and resolution. It exists as a constitutional field class now even though its concrete profile model is deferred.

### C10. Release-Control-Plane Identity Fields

Explicit release-facing identifiers such as `release_id`, `release_series`, and `channel_id`.

### C11. Target Family

A broad compatibility grouping such as a family-level platform lane or target matrix class.

### C12. Exact Target Descriptor

A machine-readable exact target statement covering the specificity needed for concrete binary meaning, such as OS, ABI, arch, toolchain family, or other exact compatibility attributes.

## D. Suite Version

Suite version is the human-facing curated snapshot identity for a coordinated Dominium suite state. The existing `VERSION_SUITE` surface demonstrates this role.

Suite version is useful for:

- release notes and changelog curation
- archive and operator-facing release references
- human discussion of a coordinated shipped or planned suite snapshot
- aligning a multi-product release moment without erasing per-product independence

Suite version must not be treated as:

- the compatibility oracle
- the semantic contract pin
- the exact target descriptor
- the immutable artifact identity
- the only version field that matters

A suite version may point humans toward a coordinated snapshot, but compatibility remains governed by explicit machine-readable fields.

## E. Product Version

Product version expresses product-scoped evolution semantics. The existing `VERSION_CLIENT`, `VERSION_SERVER`, `VERSION_GAME`, `VERSION_ENGINE`, `VERSION_TOOLS`, `VERSION_LAUNCHER`, and `VERSION_SETUP` surfaces demonstrate that products may version independently even when the repo also carries a suite-facing label.

Product version exists so later release and update systems can talk about progression within one product line without pretending that every other product must move in lockstep.

Product version differs from suite version because:

- product version speaks about one product lineage
- suite version speaks about one curated coordinated snapshot across multiple products

Product version may participate in deterministic candidate ranking inside a lawful compatibility envelope, but it must not override explicit compatibility checks.

## F. Protocol, Schema, And Format Versions

Protocol, schema, and format versions remain separate because they govern different truths.

Protocol version or range governs negotiated interoperability behavior. A product may carry a newer product version and still fail compatibility if protocol ranges do not overlap.

Schema version governs contract shape and migration or refusal law. The schema-versioning doctrine under `schema/SCHEMA_VERSIONING.md` already makes this explicit and separate from product release labels.

Format version governs persisted or transferred structure for specific artifact families such as save files, manifests, bundles, feeds, or archives.

These fields must not be collapsed into suite version or product version because doing so would blur:

- user-facing release narration
- machine-readable compatibility
- migration and refusal obligations
- persisted-format legality

## G. Semantic Contract Bundle Hash

Semantic contract bundle hash exists because semantic meaning compatibility must remain explicit and machine-readable.

This field differs from version labels because it pins meaning, not narrative release progression. It carries the CAP-NEG and semantic-contract discipline that later release and update systems must honor even when product or suite versions look compatible at a glance.

Semantic contract bundle hash must therefore remain:

- explicit
- machine-readable
- separate from suite and product version labels
- separate from build identity

Later release-contract work may bind this field into a compatibility envelope, but this field must not disappear into a version string.

## H. Build Identity

Build identity captures the exact deterministic build instance. In current repo reality, `schema/release/build_id.schema` and `release/build_id_engine.py` already show that `build_id` is derived from deterministic inputs such as product identity, semantic contract registry hash, compilation options hash, source revision, explicit build number, and platform tag when unavoidable.

Build identity is for:

- immutable provenance
- reproducibility evidence
- deterministic build comparison
- release-manifest cross-checking
- deterministic candidate tie-breaks after compatibility gates pass

Build identity is not:

- semantic precedence
- compatibility truth by itself
- a substitute for protocol, schema, or format version
- a replacement for semantic contract pinning

Content hash remains adjacent to build identity but distinct from it. Content hash identifies exact payload content. Build identity identifies the deterministic build instance that produced compatible outputs. Neither field should be silently repurposed into a suite or product version.

## I. Release Contract Profile

Release contract profile exists as a distinct field class because Dominium needs an explicit machine-readable compatibility envelope. That envelope will later bind together the relevant truths for release admission, install planning, update resolution, downgrade law, and archive continuity.

Release contract profile is necessary precisely because one version string cannot safely encode:

- product evolution
- protocol compatibility
- schema compatibility
- format compatibility
- semantic contract pinning
- target specificity
- build identity

This prompt does not implement the profile. It freezes the rule that such an envelope must remain explicit and must not be overloaded into suite version, product version, or filenames.

## J. Target Family Vs Exact Target

Target family is a broad compatibility grouping. It is useful for high-level target matrix language, operator-facing descriptions, and release-index grouping.

Exact target descriptor is the machine-readable statement of concrete binary meaning. It may need to express:

- OS family
- ABI
- architecture
- toolchain family or constraints
- runtime linkage or comparable exact compatibility details

These fields must remain distinct because family labels alone are insufficient for exact binary interpretation. A family such as `win64` or `linux-x86_64` can help humans navigate a matrix, but exact admission and compatibility need more than a family label.

## K. Filenames And Projections

Filenames, archive names, generated manifests, projected tags, and path layouts are projections of metadata.

They are useful because they:

- help humans recognize artifacts
- support deterministic packaging and archive layout
- expose metadata in an ergonomic form

They do not define truth because:

- they can be truncated or normalized for transport
- they are downstream of explicit metadata fields
- different projections may lawfully present the same artifact differently
- generated naming surfaces are derived outputs, not canonical field owners

Raw filenames must therefore never become the compatibility oracle or the identity source-of-truth.

## L. Versioning And Precedence

Dominium recognizes multiple kinds of ordering or precedence, and they must not be conflated.

Human curation order may use suite version and release-facing labels.

Product candidate ranking may use product version once explicit compatibility gates have already passed.

Deterministic tie-breaks may use build identity, artifact identity, or content-addressed fields after higher-order compatibility and policy filters have already admitted the candidate set.

Semantic precedence must remain governed by explicit compatibility surfaces such as:

- semantic contract bundle hash
- protocol version or range
- schema version where relevant
- format version where relevant
- later release contract profile

Build identity, local build numbers, filename shape, and host-local naming must not alter semantic precedence improperly.

## M. Relationship To Release Identity And Release Index

Later release identity and release-index doctrine must consume this constitution instead of redefining field meaning locally.

Release identity work consumes:

- suite version and product version semantics
- build identity semantics
- release-control-plane identifier semantics
- artifact identity and content-hash semantics

Release-index and resolution work consumes:

- product-version ranking rules
- explicit compatibility-gating fields
- target family versus exact target distinction
- the rule that filenames and projections are downstream only

This document therefore establishes the field semantics that later `Υ-3`, `Υ-4`, `Υ-5`, `Υ-6`, `Υ-7`, and `Υ-8` must treat as upstream law.

## N. Relationship To Provenance And Archive Continuity

Layered versioning supports provenance and archival continuity because it separates:

- human-facing curated release labels
- product-line evolution
- semantic compatibility
- structural compatibility
- immutable build and artifact identity
- release-control-plane lineage

Later yank, downgrade, rollback, archive, and publication doctrine depends on this separation. Silent repurposing of existing fields is therefore forbidden.

An archive may preserve filenames, release tags, manifests, and bundle names, but continuity remains lawful only when the underlying explicit fields keep their meaning.

## O. Ownership And Anti-Reinvention Cautions

This constitution carries forward the current caution set:

- `field/` is not equivalent to `fields/`
- `schema/` is canonical over `schemas/`
- `packs/` and `data/packs/` remain ownership-sensitive and must not be collapsed by convenience
- canonical versus projected or generated surfaces remain binding
- thin `runtime/` roots are not automatically canonical release law
- old planning numbering drift does not override the active checkpoint chain

Versioning law must therefore be extracted from authored doctrine, schemas, registries, release engines, and committed version surfaces that already exist in the repo. It must not be invented greenfield or rebound to whichever generated output is easiest for a tool to parse.

## P. Anti-Patterns / Forbidden Shapes

The following shapes are forbidden:

- using suite version as the compatibility oracle
- allowing build metadata or build IDs to affect semantic precedence
- treating filenames as the source of truth
- collapsing product version, protocol version, schema version, format version, and semantic contract pinning into one field
- treating target family labels as exact target descriptors
- conflating immutable artifact identity with artifact version
- allowing generated manifests or release bundles to silently redefine canonical field semantics
- letting one tool or update surface reinterpret field meaning locally

## Q. Stability And Evolution

This artifact is `CANONICAL` and `provisional`.

It is stable enough for later `Υ` prompts to consume directly, but it remains provisional because later prompts still need to freeze:

- release-contract profile structure
- artifact naming refinement
- release-index and resolution alignment
- archive and operator transaction doctrine
- publication and trust doctrine

Any update to this constitution must remain explicit, reviewed, and non-silent. Later prompts may refine field procedures, but they may not collapse layered truths back into one overloaded version string or one filename convention.
