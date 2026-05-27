Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: topic_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`

# Topic: workbench

## What This Topic Means

`workbench` is an automatically classified conversation-corpus topic. It groups archived conversations by recurring words and package labels, not by authoritative repo ownership.

## Source Conversations

- [Dominium Advanced Simulation and Infrastructure Architecture](../../_reader/by_chat/advanced_simulation_infrastructure.md) - `advanced_simulation_infrastructure`
- [Dominium Architecture, UI, Providers, and Robot OS Strategy](../../_reader/by_chat/architecture_ui_providers.md) - `architecture_ui_providers`
- [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../../_reader/by_chat/canonical_structure_and_framework.md) - `canonical_structure_and_framework`
- [Dominium Development Routes and Continuity Preservation](../../_reader/by_chat/development_routes.md) - `development_routes`
- [Dominium Architecture IV](../../_reader/by_chat/dominium_architecture_iv.md) - `Dominium_Architecture_IV`
- [Dominium + Domino Codex Planning and Handoff](../../_reader/by_chat/dominium_domino_codex_planning.md) - `dominium_domino_codex_planning`
- [Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion](../../_reader/by_chat/dominium_full_conversation.md) - `dominium_full_conversation`
- [Domino Dominium Workbench](../../_reader/by_chat/domino_dominium_workbench.md) - `Domino_Dominium_Workbench`
- [Domino/Dominium Engine Baseline, Architecture, and Feasibility](../../_reader/by_chat/engine_baseline_architecture.md) - `engine_baseline_architecture`
- [Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff](../../_reader/by_chat/foundation_workbench_codex.md) - `Foundation_Workbench_Codex`
- [Domino Framework and Open-Source Provider Architecture](../../_reader/by_chat/framework_open_source_provider.md) - `Framework_Open_Source_Provider`
- [Dominium Content and GUI Rebuild Planning](../../_reader/by_chat/gui_binary_content.md) - `gui_binary_content`
- [Dominium Language, Platform, and Architecture Baseline](../../_reader/by_chat/language_platform_architecture.md) - `Language_Platform_Architecture`
- [Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer](../../_reader/by_chat/os_interface_repo_architecture.md) - `OS_Interface_Repo_Architecture`
- [Dominium Codex Platform Renderer API Plan](../../_reader/by_chat/platform_renderer_api_plan.md) - `platform_renderer_api_plan`
- [Dominium + Domino Refactor Architecture](../../_reader/by_chat/refactor_architecture.md) - `Refactor_Architecture`
- [Dominium UI Editor and Tool Editor Planning](../../_reader/by_chat/ui_editor_tool_editor_planning.md) - `ui_editor_tool_editor_planning`
- [Dominium Universe Explorer Planning and Repo Handoff](../../_reader/by_chat/universe_explorer_planning.md) - `Universe_Explorer_Planning`
- [Dominium Architecture, Workbench, AIDE, and Product-Spine Planning](../../_reader/by_chat/workbench_aide_product_spine.md) - `Workbench_AIDE_Product_Spine`
- [Dominium World Architecture](../../_reader/by_chat/world_architecture.md) - `World_Architecture`

## Recurring Claims

- `advanced_simulation_infrastructure`: The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it.
- `advanced_simulation_infrastructure`: Finally, the chat shifted into archival mode: it produced a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader version. Those later outputs preserved the discussion for future aggregation.
- `architecture_ui_providers`: The language baseline decision matters because it changes what old renderers and toolchains matter. C17/C++17 reduces the need to design around C89/C++98 constraints but does not remove the need for C-compatible ABI boundaries. The system floor decision similarly moves many older renderers and OS targets into research/back-port categories.
- `architecture_ui_providers`: The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- `canonical_structure_and_framework`: This produced a pattern: generate a large Codex/AIDE task, the user ran it or reported a result, then the assistant evaluated what was truly fixed versus what was only validator/document churn. The user eventually demanded a one-shot "actual final cleanup" prompt because previous passes had sometimes added validators without moving directories. That prompt explicitly required real `git mv` routing, not just reports.
- `canonical_structure_and_framework`: The final provider directory doctrine became service-first: `runtime/<service>/providers/<provider>/`, not `runtime/<vendor>/<service>/`. Provider choices belong in `release/profiles/` or `content/profiles/`, not app path names. External code belongs under `external/upstream/` or `external/vendor/`, but the repo should choose one convention.
- `development_routes`: Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict determinism matters, whether replay or multiplayer are goals, whether modding matters, and what the actual game loop is. Until then, the kernel-first plan should be treated as a strong provisional proposal, not a final specification.
- `development_routes`: The first answer was assertive. It stated that Dominium must follow Route C and described the route as the only viable one for Dominium. Later parts of the chat corrected the status of that claim. FACT: the assistant made that recommendation. UNCERTAIN / UNVERIFIED: the recommendation was not validated with external sources in the chat and was not explicitly accepted by the user.
- `Dominium_Architecture_IV`: The reusable engine layer was named **Domino**. This became one of the most important naming and architectural decisions in the chat. Domino is the engine/core/platform/sim/mod layer, reusable for other games and projects. Dominium is the game/product layer built on it.
- `Dominium_Architecture_IV`: Blueprints are plans or diffs: place element, remove element, modify terrain, place machine, connect network, etc. When accepted, they generate jobs. Manual player actions and queued work for humans, robots, or other agents should use the same job pipeline. This matters because it keeps replay, AI, and automation consistent.
- `dominium_domino_codex_planning`: INFERENCE:** The user accepted this direction in practice, because the next request was to generate Codex prompts to implement each step fully. The user did not explicitly say, "I formally approve the Milestone-0 plan," but they proceeded to ask for prompts based on it.
- `dominium_domino_codex_planning`: The user then asked for recommendations. The assistant recommended a clean startup policy: explicit flags first, no environment/config override in v1, terminal detection through dsys, generic AUTO behavior, product-specific headless handling for the game, build-time GUI/TUI capabilities, and structural error codes for fallback. The user accepted this enough to request a "one big Codex prompt" to implement it.
- `dominium_full_conversation`: A future assistant must understand that this chat is not simply about UI. It records the architecture for how Dominium should build itself: through contracts, commands, services, providers, documents, patches, modules, packs, apps, workspaces, diagnostics, evidence, AIDE, Codex, and eventually Workbench.
- `dominium_full_conversation`: The user then redirected the entire plan. They argued that native OS widget GUI tools already exist through Visual Studio, Xcode, etc. The project needed a cross-platform rendered tool environment that uses the same CLI, TUI, and rendered GUI systems as the client. The old UI Editor and Tool Editor were good exploratory ideas but bad final products. This produced the Dominium Workbench concept.
- `Domino_Dominium_Workbench`: The original UI Editor / Tool Editor plan is now **superseded as a final product**. It is not lost: its useful parts become Workbench capabilities, especially Interface Studio, UI/HUD Sandbox, Theme Laboratory, TUI Studio, Rendered GUI Studio, Preview Matrix, validation panels, import/export tools, and document-patch workflows.
- `Domino_Dominium_Workbench`: The central decision is that Workbench must not become semantic authority. Workbench is a surface over contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, tests, and replay/proof. It is the richest human/agent interface over the system, but it must not bypass command, capability, refusal, validation, document, patch, or proof law.
- `engine_baseline_architecture`: This corrected the plan. The final sequencing became: first **Milestone 0: Make the baseline path honest**. That means fixing server/runtime circular import, CLI forwarding, `session_create -> session_boot`, missing time-anchor policy registry, and making the strict local playtest validator pass. Only after that should the builder/destruction lab begin.
- `engine_baseline_architecture`: The final user action uploaded `Pasted text.txt`, a detailed instruction prompt requiring a full preservation report, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That request is the current task.
- `Foundation_Workbench_Codex`: After the root skeleton improved, the assistant and user recognized that the deeper problem was no longer top-level directories. The problem became semantic duplication and governance: what is public, what is private, what is stable, what is provisional, what is generated, what is a fixture, what must stay compatible, what can be replaced, and what proof is required.
- `Foundation_Workbench_Codex`: The key conclusion was that Workbench is not the general module system; it is one consumer of the module/command/service/provider/pack/artifact system. Workbench must not call private tools directly. It must route through registered commands and typed results, diagnostics, refusals, views, and evidence.
- `Framework_Open_Source_Provider`: Finally, the user uploaded a detailed preservation prompt and requested a maximum-fidelity report, registers, spec sheet, aggregator packet, audit, and downloadable files. This package is the response to that request.
- `Framework_Open_Source_Provider`: This became the central architectural theme. The conversation refined earlier vendor-shaped paths into service-first paths. The stable pattern is:
- `gui_binary_content`: That was an important change of direction. It meant the assistant's polished prompt should not be treated as final. The work needed conceptual discussion first. The assistant then analyzed CONTENT0 and identified several issues that could cause bad assumptions to become embedded if Codex acted too soon.
- `gui_binary_content`: what start scenarios must explicitly exclude,
- `Language_Platform_Architecture`: The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.
- `Language_Platform_Architecture`: The user then consolidated a broad future plan around Domino, Dominium, Workbench, AIDE, contracts, tests, replay, and evidence. The answer agreed that the plan was strong, but identified missing central pieces: composition resolver, lockfiles, compatibility corpus, trust/permissions, virtual filesystem roots, performance budgets, and stable public-surface promotion rules.
- `OS_Interface_Repo_Architecture`: DECISION-01 - CLI mandatory, TUI expected, GUI modular.** This was part of the initial architecture baseline and was repeatedly reaffirmed. It matters because every product must remain operable in recovery/headless/automation contexts. GUI is allowed but not authoritative.
- `OS_Interface_Repo_Architecture`: DECISION-02 - Thin GUI shells over shared contracts.** The chat consistently rejected GUI families becoming separate product architectures. This affects client, launcher, setup, server admin, tools, and Workbench modules.
- `platform_renderer_api_plan`: The chat ended by generating a maximum-fidelity transfer packet, then a downloadable report package, then an in-chat reader version. The main thing to remember is this: **the active artifact is the final 9-prompt post-master Codex plan, but it is a plan, not evidence that the code exists. The repo must be inspected before execution.
- `platform_renderer_api_plan`: These ideas became the architectural heart of the final plan.
- `Refactor_Architecture`: The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.
- `Refactor_Architecture`: FACT:** This early discussion created the future UI/packs design context.
- `ui_editor_tool_editor_planning`: The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.
- `ui_editor_tool_editor_planning`: This was one of the most important structure decisions in the chat. It prevented the initial implementation from becoming too broad while preserving the long-term goal. The UI Editor would be a bootstrap tool, not the final architecture.
- `Universe_Explorer_Planning`: The pasted discussion on trees, screws, pottery, axes, chairs, tables, and machines established that the player should manipulate material, geometry, constraints, processes, tools, stations, and affordances. The conclusion is that "item classes" must not be the truth substrate. Recipes and blueprints can exist, but as higher-order formalizations.
- `Universe_Explorer_Planning`: A major theme was that useful local inventions must become portable, standardized, industrialized, and institutionally adopted. The repo now has a Formalization Chain spec and Player Desire Acceptance Map that strongly preserve this. The future work is making this playable: drafting, measuring, testing, blueprinting, certifying, teaching, manufacturing, maintaining, and revising designs.
- `Workbench_AIDE_Product_Spine`: The user noted that earlier prompts were hard to copy because they were not always contained in one code block, and that prompts should better handle dirty worktrees and concurrent tasks. From then on, generated prompts included detailed dirty worktree handling, allowed/forbidden paths, non-goals, validation, blocker classification, and commit/final-response formats.
- `Workbench_AIDE_Product_Spine`: The final recommended sequence was: finish replay proof and barebones client, run product spine review, then begin limited parallel dev. Larger parallel waves should wait until minimum AIDE workflow law exists.
- `World_Architecture`: The future relevance of this chat is high. It should feed directly into the future project spec book and into a corrected implementation prompt. But it should not be treated as final implementation detail everywhere. Many high-level decisions are settled, but solver formulas, exact file encoding details, build system integration, actual repository layout, and some numerical representations still require verification.
- `World_Architecture`: Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular, content-driven, and field-based. Chunks are not the world. Chunks are just how the world is cached, meshed, streamed, and saved.

## Contradictions And Verification Needs

- `CONTRA-0001` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0002` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0003` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0004` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0021` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `broad_workbench_ui`.
- `CONTRA-0022` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `provider_runtime`.
- `CONTRA-0023` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0024` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- `CONTRA-0025` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `native_gui`.
- `CONTRA-0026` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0027` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0028` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- `CONTRA-0029` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0033` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `provider_runtime`.
- `CONTRA-0034` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `package_runtime`.
- `CONTRA-0035` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0036` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- `CONTRA-0037` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `native_gui`.
- `CONTRA-0038` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0039` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C++98`.

## Promotion Status

`not_reviewed`; see `_promotion/PROMOTION_QUEUE.md`.
