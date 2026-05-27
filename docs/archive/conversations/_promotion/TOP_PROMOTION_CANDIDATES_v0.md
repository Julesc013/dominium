Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: top_promotion_candidates_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_synthesis
Promotion Status: not_promoted
Source Class: conversation_corpus_synthesis


# Top Promotion Candidates v0

These are the cleanest automatically triaged candidates. They are still not promoted.

## `PROMOTE-0003` - `advanced_simulation_infrastructure`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__human_readable_chat_report.txt`
- Claim: [INFERENCE] The conclusion was not a finalized implementation but a working architecture: each simulation domain should be deterministic, fixed-point, content-driven, versioned, replayable, and integrated through clear read/write boundaries.

## `PROMOTE-0027` - `development_routes`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/development_routes/dominium_development_routes__human_readable_chat_report.txt`
- Claim: The initial technical answer proposed a layered stack. It started with mathematical and temporal primitives, then moved into the deterministic simulation kernel, then world state, systems, persistence and replay, tooling, presentation, content, and finally distribution, modding, and multiplayer.

## `PROMOTE-0035` - `Dominium_Architecture_II`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`
- Claim: The entire conversation is anchored by the requirement that Dominium must run deterministically. This means the same initial state and same inputs must produce the same state across machines, compilers, operating systems, and eventually retro and modern platforms.

## `PROMOTE-0038` - `Dominium_Architecture_III`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: This context matters because the rest of the conversation happened inside those constraints. The launcher could not become a dumping ground for OS-specific behavior, sim mutation, renderer decisions, or nondeterministic game-state changes. It had to fit the project's deterministic layering.

## `PROMOTE-0059` - `domino_engine_refactor_prompts`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/domino_engine_refactor_prompts/dominium_domino_engine_refactor_prompts__human_readable_chat_report.txt`
- Claim: This became one of the central architectural ideas of the chat. It makes behavior extensible without giving minds direct write access to the world. A mod can add new sensors, observations, intents, capabilities, or actions, but state mutation still passes through a deterministic pipeline.

## `PROMOTE-0066` - `Foundation_Workbench_Codex`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: The topic came up because the project needed a model that could support world simulation, modding, tooling, Workbench, release, portability, and future games without repeating endless refactors. The conclusion was that stable contracts and semantic IDs must be separated from replaceable private implementation.

## `PROMOTE-0088` - `OS_Interface_Repo_Architecture`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- Claim: DECISION-01 - CLI mandatory, TUI expected, GUI modular.** This was part of the initial architecture baseline and was repeatedly reaffirmed. It matters because every product must remain operable in recovery/headless/automation contexts. GUI is allowed but not authoritative.

## `PROMOTE-0089` - `OS_Interface_Repo_Architecture`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- Claim: DECISION-02 - Thin GUI shells over shared contracts.** The chat consistently rejected GUI families becoming separate product architectures. This affects client, launcher, setup, server admin, tools, and Workbench modules.

## `PROMOTE-0090` - `OS_Interface_Repo_Architecture`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- Claim: DECISION-03 - Repo ownership layout.** The user pushed for repository convergence; the discussion established that folders should map to ownership and contract boundaries. This decision is final enough to guide work, but details remain subject to machine-readable layout contracts.

## `PROMOTE-0102` - `readme_ports_determinism`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/readme_ports_determinism/dominium_readme_ports_determinism__human_readable_chat_report.txt`
- Claim: The central artifact was the root `README.md`. The README describes **Domino** as the deterministic engine core and **Dominium** as the official game/tooling/runtime layer. It is written as a high-level architecture document, not a low-level implementation spec.

## `PROMOTE-0115` - `Timekeeping_and_2038_Resilience`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md`
- Claim: A future assistant should understand that this chat contributes a time architecture doctrine for Dominium: **ACT is authority; DSYS time is runtime-only; observer clocks are derived; civil/astronomical time is projection-only; wall-clock time must never drive authoritative ordering.

## `PROMOTE-0004` - `app_runtime_platform_renderers`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__human_readable_chat_report.txt`
- Claim: The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do.

## `PROMOTE-0007` - `app_testx_codehygiene`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`
- Claim: A large set of prompts was then generated to lock down architecture, determinism, performance, schema governance, rendering, epistemic UI, sharding, interest sets, and fidelity projection. This became the Phase 1 hardening layer. Additional audit prompts were introduced to ensure consistency before proceeding into life, civilization, war, content, agents, tools, mods, and final long-term policy.

## `PROMOTE-0009` - `app_testx_codehygiene`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`
- Claim: The central project is a deterministic universe engine/game. The user's ambition is not just a normal game but a world runtime that can represent everything from a single-room scenario to an AI-only universe to an MMO. The project is meant to support real-world defaults, arbitrary modding, procedural and defined content, strong epistemics, and long-term replayability.

## `PROMOTE-0018` - `Build_and_Future_Proofing`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- Claim: The final explicit goal was preservation: create a maximum-fidelity package for this chat so the user can understand it later, ask questions in this chat, merge it with other old-chat reports, and eventually build a master project spec book.

## `PROMOTE-0021` - `canonical_structure_and_framework`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- Claim: Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compatibility corpus plus tests, not intention.

## `PROMOTE-0029` - `documentation_standards_readme`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__human_readable_chat_report.txt`
- Claim: `FACT:` The chat established that public API contracts should live in headers.

## `PROMOTE-0044` - `Dominium_Complete_Conversation`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md`
- Claim: The glossary bound terms such as Authority, Law, Process, Lens, SessionSpec, UniverseIdentity, Macro Capsule, SRZ, RepoX, TestX, AuditX, CompatX, SecureX, and related terms. It matters because future assistants must not use sloppy synonyms like "mode" where the canon requires ExperienceProfile or LawProfile. This topic directly supports modularity because stable vocabulary is part of stable architecture.

## `PROMOTE-0053` - `dominium_setup`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/dominium_setup/dominium_setup_handoff__human_readable_chat_report.txt`
- Claim: These directory trees were not final, but they mattered because they exposed the user's preference for simple, shallow, logical structures and native IDE workflows that do not become the source of truth.

## `PROMOTE-0054` - `dominium_setup`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/dominium_setup/dominium_setup_handoff__human_readable_chat_report.txt`
- Claim: The user later asked where to create Visual Studio and Xcode apps after opening the repo as a folder. The assistant advised that Visual Studio and Xcode projects should be generated through CMake, not hand-authored or treated as authoritative source files. This decision became consistent with later Codex prompts.

## `PROMOTE-0063` - `engine_baseline_architecture`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/engine_baseline_architecture/domino_dominium_engine_baseline_architecture__01_human_readable_report.md`
- Claim: The central architecture distinction was that Domino should be a reusable deterministic simulation substrate, while Dominium should be one game/product layer built on it. This came up immediately when the user asked for a total description of the project. It mattered because the user wants the code to be reusable for future games and possibly other engine projects.

## `PROMOTE-0073` - `Language_Platform_Architecture`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.

## `PROMOTE-0074` - `Language_Platform_Architecture`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: The user then consolidated a broad future plan around Domino, Dominium, Workbench, AIDE, contracts, tests, replay, and evidence. The answer agreed that the plan was strong, but identified missing central pieces: composition resolver, lockfiles, compatibility corpus, trust/permissions, virtual filesystem roots, performance budgets, and stable public-surface promotion rules.

## `PROMOTE-0078` - `launcher_app_layer`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/launcher_app_layer/dominium_launcher_app_layer_handoff__human_readable_chat_report.txt`
- Claim: This phase mattered because it framed the launcher not as a menu program but as a **control plane** for installed products, packs, profiles, compatibility, and launch contracts. However, later canon tightened the permitted communication routes: cross-product communication must go through `schema/` and `libs/contracts`, not arbitrary plugin conventions.

## `PROMOTE-0081` - `Launcher_Setup_Architecture`

- Classification: `consistent_with_repo_but_not_formalized`
- Recommended disposition: `candidate_for_reconciliation`
- Reason: The claim appears compatible with current repo doctrine but has not been checked against target docs.
- Source file: `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__human_readable_chat_report.txt`
- Claim: The assistant responded by stress-testing this philosophy. It pointed out determinism risks around Lua, plugins, time sources, and ABI details, and suggested more explicit contracts for file headers, TLV sections, runtime CLI capabilities, plugin exported symbols, and setup/launcher boundaries. These were assistant proposals, not all user-stated decisions, but the user continued building on that direction.
