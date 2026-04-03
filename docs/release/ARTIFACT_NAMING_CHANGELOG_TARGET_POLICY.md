Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: `docs/release/ARTIFACT_NAMING_RULES.md` as the broader constitutional naming/changelog/target policy layer while preserving that file as historical release-surface evidence
Superseded By: none
Stability: provisional
Future Series: Υ-5, Υ-6, Υ-7, Υ-8, later checkpoints
Replacement Target: later release-index, operator-transaction, archive, publication, and trust doctrine may refine consumers and operational procedures without replacing the naming/changelog/target policy semantics
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB1.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/PRESET_AND_TOOLCHAIN_CONSOLIDATION.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_IDENTITY_CONSTITUTION.md`, `docs/release/RELEASE_INDEX_MODEL.md`, `docs/release/ARTIFACT_NAMING_RULES.md`, `docs/release/RELEASE_NOTES_v0_0_0_mock.md`, `updates/changelog.json`, `data/registries/target_matrix_registry.json`, `data/registries/os_registry.json`, `data/registries/arch_registry.json`, `data/registries/platform_registry.json`, `data/registries/product_registry.json`, `data/registries/release_channel_registry.json`, `repo/release_policy.toml`

# Artifact Naming, Changelog, And Target Naming Policy

## A. Purpose And Scope

This policy exists to freeze one canonical interpretation of artifact naming, changelog layering, and target naming after the build graph, preset/toolchain, versioning, and release-contract foundations have already been defined.

It solves a specific problem: Dominium already contains deterministic artifact naming rules, release notes, machine-readable change feeds, target registries, product registries, and release-facing descriptors, but those surfaces can still be misread as if filenames, prose summaries, or family shorthand are themselves the authoritative source of compatibility or identity truth. Later `Υ` prompts need one stable policy that says what names may project, what changelogs may summarize, and how target naming remains lawful without flattening structured metadata.

This document governs:

- how artifact names are formed constitutionally
- what filenames may and may not project
- how changelogs are layered and governed
- how target naming works at the family and exact-descriptor levels
- how these policies remain subordinate to build graph lock, preset/toolchain consolidation, versioning constitution, and release contract profile law

It does not govern:

- release-index alignment mechanics
- operator transaction structure
- archive or publication operational flows
- wholesale filename migration
- historical changelog rewrites
- codebase-wide target descriptor rewrites

Those are later `Υ` prompts. This prompt freezes the naming and change-record policy they must consume.

## B. Core Doctrine

The constitutional rules are:

- filenames are projections of metadata
- changelogs are governed records, not freeform truth sources
- target family and exact target are distinct
- names must not silently replace structured metadata
- human readability and machine readability must both be supported, but through the right layers
- projection convenience must not redefine compatibility, identity, or semantic truth

This policy is a distinct layer because Dominium needs both readable naming and structured machine truth, but those needs belong to different artifacts and must not be collapsed together.

## C. Artifact Naming Classes

The main artifact naming classes are:

### C1. Suite-Level Distributable Artifacts

Artifacts that represent a suite-facing distribution snapshot, archive, or bundle family.

### C2. Product-Level Artifacts

Artifacts that realize one product line such as client, server, engine, launcher, setup, tools, or game.

### C3. Machine-Readable Manifests And Registries

Artifacts whose names identify manifest, index, registry, lock, or profile surfaces intended primarily for machines.

### C4. Checkpoint And Support Bundles

Planning, checkpoint, continuity, or support bundles that preserve analysis state but are not release identity truth.

### C5. Generated Projections

Derived output names such as generated descriptors, dist bundle labels, or configured helper files.

### C6. Archived Artifacts

Archive or retention-oriented artifacts that project release-facing context for recovery, history, or offline transport.

### C7. Local, Development, And Build-Only Artifacts

Ephemeral or operator-local artifacts whose names may carry convenience context but must not be mistaken for governed release identity or compatibility truth.

Different artifact naming classes may project different subsets of metadata. They must not all be forced into one misleading filename grammar.

## D. Filename Projection Rules

Filenames may project:

- artifact class or kind
- product identity
- suite version or product version where useful for humans
- release channel or lane where useful
- deterministic build identity when the artifact class constitutionally benefits from it
- content-hash prefix or comparable immutable identity shorthand
- broad target-family shorthand or platform tag
- archive or checkpoint labels for continuity work

Filenames must not attempt to authoritatively encode:

- the full release contract profile
- the full exact target descriptor
- semantic contract compatibility by implication
- governance or trust policy meaning by shorthand alone
- machine-complete precedence or selection semantics
- every identity and compatibility truth at once

Filenames must remain:

- readable
- stable
- non-deceptive
- consistent within their artifact class
- explicit about being projections rather than the truth owner

The key rule is that filenames may summarize selected metadata, but they must not redefine identity, compatibility, or target truth if the structured metadata disagrees.

## E. Layered Metadata Relationship

Artifact names must relate to layered metadata as follows.

### E1. Suite Version

May appear in suite-facing filenames for human comprehension and archive continuity.

Must not be treated as the compatibility oracle.

### E2. Product Version

May appear in product-facing filenames for product-line comprehension.

Must not replace protocol, schema, format, or semantic compatibility fields.

### E3. Release Contract Profile

May be referenced indirectly through a profile id or class label only when a machine-oriented artifact class needs that projection.

The full release contract profile remains structured machine truth and must not be flattened into a filename.

### E4. Build Identity

May appear in filenames for deterministic build-produced artifacts where provenance or differentiation matters.

It remains a provenance and identity projection, not semantic precedence or compatibility meaning.

### E5. Target Family

May appear in filenames as broad human-facing shorthand such as a platform tag or family-level lane tag.

It is insufficient for exact machine-facing compatibility.

### E6. Exact Target

Must remain primarily structured machine-readable metadata.

Filenames may project a lossy shorthand, but they must not claim that shorthand is a full exact target descriptor.

### E7. Release Channel Or Lane

May appear in filenames or archive labels when useful for operator and archive clarity.

Channel and lane terms remain context fields, not substitutes for the compatibility envelope.

## F. Artifact Naming Grammar Policy

Naming grammars should be structured conceptually around the artifact class, not around one universal string template.

The governing rules are:

- every grammar must declare which metadata subset it projects
- different artifact classes may project different subsets of lawful metadata
- grammars must remain consistent inside a class
- grammars must not over-promise machine truth they do not actually encode
- machine-readable artifacts may use tighter and more structured naming than human-facing release notes or bundles

This means a product binary, a release manifest, a checkpoint zip, and an archive record may all use different legal naming grammars while still remaining constitutional.

Consistency is required, but false uniformity is not.

## G. Changelog Policy

Dominium changelogs must remain layered.

### G1. Suite-Level Changelog

Suite-level changelog prose is the human-facing curated summary of a coordinated suite snapshot. Existing release notes and future suite-facing changelog surfaces belong here.

### G2. Product-Level Changelog

Where relevant, product-level changelog surfaces summarize one product line without pretending to describe the full suite or the full compatibility envelope.

### G3. Machine-Readable Release And Change Metadata

Machine-readable surfaces such as `updates/changelog.json`, release manifests, release indices, yanks, and later operator transaction records carry structured change state for tools and automation.

### G4. Checkpoint And Planning History

Planning and checkpoint artifacts may record governance, sequencing, and doctrine evolution, but they are not release changelog truth.

### G5. Deprecation, Yank, And Supersession Notes

Deprecation, yank, rollback, downgrade, and supersession notes may have both prose and machine-readable forms. The prose explains; the structured records govern.

The changelog policy therefore distinguishes:

- human-readable narrative
- machine-readable release state
- planning continuity records
- deprecation or supersession evidence

Those layers must not be collapsed into one text file or one JSON feed by convenience.

## H. Change Record Semantics

Change records must be attributable, layered, and anchored.

At minimum, governed change recording should preserve:

- scope, such as suite, product, artifact class, or policy surface
- relevant release or compatibility anchors when applicable
- whether the record is prose, structured machine state, or planning continuity
- whether the record reflects addition, removal, supersession, deprecation, yank, or rollback context

Changelog prose may summarize changes, but it must not replace:

- release manifests
- release contract profiles
- release indices
- transaction records
- downgrade or yank decisions

Freeform summary is valuable for humans. It is not enough for exact release reconstruction.

## I. Target Naming Policy

A target family is the broad grouping used for human-facing and policy-facing target categorization. Examples in repo reality include family-level concepts exposed through `platform_tag`, OS family, or target-matrix groupings.

An exact target descriptor is the machine-readable statement of concrete binary meaning, such as:

- target matrix target id
- OS identity
- ABI identity
- architecture identity
- platform identity
- toolchain or environment anchors where relevant

They differ because:

- family naming helps people navigate a matrix
- exact descriptors govern concrete compatibility and reconstruction

Names may project either layer, but policy must remain explicit about which layer is being projected.

Target-family shorthand is therefore insufficient for:

- exact binary compatibility
- precise release admission
- exact artifact identity
- machine-complete resolution behavior

## J. Relationship To Build Graph And Preset/Toolchain Doctrine

Artifact and target naming must remain compatible with build graph lock.

That means:

- build graph law still determines target structure upstream
- target names must not redefine target ownership or target classes
- invocation surface names, preset labels, and toolchain file names must not silently become target canon
- preset and toolchain consolidation remains the interpretation layer for invocation surfaces, not the owner of target truth

Naming policy projects the build graph. It does not replace it.

## K. Relationship To Release Contract Profile

The release contract profile remains the machine-readable compatibility envelope.

Artifact names and changelogs may project aspects of release state, but they must not replace the profile.

Target naming and profile fields must remain aligned, which means:

- filenames may project target family or platform tag
- exact target descriptors remain structured profile-facing and index-facing data
- changelog prose may mention channels, versions, or release labels
- changelog prose must not silently invent compatibility claims that the profile does not declare

The profile owns compatibility composition. Names and prose only project selected aspects of that state.

## L. Canonical Vs Derived Distinctions

This policy is canonical.

Artifact filenames are derived.

Generated summaries, bundle labels, projected tags, and machine-generated convenience names are derived.

Changelog prose is governed, but prose alone is not canonical machine truth.

Machine-readable release state remains canonical only where a stronger governed artifact explicitly owns that truth, such as:

- release contract profile
- release manifest
- release index
- target matrix and related registries
- product and channel registries
- later operator transaction and downgrade records

The rule is simple: names and summaries may carry truth forward, but they must not become the raw source of truth by convenience.

## M. Ownership And Anti-Reinvention Cautions

This prompt carries forward the active caution set:

- `field/` is not equivalent to `fields/`
- `schema/` remains canonical over `schemas/`
- `packs/` and `data/packs/` remain ownership-sensitive
- canonical versus projected or generated distinctions remain binding
- thin `runtime/` roots are not automatically release-law canon
- older planning numbering drift does not override the active checkpoint chain

This matters here because artifact names, changelog prose, and target shorthands are especially prone to accidental canon drift. The policy must therefore be extracted from authored doctrine, registries, and committed release/control-plane reality that already exists in the repo rather than from whichever strings are easiest to read in generated outputs.

## N. Anti-Patterns / Forbidden Shapes

The following shapes are forbidden:

- filename as compatibility oracle
- filename as exact target truth
- changelog prose as authoritative machine state
- build id forced into semantic precedence via filenames
- one naming grammar pretending to fit every artifact class
- checkpoint bundle names treated as release identity truth
- target family treated as exact target descriptor
- release notes or changelog text treated as sufficient for rollback, downgrade, or compatibility resolution
- generated bundle labels silently redefining version, profile, or target meaning

## O. Stability And Evolution

This artifact is `CANONICAL` and `provisional`.

It is stable enough for later `Υ` prompts to consume directly, but it remains provisional because later prompts still need to freeze:

- release-index alignment
- operator transaction law
- archive and mirror policy
- publication and trust gating

Any update to this policy must remain explicit, reviewed, and non-silent. Later prompts may refine specific consumers and operational procedures, but they may not turn filenames, changelog prose, or target shorthand into shadow sources of truth.
