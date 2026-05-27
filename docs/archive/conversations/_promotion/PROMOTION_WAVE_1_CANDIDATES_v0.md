Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: promotion_wave_1_candidates_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_synthesis
Promotion Status: not_promoted
Source Class: conversation_corpus_synthesis


# Promotion Wave 1 Candidates v0

Wave 1 candidates are docs-only review candidates that appear least blocked by current queue. They still require separate microtasks.

## `PROMOTE-0003` - `architecture_doc_candidate`

- Source conversation: `advanced_simulation_infrastructure`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0003`
- Claim: [INFERENCE] The conclusion was not a finalized implementation but a working architecture: each simulation domain should be deterministic, fixed-point, content-driven, versioned, replayable, and integrated through clear read/write boundaries.

## `PROMOTE-0004` - `architecture_doc_candidate`

- Source conversation: `app_runtime_platform_renderers`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0004`
- Claim: The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do.

## `PROMOTE-0032` - `architecture_doc_candidate`

- Source conversation: `Dominium_Architecture_I`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0032`
- Claim: The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in filenames. Instead, those details should live in metadata. This became part of the future build/package design.

## `PROMOTE-0035` - `architecture_doc_candidate`

- Source conversation: `Dominium_Architecture_II`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0035`
- Claim: The entire conversation is anchored by the requirement that Dominium must run deterministically. This means the same initial state and same inputs must produce the same state across machines, compilers, operating systems, and eventually retro and modern platforms.

## `PROMOTE-0038` - `architecture_doc_candidate`

- Source conversation: `Dominium_Architecture_III`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0038`
- Claim: This context matters because the rest of the conversation happened inside those constraints. The launcher could not become a dumping ground for OS-specific behavior, sim mutation, renderer decisions, or nondeterministic game-state changes. It had to fit the project's deterministic layering.

## `PROMOTE-0050` - `architecture_doc_candidate`

- Source conversation: `dominium_full_conversation`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0050`
- Claim: The user then redirected the entire plan. They argued that native OS widget GUI tools already exist through Visual Studio, Xcode, etc. The project needed a cross-platform rendered tool environment that uses the same CLI, TUI, and rendered GUI systems as the client. The old UI Editor and Tool Editor were good exploratory ideas but bad final products. This produced the Dominium Workbench concept.

## `PROMOTE-0054` - `planning_doc_candidate`

- Source conversation: `dominium_setup`
- Proposed target: `docs/planning/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0054`
- Claim: The user later asked where to create Visual Studio and Xcode apps after opening the repo as a folder. The assistant advised that Visual Studio and Xcode projects should be generated through CMake, not hand-authored or treated as authoritative source files. This decision became consistent with later Codex prompts.

## `PROMOTE-0063` - `architecture_doc_candidate`

- Source conversation: `engine_baseline_architecture`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0063`
- Claim: The central architecture distinction was that Domino should be a reusable deterministic simulation substrate, while Dominium should be one game/product layer built on it. This came up immediately when the user asked for a total description of the project. It mattered because the user wants the code to be reusable for future games and possibly other engine projects.

## `PROMOTE-0073` - `architecture_doc_candidate`

- Source conversation: `Language_Platform_Architecture`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0073`
- Claim: The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.

## `PROMOTE-0084` - `architecture_doc_candidate`

- Source conversation: `Modularity_AIDE_Refactorability`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0084`
- Claim: The discussion proposed target-based CMake and module boundaries rather than path mythology. Public headers, private headers, allowed dependencies, and forbidden dependencies should be explicit. Apps must remain thin. Engine must not depend on game/apps/runtime UI. Runtime adapts host/platform/rendering without owning simulation truth.

## `PROMOTE-0088` - `architecture_doc_candidate`

- Source conversation: `OS_Interface_Repo_Architecture`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0088`
- Claim: DECISION-01 - CLI mandatory, TUI expected, GUI modular.** This was part of the initial architecture baseline and was repeatedly reaffirmed. It matters because every product must remain operable in recovery/headless/automation contexts. GUI is allowed but not authoritative.

## `PROMOTE-0100` - `docs_clarification_candidate`

- Source conversation: `readme_ports_determinism`
- Proposed target: `README.md or docs/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0100`
- Claim: The user pasted the final README after those cleanup changes. At that point, the README had the current active form: deterministic constraints clarified, ports unified under one source hierarchy, `/ports` metadata-only if retained, Section 9 normative, lockstep canonical, content-lock mismatch fatal, and disk format versions immutable.

## `PROMOTE-0102` - `architecture_doc_candidate`

- Source conversation: `readme_ports_determinism`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0102`
- Claim: The central artifact was the root `README.md`. The README describes **Domino** as the deterministic engine core and **Dominium** as the official game/tooling/runtime layer. It is written as a high-level architecture document, not a low-level implementation spec.

## `PROMOTE-0105` - `architecture_doc_candidate`

- Source conversation: `Refactor_Architecture`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0105`
- Claim: FACT:** All products should use shared `dsys` and `dgfx`. No product-specific platform or renderer code path.

## `PROMOTE-0112` - `architecture_doc_candidate`

- Source conversation: `testx_repox_governance`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0112`
- Claim: FACT:** The user is building Dominium / Domino as a deterministic universe engine + game, not a conventional game project. The visible chat repeatedly framed the project as long-lived, simulation-first, deterministic, modular, and designed to survive across many operating systems, toolchains, renderers, products, and distribution models.

## `PROMOTE-0114` - `architecture_doc_candidate`

- Source conversation: `testx_repox_governance`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0114`
- Claim: The user had another chat working on content and systems, and asked for a prompt to inform that chat of everything decided so far. A similar prompt was generated for the applications/platforms/renderers chat. These prompts established authoritative boundaries:

## `PROMOTE-0115` - `architecture_doc_candidate`

- Source conversation: `Timekeeping_and_2038_Resilience`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0115`
- Claim: A future assistant should understand that this chat contributes a time architecture doctrine for Dominium: **ACT is authority; DSYS time is runtime-only; observer clocks are derived; civil/astronomical time is projection-only; wall-clock time must never drive authoritative ordering.

## `PROMOTE-0131` - `architecture_doc_candidate`

- Source conversation: `World_Architecture`
- Proposed target: `docs/architecture/** after target selection`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended microtask: `DOC-PROMOTION-PROMOTE-0131`
- Claim: Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular, content-driven, and field-based. Chunks are not the world. Chunks are just how the world is cached, meshed, streamed, and saved.
