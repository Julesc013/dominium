Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: decisions_index_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`

# Decisions

Decision-like entries are extracted from archived text and are not promoted.

## [Dominium Advanced Simulation and Infrastructure Architecture](../../_reader/by_chat/advanced_simulation_infrastructure.md)

- The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it.
- Finally, the chat shifted into archival mode: it produced a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader version. Those later outputs preserved the discussion for future aggregation.
- [INFERENCE] The conclusion was not a finalized implementation but a working architecture: each simulation domain should be deterministic, fixed-point, content-driven, versioned, replayable, and integrated through clear read/write boundaries.
- [INFERENCE] This was one of the strongest architecture decisions because later topics repeatedly built on it.
- This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system.
- The key principle was that not every system should depend on decor directly. Decorative signs and decals are cheap visual objects. If they affect simulation or gameplay, they must be promoted to devices with proper STRUCT/TRANS state and ports.
- The final phase was preservation. The user asked for a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat report reader. These artifacts were about preserving the chat for future use and aggregation, not about new architecture decisions.
- The chat started as a simulation architecture task. It then became a gameplay layering task. It then became an infrastructure representation task. It then became a construction UX and arbitrary placement task. Finally, it became an implementation/handoff/reporting task.

## [Dominium APP0 Runtime, Platform, and Renderer Architecture](../../_reader/by_chat/app_runtime_platform_renderers.md)

- The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do.
- The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and introducing gameplay shortcuts. **FACT:** authoritative logic remains in engine + game.
- Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.
- The server was defined as the authoritative runtime host. It handles simulation, sharding, scheduling, law enforcement, persistence, integrity, and anti-cheat. It must be headless-capable and support AI-only autorun and MMO scale.
- The key conclusion is that the server should not depend on graphics or windowing. This matters because dedicated servers, cloud servers, and AI-only autorun must run without a GPU or display.
- The key conclusion is that the launcher must not install content or alter simulation state. That belongs to setup. This separation matters because launchers often become bloated, state-mutating, or inconsistent with installer/versioning logic.
- Tools were discussed as world inspectors, economy inspectors, replay viewers, validators, optional editors, and profilers. The important point is that tools must use the same authority rules, never bypass law, and be auditable.
- This is a distinctive part of Dominium's philosophy. Many projects treat tools as privileged by default. This chat preserved the opposite idea: tools may need elevated abilities, but those abilities must be explicit, authorized, and logged.

## [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../../_reader/by_chat/app_testx_codehygiene.md)

- A large set of prompts was then generated to lock down architecture, determinism, performance, schema governance, rendering, epistemic UI, sharding, interest sets, and fidelity projection. This became the Phase 1 hardening layer. Additional audit prompts were introduced to ensure consistency before proceeding into life, civilization, war, content, agents, tools, mods, and final long-term policy.
- Because the chat was huge, the user asked for a maximum-fidelity context transfer packet. Then they asked for downloadable report files. Then they asked for an in-chat reader. Finally, they asked for this human-readable explanatory report. This final report is meant to let a future assistant or human understand the substance without re-reading the whole conversation.
- The central project is a deterministic universe engine/game. The user's ambition is not just a normal game but a world runtime that can represent everything from a single-room scenario to an AI-only universe to an MMO. The project is meant to support real-world defaults, arbitrary modding, procedural and defined content, strong epistemics, and long-term replayability.
- The user provided a canonical repository structure and non-negotiable engine/game dependency direction. The engine is reusable and independent. The game depends on engine public APIs only. Engine internals must not leak into game/tools. Rendering backends belong to the engine, not the client. Launcher/setup logic must not enter engine/game. Client/server are executables that bind engine and game.
- This topic is central to long-term scalability. It allows future CPUs, GPUs, NPUs, heterogeneous cores, cache structures, and distributed servers to be supported by adding backend policies rather than rewriting gameplay.
- Rendering decisions were framed around explicit API first: Vulkan/DX12/Metal inform core contracts; legacy renderers are sinks or downgraded consumers. Rendering never affects authoritative simulation.
- The user also wanted AI-only civilizations that could exist outside bounds of play but become visitable and indistinguishable from real civilizations. The answer was existence states and refinement contracts. A macro civilization can be alive without micro-simulating every citizen, but if it is reachable and visitable, it must refine deterministically into micro detail consistent with its macro history.
- Large prompt families were generated for life/death/continuity, civilization/economy/governance, war/conflict, canonical content, agents, tools, mods, and final long-term maintenance. These are extensive background artifacts. Later, the chat shifted away from implementing those systems here because another bootstrap declared the core design complete and locked.

## [Dominium/Domino Architecture and Codex Prompt Roadmap](../../_reader/by_chat/architecture_codex_prompts.md)

- The most important thing to remember is this: **this chat is the architectural and implementation-roadmap backbone for Dominium/Domino, but it is not an implementation log**. It should be preserved as a design/specification source and as a prompt library, while actual code and current facts must be verified separately.
- FACT: The user opened by pasting an "Extended Master Starter Prompt - Dominium + Domino." That prompt established the role of the assistant as a senior engine architect and defined the main project philosophy. Domino was described as a deterministic, fixed-point, C89 engine portable across old and modern OS/architecture combinations. Dominium was described as the product suite built on top of Domino.
- FACT: The user asked, succinctly, how a player would build a complete machine workshop. The assistant described a progression: extract raw materials, process them into industrial materials, produce mechanical components, produce electrical components, establish power distribution, establish logistics, assemble machine frames and machines, add measurement/control tooling, then scale horizontally and vertically.
- FACT: The user then said they wanted inserters and belts, but "much more realistic" and with "WAY less processing power." They wanted conveyors/inserters to make sense in real-world use cases, and suggested inserters might be more generic robot arms. They also wanted belts constructed as splines like roads and rails.
- FACT: The user explicitly wanted packaging into crates, bags, pallets, containers, jars, cans, boxes, etc. The stated purpose was to reduce the number of physical items simulated while preserving realistic packing/unpacking mechanics and obeying mass, volume, density, and other physical constraints.
- FACT: The user then asked how hydrology, atmology, lithology, light, rain, wind, temperature, pressure, pollution, magnetic fields, radiation, gases, and similar phenomena should work with buildings and enclosed spaces. They also asked how to support blueprints/templates and how to build realistically on sloped terrain without ugly foundation blocks or forced leveling.
- FACT: The user asked whether the whole system could be made more extensible and modular. The assistant proposed applying the same pattern everywhere: core + registry + models + data. This produced the repeated architecture model used later in prompts: each subsystem has a core API, model family/vtables, data prototypes, runtime instances, registries, TLV schemas, and save/load hooks.
- FACT: The user asked to summarize the entire system and then asked for the hierarchy of data definitions/types and how to implement actual items/functions/features. The assistant produced major architectural summaries: IDs, protos, models, instances, systems; resource/env/build/trans/items/struct/vehicle/blueprints/jobs/worldgen/save.

## [Dominium Architecture, UI, Providers, and Robot OS Strategy](../../_reader/by_chat/architecture_ui_providers.md)

- The language baseline decision matters because it changes what old renderers and toolchains matter. C17/C++17 reduces the need to design around C89/C++98 constraints but does not remove the need for C-compatible ABI boundaries. The system floor decision similarly moves many older renderers and OS targets into research/back-port categories.
- The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.
- The final game direction is robotic seed civilisation, not labour management.
- 2. "Summarize the final renderer plan after the C17/C++17 transition."
- 4. "Which decisions in this chat were explicit user decisions versus assistant synthesis?"
- 5. "Which renderer/platform decisions are final, and which are still provisional?"

## [Dominium Build and Future-Proofing Architecture](../../_reader/by_chat/build_and_future_proofing.md)

- Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- The final uploaded prompt requested a complete preservation package for this chat: a human-readable explanation, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, and files/ZIP package. This response completes that export task and creates downloadable files for later reading and aggregation.
- The final explicit goal was preservation: create a maximum-fidelity package for this chat so the user can understand it later, ask questions in this chat, merge it with other old-chat reports, and eventually build a master project spec book.
- The most important caution is that only DECISION-01 is clearly a user-stated constraint in this visible chat. The other items are strong recommendations produced in response to the user's requests for best practice; they should not be merged into canon unless the user later accepts them.
- Manual drag-and-drop repo moves were rejected in earlier context and preserved here as a general risk; moves must go through migration maps, validators, shims, and proof.
- 10. **Feed this report into the master spec book aggregator.** Preserve uncertainty labels and avoid merging suggestions as decisions.
- Determinism, fixed-point behavior, and no hidden behavior are central constraints.
- Multi-floor builds must be separate artifacts.

## [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../../_reader/by_chat/canonical_structure_and_framework.md)

- This produced a pattern: generate a large Codex/AIDE task, the user ran it or reported a result, then the assistant evaluated what was truly fixed versus what was only validator/document churn. The user eventually demanded a one-shot "actual final cleanup" prompt because previous passes had sometimes added validators without moving directories. That prompt explicitly required real `git mv` routing, not just reports.
- The final provider directory doctrine became service-first: `runtime/<service>/providers/<provider>/`, not `runtime/<vendor>/<service>/`. Provider choices belong in `release/profiles/` or `content/profiles/`, not app path names. External code belongs under `external/upstream/` or `external/vendor/`, but the repo should choose one convention.
- Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compatibility corpus plus tests, not intention.
- INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly different engine implementations.
- The closed root model was the most emotionally and technically important decision. The user repeatedly objected to root proliferation; the final root set became the anchor for all later advice. This decision affects every future proposal: if a concept can fit under an existing root, it should not become a new top-level root.
- The no-`src` rule was also critical. The user considered repeated `src/` and `source/` folders as a central symptom of bad architecture. The final doctrine is that ownership directories are already source roots; implementation should live under meaningful module/subsystem folders, not generic `src` wrappers.
- The framework-boundary decision rejected a top-level `framework/` root. The accepted model is that Domino Framework exists as public surfaces, ABI headers, contracts, and provider/service law. This prevents root sprawl while still supporting SDK/export concepts later.
- The provider model decision was a major response to raylib/SDL/Lua discussions. Third-party libraries should be providers behind first-party service contracts. They can accelerate visible progress but must not own saved data, game law, public ABI, or content schemas.

## [Dominium Chronology & Celestial Systems](../../_reader/by_chat/chronology_celestial_systems.md)

- This reinforced the core celestial-content rule: locations should exist explicitly when they change player decisions.
- This became the spatial foundation for later time/calendar decisions because every major body or region could potentially have its own local time, calendar, or operational standard.
- The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.
- This material is useful but less final than the Earth calendar. The user asked to apply the same approach broadly, but did not individually confirm every name or number. The final package correctly marks these as needing review.
- The final state is that this chat became both a design discussion and a packaged source document for future aggregation.
- The conclusion was not "simulate everything." The conclusion was to classify content by relevance. Explicit objects are justified when they create gameplay, physics, navigation, history, strategy, or meaningful decisions. Otherwise, they should be procedural or statistical.
- What remains uncertain is the exact verified object list. The assistant generated a real Milky Way system list, but that list must be checked before becoming data.
- The conclusion was that every explicit celestial feature should change player decisions in at least one way. If it does not, it probably should not be explicit.

## [Dominium Development Routes and Continuity Preservation](../../_reader/by_chat/development_routes.md)

- Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict determinism matters, whether replay or multiplayer are goals, whether modding matters, and what the actual game loop is. Until then, the kernel-first plan should be treated as a strong provisional proposal, not a final specification.
- The first answer was assertive. It stated that Dominium must follow Route C and described the route as the only viable one for Dominium. Later parts of the chat corrected the status of that claim. FACT: the assistant made that recommendation. UNCERTAIN / UNVERIFIED: the recommendation was not validated with external sources in the chat and was not explicitly accepted by the user.
- The initial technical answer proposed a layered stack. It started with mathematical and temporal primitives, then moved into the deterministic simulation kernel, then world state, systems, persistence and replay, tooling, presentation, content, and finally distribution, modding, and multiplayer.
- The user then asked to turn the Context Transfer Packet and visible chat context into a final downloadable, shareable, reusable report package. This was a packaging and normalization task. The user specified exact output files: a full chat report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit file, manifest, and ZIP package.
- After the downloadable package was generated, the user asked not to create another handoff package but to render the package contents into a readable, navigable in-chat report. This led to an "IN-CHAT REPORT READER" response. That response explained the package contents, the workstreams, decisions, tasks, constraints, artifacts, risks, verification queue, and next questions.
- The final state of the conversation is therefore: the chat has produced an architectural proposal for Dominium, converted that proposal into preservation artifacts, rendered those artifacts back into an in-chat reader format, and now requires a plain-English briefing that explains the substance and significance of the conversation.
- FACT: these three routes were discussed.
- FACT: Route C was recommended by the assistant.

## [Documentation Standards, README Strategy, and Handoff Packaging](../../_reader/by_chat/documentation_standards_readme.md)

- The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.
- `FACT:` The chat established that public API contracts should live in headers.
- `FACT:` Source files should document implementation rationale, non-obvious invariants, and hazards.
- `FACT:` External docs should cover architecture, dependency rules, extension recipes, and subsystem-level explanations.
- `FACT:` The examples were generated in the chat.
- `FACT:` They were not claimed to exist in the repository.
- This was a major decision: README should not be the full spec. It should orient readers and point them to the deeper docs.
- The final phase of the chat moved away from project documentation and into preserving the chat itself. The user requested a maximum-fidelity Context Transfer Packet, then requested that it be turned into a final downloadable/shareable report package. That package was created and included a full report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit file, manifest, and ZIP archive.

## [Dominium Architecture I](../../_reader/by_chat/dominium_architecture_i.md)

- During this stage, the work was still broadly about "the project spec." The user wanted a comprehensive description of the game and its technical systems. The assistant produced large design documents, but many of those earlier contents are not visible in the retained transcript. This is important because the final report package marks those earlier outputs as referenced but not fully recovered.
- The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in filenames. Instead, those details should live in metadata. This became part of the future build/package design.
- The key change came when the user decided that Codex could not read the entire conversation at once. **FACT:** The user said they would copy and paste the transcript with timestamps and would not edit it manually, but because Codex could not read the whole context at once, they would not bother asking Codex to compile a full book directly from the whole chat.
- The user provided a large `devspec/` file tree. It included top-level docs, engine, platform, render, audio, systems, game, UI, launcher, mods, tools, data, tests, and scripts. Then the user changed one important thing: **FACT:** they decided to skip the top-level `.txt` files because the original Markdown docs already existed in `/docs/...`.
- The game layer began with `g_core.h`, `g_core.cpp`, and `g_world.h`. The user then shifted to handoff/report work before `g_world.cpp` was produced. **FACT:** The next strict-order file is therefore `game/g_world.cpp.txt`.
- The final generated package contains seven report files and a ZIP archive. The latest user request asks for a human-readable explanation rather than another machine-readable packet. This current report is therefore the narrative version: it explains what happened, what mattered, and what should be remembered.
- FACT:** The whole chat revolves around the Dominium Game project. Dominium is described through its architecture: a deterministic, cross-platform simulation game with industrial, economic, logistics, climate, terrain, AI, research, and modding systems. The user was not merely asking for isolated code snippets. They were building a full software architecture.
- The most important conclusion is that determinism is central. Systems are repeatedly specified to avoid hidden randomness, OS timers, platform dependence, uncontrolled floating point, and runtime allocation during simulation ticks. The visible rationale is that the project needs replay, save/load, and likely lockstep multiplayer compatibility. This requirement affects nearly every generated spec.

## [Dominium Architecture II](../../_reader/by_chat/dominium_architecture_ii.md)

- The last part of the chat was handoff extraction. The user asked for discovery inventory, structured registers, a context transfer packet, and then a downloadable package. The generated package captured the chat's workstreams, decisions, tasks, constraints, open questions, artifacts, risks, and verification items. This current report is a plain-language explanation of that substance.
- The entire conversation is anchored by the requirement that Dominium must run deterministically. This means the same initial state and same inputs must produce the same state across machines, compilers, operating systems, and eventually retro and modern platforms.
- The chat discussed fixed tick phases, virtual lanes, merge order, command buffers, event queues, and deterministic serialization. The simulation must not depend on render FPS, wall-clock time, OS scheduler behaviour, GPU state, or floating-point quirks. This explains many later decisions: C89 core, integer/fixed-point math, no sim floats, no platform headers in simulation, and renderer as pure observer.
- What remains uncertain is the exact code-level API and component layouts. The chat produced specs and prompts, not final source code.
- The decision to use on-rails orbital mechanics mattered because it avoids the complexity of full n-body simulation. Instead of integrating every orbital body continuously, the game can use deterministic graph-like orbital states and transitions. This fits the rest of the engine: graphs, fields, frames, and state machines.
- Railways began as a major topic but later became part of the larger transport framework. Roads, waterways, airways, and spaceways were all discussed. The final architecture treats transport as graph/corridor/path systems. Rail and road use alignments and nodes. Water can use depth fields plus navigation graphs. Air can use flight corridors, runways, and holding patterns. Space uses orbital graphs.
- The final portion of the chat created a formal package of reports: full chat report, YAML spec sheet, aggregator packet, registers, reader brief, audit file, and manifest. These are not design decisions themselves, but they are important artifacts for later Project aggregation. The current response exists because the user wanted a human-readable explanation of the chat rather than more machine-readable outputs.
- The building-system goal also evolved. The user originally asked vector versus voxel. The final model became hybrid: discrete blocks/cells/faces/edges as sim truth, vector as authoring/generation/visual layer.

## [Dominium Architecture III: Launcher, Platform, Renderer, and Handoff Architecture](../../_reader/by_chat/dominium_architecture_iii.md)

- The view system then expanded beyond the launcher. **FACT:** The user wants instant zoom to any scale, instant switching between top-down 2D and first-person 3D, and arbitrary cameras for free cam, map viewing, content creation, HUD cameras, CCTV, overlays, windows, and offscreen targets. These are client/render-side concerns, not simulation concerns.
- This context matters because the rest of the conversation happened inside those constraints. The launcher could not become a dumping ground for OS-specific behavior, sim mutation, renderer decisions, or nondeterministic game-state changes. It had to fit the project's deterministic layering.
- The user then uploaded `dominium.7z`, saying it was the git repository as of that moment. **FACT:** The prior assistant said it could not open `.7z` archives in that environment. That means the actual repository state remained unverified at that stage. This became important later, because many implementation ideas were discussed without confirmed access to the repo contents.
- The user clarified: **FACT:** "The settings selected in the launcher will be used to execute client or server binaries."
- The user then specified another important constraint: **FACT:** the launcher backend should be C89, while frontend code for each binary can use C++98. The user also said client/server binaries can have single-system support.
- A **C89 launcher backend/core** owns logical decisions.
- The final direction became:
- The conversation then refined the renderer design. The assistant had discussed `vector_soft`, but the user rejected the idea of having a separate vector-only renderer. **FACT:** The user asked whether instead Dominium could have "just software renderers" capable of vector graphics and graphics using texture files on all systems as a fallback.

## [Dominium Architecture IV](../../_reader/by_chat/dominium_architecture_iv.md)

- The reusable engine layer was named **Domino**. This became one of the most important naming and architectural decisions in the chat. Domino is the engine/core/platform/sim/mod layer, reusable for other games and projects. Dominium is the game/product layer built on it.
- Blueprints are plans or diffs: place element, remove element, modify terrain, place machine, connect network, etc. When accepted, they generate jobs. Manual player actions and queued work for humans, robots, or other agents should use the same job pipeline. This matters because it keeps replay, AI, and automation consistent.
- The user then asked how to structure Codex prompts. The final high-level roadmap became:
- The assistant generated detailed Phase 1 prompts, platform backend templates, renderer backend templates, setup prompts, launcher prompts, tools prompts, and finally a Phase 7+ roadmap for the game. The game phase itself was not expanded into the same full prompt detail as Phases 1-6. That remains a future task.
- At the end, the user shifted from architecture planning to chat retirement. The chat produced a discovery inventory, a context transfer packet, a final downloadable report package, and then an in-chat reader version. The current request asks for a human-readable narrative explanation rather than more registers or machine-oriented handoff files.
- The conclusion was clear and accepted: **Domino is the reusable engine; Dominium is the game/product layer**. What remains uncertain is the actual repository state. The chat planned the split, but did not verify whether the repo already matches it.
- The conclusion was to define UI modes separately from UI backends. This is one of the central product architecture decisions.
- The package/instance system is central to the whole ecosystem. The user wants installed versions, official base/DLC/mod content, downloaded third-party mods and packs, shared data, instance-specific overrides, and arbitrary combinations without duplicating every possible mix.

## [Dominium Canon, Repository Alignment, and Portability Doctrine](../../_reader/by_chat/dominium_complete_conversation.md)

- This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still follows that contract, and finally broadening the question into a platform-engineering doctrine for portability, modularity, extensibility, reuse, future-proofing, and long-term compatibility.
- The glossary bound terms such as Authority, Law, Process, Lens, SessionSpec, UniverseIdentity, Macro Capsule, SRZ, RepoX, TestX, AuditX, CompatX, SecureX, and related terms. It matters because future assistants must not use sloppy synonyms like "mode" where the canon requires ExperienceProfile or LawProfile. This topic directly supports modularity because stable vocabulary is part of stable architecture.
- Uncertainty: during this preservation pass, a potential inconsistency appeared: some docs claim product roots moved under `apps/`, while an earlier inspected code path under root `client/` was available and `apps/client` was not fetched successfully. This must be verified against the current physical tree.
- DECISION-01:** The old v1 contract/glossary were accepted as the baseline for this chat because the user supplied them as the old ground truth and asked later questions against them.
- DECISION-02:** The live repo audit refined authority: the repo-materialized canon files and canon index are stronger for current repository work than raw prompts.
- DECISION-03:** Ownership-root layout was preferred because it encodes who owns a file or subsystem, while generic `src`/`source` hides responsibility.
- DECISION-04:** Stable contracts plus replaceable implementations best satisfy the user's desire for rewrites/refactors without losing compatibility.
- DECISION-05:** The repo should not be described as fully implementing the old v1 vision yet; many systems are still declarative, scaffolded, or deferred.

## [Dominium + Domino Codex Planning and Handoff](../../_reader/by_chat/dominium_domino_codex_planning.md)

- INFERENCE:** The user accepted this direction in practice, because the next request was to generate Codex prompts to implement each step fully. The user did not explicitly say, "I formally approve the Milestone-0 plan," but they proceeded to ask for prompts based on it.
- The user then asked for recommendations. The assistant recommended a clean startup policy: explicit flags first, no environment/config override in v1, terminal detection through dsys, generic AUTO behavior, product-specific headless handling for the game, build-time GUI/TUI capabilities, and structural error codes for fallback. The user accepted this enough to request a "one big Codex prompt" to implement it.
- However, the later context transfer packet treated that inspection claim as **UNCERTAIN / UNVERIFIED**. This was careful and correct: within the visible chat, there was no reliable tool trace proving the repo had actually been inspected. Therefore, future assistants must verify `dominium.zip` or the active checkout before relying on the platform/render/API answer.
- The core topic was the architecture of the Dominium + Domino project. **FACT:** The user defined Domino as a deterministic, fixed-point, C89 engine layer and Dominium as a C++98 product suite. This matters because every implementation decision had to respect those boundaries.
- The conclusions were clear: future code must not bypass dsys or dgfx, deterministic sim must not use host floating-point, product code should not directly call OS APIs, and old content must not silently break. These are not just preferences; they are the governing rules of the project.
- The numeric core was central because deterministic simulation depends on it. The generated prompt specified fixed-point types, deterministic RNG, saturating arithmetic, and a numeric test harness.
- The unresolved complication is C89 portability. Standard C89 does not provide `long long`, but `u64`, `i64`, and `q48_16` require 64-bit representation. Future work must decide whether to allow compiler extensions, emulate 64-bit values for strict retro targets, or define platform tiers with conditional support.
- Prompt 4 translated this into a minimal repo manifest system. It proposed product manifests, compatibility profile fields, and a launcher path that loads a primary game product. This was important because the launcher->game relationship is central to Dominium as a product suite.

## [Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion](../../_reader/by_chat/dominium_full_conversation.md)

- A future assistant must understand that this chat is not simply about UI. It records the architecture for how Dominium should build itself: through contracts, commands, services, providers, documents, patches, modules, packs, apps, workspaces, diagnostics, evidence, AIDE, Codex, and eventually Workbench.
- The user then redirected the entire plan. They argued that native OS widget GUI tools already exist through Visual Studio, Xcode, etc. The project needed a cross-platform rendered tool environment that uses the same CLI, TUI, and rendered GUI systems as the client. The old UI Editor and Tool Editor were good exploratory ideas but bad final products. This produced the Dominium Workbench concept.
- The discussion then moved into AIDE. The user wanted to automate as much as possible through Codex and AIDE. We developed a task operating model: AIDE creates WorkUnits, tracks attempts, blockers, evidence, repairs, resumes, checkpoints, and promotion decisions. Codex executes bounded tasks. Development can continue with classified partials and repairable blockers; promotion to main requires evidence.
- The final part of the conversation dealt with repo status and task queue. The user pasted status reports indicating that `PRESENTATION-CONTRACT-01` completed with warnings, and then chose to generate six maintenance prompts before replanning. `FULL-GATE-LEGACY-TEST-ROUTE-01` was generated. This preservation task followed.
- The early UI Editor plan was a structured attempt to fix the launcher UI and build a tool for UI authoring. It covered DUI/TLV, native widgets, Win32 preview, deterministic TLV/JSON, layout, validation, codegen, `ops.json`, import/export, and launcher/setup generation. The conclusion was that these are useful components but not the final product architecture. They should become Workbench modules and services.
- Workbench became the central product concept. It is a cross-platform rendered production environment, not a monolithic editor. It hosts workspaces and modules over contracts, commands, documents, patches, services, providers, packs, artifacts, evidence, and tests. It eventually self-hosts by editing its own safe artifacts first, then product UIs, packs, modules, apps, and AIDE work units.
- The rendered GUI must be backend-agnostic. Layouts, controls, widgets, themes, styles, views, and workspaces should be modular and extensible. Themes include first-party primitive-only profiles and OEM+ mimic profiles. The GUI should be task-first, command-backed, evidence-visible, and projection-neutral.
- Preserve all decisions, tasks, prompts, constraints, files, and artifacts in a downloadable package.

## [Dominium Setup Architecture and Handoff](../../_reader/by_chat/dominium_setup.md)

- Near the end, the chat shifted into preservation mode. The user asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat reader version of that package. Those outputs preserved the decisions, tasks, constraints, artifacts, rejected options, and verification queue for future assistants or aggregation into a larger Project Spec Book.
- These directory trees were not final, but they mattered because they exposed the user's preference for simple, shallow, logical structures and native IDE workflows that do not become the source of truth.
- The user later asked where to create Visual Studio and Xcode apps after opening the repo as a folder. The assistant advised that Visual Studio and Xcode projects should be generated through CMake, not hand-authored or treated as authoritative source files. This decision became consistent with later Codex prompts.
- Finally, the user retired the chat and asked for a maximum-fidelity context transfer packet. The assistant produced one. The user then asked for a downloadable shareable report package. The assistant created Markdown/YAML/report files and a ZIP. The user then asked for an in-chat reader version of the package, and the assistant rendered the package contents directly into the conversation.
- The central topic was the setup system itself. It was discussed because the user needed a robust installer/updater/verifier capable of supporting many platforms, distribution channels, legacy environments, package managers, and future update flows.
- FACT: The setup system was repeatedly defined as the only component allowed to install files, modify system/installation state, own installed-file metadata, repair installs, verify artifacts, uninstall, downgrade, upgrade, and roll back. This is the most important architectural rule from the chat.
- The reason this mattered is that Dominium / Domino is a long-lived deterministic system. If launchers, engines, tools, package scripts, or platform installers each had their own install logic, the result would be untestable, non-deterministic, and difficult to audit. The setup system needed to be a central authority so that installed state, ownership, rollback, and verification all remain coherent.
- What remains uncertain is the actual current implementation state in the repository after the applied Codex prompts. The design is clear, but the repo must still be inspected.

## [Domino Dominium Workbench](../../_reader/by_chat/domino_dominium_workbench.md)

- The original UI Editor / Tool Editor plan is now **superseded as a final product**. It is not lost: its useful parts become Workbench capabilities, especially Interface Studio, UI/HUD Sandbox, Theme Laboratory, TUI Studio, Rendered GUI Studio, Preview Matrix, validation panels, import/export tools, and document-patch workflows.
- The central decision is that Workbench must not become semantic authority. Workbench is a surface over contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, tests, and replay/proof. It is the richest human/agent interface over the system, but it must not bypass command, capability, refusal, validation, document, patch, or proof law.
- The second central decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless automation must be **projections of the same command/result/refusal/document/view spine**. A GUI button, a TUI hotkey, a CLI command, a headless JSON job, and a future OS-native widget action should route through the same command/service path and produce the same typed result, diagnostics, refusals, logs, and evidence.
- The user then rejected the old UI Editor / Tool Editor as final products. The user wanted cross-platform tools that use the same CLI, TUI, and rendered GUI systems as the client, not tools dependent on OS-native widgets. OS-native tools like Visual Studio and Xcode remain useful, but they are not the core presentation platform. This changed the plan from a UI editor to a **Workbench Platform**.
- The final major expansion connected Workbench to the actual game direction. Universe Explorer was framed as a lawful inspection/materialization/reference-frame proof surface, not a renderer/free-camera demo. It should prove scale continuity, no modal loading, reference frames, materialization, representation ladders, interest sets, fidelity, provenance, renderer purity, and evidence.
- Decision:** Old UI Editor and Tool Editor are superseded as final products.
- Decision:** Workbench is not authority.
- Reason:** If Workbench mutates files, truth, or product behavior directly, it will drift from CLI/headless/TUI/runtime semantics. Workbench must issue commands, produce patches, preview, validate, commit transactions, and record evidence.

## [Dominium/Domino Engine Refactor Planning](../../_reader/by_chat/domino_engine_refactor_prompts.md)

- FACT:** The Domino engine must be ISO C89. The Dominium UI/tools layer must be portable C++98. Engine code must not use OS APIs. Determinism matters, so floats are disallowed in deterministic paths. The engine must avoid platform-dependent behavior and hardcoded game semantics. Everything should be content-driven.
- This became one of the central architectural ideas of the chat. It makes behavior extensible without giving minds direct write access to the world. A mod can add new sensors, observations, intents, capabilities, or actions, but state mutation still passes through a deterministic pipeline.
- After the architecture and prompts were created, the user asked for a maximum-fidelity context transfer packet. The assistant produced one. The user then asked for a downloadable report package; the assistant generated package files and a ZIP. The user later asked for an in-chat reader version of that package, and finally requested this current human-readable explanatory report.
- The final state of the conversation is therefore not just an architecture. It is an architecture plus an implementation roadmap plus preservation artifacts. The important substance remains the deterministic engine design and the prompt plan, not the packaging files.
- The core idea is that deterministic simulation cannot tolerate platform-dependent behavior, nondeterministic iteration, floating-point inconsistencies, OS dependencies, or UI-driven state mutation. The engine must be portable, reproducible, and replayable. Therefore the architecture repeatedly favored fixed-size integer IDs, fixed-point math, TLV schemas, sorted iteration, deterministic queues, and replay hashes.
- The conclusion was not a final physics implementation. It was a framework direction: each physics family should be a deterministic family plugged into the scheduler, using content-defined TLV prototypes, fixed iteration solvers, stable vtables, and replay hooks.
- The user asked whether the same methods could apply across the whole engine. The answer was yes. This became a central theme.
- Instead of storing final geometry as truth, buildings store footprints, volumes, enclosure definitions, surfaces, sockets, carrier intents, and edit records. Derived compilers produce occupancy, voids, enclosure graphs, surface graphs, support graphs, and carrier artifacts. These are caches, not authority.

## [Domino/Dominium Engine Baseline, Architecture, and Feasibility](../../_reader/by_chat/engine_baseline_architecture.md)

- This corrected the plan. The final sequencing became: first **Milestone 0: Make the baseline path honest**. That means fixing server/runtime circular import, CLI forwarding, `session_create -> session_boot`, missing time-anchor policy registry, and making the strict local playtest validator pass. Only after that should the builder/destruction lab begin.
- The final user action uploaded `Pasted text.txt`, a detailed instruction prompt requiring a full preservation report, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That request is the current task.
- The central architecture distinction was that Domino should be a reusable deterministic simulation substrate, while Dominium should be one game/product layer built on it. This came up immediately when the user asked for a total description of the project. It mattered because the user wants the code to be reusable for future games and possibly other engine projects.
- The visible conclusion was that the engine has real deterministic substrate pieces, but these must be hardened through small playable slices and proof/replay tests. Determinism is not only a mathematical preference; it enables multiplayer authority, replay, audit, mod compatibility, and long-term artifact preservation.
- This became the practical pivot. The user pasted evidence that the repo has compiled targets and some passing tests but lacks a finished playable path. The final decision was that before game features, the team must create one canonical repo-local playable baseline command that passes strict validation.
- Uncertainty: this remains strategic architecture, not an implemented decision.
- The user explicitly accepted the correction that before a builder/destruction lab, the first deliverable should be one canonical repo-local playable baseline command passing strict validation. This is the most important sequencing decision in the chat.
- This was a recommended architectural conclusion after reading live repo docs. It is not a single user-typed acceptance sentence, but the user continued building on it. It should be treated as a strong strategic direction, not a final immutable spec.

## [Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff](../../_reader/by_chat/foundation_workbench_codex.md)

- After the root skeleton improved, the assistant and user recognized that the deeper problem was no longer top-level directories. The problem became semantic duplication and governance: what is public, what is private, what is stable, what is provisional, what is generated, what is a fixture, what must stay compatible, what can be replaced, and what proof is required.
- The key conclusion was that Workbench is not the general module system; it is one consumer of the module/command/service/provider/pack/artifact system. Workbench must not call private tools directly. It must route through registered commands and typed results, diagnostics, refusals, views, and evidence.
- The topic came up because the project needed a model that could support world simulation, modding, tooling, Workbench, release, portability, and future games without repeating endless refactors. The conclusion was that stable contracts and semantic IDs must be separated from replaceable private implementation.
- The repo root cleanup dominated much of the conversation. The old root structure was visibly unacceptable and triggered intense user frustration. The conversation explored cautious moves, gates, root inventories, salvage maps, bulk routing, and deterministic quarantine. The final stance was that the root skeleton is now mostly settled and should not be re-litigated unless validators show a live violation.
- The language policy shifted from historical C89/C++98 to C17/C++17. The mainline native architecture policy shifted toward 64-bit source-native: x86_64 and arm64. Public ABI remains C-compatible. Persisted formats must be fixed-width, explicit little-endian, and pointer-width independent.
- Workbench is a future product surface, not the center of authority. The user wants to get to Workbench and code soon, but Workbench must route through commands/services/views/evidence rather than private direct mutation. The first Workbench slice was narrow validation. The next needed bridge is command-result-view projection.
- Workbench's final shape is a shell hosting modules and workspaces. It eventually includes Project Graph Explorer, Interface Studio, Module/Pack Foundry, App Composer, Release Forge, Agent Work Board, Pack Browser, Renderer/Theme Laboratory, Replay/Trace Viewer, and related tools.
- This became the immediate next frontier. The system must avoid separate CLI, TUI, Workbench, rendered, native, and headless implementations of the same behavior. The next slice should prove a command result can become a semantic view projected across multiple surfaces, preserving the same result schema, refusal codes, diagnostics, and evidence.

## [Domino Framework and Open-Source Provider Architecture](../../_reader/by_chat/framework_open_source_provider.md)

- Finally, the user uploaded a detailed preservation prompt and requested a maximum-fidelity report, registers, spec sheet, aggregator packet, audit, and downloadable files. This package is the response to that request.
- This became the central architectural theme. The conversation refined earlier vendor-shaped paths into service-first paths. The stable pattern is:
- The chat inspected `julesc013/dominium` and found evidence of existing abstractions such as system and graphics layers, stubs, and soft-backed backends. The finding was that raylib could fill concrete provider gaps without replacing the architecture. However, current repo facts are stale/uncertain and must be verified, especially the C17/C++17 vs C90/C++98 baseline contradiction.
- The user's large game vision requires an architecture where the world is infinite by addressability but finite by active simulation. The chat proposed activity states such as cold, warm, scheduled, active, and hot. It also proposed cells/islands/constructs as units of scheduling and authority. Clients can contribute compute, but state changes must be host-verified. This topic should become a formal spec chapter.
- The final topic is this package. The user requested a preservation report that is human-readable first, with registers, spec sheet, aggregator packet, self-audit, and downloadable files. This report preserves the visible chat, not any inaccessible past-chat transcripts.
- The exact first implementation branch, versions, and dependency pins are unresolved. The exact Domino Framework ABI is unresolved. The exact Lua version is unresolved. The current repository baseline must be verified. The formal policy for GPL/LGPL/unclear license material is unresolved. The sparse simulation and CAD systems need formal specs and prototypes.
- The main accepted direction was the framework/provider approach. The user explicitly said they liked the framework approach and asked whether it could be used to make a Domino framework provided by any engine implementation and consumed by any Dominium game implementation. This makes sense because it lets the project use raylib and other libraries quickly without baking them into game law.
- The raylib decision was also directionally accepted. The user repeatedly expressed enthusiasm for raylib and asked about using as much of raylib infrastructure as possible. The caveat is that raylib is a provider suite, not architecture. This affects rendering, audio, input, asset preview, and Workbench bootstrap.

## [Dominium Content and GUI Rebuild Planning](../../_reader/by_chat/gui_binary_content.md)

- That was an important change of direction. It meant the assistant's polished prompt should not be treated as final. The work needed conceptual discussion first. The assistant then analyzed CONTENT0 and identified several issues that could cause bad assumptions to become embedded if Codex acted too soon.
- what start scenarios must explicitly exclude,
- This shifted the content work from "populate required files" to "design a scalable content representation system." It also made clear that procedural generation and defined data are not enemies in the user's vision. The desired architecture must allow them to coexist.
- The user then made a strong decision: **"I've decided I want to redo the GUIs from scratch."
- This was the most important decision in the GUI part of the chat. It changed the task from "can we make cross-platform GUIs?" to "how do we design a full multi-platform GUI and binary matrix without losing backend consistency?"
- Those caveats were not final user decisions, but they are important warnings.
- After this, the user said the chat was being retired and requested a maximum-fidelity context transfer packet. The assistant produced a long state-transfer document with sections for bootstrap, user preferences, workstreams, decisions, tasks, constraints, open questions, rejected options, artifacts, rationale, risks, and a copy-paste prompt.
- Finally, the user asked for this current response: not a machine-readable handoff, not a register dump, not another package, but a clear, human-readable report explaining the substance of the conversation.

## [Dominium Language, Platform, and Architecture Baseline](../../_reader/by_chat/language_platform_architecture.md)

- The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.
- The user then consolidated a broad future plan around Domino, Dominium, Workbench, AIDE, contracts, tests, replay, and evidence. The answer agreed that the plan was strong, but identified missing central pieces: composition resolver, lockfiles, compatibility corpus, trust/permissions, virtual filesystem roots, performance budgets, and stable public-surface promotion rules.
- Finally, the user pasted advice favoring C99 or C++11 due to raylib/SDL and legacy targets. The answer rejected a pivot. Raylib and SDL2 being C APIs only means provider boundaries should be C-callable; it does not force the whole engine or game to C99. The final recommendation remained C17 + C++17, with raylib/SDL2 treated as providers and with external deployment claims placed into the verification queue.
- The chat repeatedly compared C89, C99, C11/C17, C23, C++98, C++11, C++17, and newer C++ standards. The final working direction is C17 + C++17 for the mainline. C99 and C++11 were considered but not adopted as the project-wide baseline. Newer C23/C++20/C++23/C++26 were treated as future provider/tool lanes, not current mainline law.
- The project must retain a C-compatible ABI. The public boundary should remain POD-only, versioned, return-code/refusal based, and free of exceptions, STL containers, classes, templates, allocator ownership, and C++ ABI assumptions. This allows providers, plugins, tools, projections, and future bindings to survive implementation changes.
- The deterministic simulation law remains more important than the language standard. Authoritative simulation must use stable IDs, canonical ordering, fixed-width values, fixed-point math, explicit little-endian encoding, and deterministic scheduler phases. Threads may accelerate derived work, but final authoritative commit must be canonical and not depend on OS timing or thread completion.
- Avoid another cleanup cycle by locking hard-to-change decisions early.
- The goal changed from "should old C/C++ standards be upgraded?" to "what is the full future architecture baseline?" The user initially entertained C89/C++98 staging, then accepted C17/C++17 as mainline. The user also moved from "maybe support old systems directly" to "support old systems through constrained/projection/archive lanes."

## [Dominium Launcher Application-Layer Handoff](../../_reader/by_chat/launcher_app_layer.md)

- Someone reading this report should understand one central thing: this chat is not about inventing new launcher features anymore. It is about preserving boundaries, making the launcher implementation explicit, and ensuring future work happens on top of verified code rather than vague architectural memory.
- There was also an early suggestion to create a `DUI` facade, a Dominium UI abstraction, to support native widgets and fallback rendering. This idea was useful as a conceptual stepping stone but was not ultimately locked as a final requirement in the form originally suggested. Later application-layer canon emphasized **UI IR**, **command graphs**, and **binding validation** rather than a specific `DUI` facade design.
- This phase mattered because it framed the launcher not as a menu program but as a **control plane** for installed products, packs, profiles, compatibility, and launch contracts. However, later canon tightened the permitted communication routes: cross-product communication must go through `schema/` and `libs/contracts`, not arbitrary plugin conventions.
- This later became one of the clearest examples of a superseded path. The user subsequently pasted applied Codex prompts that explicitly required CMake to generate the Visual Studio solution/projects and stated that hand-written `.vcxproj` files must not be the authoritative build. Therefore, all earlier "manual IDE projects as canonical" advice is no longer current.
- That product-first direction was then finalized by a later user prompt defining the canonical repo structure.
- The second was a final purity and contract-ownership repair prompt. It required engine purity, moved cross-product contracts to `libs/contracts/include/dom_contracts`, evicted non-engine content from `engine/`, and hardened sanity scripts.
- This changed the correct future behavior. The next assistant must not redesign. It must implement, audit, maintain, document, verify, and harden.
- The user asked for a maximum-fidelity Context Transfer Packet. That packet was produced. Then the user asked for a final downloadable report package, which was created. Then the user asked to inspect that package in-chat, and an in-chat reader version was produced.

## [Dominium Launcher and Setup Architecture](../../_reader/by_chat/launcher_setup_architecture.md)

- The chat also produced multiple Codex work-order prompts and finally a downloadable report package. Those artifacts are useful, but the substance is the architecture: keep engine deterministic, keep setup/launcher/runtime boundaries explicit, make the launcher optional and modular, use a strong process/instance model, and now implement the launcher over dsys/dgfx rather than ad hoc platform UI stacks.
- FACT:** The user's initial architecture text emphasized:
- The assistant responded by stress-testing this philosophy. It pointed out determinism risks around Lua, plugins, time sources, and ABI details, and suggested more explicit contracts for file headers, TLV sections, runtime CLI capabilities, plugin exported symbols, and setup/launcher boundaries. These were assistant proposals, not all user-stated decisions, but the user continued building on that direction.
- The next important refinement was the user's explicit statement that the launcher should be capable of supervising, but the game must always run perfectly fine with no launcher. This prevented the design from turning into a launcher-dependent ecosystem.
- INFERENCE:** The user accepted this direction by continuing the conversation and later asking for the entire system to be detailed. However, not every proposed ABI field should be treated as final until implemented or confirmed.
- The user then requested a maximum-fidelity Context Transfer Packet, followed by a final downloadable report package, followed by an in-chat reader version of that package. The assistant generated the package and then rendered its structured contents in chat.
- Uncertainty:** The final language boundary for setup remains unresolved after the later C89/dsys/dgfx launcher direction.
- Conclusion reached:** Launcher integration is optional and additive. Runtime binaries must not require launcher metadata.

## [Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture](../../_reader/by_chat/modularity_aide_refactorability.md)

- The final user action was uploading a preservation-package prompt. That prompt requested a maximum-fidelity preservation report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, downloadable files, and a final in-chat reader. This package is the result.
- The user objected to the XStack/AuditX/RepoX/TestX framing and wanted AIDE adopted quickly. The resulting plan made AIDE the repo-native control plane for inventory, task queues, policies, move maps, salvage maps, evidence ledgers, validation, and refactor history. Existing tools should be recycled, not discarded. This is central to future refactorability.
- The discussion proposed target-based CMake and module boundaries rather than path mythology. Public headers, private headers, allowed dependencies, and forbidden dependencies should be explicit. Apps must remain thin. Engine must not depend on game/apps/runtime UI. Runtime adapts host/platform/rendering without owning simulation truth.
- The uploaded prompt converted the conversation into a preservation task. It requires a human-readable report first, then registers, spec sheet, aggregator packet, self-audit, and downloadable files. This final package is intended to be merged later with old-chat reports into a master Project Spec Book.
- The conversation implies a goal of turning Dominium into a long-lived product-line platform rather than a single-game repository. It also implies a desire for auditability: decisions should be grounded, visible, mechanically enforceable, and later aggregatable into a master spec. The user appears to value stable boundaries, explicit compatibility policy, and practical Codex/AIDE tasks.
- The initial focus was directory and distribution structure. It then widened to component naming, repository convergence, AIDE governance, refactorability, and finally broad software engineering doctrine for reusable engine/platform development. The most important change was the rejection of the XStack-style framing and the shift toward AIDE as the near-term control plane.
- The live repo still needs verification. The exact AIDE files, contracts, validators, and migration tasks must be implemented. It remains unresolved which existing roots and tools map to which final homes, which APIs become stable, which code is reusable across products/games/projects, and which prior assistant recommendations should become formal requirements after user review.
- Status: recommendation. Basis: Final response emphasized stabilizing correct public seams only. Rationale: Avoids maintenance paralysis. Implications: Need stability levels and deprecation policy. Related workstream: WORKSTREAM-06. Confidence: medium. Label: INFERENCE. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

## [Dominium Omega/Xi/Pi Architecture & Future-Proofing Planning](../../_reader/by_chat/omega_xi_pi_architecture_future.md)

- The final strategic direction before this preservation request was to run a ?-series: snapshot intake, reality extraction, blueprint reconciliation, foundation readiness, and final prompt synthesis. This is needed because plans must now be mapped onto current repo reality rather than executed abstractly. The next chat should pick up there.
- The user later reported Xi completion. The enduring lesson is that prompt instructions are not enough; architecture must be machine-readable and enforced.
- 4. Preserve all plans, tasks, constraints, risks, decisions, artifacts, and future directions across chats.
- 1. Current repo reality must be reconciled with the blueprint.
- 2. Final Sigma/Phi/Upsilon/Z execution plans must be generated from current repo reality.
- 3. Exact runtime component boundaries must be mapped to existing code.
- 4. Agent governance and vendor mirrors must be implemented.
- 5. Build/release preset drift must be audited and consolidated.

## [Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer](../../_reader/by_chat/os_interface_repo_architecture.md)

- DECISION-01 - CLI mandatory, TUI expected, GUI modular.** This was part of the initial architecture baseline and was repeatedly reaffirmed. It matters because every product must remain operable in recovery/headless/automation contexts. GUI is allowed but not authoritative.
- DECISION-02 - Thin GUI shells over shared contracts.** The chat consistently rejected GUI families becoming separate product architectures. This affects client, launcher, setup, server admin, tools, and Workbench modules.
- DECISION-03 - Repo ownership layout.** The user pushed for repository convergence; the discussion established that folders should map to ownership and contract boundaries. This decision is final enough to guide work, but details remain subject to machine-readable layout contracts.
- DECISION-04 - Current post-CONVERGE authority.** The final audit and layout target docs define current roots and authority stack. Older docs remain context but not current physical-layout authority.
- DECISION-05 - OS-like deterministic operating environment.** The user proposed this framing and the assistant endorsed it. It is not a literal OS decision; it is a conceptual architecture decision. It should be formalized before implementation.
- DECISION-06 - Workbench modular host.** The user explicitly accepted the idea of one integrated environment with many focused modules. This supersedes the old UI Editor / Tool Editor final-product plan.
- DECISION-07 - Interface Operating Layer.** The final UI discussion generalized Workbench into a cross-product interface platform. This is a strong direction, but it should be formalized as doctrine and contract work before being treated as implemented.
- DECISION-08 - Rendered mode product-declared.** This was an assistant correction based on AppShell docs. It is necessary because current AppShell docs say rendered mode is client-only. User has not yet separately confirmed the doctrine change, so treat it as a required proposed decision.

## [Dominium Codex Platform Renderer API Plan](../../_reader/by_chat/platform_renderer_api_plan.md)

- The chat ended by generating a maximum-fidelity transfer packet, then a downloadable report package, then an in-chat reader version. The main thing to remember is this: **the active artifact is the final 9-prompt post-master Codex plan, but it is a plan, not evidence that the code exists. The repo must be inspected before execution.
- These ideas became the architectural heart of the final plan.
- Stable ABI boundaries must use C ABI, POD structs, explicit function tables, and `u32 abi_version` plus `u32 struct_size` first.
- Every evolvable subsystem must use a facade/backend model.
- A central capability registry must drive deterministic selection.
- Determinism grades D0/D1/D2 must be formalized.
- Launcher profiles must select feature sets/backends, not language standards.
- Serialization/assets/saves/replays must be treated as ABI.

## [Dominium Platform Support Planning](../../_reader/by_chat/platform_support.md)

- FACT: That early answer was generated by the assistant, not stated by the user as a final decision. It matters because it introduced a very broad portability ambition, but it was later superseded by more practical platform planning. It should now be treated as historical context or possible research scope, not as a controlling product commitment.
- The user then supplied a detailed inventory covering PlayStation, Xbox, Nintendo, PC handhelds, Android devices, Apple devices, Web platforms, AR, VR, and cross-cutting software targets. This inventory became the central artifact of the chat.
- FACT: The user's list included legacy and current consoles, handhelds, firmware/OS names, Android software variants, Apple OSes, Web runtimes, AR/VR hardware, XR platforms, and graphics/runtime APIs. FACT: It was a list of desired coverage or consideration, not a final statement that every item must receive full parity support.
- FACT: This is the strongest user-made decision in the chat. It overrides any framing where Android, iOS, or Web are treated as optional, secondary, or late-stage ports.
- The central topic was what platforms Dominium should support and how to prioritise them. The discussion moved from a broad and somewhat speculative support vision toward a clearer product hierarchy.
- FACT: The user explicitly decided that PC is the first primary focus and that Android, iOS, and Web are also primary top-tier support. This means future work should treat these platforms as architectural roots. They are not optional ports.
- PC was treated as the starting primary platform. FACT: The assistant repeatedly described PC as Windows, macOS, and Linux. The user's final platform-priority statement referred to Android, iOS, and Web "after PC," which establishes PC as the first major category.
- The key point is that Android is not just "phones." It is a fragmented ecosystem with different screen sizes, input methods, performance tiers, distribution channels, and system behaviours. Android support forces architecture decisions about lifecycle handling, backgrounding, memory pressure, graphics backends, touch input, controller input, asset size, save storage, permissions, and QA device coverage.

## [Domino/Dominium Portability, Assurance, and Future-Proof Architecture](../../_reader/by_chat/portability_assurance_future_proof.md)

- The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.
- Status: Assistant recommendation; not separately accepted after answer.
- Rationale: Replacement must be objectively testable.
- Status: Decision in this package.
- Rationale: Preservation must be honest about source scope.
- The user explicitly required human-readable preservation, uncertainty labels, no invented facts, no silent inference, and no treating assistant recommendations as user decisions. The user explicitly values portability, modularity, extensibility, reuse, replaceability, future-proofing, and proper long-lived engineering.
- Known: Assistant recommended DDAP; user has not explicitly accepted it.
- Unknown: User's final acceptance and desired strictness.

## [Dominium README Architecture, Ports, and Determinism](../../_reader/by_chat/readme_ports_determinism.md)

- The user pasted the final README after those cleanup changes. At that point, the README had the current active form: deterministic constraints clarified, ports unified under one source hierarchy, `/ports` metadata-only if retained, Section 9 normative, lockstep canonical, content-lock mismatch fatal, and disk format versions immutable.
- After the README work, the user asked for a maximum-fidelity context transfer packet. The assistant produced a long state-transfer document with sections for project inventory, decisions, tasks, constraints, open questions, artifacts, risks, and next actions.
- The central artifact was the root `README.md`. The README describes **Domino** as the deterministic engine core and **Dominium** as the official game/tooling/runtime layer. It is written as a high-level architecture document, not a low-level implementation spec.
- The conclusion reached was that the README should remain descriptive, while normative rules belong in `/docs/spec`. This was already stated in the README and preserved. The README should therefore be clear enough to guide contributors but should avoid pretending to be the final binding technical specification.
- What remains uncertain is whether the actual repository `README.md` matches the final pasted version. The chat only saw pasted text and generated prompts; it did not inspect a Git repository.
- The important distinction was between **authoritative** and **non-authoritative** code. Authoritative code mutates canonical simulation state or engine-controlled serialized formats. That code must not use floating point. The engine core and engine-controlled on-disk formats must not contain `float` or `double`.
- The chat also strengthened RNG discipline. RNG streams can only advance during deterministic tick phases. Debug overlays, UI, rendering, and other non-simulation layers must not advance engine RNG streams.
- The README already listed immutable global simulation tick phases: Input, Pre-State, Simulation Lanes, Networks, Fluids & Fields/Merge, Post-Process, and Finalize. The chat added two important constraints.

## [Dominium + Domino Refactor Architecture](../../_reader/by_chat/refactor_architecture.md)

- The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.
- FACT:** This early discussion created the future UI/packs design context.
- FACT:** All products should use shared `dsys` and `dgfx`. No product-specific platform or renderer code path.
- The user wanted separate version numbers for Core, Launcher, Game, Setup, Tools, and protocols. The assistant proposed independent SemVer product versions, integer format/protocol versions, and `DomProductInfo`/introspection metadata so arbitrary mixes could degrade gracefully. The user corrected one important point: **Suite version should be the Game version**, not Core version. That became a final rule.
- FACT:** Official suite releases should conventionally ship base modpack version equal to Game/Suite version.
- FACT:** Engine logic should not hardwire strict equality. Compatibility ranges should decide validity.
- The user asked about directory structure and then made a specific correction: remove `products` under Dominium. The final source structure became:
- This is a user-stated decision and one of the most important carry-forward points.

## [AIDE, XStack, and Dominium Refactor Control Plane](../../_reader/by_chat/refactor_control_plane.md)

- The user then asked about optimizing prompts for GPT-5.3/GPT-5.4 and later supplied advice about harness engineering. That advice argued that teams succeed by engineering the environment around agents: tools, docs, linters, feedback loops, memory, and observability. The conversation accepted the core point: the model is not the whole system; the harness is the multiplier.
- The Grug Brained Developer became a design filter: avoid complexity, avoid premature abstraction, do small safe refactors, prefer integration tests, invest in logging, and respect existing structures before tearing them down. This influenced the decision to narrow AIDE and not overbuild runtime/hosts too early.
- The user eventually named AIDE: Automated Integrated Development Environment. The accepted split became: XStack remains Dominium's strict local governance/proof profile; AIDE becomes the portable public layer. AIDE would live in its own repo, be usable as a standalone repo pack, later as CLI/app/extensions, and eventually perhaps a runtime/service/host system.
- The current Dominium repo has improved governance and build proof but still contains many messy roots. The final plan is AIDE-controlled root recycling: inventory, classify, salvage, move, rewrite references, validate, shim, and retire exceptions. No broad feature work or root moving should occur before CTest/RepoX blockers are classified and AIDE refactor machinery exists.
- The user supplied AIDE advice around dev branches, structured commits, and WorkUnit recovery. The accepted model is `main` as canonical truth, `dev` as governed integration, `task/*` as bounded work, and release/hotfix branches as needed. AIDE should enforce commit trailers, branch roles, safe sync/land/promote/prune, and repo-state-first recovery when prompts are repeated or out of order.
- Unresolved goals include finishing AIDE Q35-Q57, stabilizing Dominium CTest/RepoX blockers, defining final AIDE install/upgrade bundles, implementing root recycling machinery, deciding when product boot proof can proceed, and later deciding whether AIDE Runtime/Gateway/Hosts are truly needed.
- Several decisions are strategic rather than fully implemented. The version/capability model, Git workflow model, install/repair/upgrade model, and tool absorption model are accepted directions but require schemas and code. Future assistants must not mistake them for already completed implementations.
- UNCERTAIN: Exact public-facing naming for AIDE Core/Kernel remains partly open. Exact threshold for accepting CTest-warning status remains a user/repo governance decision. Exact final AIDE installation packaging details remain pending.

## [Dominium XStack Release Identity and Versioning](../../_reader/by_chat/release_identity_and_versioning.md)

- The user then objected to versioning policy drift in real products and expressed concern about SemVer's "1.x forever" failure mode. The first proposed answer was a four-part public version scheme, `GEN.EPOCH.FEATURE.PATCH`, meant to avoid fake major bumps. That idea was useful as an intermediate step but later became less central because XStack already has GBN for dense build history and separate build identity.
- The conversation then moved into how this might fit XStack. The model shifted from "better public version number" to "layered identity model." The assistant recommended preserving per-product versions, a global build number, build IDs, compatibility versions, and suite versions as separate layers. This became the foundation for later decisions.
- The user suggested that suites might use a separate consumer-facing or marketing version, while each component could use stricter SemVer. The chat accepted this as a mature pattern: suites are curated bundles, while components may have technical versions. The model was refined to avoid synchronized fake versioning and to avoid treating a suite major version as universal breakage.
- The user then asked if the suite version should still encode enough meaning to infer internal and external compatibility. The conversation clarified that the suite version can communicate a compatibility envelope or release family, but exact compatibility must live in explicit metadata. This led to the idea of compatibility profiles and later capabilities.
- The chat was then summarized into a knowledge base. After that, the user proposed an even deeper internal rule: use capabilities instead of versions for compatibility. The response accepted this as a stronger model: versions identify releases; capabilities decide interoperability; GBN/BII/hash identify exact artifacts. That is the current final design direction.
- The main design conclusion was that release identity should be layered: product/suite version, component version, build identity, compatibility/capability contracts, lifecycle channel, target/platform, package kind, and manifest metadata should remain separate. This is the central principle to carry forward.
- The chat rebuilt SemVer from first principles and decided that strict SemVer should apply only to components with declared public contracts. Candidate true-SemVer entities include SDKs, engine libraries, tool APIs/CLIs, protocol libraries, plugin hosts, schema libraries, and reusable runtime libraries. It remains unresolved which exact repo modules qualify.
- The user liked the visual shape of SemVer even for consumer-facing items. The chat accepted `X.Y.Z[-pre][+build]` as a useful shape, but required that non-SemVer products/suites be documented as release identifiers rather than API-compatibility promises.

## [Dominium TestX/RepoX Governance and Handoff Chat](../../_reader/by_chat/testx_repox_governance.md)

- FACT:** The user is building Dominium / Domino as a deterministic universe engine + game, not a conventional game project. The visible chat repeatedly framed the project as long-lived, simulation-first, deterministic, modular, and designed to survive across many operating systems, toolchains, renderers, products, and distribution models.
- The user then asked whether the implementation was industry-accepted and what could be improved. The response framed the approach as closer to game engines, operating systems, and long-lived infrastructure than typical game development. The important conclusion was that the design was not exotic, but it was unusually rigorous for games.
- The user had another chat working on content and systems, and asked for a prompt to inform that chat of everything decided so far. A similar prompt was generated for the applications/platforms/renderers chat. These prompts established authoritative boundaries:
- engine/game/content must be zero-asset and capability-driven;
- applications must be thin shells;
- build/versioning rules must not be bypassed;
- This chat then generated new prompts, `EG-TESTX` and `AP-TESTX`, to send to engine/game/content and application/platform/render teams. Those prompts required response prompts from those teams. The user pasted back their responses. Both accepted TESTX canon and identified tensions.
- Another important tension was "no silent fallback" versus renderer fallback. The application/platform response resolved this by saying explicit renderer selection must fail if unavailable, while `auto` mode can fallback only with explicit logging. This distinction became important for testability and user transparency.

## [Dominium Timekeeping and 2038 Resilience](../../_reader/by_chat/timekeeping_and_2038_resilience.md)

- A future assistant should understand that this chat contributes a time architecture doctrine for Dominium: **ACT is authority; DSYS time is runtime-only; observer clocks are derived; civil/astronomical time is projection-only; wall-clock time must never drive authoritative ordering.
- What remains uncertain is the precise target list of legacy machines/toolchains and how far compatibility must go, especially for 16-bit compilers with weak or absent 64-bit arithmetic.
- The final topic is this export task. The user requested a human-readable report first, followed by registers, spec prep, context-transfer packet, aggregator packet, self-audit, and files. This package is designed to let the chat be read later without reopening the full transcript and to support merger into a larger Dominium spec book.
- The goal evolved from "will things break after 2038?" to "how should I design time for projects that should last?" and then to "does Dominium already match that doctrine?" The final upload changed the goal again into preservation and handoff.
- The exact acceptable precision for Dominium ACT is not established. The exact legacy OS/toolchain floor is not fully established inside this chat. The user has not explicitly accepted every assistant recommendation as final doctrine.
- Likely formal requirements include: authoritative logic must not depend on wall-clock time; ACT must remain versioned/fixed-width/logical; cross-shard ordering must use deterministic keys; platform time must remain DSYS-owned and non-authoritative; civil time must be projection-only.
- Which decisions were repo-grounded versus merely assistant suggestions?
- What external platform facts must be verified before formalizing the spec?

## [Dominium UE6, Domino, and Deterministic Universe Feasibility](../../_reader/by_chat/ue6_domino_deterministic_universe.md)

- FACT: This package preserves the currently visible chat about whether Dominium should use UE6, UE5, Domino, Unreal, or a custom engine layer for a highly ambitious deterministic solar-system-scale game. It also preserves the current uploaded prompt as an artifact because it defines this preservation task.
- That response also introduced a rule that shaped the rest of the chat: Unreal should render and host Dominium, but Unreal should not define Dominium. That was the first major conceptual decision point. It reframed Dominium not as an engine project in the narrow sense, but as a portable game/simulation system with replaceable frontends.
- Conclusion: machine gameplay must be designed as a scalable graph simulation, not as unrestricted physics.
- The user asked whether every client can share compute load. The answer said this is only safe in limited forms. The core pattern must be client proposes, server verifies, server commits. Full client authority would break the economy, fog of war, and anti-cheat model.
- The chat did not settle whether Unreal should definitely be used as the first client. It recommended Unreal as a plausible first high-quality frontend, but the final choice still depends on prototype results, licensing, team capacity, platform targets, and how much custom simulation work is required.
- The assistant recommended against starting directly on UE6 because public technical access and production documentation were not treated as available in the visible chat. This was not framed as a permanent rejection of UE6. It was a timing decision: do not wait for a future engine to solve current architecture problems.
- This is the highest-value decision candidate. Core rules, simulation, save format, economy, factory logic, fog-of-war state, and replay/hash systems should be portable. This matters because Domino portability is only plausible if the core does not depend on Unreal object lifecycles and assets.
- The chat rejected the idea that clients can authoritatively simulate resource production, hidden state, enemy bases, combat, or persistent terrain changes in an MMO. Clients can assist, but the server must verify and commit.

## [Dominium UI Editor and Tool Editor Planning](../../_reader/by_chat/ui_editor_tool_editor_planning.md)

- The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.
- This was one of the most important structure decisions in the chat. It prevented the initial implementation from becoming too broad while preserving the long-term goal. The UI Editor would be a bootstrap tool, not the final architecture.
- The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical layout description, and the user accepted it as useful. Future work should inspect the bundles before claiming exact screenshot fidelity.
- The final state of the conversation is therefore not "the tool is built," but "the architecture, constraints, prompt plans, and continuation state have been carefully documented."
- The most important technical discovery was that the project already has a UI system. **FACT:** The user described the current launcher GUI as the Dominium UI, or DUI, schema/state system using TLV. It has at least three backends: Win32 common controls through `comctl32`, DGFX through Domino's renderer/event pump, and a null backend.
- What remains uncertain is the actual state of the code. The user named files, but the chat did not inspect the repository. A future assistant must verify exact paths, build targets, TLV parser implementation, and current launcher behavior.
- FACT:** The user explicitly chose to make the UI Editor first. This first tool is a minimal Windows-only editor that can visually edit layouts and generate TLV directly. **FACT:** The Tool Editor comes later and is intended to become the full first-class DUI authoring environment.
- This matters because the final Tool Editor is too large to build as the first move. The UI Editor is a bootstrap tool. It should become capable enough to create the Tool Editor's own UI. Then the Tool Editor can eventually edit itself, the setup program, the launcher, the game, and other tools.

## [Dominium Universe Explorer Planning and Repo Handoff](../../_reader/by_chat/universe_explorer_planning.md)

- The pasted discussion on trees, screws, pottery, axes, chairs, tables, and machines established that the player should manipulate material, geometry, constraints, processes, tools, stations, and affordances. The conclusion is that "item classes" must not be the truth substrate. Recipes and blueprints can exist, but as higher-order formalizations.
- A major theme was that useful local inventions must become portable, standardized, industrialized, and institutionally adopted. The repo now has a Formalization Chain spec and Player Desire Acceptance Map that strongly preserve this. The future work is making this playable: drafting, measuring, testing, blueprinting, certifying, teaching, manufacturing, maintaining, and revising designs.
- Workbench was treated as the likely first surface for the Universe Explorer, but only if it remains projection, not authority. The repo queue says `PRESENTATION-CONTRACT-01` is next, with `PROJECTION-CONFORMANCE-01` as alternate. The conclusion was that presentation/projection contracts must come before building UI or renderer features.
- The final plan accepted the newer repo status: structure is clean enough to stop giant structure prompts. Remaining cleanup should be targeted: stale full-gate tests, pack layout canon, residual taxonomy, AIDE state classification, public header ABI, provider split. This is a planning recommendation, not yet an explicitly accepted user decision.
- The early goal was broad recovery of lost architecture. It became repo-audited synthesis. Then it shifted toward a concrete first milestone: Universe Explorer. Finally it shifted toward packaging the chat for preservation.
- DECISION-01 was made by the user when they corrected the assistant: the chat's job is not to implement anything, but to plan, explore, and discuss. This governs the rest of the chat.
- DECISION-04 is the user's strongest product-direction statement. The user said the first major objective should be a seamless 1:1 scale universe explorer before embodiment and deeper simulation systems. The assistant refined it but did not reject it.
- DECISION-06 is not fully user-accepted yet. It is a best-plan recommendation based on the pasted repo-status and verified docs.

## [Dominium Architecture, Workbench, AIDE, and Product-Spine Planning](../../_reader/by_chat/workbench_aide_product_spine.md)

- The user noted that earlier prompts were hard to copy because they were not always contained in one code block, and that prompts should better handle dirty worktrees and concurrent tasks. From then on, generated prompts included detailed dirty worktree handling, allowed/forbidden paths, non-goals, validation, blocker classification, and commit/final-response formats.
- The final recommended sequence was: finish replay proof and barebones client, run product spine review, then begin limited parallel dev. Larger parallel waves should wait until minimum AIDE workflow law exists.
- The user then requested this full preservation package so a new chat could continue without re-explaining everything. This final handoff is itself part of the preservation output.
- The conversation treated epistemics and diegetics as more than flavor. They determine what must be simulated, loaded, rendered, or refined. If a player has not observed something, it can remain summarized so long as future expansion is consistent with seed, law, and causal history.
- DECISION-01 matters because the user's ambitions include worldgen, player invention, civilizations, modding, Workbench, AIDE, and future interfaces. A normal game-feature model would collapse. A deterministic simulation operating environment lets each capability become a contract-backed subsystem.
- DECISION-05 matters because the user wants many agents and machines to work in parallel without being stopped by every blocker. But main cannot become a dumping ground. This is why dev is permissive and main is evidence-blocked.
- DECISION-09 matters because separate CLI, TUI, GUI, and native systems would duplicate behavior and drift. The chosen architecture makes command/result/refusal/view/action the truth and projections the surface.
- DECISION-14 matters because `PACKAGE-MOUNT-SLICE-01` has only proven fixtures and reports. Treating it as package runtime would create false implementation claims.

## [Dominium World Architecture](../../_reader/by_chat/world_architecture.md)

- The future relevance of this chat is high. It should feed directly into the future project spec book and into a corrected implementation prompt. But it should not be treated as final implementation detail everywhere. Many high-level decisions are settled, but solver formulas, exact file encoding details, build system integration, actual repository layout, and some numerical representations still require verification.
- Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular, content-driven, and field-based. Chunks are not the world. Chunks are just how the world is cached, meshed, streamed, and saved.
- This comparison was not a final technical dependency, but it helped clarify the design goal: Dominium should not simply copy any one of these systems. It should combine their useful elements while avoiding their limits.
- The user then introduced and refined a power-of-two naming system. The final scale names are:
- This was a major turning point because it standardized the vocabulary. "Country," "state," and other geographic names were discarded in favor of neutral, technical scale names. The user also refined the universe addressing model over time. Earlier values changed; the final stated limits became `2^8` galaxies per universe, `2^24` systems per galaxy, and `2^16` planets per system.
- A key refinement came when the user decided that working memory should use Q16.16 and save files should store Q4.12. This was important because it separated high-precision transient simulation from compact persistent storage. Runtime moving objects get finer precision. Static or saved objects are represented locally within chunks.
- Another major decision was that untouched chunks should not be saved. Even if a procedural chunk is loaded temporarily for rendering or collision, it should not become persistent unless it contains actual dynamic state or overrides. This led to the distinction between untouched, procedural, and overridden chunks. Procedural chunks are temporary caches. Overridden chunks contain edits, objects, or saved changes.
- Near the end, the user asked for a Codex 5.1 implementation prompt. A long prompt was produced, instructing Codex to implement the engine core, fixed-point types, world addressing, chunking, save formats, ECS, engine API, runtime CLI, and docs. Later, the context packet and final report package audited that prompt and found important defects. The prompt is useful, but not safe to use directly.

## [Dominium XStack and Lab Galaxy Handoff](../../_reader/by_chat/xstack_lab_galaxy.md)

- and XStack must serve development rather than development serving XStack.
- After the transcript appeared, the user asked for a maximum-fidelity Context Transfer Packet. The assistant produced one, with sections such as workstreams, decisions, tasks, constraints, open questions, risks, artifacts, and verification queue. Then the user asked to turn that into a downloadable report package. The assistant created Markdown/YAML files and a ZIP archive.
- Finally, the user asked not for another package, but for an in-chat reader version of the package. The assistant rendered a structured in-chat reader. The user then asked for this current response: a human-readable, intuitive narrative report.
- The final state of the conversation is therefore not "we are ready to code the next feature." It is: **we have a large handoff/report package that captures the state, but the next real action is repository verification and consistency audit.
- The conclusion was that Dominium's architecture must preserve determinism, replayability, epistemic boundaries, and modularity. This remains a binding direction, but actual repository implementation must still be verified.
- XStack became a central topic because the user needed reliable autonomous development. It was not just a testing layer; it was a development control substrate. RepoX enforces invariants, TestX proves behavior, AuditX detects drift, ControlX orchestrates, PerformX monitors budgets/performance, CompatX handles schema migration, SecureX handles trust/security, and gate/tools/xstack/run provide execution surfaces.
- The key conclusion was that XStack must be **portable and removable**. It should be possible to use XStack in other projects or remove it from Dominium without breaking runtime. This is still one of the biggest constraints and must be verified.
- The conclusion was that docs should be layered: README for accessibility; architecture docs for technical explanation; canon/glossary/contracts for binding doctrine. The 13-prompt transcript reports that docs/canon and many architecture/contract docs were created, but this must be verified.
