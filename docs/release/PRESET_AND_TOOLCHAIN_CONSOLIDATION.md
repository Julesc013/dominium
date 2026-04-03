Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-2, Υ-3, Υ-4, Υ-5, Υ-6, Υ-7, Υ-8, later checkpoints
Replacement Target: later versioning, release-contract, naming, release-index, archive, and operator-transaction doctrine may refine the consolidated matrix without replacing the underlying preset/toolchain classifications
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB1.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `CMakePresets.json`, `CMakeLists.txt`, `cmake/toolchains/`, `cmake/ide/`, `cmake/toolchain_descriptor.json.in`, `.vscode/tasks.json`, `scripts/ci/check_repox_rules.py`, `scripts/verify_projection_regen_clean.py`, `scripts/repox/repox_release.py`, `tools/xstack/ci/`, `data/planning/reality/toolchain_and_preset_map.json`, `data/registries/target_matrix_registry.json`, `data/registries/toolchain_matrix_registry.json`, `data/registries/install_profile_registry.json`, `repo/release_policy.toml`

# Preset And Toolchain Consolidation

## A. Purpose And Scope

Preset and toolchain consolidation exists to freeze one constitutional interpretation of the preset matrix, toolchain surfaces, IDE projection helpers, and invocation pathways already present in the Dominium repository.

It solves a specific problem: the repo already contains a large authored preset and toolchain substrate, but that substrate spans visible developer entry lanes, hidden scaffold presets, legacy compatibility lanes, IDE projection presets, explicit toolchain files, CI profiles, editor tasks, release dry-run entrypoints, and generated descriptors. Without consolidation law, later `Υ` prompts could read different meanings into the same surfaces and accidentally let presets, toolchain names, or CI scripts become hidden canon.

This document governs:

- what presets and toolchain surfaces mean in Dominium
- how authored invocation surfaces are classified after `Υ-0`
- how canonical, derived, transitional, deprecated, and review-gated statuses are assigned
- how preset and toolchain lanes relate to products, platforms, target matrix, and build graph lock
- what later `Υ` prompts must consume rather than reinterpret

It does not govern:

- a wholesale preset rewrite
- a build-system rewrite
- versioning doctrine
- release contract meaning
- artifact naming
- release index semantics
- publication or archive workflows

Those are later `Υ` prompts. This prompt freezes the preset/toolchain interpretation layer that they consume.

## B. Core Definition

In Dominium, a preset is an authored invocation surface that selects or constrains a build lane over the already-locked build graph. A preset may capture generator choice, binary directory, cache-variable bindings, product- or platform-relevant toggles, and downstream build or test entry behavior, but it does not create build canon on its own.

A toolchain surface is an authored configuration surface that constrains compiler family, runtime linkage, target architecture, generator family, SDK expectations, or legacy IDE projection policy for a lawful build lane.

Consolidation means freezing the shared interpretation of those surfaces so every later prompt, tool, CI path, and release/control-plane consumer reads the same matrix the same way. Consolidation is not the same thing as flattening the matrix into one lane, deleting legacy scaffolding, or rewriting CMake.

This layer differs from:

- rewriting the build system
- changing target taxonomy
- versioning policy
- release contract profile
- artifact naming policy
- release index policy

It is a distinct constitutional layer because the preset/toolchain matrix is already rich enough that drift now comes mostly from interpretation, duplication, and status ambiguity rather than from missing files.

## C. Why Consolidation Is Necessary

Consolidation is necessary because:

- multiple preset families already overlap in meaning and can drift if left undocumented
- target and build meaning must not vary depending on whether the caller used visible presets, hidden bases, CI JSON, editor tasks, IDE projection presets, or release scripts
- `Υ-0` build graph lock needs a stable projection into preset and toolchain lanes
- later release/control-plane work requires one coherent answer to which lanes are operator-facing, which are scaffold-only, which are projection-only, which are compatibility-only, and which are downstream or generated
- generated IDE outputs and configured toolchain descriptors are useful evidence but must not become configuration law by convenience

Without this consolidation, two agents could look at the same repo and disagree about whether `local`, `windows-msvc-vs2026`, `release-winnt-x86_64`, `ide-win-vs2026-win11-client-gui`, or a generated projection manifest is the real entry surface.

## D. Preset/Toolchain Element Classes

The main element classes are:

### D1. Canonical Preset Matrix Surface

The authored preset matrix in `CMakePresets.json` is the primary preset-definition surface for this layer. It is canonical within the preset/toolchain layer, while still remaining downstream of build graph lock.

### D2. Canonical Toolchain Module Surfaces

The authored toolchain modules under `cmake/toolchains/` are canonical toolchain surfaces. They constrain architecture and system assumptions for explicit lanes such as `win16-x86_16` and `dos-x86_16`.

### D3. Canonical IDE Projection Support Surfaces

The authored helpers under `cmake/ide/` are canonical projection-support surfaces. They define how projection presets and projection manifests are generated, classified, and constrained without making generated IDE outputs canonical.

### D4. Platform-Specific Preset Lanes

These are authored presets that realize platform and toolchain families such as:

- Windows/MSVC
- Linux GCC or Clang
- macOS/Xcode or Cocoa-family lanes
- alternate Windows toolchain lanes such as `windows-clangcl-debug` and `windows-mingw-debug`

### D5. Operator-Facing Dev, Verify, And Release-Check Lanes

These are the visible lanes used by humans and tooling for common operation. Observed examples include:

- `local`
- `verify`
- `release-check`
- `linux-verify`
- `linux-verify-full`
- `macos-verify`
- `macos-verify-full`
- `linux-gcc-dev`
- `linux-clang-dev`
- `macos-dev`
- `release-winnt-x86_64`
- `release-linux-x86_64`
- `release-macos-arm64`

### D6. Hidden Scaffold And Alias Surfaces

These are authored but hidden presets used to factor common policy and reduce duplication. Observed examples include:

- `msvc-base`
- `dev-win-vs2026`
- `verify-win-vs2026`
- `release-win-vs2026`
- `linux-debug`
- `linux-clang-debug`
- `macos-xcode-debug`

These are canonical scaffolding surfaces, but they are not the whole operator-facing contract.

### D7. Legacy Or Projection-Oriented Preset Surfaces

These include:

- legacy compatibility presets such as `win9x-x86_32-legacy`, `win16-x86_16`, `dos-x86_16`, `legacy-win-vs2015`, `base-msys2`, `msys2-debug`, and `msys2-release`
- IDE projection presets such as `ide-win-vc6-win9x-client-gui` and `ide-linux-clang-modern-client-gui`

They remain relevant, but they require explicit classification so they do not silently override modern operator lanes.

### D8. CI-Oriented Invocation Surfaces

These are authored consumers of the matrix, including:

- `tools/xstack/ci/profiles/*.json`
- `tools/xstack/ci/xstack_ci_entrypoint.py`
- `.vscode/tasks.json`
- `scripts/repox/repox_release.py`
- `scripts/verify_projection_regen_clean.py`
- `scripts/ci/check_repox_rules.py`

They are not preset canon, but they are authoritative consumers whose alignment must be auditable.

### D9. Generated Projection And Descriptor Surfaces

Derived outputs include:

- configured toolchain descriptors emitted from `cmake/toolchain_descriptor.json.in`
- generated IDE project trees under `ide/`
- generated projection manifests under `ide/manifests/*.projection.json`

These are useful, but they remain derived.

## E. Canonical Vs Derived Distinction

Canonical preset/toolchain surfaces are authored repo surfaces that define or constrain invocation meaning for this layer. In current repo reality those include:

- `CMakePresets.json`
- `cmake/toolchains/*.cmake`
- `cmake/ide/*.cmake`
- CI and editor invocation contract surfaces that verify or consume the matrix without redefining it

Derived or generated surfaces include:

- configured toolchain descriptors
- generated IDE files
- generated projection manifests
- build output trees
- dist output trees

Generated IDE files, generated manifests, and configured descriptors are not canonical configuration law. They may mirror or prove a lane, but they may not author it.

This distinction remains binding even when a derived surface is easier for a tool to consume than the authored preset matrix.

## F. Relationship To Build Graph Lock

Preset and toolchain consolidation remains subordinate to `Υ-0` build graph lock.

That means:

- presets realize the already-locked graph rather than redefine it
- toolchain surfaces constrain how a target lane is built rather than create new target classes
- product registration, source/build ownership, and target-family meaning remain upstream
- presets may select a realization lane, but they may not silently change product identity
- toolchain names may suggest families, but they may not become the real target taxonomy

Consolidation must therefore preserve the build graph lock answer to “what exists” and only refine how lawful invocation surfaces are grouped and interpreted.

It must also preserve post-`Φ` runtime vocabulary:

- `kernel` is not identical to one compiler or preset family
- `component` is not identical to one library or project-generation lane
- `service` is not identical to one executable invocation path
- `product` is not identical to one preset or one platform lane

Preset and toolchain consolidation may describe how those layers are realized during build, but it may not redefine their meaning by build folklore.

## G. Relationship To Products, Platforms, And Target Matrix

Preset and toolchain surfaces may realize product, platform, architecture, and compiler lanes, but they do not erase the difference between those concepts.

The current repo already shows several important distinctions:

- product identity is carried by product registrations and downstream release surfaces, not by preset names alone
- one product may appear across multiple lawful preset families without becoming a different product
- one target-matrix row may be realized by multiple preset or environment families over time
- some toolchain-matrix rows align by canonical match while others are only family projections
- some legacy or projection lanes intentionally do not imply shipping support

Consolidation therefore requires explicit machine-readable linkage between:

- preset families
- toolchain families
- platform and architecture identifiers
- target-matrix expectations
- product realizations where relevant

No tool or script may infer these links differently by invocation path.

## H. Consolidation Rules

At doctrine level, consolidation means:

### H1. One Meaning Per Lane Family

Each lane family must have one stable interpretation. If multiple presets express the same lane with different visibility or convenience names, the relationship must be explicit rather than guessed.

### H2. Hidden Bases Remain Support Surfaces

Hidden scaffold presets may remain authored and canonical as support surfaces, but they do not become the default operator contract just because other presets inherit from them.

### H3. Visible Operator Lanes Must Stay Explicit

Visible development, verification, and release-check lanes remain the main human-facing invocation contract and must stay aligned with CI and editor tasks.

### H4. Release-Labeled Lanes Are Not Full Release Doctrine

Release-oriented presets such as `release-winnt-x86_64`, `release-linux-x86_64`, and `release-macos-arm64` may exist now, but their later control-plane and publication meaning remains downstream of future `Υ` prompts.

### H5. Projection Lanes Stay Projection Lanes

IDE projection presets and their manifests may remain authored and useful, but they stay projection-oriented lanes rather than universal build canon.

### H6. Legacy Meaning Must Be Explicit

Legacy or nostalgia-target lanes may remain present, but they must be marked as transitional, deprecated, frozen, best-effort, or review-gated rather than silently treated as equal to primary shipping lanes.

### H7. CI, Editor, And Script Consumers Must Align

CI profiles, editor tasks, release dry-run scripts, and projection-regeneration checks must consume the consolidated matrix without inventing new lane meaning.

### H8. Consolidation Is Not Immediate Destructive Rewrite

Consolidation eliminates silent contradiction first. It does not require immediate deletion of all overlap if overlap is still serving compatibility, legacy projection, or family scaffolding purposes.

## I. Transitional And Legacy Handling

Transitional or legacy preset/toolchain surfaces may remain when they serve one of these purposes:

- preserving a compatibility lane whose support meaning is still explicitly provisional
- preserving a projection lane used for IDE generation or nostalgia-target evidence
- preserving a scaffold or alias relationship that later prompts may simplify more safely
- preserving a best-effort alternate toolchain lane that later prompts still need to classify

Such surfaces should be classified using explicit status tags rather than deleted by reflex.

Consolidation is therefore not equivalent to deletion. It is the act of making the status of each family explicit so later prompts can decide what to retain, deprecate, or tighten without guesswork.

In current repo evidence:

- `base-msys2`, `msys2-debug`, and `msys2-release` already advertise a legacy/not-supported posture
- `win9x-x86_32-legacy`, `win16-x86_16`, `dos-x86_16`, and `legacy-win-vs2015` clearly sit in compatibility or nostalgia territory
- the `ide-*` presets are intentionally projection-oriented and generate manifests and output trees under `ide/`

Those surfaces may remain present, but they are not default operator canon.

## J. Relationship To Later Υ Work

Later `Υ` prompts consume this consolidation layer directly:

- `Υ-2` versioning constitution consumes stable lane and environment meaning
- `Υ-3` release-index and resolution alignment consumes consolidated release-facing lane interpretation
- `Υ-4` release contract profile consumes stable product/platform/toolchain realization rules
- `Υ-5` build reproducibility work consumes the classified matrix and its deterministic linkage surfaces
- `Υ-6`, `Υ-7`, and `Υ-8` consume the same stable interpretation for archive, naming, and control-plane alignment

Later release, archive, publication, and operator-transaction work may not invent their own preset matrix semantics or silently promote generated projections into law.

## K. Validation And Auditability

The consolidated layer must support auditability and testability in principle.

Later systems should be able to verify:

- preset and toolchain surface class
- canonical, derived, transitional, deprecated, or review-gated status
- configure/build/test linkage consistency
- target-matrix and toolchain-matrix linkage consistency
- CI, editor, and script alignment to the same lane meaning
- projection lanes remaining projection lanes
- release-labeled lanes setting explicit release markers when required

Current repo evidence already supports this through authored checks and consumers such as:

- `scripts/ci/check_repox_rules.py` and `INV-BUILD-PRESET-CONTRACT`
- `.vscode/tasks.json`
- `scripts/verify_projection_regen_clean.py`
- `scripts/repox/repox_release.py`
- `tools/xstack/ci/profiles/*.json`
- `data/planning/reality/toolchain_and_preset_map.json`
- `data/registries/toolchain_matrix_registry.json`

## L. Ownership And Anti-Reinvention Cautions

The following cautions remain binding:

- `field/` vs `fields/`
- `schema/` vs `schemas/`
- `packs/` vs `data/packs/`
- canonical vs projected/generated distinctions
- thin `runtime/` root not automatically canonical
- stale planning numbering or titles do not override the active checkpoint stack

Additional preset/toolchain cautions now frozen are:

- preset/toolchain consolidation must be extracted from repo reality and `Υ-0`, not invented as a greenfield cleanup fantasy
- visible invocation convenience does not create authority
- generated projection files under `ide/` or configured descriptors under build trees do not become canonical because they look machine-friendly
- CI or editor tasks may consume the matrix, but they may not redefine product, platform, target, or release meaning

## M. Anti-Patterns / Forbidden Shapes

The following shapes are forbidden:

- treating `CMakePresets.json` as the source of overall build canon instead of as a downstream invocation matrix under build graph lock
- treating toolchain file names as the real target taxonomy
- letting CI scripts silently redefine product, platform, or release meaning
- treating generated IDE projections or configured descriptors as canonical preset/toolchain law
- collapsing modern lanes, projection lanes, legacy lanes, and alternate-toolchain lanes into one flat undifferentiated matrix
- deleting transitional or deprecated surfaces without explicit classification and rationale
- using preset or toolchain convenience to flatten `kernel`, `component`, `service`, and `product` distinctions into build folklore

## N. Stability And Evolution

This artifact is `provisional` but canonical for the current `Υ-A` block.

Later prompts may refine it by:

- freezing version and release identity semantics
- tightening release-lane meaning
- defining artifact naming and release-index relationships
- introducing reproducibility and operator-transaction discipline over the already-consolidated matrix

Any update must remain explicit, non-silent, and subordinate to:

- canonical governance
- the active checkpoint stack
- build graph lock
- runtime vocabulary distinctions
- canonical versus derived surface discipline

This artifact now enables:

- `Υ-2` versioning constitution
- `Υ-3` release-index and resolution alignment
- `Υ-4` release contract profile
- `Υ-5` build reproducibility matrix work
- later `Υ` archive, naming, and operator/control-plane prompts
- future checkpoints that need to reassess `Υ` progress against the risky `Φ-B` tail
