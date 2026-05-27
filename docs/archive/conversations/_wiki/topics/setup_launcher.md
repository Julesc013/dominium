Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: topic_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`

# Topic: setup_launcher

## What This Topic Means

`setup_launcher` is an automatically classified conversation-corpus topic. It groups archived conversations by recurring words and package labels, not by authoritative repo ownership.

## Source Conversations

- [Dominium APP0 Runtime, Platform, and Renderer Architecture](../../_reader/by_chat/app_runtime_platform_renderers.md) - `app_runtime_platform_renderers`
- [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../../_reader/by_chat/app_testx_codehygiene.md) - `app_testx_codehygiene`
- [Dominium/Domino Architecture and Codex Prompt Roadmap](../../_reader/by_chat/architecture_codex_prompts.md) - `architecture_codex_prompts`
- [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../../_reader/by_chat/canonical_structure_and_framework.md) - `canonical_structure_and_framework`
- [Documentation Standards, README Strategy, and Handoff Packaging](../../_reader/by_chat/documentation_standards_readme.md) - `documentation_standards_readme`
- [Dominium Architecture I](../../_reader/by_chat/dominium_architecture_i.md) - `Dominium_Architecture_I`
- [Dominium Architecture III: Launcher, Platform, Renderer, and Handoff Architecture](../../_reader/by_chat/dominium_architecture_iii.md) - `Dominium_Architecture_III`
- [Dominium Architecture IV](../../_reader/by_chat/dominium_architecture_iv.md) - `Dominium_Architecture_IV`
- [Dominium + Domino Codex Planning and Handoff](../../_reader/by_chat/dominium_domino_codex_planning.md) - `dominium_domino_codex_planning`
- [Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion](../../_reader/by_chat/dominium_full_conversation.md) - `dominium_full_conversation`
- [Dominium Setup Architecture and Handoff](../../_reader/by_chat/dominium_setup.md) - `dominium_setup`
- [Domino Dominium Workbench](../../_reader/by_chat/domino_dominium_workbench.md) - `Domino_Dominium_Workbench`
- [Dominium Content and GUI Rebuild Planning](../../_reader/by_chat/gui_binary_content.md) - `gui_binary_content`
- [Dominium Launcher Application-Layer Handoff](../../_reader/by_chat/launcher_app_layer.md) - `launcher_app_layer`
- [Dominium Launcher and Setup Architecture](../../_reader/by_chat/launcher_setup_architecture.md) - `Launcher_Setup_Architecture`
- [Dominium Omega/Xi/Pi Architecture & Future-Proofing Planning](../../_reader/by_chat/omega_xi_pi_architecture_future.md) - `omega_xi_pi_architecture_future`
- [Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer](../../_reader/by_chat/os_interface_repo_architecture.md) - `OS_Interface_Repo_Architecture`
- [Dominium Codex Platform Renderer API Plan](../../_reader/by_chat/platform_renderer_api_plan.md) - `platform_renderer_api_plan`
- [Domino/Dominium Portability, Assurance, and Future-Proof Architecture](../../_reader/by_chat/portability_assurance_future_proof.md) - `Portability_Assurance_Future_Proof`
- [Dominium + Domino Refactor Architecture](../../_reader/by_chat/refactor_architecture.md) - `Refactor_Architecture`
- [Dominium XStack Release Identity and Versioning](../../_reader/by_chat/release_identity_and_versioning.md) - `Release_Identity_and_Versioning`
- [Dominium TestX/RepoX Governance and Handoff Chat](../../_reader/by_chat/testx_repox_governance.md) - `testx_repox_governance`
- [Dominium UI Editor and Tool Editor Planning](../../_reader/by_chat/ui_editor_tool_editor_planning.md) - `ui_editor_tool_editor_planning`
- [Dominium Architecture, Workbench, AIDE, and Product-Spine Planning](../../_reader/by_chat/workbench_aide_product_spine.md) - `Workbench_AIDE_Product_Spine`
- [Dominium World Architecture](../../_reader/by_chat/world_architecture.md) - `World_Architecture`

## Recurring Claims

- `app_runtime_platform_renderers`: The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do.
- `app_runtime_platform_renderers`: The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and introducing gameplay shortcuts. **FACT:** authoritative logic remains in engine + game.
- `app_testx_codehygiene`: A large set of prompts was then generated to lock down architecture, determinism, performance, schema governance, rendering, epistemic UI, sharding, interest sets, and fidelity projection. This became the Phase 1 hardening layer. Additional audit prompts were introduced to ensure consistency before proceeding into life, civilization, war, content, agents, tools, mods, and final long-term policy.
- `app_testx_codehygiene`: Because the chat was huge, the user asked for a maximum-fidelity context transfer packet. Then they asked for downloadable report files. Then they asked for an in-chat reader. Finally, they asked for this human-readable explanatory report. This final report is meant to let a future assistant or human understand the substance without re-reading the whole conversation.
- `architecture_codex_prompts`: The most important thing to remember is this: **this chat is the architectural and implementation-roadmap backbone for Dominium/Domino, but it is not an implementation log**. It should be preserved as a design/specification source and as a prompt library, while actual code and current facts must be verified separately.
- `architecture_codex_prompts`: FACT: The user opened by pasting an "Extended Master Starter Prompt - Dominium + Domino." That prompt established the role of the assistant as a senior engine architect and defined the main project philosophy. Domino was described as a deterministic, fixed-point, C89 engine portable across old and modern OS/architecture combinations. Dominium was described as the product suite built on top of Domino.
- `canonical_structure_and_framework`: This produced a pattern: generate a large Codex/AIDE task, the user ran it or reported a result, then the assistant evaluated what was truly fixed versus what was only validator/document churn. The user eventually demanded a one-shot "actual final cleanup" prompt because previous passes had sometimes added validators without moving directories. That prompt explicitly required real `git mv` routing, not just reports.
- `canonical_structure_and_framework`: The final provider directory doctrine became service-first: `runtime/<service>/providers/<provider>/`, not `runtime/<vendor>/<service>/`. Provider choices belong in `release/profiles/` or `content/profiles/`, not app path names. External code belongs under `external/upstream/` or `external/vendor/`, but the repo should choose one convention.
- `documentation_standards_readme`: The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.
- `documentation_standards_readme`: `FACT:` The chat established that public API contracts should live in headers.
- `Dominium_Architecture_I`: During this stage, the work was still broadly about "the project spec." The user wanted a comprehensive description of the game and its technical systems. The assistant produced large design documents, but many of those earlier contents are not visible in the retained transcript. This is important because the final report package marks those earlier outputs as referenced but not fully recovered.
- `Dominium_Architecture_I`: The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in filenames. Instead, those details should live in metadata. This became part of the future build/package design.
- `Dominium_Architecture_III`: The view system then expanded beyond the launcher. **FACT:** The user wants instant zoom to any scale, instant switching between top-down 2D and first-person 3D, and arbitrary cameras for free cam, map viewing, content creation, HUD cameras, CCTV, overlays, windows, and offscreen targets. These are client/render-side concerns, not simulation concerns.
- `Dominium_Architecture_III`: This context matters because the rest of the conversation happened inside those constraints. The launcher could not become a dumping ground for OS-specific behavior, sim mutation, renderer decisions, or nondeterministic game-state changes. It had to fit the project's deterministic layering.
- `Dominium_Architecture_IV`: The reusable engine layer was named **Domino**. This became one of the most important naming and architectural decisions in the chat. Domino is the engine/core/platform/sim/mod layer, reusable for other games and projects. Dominium is the game/product layer built on it.
- `Dominium_Architecture_IV`: Blueprints are plans or diffs: place element, remove element, modify terrain, place machine, connect network, etc. When accepted, they generate jobs. Manual player actions and queued work for humans, robots, or other agents should use the same job pipeline. This matters because it keeps replay, AI, and automation consistent.
- `dominium_domino_codex_planning`: INFERENCE:** The user accepted this direction in practice, because the next request was to generate Codex prompts to implement each step fully. The user did not explicitly say, "I formally approve the Milestone-0 plan," but they proceeded to ask for prompts based on it.
- `dominium_domino_codex_planning`: The user then asked for recommendations. The assistant recommended a clean startup policy: explicit flags first, no environment/config override in v1, terminal detection through dsys, generic AUTO behavior, product-specific headless handling for the game, build-time GUI/TUI capabilities, and structural error codes for fallback. The user accepted this enough to request a "one big Codex prompt" to implement it.
- `dominium_full_conversation`: A future assistant must understand that this chat is not simply about UI. It records the architecture for how Dominium should build itself: through contracts, commands, services, providers, documents, patches, modules, packs, apps, workspaces, diagnostics, evidence, AIDE, Codex, and eventually Workbench.
- `dominium_full_conversation`: The user then redirected the entire plan. They argued that native OS widget GUI tools already exist through Visual Studio, Xcode, etc. The project needed a cross-platform rendered tool environment that uses the same CLI, TUI, and rendered GUI systems as the client. The old UI Editor and Tool Editor were good exploratory ideas but bad final products. This produced the Dominium Workbench concept.
- `dominium_setup`: Near the end, the chat shifted into preservation mode. The user asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat reader version of that package. Those outputs preserved the decisions, tasks, constraints, artifacts, rejected options, and verification queue for future assistants or aggregation into a larger Project Spec Book.
- `dominium_setup`: These directory trees were not final, but they mattered because they exposed the user's preference for simple, shallow, logical structures and native IDE workflows that do not become the source of truth.
- `Domino_Dominium_Workbench`: The original UI Editor / Tool Editor plan is now **superseded as a final product**. It is not lost: its useful parts become Workbench capabilities, especially Interface Studio, UI/HUD Sandbox, Theme Laboratory, TUI Studio, Rendered GUI Studio, Preview Matrix, validation panels, import/export tools, and document-patch workflows.
- `Domino_Dominium_Workbench`: The central decision is that Workbench must not become semantic authority. Workbench is a surface over contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, tests, and replay/proof. It is the richest human/agent interface over the system, but it must not bypass command, capability, refusal, validation, document, patch, or proof law.
- `gui_binary_content`: That was an important change of direction. It meant the assistant's polished prompt should not be treated as final. The work needed conceptual discussion first. The assistant then analyzed CONTENT0 and identified several issues that could cause bad assumptions to become embedded if Codex acted too soon.
- `gui_binary_content`: what start scenarios must explicitly exclude,
- `launcher_app_layer`: Someone reading this report should understand one central thing: this chat is not about inventing new launcher features anymore. It is about preserving boundaries, making the launcher implementation explicit, and ensuring future work happens on top of verified code rather than vague architectural memory.
- `launcher_app_layer`: There was also an early suggestion to create a `DUI` facade, a Dominium UI abstraction, to support native widgets and fallback rendering. This idea was useful as a conceptual stepping stone but was not ultimately locked as a final requirement in the form originally suggested. Later application-layer canon emphasized **UI IR**, **command graphs**, and **binding validation** rather than a specific `DUI` facade design.
- `Launcher_Setup_Architecture`: The chat also produced multiple Codex work-order prompts and finally a downloadable report package. Those artifacts are useful, but the substance is the architecture: keep engine deterministic, keep setup/launcher/runtime boundaries explicit, make the launcher optional and modular, use a strong process/instance model, and now implement the launcher over dsys/dgfx rather than ad hoc platform UI stacks.
- `Launcher_Setup_Architecture`: FACT:** The user's initial architecture text emphasized:
- `omega_xi_pi_architecture_future`: The final strategic direction before this preservation request was to run a ?-series: snapshot intake, reality extraction, blueprint reconciliation, foundation readiness, and final prompt synthesis. This is needed because plans must now be mapped onto current repo reality rather than executed abstractly. The next chat should pick up there.
- `omega_xi_pi_architecture_future`: The user later reported Xi completion. The enduring lesson is that prompt instructions are not enough; architecture must be machine-readable and enforced.
- `OS_Interface_Repo_Architecture`: DECISION-01 - CLI mandatory, TUI expected, GUI modular.** This was part of the initial architecture baseline and was repeatedly reaffirmed. It matters because every product must remain operable in recovery/headless/automation contexts. GUI is allowed but not authoritative.
- `OS_Interface_Repo_Architecture`: DECISION-02 - Thin GUI shells over shared contracts.** The chat consistently rejected GUI families becoming separate product architectures. This affects client, launcher, setup, server admin, tools, and Workbench modules.
- `platform_renderer_api_plan`: The chat ended by generating a maximum-fidelity transfer packet, then a downloadable report package, then an in-chat reader version. The main thing to remember is this: **the active artifact is the final 9-prompt post-master Codex plan, but it is a plan, not evidence that the code exists. The repo must be inspected before execution.
- `platform_renderer_api_plan`: These ideas became the architectural heart of the final plan.
- `Portability_Assurance_Future_Proof`: The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.
- `Portability_Assurance_Future_Proof`: Status: Assistant recommendation; not separately accepted after answer.
- `Refactor_Architecture`: The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.
- `Refactor_Architecture`: FACT:** This early discussion created the future UI/packs design context.
- `Release_Identity_and_Versioning`: The user then objected to versioning policy drift in real products and expressed concern about SemVer's "1.x forever" failure mode. The first proposed answer was a four-part public version scheme, `GEN.EPOCH.FEATURE.PATCH`, meant to avoid fake major bumps. That idea was useful as an intermediate step but later became less central because XStack already has GBN for dense build history and separate build identity.
- `Release_Identity_and_Versioning`: The conversation then moved into how this might fit XStack. The model shifted from "better public version number" to "layered identity model." The assistant recommended preserving per-product versions, a global build number, build IDs, compatibility versions, and suite versions as separate layers. This became the foundation for later decisions.
- `testx_repox_governance`: FACT:** The user is building Dominium / Domino as a deterministic universe engine + game, not a conventional game project. The visible chat repeatedly framed the project as long-lived, simulation-first, deterministic, modular, and designed to survive across many operating systems, toolchains, renderers, products, and distribution models.
- `testx_repox_governance`: The user then asked whether the implementation was industry-accepted and what could be improved. The response framed the approach as closer to game engines, operating systems, and long-lived infrastructure than typical game development. The important conclusion was that the design was not exotic, but it was unusually rigorous for games.
- `ui_editor_tool_editor_planning`: The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.
- `ui_editor_tool_editor_planning`: This was one of the most important structure decisions in the chat. It prevented the initial implementation from becoming too broad while preserving the long-term goal. The UI Editor would be a bootstrap tool, not the final architecture.
- `Workbench_AIDE_Product_Spine`: The user noted that earlier prompts were hard to copy because they were not always contained in one code block, and that prompts should better handle dirty worktrees and concurrent tasks. From then on, generated prompts included detailed dirty worktree handling, allowed/forbidden paths, non-goals, validation, blocker classification, and commit/final-response formats.
- `Workbench_AIDE_Product_Spine`: The final recommended sequence was: finish replay proof and barebones client, run product spine review, then begin limited parallel dev. Larger parallel waves should wait until minimum AIDE workflow law exists.
- `World_Architecture`: The future relevance of this chat is high. It should feed directly into the future project spec book and into a corrected implementation prompt. But it should not be treated as final implementation detail everywhere. Many high-level decisions are settled, but solver formulas, exact file encoding details, build system integration, actual repository layout, and some numerical representations still require verification.
- `World_Architecture`: Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular, content-driven, and field-based. Chunks are not the world. Chunks are just how the world is cached, meshed, streamed, and saved.

## Contradictions And Verification Needs

- `CONTRA-0005` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `runtime_module_loader`.
- `CONTRA-0006` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `provider_runtime`.
- `CONTRA-0007` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0008` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- `CONTRA-0009` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0010` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0011` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- `CONTRA-0012` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0013` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0014` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- `CONTRA-0015` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- `CONTRA-0016` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `provider_runtime`.
- `CONTRA-0017` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0018` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0019` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0020` `stale_external_claim`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0033` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `provider_runtime`.
- `CONTRA-0034` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `package_runtime`.
- `CONTRA-0035` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0036` `conversation_vs_current_queue`: Archived conversation discusses work related to blocked scope `renderer_implementation`.

## Promotion Status

`not_reviewed`; see `_promotion/PROMOTION_QUEUE.md`.
