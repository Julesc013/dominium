Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-1, Υ-2, Υ-3, Υ-4, Υ-5, Υ-6, Υ-7, Υ-8, later checkpoints
Replacement Target: later release and control-plane constitutions may refine target matrix, preset, versioning, naming, pipeline, and operator transaction law without replacing the locked build-graph substrate
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB1.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `CMakeLists.txt`, `CMakePresets.json`, `cmake/DomIntegration.cmake`, `cmake/DominiumBundleRuntime.cmake`, `cmake/DominiumReproducible.cmake`, `cmake/dist_output.cmake`, `scripts/verify_build_target_boundaries.py`, `repo/release_policy.toml`, `data/registries/target_matrix_registry.json`, `data/registries/component_graph_registry.json`, `data/registries/install_profile_registry.json`

# Build Graph Lock

## A. Purpose And Scope

Build graph lock exists to freeze the authoritative structural model of how Dominium sources, targets, products, validation surfaces, presets, toolchains, and downstream release consumers relate to one another.

It solves a specific problem: the repo already contains a substantial build and release substrate, but that structure is spread across top-level CMake, subordinate target files, preset surfaces, packaging support, validation scripts, and release registries. Without an explicit lock, later `Υ` prompts could infer different target boundaries, target owners, or product realizations from convenience rather than from one shared constitutional model.

This document governs:

- what counts as the build graph in Dominium
- which surfaces are authoritative for build topology
- how source and target ownership should be understood
- how product realization differs from target grouping, presets, toolchains, and downstream release graphs

It does not govern:

- preset normalization in detail
- toolchain consolidation in detail
- versioning semantics
- release contract meaning
- artifact naming rules
- release index policy
- release pipeline or publication flow behavior

Those are later `Υ` prompts. This prompt locks the structural substrate they consume.

## B. Core Definition

In Dominium, the build graph is the authoritative structural relation among:

- source roots and target definitions
- target families and target aliases
- product registrations and target realizations
- validation and packaging support targets
- preset and toolchain consumer surfaces
- downstream machine-readable platform, component, and install-profile consumers

Locking the build graph means freezing the lawful categories, ownership rules, and surface hierarchy that later prompts must treat as the auditable model of build structure.

Build graph lock is not:

- a wholesale rewrite of CMake
- a promise that no target will ever change
- a preset or toolchain decision
- a versioning constitution
- a release index policy
- an artifact naming policy
- a release pipeline implementation

It is a distinct constitutional layer because the repo needs one stable answer to the question “what build structure exists and which surfaces define it?” before later release and control-plane doctrine can safely build on that answer.

## C. Why Build Graph Lock Is Necessary

Build graph lock is necessary because:

- build identity and target topology must not be guessed from scattered files
- products, runtime-support targets, tools, tests, packaging helpers, and generated outputs already coexist in the repo and must not be collapsed into one undifferentiated “build system”
- release and control-plane doctrine needs an auditable substrate for product-to-target mapping, platform matrices, install profiles, release manifests, and operator transaction work
- presets and toolchains expose useful structure, but they are configuration consumers and cannot be allowed to become hidden build canon
- generated outputs, dist trees, and release manifests are downstream realizations and cannot become source-of-truth build law by convenience

Without this lock, later `Υ` prompts would risk turning current implementation habits into policy, or worse, letting multiple tools infer different target ownership and topology from the same repo.

## D. Build Graph Elements

The constitutional build graph elements are:

### D1. Source Roots

Source roots are canonical authored surfaces that contribute code or build declarations. Observed examples include:

- root `CMakeLists.txt`
- subordinate `CMakeLists.txt` files under `engine`, `game`, `client`, `server`, `launcher`, `setup`, `tools`, `app`, `libs`, and packaging-support roots
- build-law helper modules under `cmake/`
- boundary and audit scripts under `scripts/`

### D2. Target Definitions

Target definitions are the explicit declarations that create libraries, executables, interface targets, or custom targets. In current repo reality they are expressed primarily through authored CMake files, not through generated manifests.

### D3. Target Families

Target families are broad structural classes such as product executables, runtime-support libraries, tooling executables, validation targets, packaging targets, projection or generation targets, and alias surfaces.

### D4. Product Registration Surfaces

Product registration surfaces bind a product identity to a specific target realization. In the current repo this occurs through `dom_register_product(...)` in `cmake/DomIntegration.cmake`.

### D5. Configuration Consumer Surfaces

Presets, toolchains, generator descriptors, and CI profiles consume the build graph. They reveal and constrain usage of the graph but do not define build canon by themselves.

### D6. Downstream Release Consumers

Target matrix, component graph, install profile, release manifest, and release index surfaces consume build topology and product identity. They are downstream machine-readable realizations and must remain subordinate to the locked build graph.

## E. Source/Build Ownership

A source surface belongs to a build target or target family only when that relationship is explicit in authoritative build-definition surfaces.

Build ownership therefore means:

- authored source membership is declared by target definition or authoritative helper surface
- target membership is not inferred from directory adjacency alone
- alias targets point at ownership; they do not create new ownership
- product registration records product realization; it does not replace source membership

Build ownership is not the same thing as semantic or domain ownership. A source file may semantically participate in runtime, product, or domain law while being structurally owned by a library or executable target for compilation purposes.

Canonical versus generated distinctions remain binding here:

- authored CMake and helper surfaces may define build ownership
- generated descriptors, build outputs, package trees, and release manifests may describe or reflect build ownership, but they do not become the owning source

## F. Target Classes

The high-level target classes are:

### F1. Product Targets

Targets that realize user- or operator-facing products. In the current repo, the observed registered products are:

- `client` via `dominium_client`
- `server` via `dominium_server`
- `launcher` via `launcher_cli`
- `setup` via `setup_cli`
- `tools` via `dominium-tools`

### F2. Runtime-Support Targets

Targets that compile runtime-support structure but are not themselves product identity. Observed examples include:

- `domino_engine`
- `dominium_game`
- `dominium_app_runtime`
- `launcher_core`
- `setup_core`
- `tools_shared`
- backend interface libraries such as `dom_render_backend_*` and `dom_platform_backend_*`

### F3. Tooling Targets

Targets that exist for inspection, transformation, validation, generation, or operator support. Observed examples include:

- `dom_tool_*` executables
- `coredata_compile`
- `coredata_validate`
- `data_validate`
- UI tooling executables and editors

### F4. Validation/Test Targets

Targets that provide structural, runtime, regression, or contract validation rather than product realization. Observed examples include:

- `check_*` and `verify_*` custom targets
- engine, game, and server test executables
- `testx_*` group targets

### F5. Packaging/Distribution-Support Targets

Targets that stage or package already-built outputs without becoming the source of build canon. Observed examples include:

- `dist_*`
- `pkg_*`
- `dominium_stage_dist`
- `dominium_portable_zip`
- installer and platform package targets under packaging roots

### F6. Projection/Generation Targets

Targets or helper flows that emit generated metadata, IDE projections, configured descriptors, or manifests. They are legitimate graph elements, but their outputs remain derived.

### F7. Alias And Aggregation Targets

Aliases and aggregate targets provide stable handles or grouped entrypoints:

- aliases such as `dom_client`, `dom_server`, `dom_setup`, `dom_launcher`, and namespaced target aliases
- aggregate targets such as `all_libs`, `all_apps`, `all_tools`, `all_runtime`, `check_all`, and `dist_all`

These are graph structure, but not independent product or semantic ontology.

## G. Canonical Vs Derived Build Surfaces

### G1. Canonical Build Surfaces

Current canonical build-graph surfaces are:

- top-level and subordinate authored `CMakeLists.txt`
- authored helper modules in `cmake/` that define graph structure, product registration, reproducibility, and distribution support
- authored boundary checks such as `scripts/verify_build_target_boundaries.py`

These define or constrain build topology directly.

### G2. Derived Configuration Surfaces

Important but non-canonical-by-themselves configuration consumers include:

- `CMakePresets.json`
- `cmake/toolchain_descriptor.json.in`
- CI profile JSON files
- control-plane helpers that invoke builds using named presets or profiles

They may expose build structure, but they do not become build canon merely because they are easier for tools to consume.

### G3. Generated And Distribution Surfaces

Generated and downstream surfaces include:

- configured toolchain descriptors
- build output directories such as `build/` and `out/`
- dist staging trees
- archive outputs
- generated manifests and release artifacts

These are downstream realizations. They are not authoritative build law.

### G4. Downstream Machine-Readable Release Consumers

Registries such as:

- `data/registries/target_matrix_registry.json`
- `data/registries/component_graph_registry.json`
- `data/registries/install_profile_registry.json`

are downstream release-control-plane consumers. They depend on build graph clarity but must not redefine the build graph by convenience.

## H. Build Graph Relationship To Runtime Doctrine

Build targets may realize runtime layers, but build grouping is not runtime law.

This lock therefore preserves all post-`Φ` distinctions:

- kernel is not “the engine target” by mere build naming
- components are not defined solely by library boundaries
- services are not defined solely by executable boundaries
- domain-service bindings are not created by link edges alone
- state, lifecycle, replay, snapshot, and isolation law are not authored by target shape
- product identity is not reducible to one compiled artifact

The build graph realizes these layers structurally. It does not redefine them semantically.

## I. Build Graph Relationship To Release/Control-Plane Doctrine

Later `Υ` prompts consume this lock as the structural substrate for:

- `Υ-1` preset and toolchain consolidation
- `Υ-2` versioning constitution
- `Υ-3` release index and resolution alignment
- `Υ-4` release contract profile
- `Υ-5` artifact and target naming policy
- `Υ-6` changelog policy
- `Υ-7` release pipeline and archive model
- `Υ-8` operator transaction log model

Those prompts may refine policy over the locked graph, but they must not invent a different graph or silently promote downstream release surfaces into build canon.

## J. Build Graph Relationship To Products And Platforms

Products are not just build targets, but every product must have an explicit build realization.

Current repo reality shows a lawful distinction:

- product identity is recorded through product registration
- product realization is supplied by a specific target
- platform support is expressed through target matrix and release consumers
- the same product identity may later admit multiple lawful realizations without losing identity

This prevents a mistaken collapse where one target name, one preset, or one platform row becomes the whole meaning of a product.

## K. Build Graph Relationship To Presets/Toolchains

Presets and toolchains are important, but they are consumers of build-graph law.

Current evidence shows:

- presets capture configuration lanes such as local, verify, and release-check
- toolchain descriptors capture compiler, stdlib, runtime, linker, target, and generator facts
- strict toolchain checks constrain lawful configure behavior

None of those surfaces are the source of build canon. They express how the locked graph is configured, selected, or verified.

Later `Υ-1` may normalize those surfaces more deeply. `Υ-0` only freezes the rule that they remain downstream of the graph lock.

## L. Build Graph Relationship To Generated And Distribution Surfaces

Generated artifacts, package outputs, distribution bundles, and release manifests are downstream of the build graph.

This means:

- dist or archive outputs do not become source-of-truth build structure
- package layout does not define target ownership
- generated manifests do not define build canon
- release component graphs and install profiles may consume product and target structure, but they do not replace the authored graph

This keeps later archive, mirror, release pipeline, and publication work compatible with the lock without letting those later layers rewrite it.

## M. Validation And Auditability

Build graph lock must remain auditable and testable in principle.

Later systems should be able to verify:

- target existence and target class
- explicit product registration and product-to-target mapping
- source/build ownership from authored graph surfaces
- alias versus owning-target distinction
- canonical versus derived build-surface distinction
- target matrix consistency against product realizations
- component-graph and install-profile consistency against locked product surfaces
- preset and toolchain linkage consistency without granting them canonical ownership

Existing evidence already supports this direction through:

- `scripts/verify_build_target_boundaries.py`
- top-level CMake guard targets and configure-time verification hooks
- release/control-plane consumers that already require deterministic platform and component registries

## N. Ownership And Anti-Reinvention Cautions

The following cautions remain binding:

- ownership-sensitive roots remain active, including `field/` versus `fields/`, `schema/` versus `schemas/`, and `packs/` versus `data/packs/`
- canonical versus projected or generated distinctions remain binding
- the thin `runtime/` root is not automatically canonical simply because the build references runtime-adjacent code
- build law must be extracted from repo reality and stronger doctrine, not invented greenfield
- stale planning numbering drift must not override the active post-safe-`Φ-B` checkpoint and forward-order artifacts

This lock also carries a build-specific caution:

- `data/planning/final_prompt_inventory.json` contains stale `Υ` numbering for part of the release band, so active checkpoint and next-order artifacts outrank that drift for current prompt sequencing

## O. Anti-Patterns / Forbidden Shapes

The following shapes are forbidden:

- treating preset files as hidden build canon
- treating generated manifests as authoritative build truth
- using target names as semantic ontology
- silently equating product identity with one build-target realization
- guessing ownership from directory adjacency instead of target definition
- treating dist or archive outputs as source-of-truth build structure
- letting downstream release registries redefine the authored graph by convenience
- flattening runtime product, support-library, tooling, validation, and packaging targets into one undifferentiated “system target” vocabulary

## P. Stability And Evolution

This artifact is `provisional`, but binding for the current `Υ-A` band.

Later prompts may refine:

- preset and toolchain structure in `Υ-1`
- version meaning in `Υ-2`
- release-index and resolution alignment in `Υ-3`
- release contract semantics in `Υ-4`
- naming, changelog, pipeline, archive, and operator transaction work in `Υ-5` through `Υ-8`

Those later prompts must remain explicit and non-silent. They may refine how the locked graph is consumed, but they must not silently replace:

- the authoritative build surfaces
- the target class model
- the source/build ownership rules
- the canonical versus derived build-surface distinction
