Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: tasks_index_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`

# Tasks And Future Work

Task-like entries are historical unless stronger current repo authority opens them.

## [Dominium Advanced Simulation and Infrastructure Architecture](../../_reader/by_chat/advanced_simulation_infrastructure.md)

- The user then asked whether the corridor model could be made more extensible and performant. That prompted a refinement: the editable corridor should not be the same as the runtime representation. Users and tools manipulate high-level splines, attachments, and features. The engine compiles that into microsegments, indices, occupancy bitsets, connectivity edges, structural references, and render/sim extraction data.
- The next step was integration. The user asked what other systems this should link into. The answer identified many: RES, ENV, BUILD, TRANS, STRUCT, SIM, POWER, FLUID/HYDRO, HEAT, ATMO, VEHICLE, JOB, AGENT, logistics, inventory, rendering, save/load, replay, multiplayer checksums, ownership/authority, permissions, construction zones, and localization.
- The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it.
- After the architecture was established, the user asked for a Codex prompt plan to implement any necessary changes. A nine-step plan was produced: coordinate/placement specs, deterministic pose/frame math, TRANS 3D corridors, STRUCT arbitrary orientation and anchors, DECOR host placement, deterministic command schemas, UI snapping refactor, performance hardening, and docs/migration notes.
- Finally, the chat shifted into archival mode: it produced a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader version. Those later outputs preserved the discussion for future aggregation.
- Once the architecture was clear, the user wanted implementation planning. The chat produced a nine-step Codex prompt plan covering specs, fixed-point pose/frame math, TRANS, STRUCT, DECOR, deterministic commands, UI snapping, performance hardening, and docs.
- Then it produced a prompt for another GPT-5.2 chat that already had a refactor/optimization plan. That prompt told the other chat to amend its existing plan instead of restarting, and to verify coverage of arbitrary placement, unified spatial primitives, co-location, signage, buildings, and determinism/performance.
- The final phase was preservation. The user asked for a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat report reader. These artifacts were about preserving the chat for future use and aggregation, not about new architecture decisions.

## [Dominium APP0 Runtime, Platform, and Renderer Architecture](../../_reader/by_chat/app_runtime_platform_renderers.md)

- The conversation started when the user provided a structured prompt called **APP0 - Runtimes, Applications, Platforms & Renderers**. It was addressed to **GPT-5.2 Codex** and framed as part of the ongoing **Dominium / Domino project**. The prompt's purpose was to build executable and platform support correctly while staying inside the application/runtime layer.
- The initial APP0 prompt established several hard rules. The assistant was not allowed to redesign simulation rules, alter content definitions, change life/civilization/economy logic, or introduce gameplay shortcuts. This mattered because Dominium appears to have a strong distinction between **authoritative simulation/game logic** and the shells that host, display, launch, inspect, or distribute that logic.
- A first assistant response converted the user's APP0 prompt into a large implementation pack. It proposed repository shapes, CMake targets, executable names, renderer backends, CLI flags, smoke tests, and a commit sequence. It was useful as an implementation artifact, but it was premature relative to the user's actual desired process.
- The user immediately corrected the direction: **"First, let's discuss this before we plan or generate any prompts."** That was an important change. It meant the user did not want a Codex prompt yet. They wanted to reason about the architecture before locking implementation instructions.
- The user then explained that by the end of the macro-prompt plan, the project should have a **running executable** capable of displaying an **interactive and resizable window** for each supported platform and renderer combination. This made the discussion more concrete. APP0 was no longer just about docs and stubs; it had to create a real runtime path.
- The user then stated that future implementation would have permission to modify `render`, `platform`, `application`, `client`, `server`, and docs. They asked whether this was enough or whether `engine` and `game` also needed write access.
- The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do.
- Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.

## [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../../_reader/by_chat/app_testx_codehygiene.md)

- A large set of prompts was then generated to lock down architecture, determinism, performance, schema governance, rendering, epistemic UI, sharding, interest sets, and fidelity projection. This became the Phase 1 hardening layer. Additional audit prompts were introduced to ensure consistency before proceeding into life, civilization, war, content, agents, tools, mods, and final long-term policy.
- This was one of the most important engineering turns in the conversation. It made future performance work a backend/policy problem rather than a gameplay rewrite problem.
- Because the chat was huge, the user asked for a maximum-fidelity context transfer packet. Then they asked for downloadable report files. Then they asked for an in-chat reader. Finally, they asked for this human-readable explanatory report. This final report is meant to let a future assistant or human understand the substance without re-reading the whole conversation.
- This topic is central to long-term scalability. It allows future CPUs, GPUs, NPUs, heterogeneous cores, cache structures, and distributed servers to be supported by adding backend policies rather than rewriting gameplay.
- Large prompt families were generated for life/death/continuity, civilization/economy/governance, war/conflict, canonical content, agents, tools, mods, and final long-term maintenance. These are extensive background artifacts. Later, the chat shifted away from implementing those systems here because another bootstrap declared the core design complete and locked.
- For future use, those prompt families are historical/planned artifacts. They may be useful in content/spec aggregation, but current work should not redesign them.
- Later, the user pasted a newer build/version model from another chat. That model superseded simpler earlier ideas: GBN is only for distributed artifacts, BII exists always, build kind and channel are distinct, product SemVer is manual, and all protocols/schemas/API/ABI versions are orthogonal. This matters because future testing and app prompts must use BUILD-ID-0, not the earlier model.
- INFERENCE:** The user wanted to prevent future chats or Codex sessions from drifting, forgetting, or simplifying. They care deeply about maintaining continuity across many chats and turning fragmented planning into a stable project corpus.

## [Dominium/Domino Architecture and Codex Prompt Roadmap](../../_reader/by_chat/architecture_codex_prompts.md)

- UNCERTAIN / UNVERIFIED: No repository code was inspected or modified in this chat. The prompts and architecture are plans and artifacts, not proof that implementation exists. The actual repository state, build system, existing code quality, GUI backend availability, TLV schemas, and whether any prompts have been applied remain unverified.
- The most important thing to remember is this: **this chat is the architectural and implementation-roadmap backbone for Dominium/Domino, but it is not an implementation log**. It should be preserved as a design/specification source and as a prompt library, while actual code and current facts must be verified separately.
- FACT: The user opened by pasting an "Extended Master Starter Prompt - Dominium + Domino." That prompt established the role of the assistant as a senior engine architect and defined the main project philosophy. Domino was described as a deterministic, fixed-point, C89 engine portable across old and modern OS/architecture combinations. Dominium was described as the product suite built on top of Domino.
- This phase introduced one of the chat's most durable ideas: **engine systems should operate on generic IDs, tags, models, and TLV parameters, not hardcoded content families.
- FACT: The user asked whether the whole system could be made more extensible and modular. The assistant proposed applying the same pattern everywhere: core + registry + models + data. This produced the repeated architecture model used later in prompts: each subsystem has a core API, model family/vtables, data prototypes, runtime instances, registries, TLV schemas, and save/load hooks.
- FACT: The user asked for a plan for a prompt to Codex to implement all the changes and document them. Then the user asked how to split it into multiple prompts under ten. The assistant split the work into seven major prompts. The user then repeatedly said "Next," and the assistant generated Prompts 1 through 7 in detail.
- Those first seven prompts covered:
- FACT: After the first seven prompts, the user said they wanted a minimal GUI and did not want to test only in CLI. They also reminded that the engine and core know nothing about actual data definitions and that those need to stay in base/mods/packs.

## [Dominium Architecture, UI, Providers, and Robot OS Strategy](../../_reader/by_chat/architecture_ui_providers.md)

- The user then said the latest docs and code were live at `julesc013/dominium`. The assistant treated the repo as an implementation baseline and observed that AppShell, UI mode resolution, distribution doctrine, and component matrices already existed. This changed the task from inventing a GUI strategy from scratch to reconciling the transfer brief with existing repository doctrine.
- INFERENCE: The user wants to turn Dominium into a platform-level project whose architecture can survive decades of refactors, ports, new games, new providers, and evolving standards. The user also wants future assistants to stop re-litigating already-settled principles and instead build upon the emerging doctrine.
- The user appears to prefer source layouts and naming that remain meaningful years later. They dislike vendor-shaped, framework-shaped, and status-word architecture. Future assistants should not propose "just use X framework" as the answer. They should instead map libraries to providers, profiles, and contracts.
- The UI should feel like a customizable robot OS whose HUD, menus, TUI, CLI, Workbench, and future VR shell are projections of the same system.
- The most important immediate next task is provider/Robot OS wedge planning with validators and manifests.
- 7. "Turn PROVIDER-WEDGE-01 into a Codex-ready implementation task."

## [Dominium Build and Future-Proofing Architecture](../../_reader/by_chat/build_and_future_proofing.md)

- The user then pushed beyond build mechanics. They asked what else they were missing about portability, modularity, extensibility, replacement, rewriteability, and reuse across future games and engines. They explicitly wanted Dominium to be developed like a proper OS or game-engine platform, not a one-off indie project.
- The final uploaded prompt requested a complete preservation package for this chat: a human-readable explanation, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, and files/ZIP package. This response completes that export task and creates downloadable files for later reading and aggregation.
- The user wanted reusable code for different games on the Domino engine and possibly unrelated future engine/game projects. The answer was to freeze contracts rather than implementations. Stable ABI/API/data/protocol surfaces should be explicitly versioned and tested; implementations should be replaceable behind black-box conformance tests. This is the basis for future rewrites without breaking compatibility.
- The uploaded prompt requested a complete chat preservation package with human report, registers, handoff packet, spec sheet, aggregator packet, audit, and downloadable files. This output creates that package and labels its limitations.
- The user explicitly wanted to design a robust Dominium build system that could handle many machines, IDEs, compilers, OS floors, CMake presets, CI lanes, distribution outputs, and historical toolchains. The user also explicitly wanted Dominium's codebase to be portable, modular, extensible, reusable across future games and engines, and refactorable at the level of whole files and directories.
- INFERENCE: The user is trying to prevent Dominium from accumulating accidental architecture. They want mechanical governance rather than relying on memory or assistant recommendations. They also want future assistants to stop repeating conceptual advice and instead preserve actionable structure, constraints, risks, and next tasks.
- The unresolved goals are implementation goals: deciding which recommendations become canon, adding public-surface/dependency/build contracts, validating the current live repo state, and applying the proposed cleanup tasks. The preservation package is complete, but the engineering work it describes remains pending.
- The user wants future assistants to preserve tentative status and not over-canonize recommendations.

## [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../../_reader/by_chat/canonical_structure_and_framework.md)

- This produced a pattern: generate a large Codex/AIDE task, the user ran it or reported a result, then the assistant evaluated what was truly fixed versus what was only validator/document churn. The user eventually demanded a one-shot "actual final cleanup" prompt because previous passes had sometimes added validators without moving directories. That prompt explicitly required real `git mv` routing, not just reports.
- INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly different engine implementations.
- The closed root model was the most emotionally and technically important decision. The user repeatedly objected to root proliferation; the final root set became the anchor for all later advice. This decision affects every future proposal: if a concept can fit under an existing root, it should not become a new top-level root.
- The Workbench discussion involved a similar tradeoff. The user wanted powerful authoring workspaces, but the architecture must not make Workbench a privileged bypass. Therefore, Workbench modules and workspaces should operate through the same commands, views, actions, documents, diagnostics, and evidence packets that CLI, CI, headless, server, and future apps use.
- The strongest immediate maintenance tasks are: refresh stale generated evidence, repair launcher pack-verification marker debt if still blocking fast strict, run or audit full CTest/T4 failures, and classify remaining full-gate failures by cause. The task names discussed include `FULL-GATE-GENERATED-EVIDENCE-REFRESH-01`, `FAST-STRICT-EVIDENCE-MARKER-REPAIR-01`, and `FULL-CTEST-AUDIT-NONPATH-01`.
- Mainline tasks discussed include `PRESENTATION-CONTRACT-01`, `PROJECTION-CONFORMANCE-01`, `COMMAND-RESULT-VIEW-SLICE-01`, `PACKAGE-MOUNT-SLICE-01`, and `WORKBENCH-VALIDATION-SLICE-01`. The rule is to prove narrow slices before broad UI, gameplay, renderer, provider runtime, or package runtime expansion.
- The user wants structure to support modularity, portability, extensibility, reuse, modding, backwards compatibility, and future replacement.
- The user strongly prefers actual execution/move prompts over endless micro-planning when structure is blocking work.

## [Dominium Chronology & Celestial Systems](../../_reader/by_chat/chronology_celestial_systems.md)

- The final state is that this chat became both a design discussion and a packaged source document for future aggregation.
- What remains unresolved is the exact mathematical implementation of these frames and how much relativistic fidelity should exist in phase one.
- The user asked how to extend calendars beyond planets. The answer was that the larger the scale, the less ordinary calendar structure survives. Sol can have a system-wide civil time and epoch calendar. The Milky Way should use galactic coordinate time and epoch blocks. The universe should use cosmological time and large phases/ages/eras.
- The reason is to avoid losing context across chats and to support a future Project Spec Book. This chat produced many artifacts: prompts, reports, registers, YAML, a ZIP package, and explanatory summaries. The artifacts matter, but the substance remains the design decisions described above.
- It is reasonable to infer that the user wants a future implementation path, likely through another assistant and eventually Codex, but does not want premature code before the broader project context is inspected.
- It is also reasonable to infer that the user wants a future Project Spec Book assembled from multiple old-chat reports, and that this chat should contribute the chronology/celestial/timekeeping chapters.
- This decision makes sense because it separates clean internal logic from messy external software expectations. However, it is less directly user-confirmed than the month order. Future work should ask whether compatibility projection should be default or optional.
- The future project architecture can support data-driven systems.

## [Dominium Development Routes and Continuity Preservation](../../_reader/by_chat/development_routes.md)

- The conversation therefore produced both a **substantive technical proposal** and a **continuity-preservation workflow**. The technical proposal concerns how Dominium might be built. The preservation workflow concerns how the ideas from this chat should be carried forward into future chats and eventually into a larger **Project Spec Book** or **Master Living State File**.
- Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict determinism matters, whether replay or multiplayer are goals, whether modding matters, and what the actual game loop is. Until then, the kernel-first plan should be treated as a strong provisional proposal, not a final specification.
- After the initial planning answer, the user said the chat was being retired and asked for a **maximum-fidelity Context Transfer Packet**. This changed the task. The goal was no longer to continue designing Dominium directly. The goal became preserving everything necessary for a future assistant to continue without making the user repeat context.
- The assistant produced a large Context Transfer Packet. It preserved the technical route proposal, the caveats around its uncertainty, the proposed phase order, the open questions, the risks, the artifacts, and the next actions.
- The user then asked to turn the Context Transfer Packet and visible chat context into a final downloadable, shareable, reusable report package. This was a packaging and normalization task. The user specified exact output files: a full chat report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit file, manifest, and ZIP package.
- After the downloadable package was generated, the user asked not to create another handoff package but to render the package contents into a readable, navigable in-chat report. This led to an "IN-CHAT REPORT READER" response. That response explained the package contents, the workstreams, decisions, tasks, constraints, artifacts, risks, verification queue, and next questions.
- This topic connects to future work because choosing the route determines the order of implementation. If Route C is accepted, work begins with simulation primitives and determinism rather than UI or content.
- Future work must decide how strict determinism really needs to be. Full determinism can be valuable, but it can also impose cost and complexity.

## [Documentation Standards, README Strategy, and Handoff Packaging](../../_reader/by_chat/documentation_standards_readme.md)

- The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.
- This became the foundation for nearly every later prompt and plan.
- The user then asked for a prompt that Codex could use to read through every file and insert, append, amend, or create documentation, including inline comments, block comments, and docs/README content.
- That prompt was the first large artifact in the chat. It was execution-ready but not executed here.
- The assistant converted this into a Codex prompt. The proposed deliverables were:
- The user then provided the earlier documentation prompt and asked to optimize it to conform more strictly to international code documentation standards for the relevant languages and documentation formats. A stricter prompt was generated, aligned with ISO C89/C90, C++98, assembly, Doxygen-compatible structured comments, Markdown docs, and ASCII-safe source compatibility.
- There was one known defect in that prompt: a typo line, `Determininism guarantees remembered` / `Determinism guarantees remembered`, depending on the preserved version. The report package later marked that as something to correct before reusing the prompt.
- Later, the user said the project had been heavily refactored in the setup, launcher, and game design chats. They wanted a prompt to scan the repository, read the code, ensure every file in `docs/` was consistent and up to date, and overhaul README in an industry-standard format that could serve as a landing page until a website exists.

## [Dominium Architecture I](../../_reader/by_chat/dominium_architecture_i.md)

- The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in filenames. Instead, those details should live in metadata. This became part of the future build/package design.
- The user then gave the "big task": create a set of `.txt` files, one for each file in the git directory, telling Codex how to implement it. These were not intended to be source files themselves. They were implementation-instruction files: requirements, prohibitions, dependencies, functions, declarations, and design constraints. This became the dominant workstream of the chat.
- After the spec-generation work, the user changed the task again: the chat was being retired. The user asked for an OC-1 discovery inventory, then a maximum-fidelity Context Transfer Packet, then a downloadable package with Markdown/YAML reports, then an in-chat reader version of that package. Those handoff tasks did not continue project design; they preserved the state of the chat.
- The conclusion was to create one `.txt` implementation-spec prompt per repository file. Each prompt would tell Codex how to implement that file without needing the entire conversation. This became the main practical output of the chat.
- What remains uncertain is the current real-world status and capabilities of "Codex 5.1 Max." That is an external tool fact and requires verification before future use.
- This is a formal packaging/build policy. It should feed into future build scripts, package manifests, release metadata, and possibly save/replay compatibility metadata.
- The most important unresolved issue is duplication and contradiction. `dweather`, `dhydro`, and `dai_core` were generated in more than one form. The package does not choose a final version. A future assistant should not implement any of those blindly.
- The user explicitly wanted Codex to help with implementation. This goal drove the conversation toward file-specific implementation prompts.

## [Dominium Architecture II](../../_reader/by_chat/dominium_architecture_ii.md)

- The last part of the chat was handoff extraction. The user asked for discovery inventory, structured registers, a context transfer packet, and then a downloadable package. The generated package captured the chat's workstreams, decisions, tasks, constraints, open questions, artifacts, risks, and verification items. This current report is a plain-language explanation of that substance.
- This matters because it prevented future implementation from chasing arbitrary continuous geometry in the deterministic core. The user wanted arbitrary shapes, but also deterministic integer math and old-platform support. The compromise was to allow rich authoring tools while baking runtime state into deterministic structures.
- The chat discussed fixed tick phases, virtual lanes, merge order, command buffers, event queues, and deterministic serialization. The simulation must not depend on render FPS, wall-clock time, OS scheduler behaviour, GPU state, or floating-point quirks. This explains many later decisions: C89 core, integer/fixed-point math, no sim floats, no platform headers in simulation, and renderer as pure observer.
- What remains uncertain is the exact code-level API and component layouts. The chat produced specs and prompts, not final source code.
- This was one of the most important conceptual outputs. It provides the future assistant with a mental model for everything else. Railways are graph/corridor systems. Buildings are microgrid frames plus archetypes and fixtures. Terrain is base fields plus delta fields. Power, data, and fluids are graph/field systems. Construction is blueprints and jobs. Space travel is an orbital graph/domain system.
- The default world is Earth in Sol in the Milky Way. The base game MVP is one surface, but the architecture should support galaxies, systems, planets, and future server/shard arrangements.
- The user also wanted buildings rigid for now but future collapse/destruction support. The conclusion was to include future-proof structural fields but not implement collapse in the MVP.
- This is important for future hydrology, geology, stability, collapse, pathing, and undo/history.

## [Dominium Architecture III: Launcher, Platform, Renderer, and Handoff Architecture](../../_reader/by_chat/dominium_architecture_iii.md)

- The assistant generated script templates and Codex prompts for these. Those prompts should be treated as implementation artifacts, not proof that code was actually changed.
- These ideas were accepted as direction by continued user refinement, but implementation remains future work.
- The user then asked for a Codex prompt to implement and document this. That means the keybinding map was accepted enough to become implementation material, but it should still be documented as a default binding specification rather than an immutable law.
- The final phase of the chat was meta-work: extracting this chat into handoff forms. The user asked for OC-1 discovery inventory, then OC-2 registers, then a maximum-fidelity Context Transfer Packet, then a downloadable report package, then an in-chat reader version, and now this human-readable explanatory report.
- Those outputs are important artifacts, but they are not the substance of the design. Their purpose is to preserve this chat's decisions, uncertainty, and future work for later aggregation into a master Project Spec Book.
- This matters because future assistants must not implement launcher logic directly in Win32 widgets, Cocoa classes, SDL callbacks, or modern C++ code.
- The user later reversed this. The final decision was to remove minimal versions and use full single implementations. This means the architecture should not split platform/render backends into minimal and full variants unless future technical constraints force it.
- This remains a future implementation plan.

## [Dominium Architecture IV](../../_reader/by_chat/dominium_architecture_iv.md)

- A number of Codex prompts were generated earlier in the chat for refactoring the repo, implementing runtime/platform/render APIs, setup, launcher, game bootstrap, ECS/SIM, and world/terrain/hydrology. However, the user later clarified that none of the Phase 2.5+ prompts had been implemented yet and wanted to pause before going further. The user wanted the systems to be more extensible and modular before committing.
- The user then asked how to structure Codex prompts. The final high-level roadmap became:
- The assistant generated detailed Phase 1 prompts, platform backend templates, renderer backend templates, setup prompts, launcher prompts, tools prompts, and finally a Phase 7+ roadmap for the game. The game phase itself was not expanded into the same full prompt detail as Phases 1-6. That remains a future task.
- The topic mattered because every Codex prompt depends on paths and module boundaries. If the repo layout is inconsistent, prompts will fail or scatter code into the wrong places.
- A platform backend prompt template was generated, along with parameter sets for Win32, Win16, DOS32, DOS16, CP/M-80, CP/M-86, Carbon, Cocoa, X11, Wayland, POSIX, SDL1, SDL2, and null.
- The unresolved issue is the exact manifest/schema format. JSON, TOML, and INI-like examples appeared in prompts, but no final schema choice was made.
- A full set of Phase 5 prompts was generated for launcher core, CLI, TUI, GUI, and extensions.
- Phase 6 prompts were generated for the tool framework, core dev tools, editing backends, and GUI editor host.

## [Dominium Canon, Repository Alignment, and Portability Doctrine](../../_reader/by_chat/dominium_complete_conversation.md)

- This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still follows that contract, and finally broadening the question into a platform-engineering doctrine for portability, modularity, extensibility, reuse, future-proofing, and long-term compatibility.
- The conversation opened with a deliberate reconstitution of canon. The user supplied an old self-contained constitutional architecture prompt for Dominium and Domino. The assistant acknowledged it as authoritative within the conversation. The user then supplied a canonical glossary v1.0.0, and the assistant acknowledged that the glossary constrained future terms.
- This preservation task was then uploaded as `Pasted text.txt`. It requested a maximum-fidelity report package for the current chat, with human-readable explanation first, structured registers, context-transfer packet, spec sheet, aggregator packet, self-audit, and downloadable files.
- Uncertainty: the raw pasted prompt is not the current repo authority unless materialized in repo canon. The later audit found that it had in fact been materialized under `docs/canon/constitution_v1.md`.
- The glossary bound terms such as Authority, Law, Process, Lens, SessionSpec, UniverseIdentity, Macro Capsule, SRZ, RepoX, TestX, AuditX, CompatX, SecureX, and related terms. It matters because future assistants must not use sloppy synonyms like "mode" where the canon requires ExperienceProfile or LawProfile. This topic directly supports modularity because stable vocabulary is part of stable architecture.
- The user then asked what practices would make the code reusable for other games and even other engine projects. The assistant answered that the correct goal is not to make all files permanent, but to make boundaries explicit and stable. The doctrine became: stable contracts, replaceable implementations, deterministic behavior, portable projections, and no accidental authority from paths/tools/UIs/prompts.
- The uploaded prompt requested this full preservation package. It requires a human-readable report, registers, context transfer packet, spec sheet, aggregator packet, self-audit, exported files, and an in-chat reader.
- The explicit goals were to restore/preserve old Dominium canon, assess current repository alignment, understand what the docs and code actually say/do, and identify practices to make the code portable, modular, extensible, replaceable, future-proof, and backward compatible.

## [Dominium + Domino Codex Planning and Handoff](../../_reader/by_chat/dominium_domino_codex_planning.md)

- The most important things to remember are: the project's strict architecture constraints, the Milestone-0 prompt sequence, the later shared CLI/TUI/GUI/input/render prompt sequences, the missing pack-system prompt, the unified startup policy, the unresolved repo-verification issue, and the need to treat generated prompts as plans rather than proof of implementation.
- The user then asked for a plan going forward. The assistant produced a phased plan covering specification consolidation, directory/CMake layout, dsys, dgfx, UI core, DOMINIUM_HOME metadata, launcher v0, game v0, tools, packs, retro backends, replay/networking, and documentation/examples.
- INFERENCE:** The user accepted this direction in practice, because the next request was to generate Codex prompts to implement each step fully. The user did not explicitly say, "I formally approve the Milestone-0 plan," but they proceeded to ask for prompts based on it.
- The user asked for six Codex prompts and reminded the assistant about supported numeric formats: `U8`, `I8`, `U16`, `I16`, `Q4.12`, `U32`, `I32`, `q16.16`, `Q24.8`, `u64`, `i64`, `q48.16`, and similar formats. That correction mattered because it broadened the numeric core beyond only Q16.16/Q24.8.
- The assistant then generated six long prompts:
- 1. **Prompt 1** created `SPEC_IDENTITY.md` and `SPEC_PRODUCTS.md`, documentation only.
- 2. **Prompt 2** created the canonical repo layout, CMake skeleton, core headers, and product stubs.
- 3. **Prompt 3** implemented deterministic numeric core types, fixed-point operations, RNG, and a numeric test harness.

## [Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion](../../_reader/by_chat/dominium_full_conversation.md)

- A future assistant must understand that this chat is not simply about UI. It records the architecture for how Dominium should build itself: through contracts, commands, services, providers, documents, patches, modules, packs, apps, workspaces, diagnostics, evidence, AIDE, Codex, and eventually Workbench.
- The conversation began with the user wanting a product designer/software architect/prompt engineer to help design an internal graphical UI creation tool. The immediate pain point was the Dominium Windows launcher UI: it looked mangled and flickered. The user wanted a tool that could visually design pixel-perfect UIs and broad-strokes functionality for setup, launcher, game, and tools.
- A large prompt plan followed: repo scaffolding, canonical UI IR, TLV I/O, capability system, layout engine, splitter/tabs/scroll widgets, action codegen, Phase A UI Editor, Tool Editor bootstrap, Win32 batching/flicker fixes, tests, docs, and capability tests through launcher/setup redesigns.
- The discussion then moved into AIDE. The user wanted to automate as much as possible through Codex and AIDE. We developed a task operating model: AIDE creates WorkUnits, tracks attempts, blockers, evidence, repairs, resumes, checkpoints, and promotion decisions. Codex executes bounded tasks. Development can continue with classified partials and repairable blockers; promotion to main requires evidence.
- This led to generated prompts: `STATUS-RECONCILE-02`, `AIDE-WORKFLOW-LAW-01`, `AIDE-WORKUNIT-SCHEMA-01`, `AIDE-DEV-MAIN-POLICY-01`, `AIDE-CHECKPOINT-LOOP-01`, and `AIDE-CAPABILITY-REALITY-LEDGER-01`. The user wanted to run AIDE workflow, WorkUnit schema, and dev/main policy concurrently on the same machine via separate Codex tasks.
- This prompted a provider structure: `runtime/<service>/providers/<provider>`, `contracts/provider`, `contracts/capability`, `contracts/schema/runtime/<service>`, `release/profiles`, `content/profiles`, and `external/upstream`. The plan explicitly rejected `runtime/raylib/render`, `apps/client/rendered/raylib`, `contracts/raylib`, top-level `profiles`, and top-level `labs`.
- The final part of the conversation dealt with repo status and task queue. The user pasted status reports indicating that `PRESENTATION-CONTRACT-01` completed with warnings, and then chose to generate six maintenance prompts before replanning. `FULL-GATE-LEGACY-TEST-ROUTE-01` was generated. This preservation task followed.
- The rendered GUI must be backend-agnostic. Layouts, controls, widgets, themes, styles, views, and workspaces should be modular and extensible. Themes include first-party primitive-only profiles and OEM+ mimic profiles. The GUI should be task-first, command-backed, evidence-visible, and projection-neutral.

## [Dominium Setup Architecture and Handoff](../../_reader/by_chat/dominium_setup.md)

- Near the end, the chat shifted into preservation mode. The user asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat reader version of that package. Those outputs preserved the decisions, tasks, constraints, artifacts, rejected options, and verification queue for future assistants or aggregation into a larger Project Spec Book.
- The first major input was a detailed master prompt for the **Dominium / Domino Setup & Installation System**. It said this chat was about setup, installation, packaging, distribution, and uninstallation across supported platforms. It explicitly excluded launcher UI work. The setup system was described as a deterministic deployment control plane, not a simple GUI wizard or a store/DRM mechanism.
- The assistant responded with **Phase 1: Setup Core Architecture**, proposing modules such as manifest parsing, resolution, planning, transaction execution, filesystem/path policy, installed-state, logging, and a platform interface. This was the first conceptual baseline.
- The user then asked for a "plan of plans" called **Plan S**, with subplans S-1, S-2, S-3, and so on. The assistant produced a structured setup roadmap. It covered governance, setup core architecture, manifest schema, installed-state schema, transaction engine, filesystem policy, audit logging, CLI, Windows/macOS/Linux adapters, Steam integration, distribution pipeline, side-by-side upgrades, tests, and documentation.
- At that stage, the plan was still mostly abstract and platform-oriented. It was useful because it separated the work into durable phases, but later repository changes made some of its directory assumptions obsolete.
- The user later asked where to create Visual Studio and Xcode apps after opening the repo as a folder. The assistant advised that Visual Studio and Xcode projects should be generated through CMake, not hand-authored or treated as authoritative source files. This decision became consistent with later Codex prompts.
- The user then gave a strict system-role prompt saying the repository had undergone a major structural refactor and that the filesystem was now canonical ground truth. This superseded earlier structures. The locked top-level products became:
- This became a decisive turning point. Earlier `setup/adapters`, `setup/packaging`, and `core/source` structures became historical and superseded. The assistant amended Plan S to match the new canonical structure and later produced an authoritative Phase 2 directory tree under that model.

## [Domino Dominium Workbench](../../_reader/by_chat/domino_dominium_workbench.md)

- The second central decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless automation must be **projections of the same command/result/refusal/document/view spine**. A GUI button, a TUI hotkey, a CLI command, a headless JSON job, and a future OS-native widget action should route through the same command/service path and produce the same typed result, diagnostics, refusals, logs, and evidence.
- The resulting old plan included canonical UI IR, deterministic TLV output, JSON mirrors, safe atomic saves, stable IDs, capability validation, layout engines, splitter/tabs/scroll widgets, action stubs, event dispatch, UI Editor GUI, Tool Editor bootstrap, import/export, CLI scripting, `ops.json`, and tests. Many Codex prompts were generated around those ideas.
- The plan was then extended so the UI Editor could import existing tool UIs, provide a CLI suitable for Codex automation, and use scripted `ops.json` changes to create logical "Minecraft-style" launcher and setup layouts. The user clarified that "Minecraft-style" referred to layout and flow, not visual skin. All controls were to remain native Win32 controls in that earlier phase.
- That phase generated more Codex prompts: UI discovery/import/export, CLI validate/format/codegen, `ops.json` editing, launcher UI generation, setup UI generation, and hardening/CI. These are now **historical/superseded** but still useful as implementation material for future document/patch/CLI authoring workflows.
- Reason:** The old plan risked becoming a separate one-off tool architecture. Workbench can instead prove and reuse the same systems as the client, launcher, setup, server, and future tools.
- The renderer does not know what a Validation Dashboard, Pack Browser, Windows XP theme, or Workbench module is. This keeps the renderer reusable by client, setup, launcher, server admin surfaces, Workbench, and future games.
- 7. Use validation dashboard to monitor future work.
- 1. Multiple old UI Editor Codex prompts and prompt plans.

## [Dominium/Domino Engine Refactor Planning](../../_reader/by_chat/domino_engine_refactor_prompts.md)

- The chat then produced a maximum-fidelity context transfer packet and later a downloadable report package. Those are artifacts of preservation, but the substance of the chat is the architecture itself: a deterministic, modular, data-driven engine plan that can scale from plants and wildlife to cities, power grids, spacecraft, fog of war, and future DLCs without violating strict determinism.
- 4. deltas are applied later in a deterministic commit phase.
- The answer also introduced incremental compilation from edit buffers into derived artifacts: occupancy, ports, connectivity, enclosures, surfaces, supports, nav hints, and boundary lists. This later became a key part of the TRANS/STRUCT/DECOR prompt plan.
- The user introduced future **Interstellar** and **Wargames** DLCs. This could have led to hardcoded space and combat systems, but the answer deliberately generalized the requirements.
- The answer produced a delta plan showing what was already satisfied and what needed to be added. Then the user asked for the full new prompt plan.
- The assistant produced a full prompt plan for Codex. The user then requested each prompt one by one with "Next." Fourteen prompts were generated:
- The user then asked for a documentation validation prompt to ensure the docs remain valid, consistent, and correct. That prompt was generated as well.
- After the architecture and prompts were created, the user asked for a maximum-fidelity context transfer packet. The assistant produced one. The user then asked for a downloadable report package; the assistant generated package files and a ZIP. The user later asked for an in-chat reader version of that package, and finally requested this current human-readable explanatory report.

## [Domino/Dominium Engine Baseline, Architecture, and Feasibility](../../_reader/by_chat/engine_baseline_architecture.md)

- The uploaded preservation prompt requires a maximum-fidelity human-readable handoff, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That prompt itself is an artifact of this chat and should be preserved. Source: ?filecite?turn44file0?
- The conclusion changed: the project already had more infrastructure than the generic future plan assumed. The recommendation shifted from "invent the architecture" to "converge the architecture." The answer proposed that Dominium should become a **contract-compiled simulation platform**: contracts -> registries -> compiled locks -> capabilities -> Work IR -> deterministic runtime -> proof/replay -> product shells.
- The final user action uploaded `Pasted text.txt`, a detailed instruction prompt requiring a full preservation report, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That request is the current task.
- The central architecture distinction was that Domino should be a reusable deterministic simulation substrate, while Dominium should be one game/product layer built on it. This came up immediately when the user asked for a total description of the project. It mattered because the user wants the code to be reusable for future games and possibly other engine projects.
- The conversation repeatedly returned to determinism. The project's value depends on identical inputs producing identical outputs, replay equivalence, stable commit ordering, named RNG streams, explicit Work IR/Access IR, and no hidden global scans. The assistant inspected execution model docs and source files such as task graph, access set, scheduler, and work queue.
- The conclusion was that future work should build active-set runtime, capsule/refinement contracts, compatibility edition matrix, golden replay corpus, and toolchain-first authoring. Later, after reading live repo docs, this plan was tightened into "contract-compiled simulation platform."
- This connects to future work because a construction/destruction game cannot rely on one universal representation. Different domains need different data structures.
- how to make the engine portable, modular, reusable, and future-proof;

## [Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff](../../_reader/by_chat/foundation_workbench_codex.md)

- The topic came up because the project needed a model that could support world simulation, modding, tooling, Workbench, release, portability, and future games without repeating endless refactors. The conclusion was that stable contracts and semantic IDs must be separated from replaceable private implementation.
- Workbench is a future product surface, not the center of authority. The user wants to get to Workbench and code soon, but Workbench must route through commands/services/views/evidence rather than private direct mutation. The first Workbench slice was narrow validation. The next needed bridge is command-result-view projection.
- The user wanted to run many autonomous tasks concurrently. The assistant designed branch/worktree isolation and strict parallel-worker rules. Workers do not push to main, do not update global latest AIDE files, and produce task-local evidence. Coordinator merges serially and runs fast strict.
- This topic matters operationally because the user wants speed. The new chat should be ready to generate more parallel prompts or a coordinator review prompt depending on current repo state.
- This matters for the eventual master Project Spec Book and future domain feature work.
- to make the repository tidy and future-proof,
- minimize future architectural reversals;
- make Codex prompts operational rather than theoretical;

## [Domino Framework and Open-Source Provider Architecture](../../_reader/by_chat/framework_open_source_provider.md)

- Finally, the user uploaded a detailed preservation prompt and requested a maximum-fidelity report, registers, spec sheet, aggregator packet, audit, and downloadable files. This package is the response to that request.
- Future work should convert this into a dependency policy: use permissive/weak-copyleft libraries as providers where appropriate; use GPL/proprietary/unclear projects as research references unless explicitly quarantined; require provider manifests, license manifests, and conformance tests.
- The user appears to want a long-lived, auditable project spec that can survive chat transitions and aggregation. The preservation prompt confirms this.
- The user appears to want architecture that remains portable across older desktop systems and future render/platform providers. This was inferred from the platform floor and repeated concern with portability/modularity/extensibility.
- The user requires source-grounded, audit-ready, uncertainty-labelled responses. The preservation prompt explicitly requires FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT labels, no invented facts, no treating brainstorms as decisions, and no over-compression. The prompt also requires a human-readable report first and downloadable files if possible ?filecite?turn29file0?.
- The user prefers modular architecture over monolithic engine forks. The user prefers long-term portability, extensibility, and replaceability. The user cares about preserving reasoning and rejected options for future aggregation.
- The main uploaded artifact is `Pasted text.txt`, containing the preservation task prompt and output requirements ?filecite?turn29file0?. Before this task, no generated report/ZIP package was visible in this chat. This response creates the requested package.
- A future assistant might incorrectly say "we decided to use raylib as the engine." The correct statement is that raylib is a first visible provider suite. Another common mistake would be to treat every assistant proposal as a user decision. Several items are recommended directions, not implemented decisions.

## [Dominium Content and GUI Rebuild Planning](../../_reader/by_chat/gui_binary_content.md)

- The conversation opened with a large prompt titled **"PROMPT CONTENT0 - CANONICAL GAME CONTENT & DATA POPULATION."** The target was GPT-5.2 Codex, and the scope was explicitly limited to **data, schema extensions, and documentation**. The user framed the assistant as continuing the Dominium / Domino project, but only at the content layer.
- An assistant responded by turning the prompt into a cleaner, more formal Codex-ready version. That output was useful, but it was premature relative to the user's actual desired process.
- The user then said: **"First, let's discuss this before we plan or generate any prompts."
- That was an important change of direction. It meant the assistant's polished prompt should not be treated as final. The work needed conceptual discussion first. The assistant then analyzed CONTENT0 and identified several issues that could cause bad assumptions to become embedded if Codex acted too soon.
- This stage established a pattern that continues throughout the chat: the user does not want impressive-looking prompts that hide unresolved design choices. The user wants the assumptions exposed before anything is formalized.
- The user then described a larger goal: at the end of an "optimally large macro prompt plan," they wanted a **full universe** defined efficiently with minimal storage and memory. This universe system should work across a spectrum:
- This was the most important decision in the GUI part of the chat. It changed the task from "can we make cross-platform GUIs?" to "how do we design a full multi-platform GUI and binary matrix without losing backend consistency?"
- SwiftUI for 64-bit Intel and ARM future launcher and server, with graceful degradation to macOS 11.0.

## [Dominium Language, Platform, and Architecture Baseline](../../_reader/by_chat/language_platform_architecture.md)

- The user then consolidated a broad future plan around Domino, Dominium, Workbench, AIDE, contracts, tests, replay, and evidence. The answer agreed that the plan was strong, but identified missing central pieces: composition resolver, lockfiles, compatibility corpus, trust/permissions, virtual filesystem roots, performance budgets, and stable public-surface promotion rules.
- The chat repeatedly compared C89, C99, C11/C17, C23, C++98, C++11, C++17, and newer C++ standards. The final working direction is C17 + C++17 for the mainline. C99 and C++11 were considered but not adopted as the project-wide baseline. Newer C23/C++20/C++23/C++26 were treated as future provider/tool lanes, not current mainline law.
- The project must retain a C-compatible ABI. The public boundary should remain POD-only, versioned, return-code/refusal based, and free of exceptions, STL containers, classes, templates, allocator ownership, and C++ ABI assumptions. This allows providers, plugins, tools, projections, and future bindings to survive implementation changes.
- The deterministic simulation law remains more important than the language standard. Authoritative simulation must use stable IDs, canonical ordering, fixed-width values, fixed-point math, explicit little-endian encoding, and deterministic scheduler phases. Threads may accelerate derived work, but final authoritative commit must be canonical and not depend on OS timing or thread completion.
- Support Windows 7, macOS Mavericks, Linux, and possibly older/future systems.
- Keep future assistants from repeating rejected advice such as pure C99 or pure C++11.
- Prepare material for a future Project Spec Book.
- The goal changed from "should old C/C++ standards be upgraded?" to "what is the full future architecture baseline?" The user initially entertained C89/C++98 staging, then accepted C17/C++17 as mainline. The user also moved from "maybe support old systems directly" to "support old systems through constrained/projection/archive lanes."

## [Dominium Launcher Application-Layer Handoff](../../_reader/by_chat/launcher_app_layer.md)

- Someone reading this report should understand one central thing: this chat is not about inventing new launcher features anymore. It is about preserving boundaries, making the launcher implementation explicit, and ensuring future work happens on top of verified code rather than vague architectural memory.
- The user started by asking whether the latest system, after Plan 8, could support a common launcher for all operating systems with one shared codebase, native OS elements, and minimal rendering. The user attached several screenshots of older Minecraft launchers as visual examples and referenced a Plan 8 prompt file and a repo archive.
- The user then asked how to make the entire system more modular and extensible, especially with existing systems, mods, and packs. The answer proposed a data-first approach: facades, registries, versioned contracts, TLV/schema-based manifests, declarative settings, pack tasks, and rare executable plugins only when unavoidable.
- This phase mattered because it framed the launcher not as a menu program but as a **control plane** for installed products, packs, profiles, compatibility, and launch contracts. However, later canon tightened the permitted communication routes: cross-product communication must go through `schema/` and `libs/contracts`, not arbitrary plugin conventions.
- The response executed Phase 1 of that prompt and described the launcher core as a deterministic control-plane library. This included modules like manifest parsing, discovery, catalog building, profile policy, integrity checks, resolution, launch planning, execution, and audit logging. It also defined host service vtables, opaque handles, deterministic ordering rules, error models, and safety assumptions.
- That Phase 1 answer remains useful, but only after being rebased into the later canonical repo structure.
- This later became one of the clearest examples of a superseded path. The user subsequently pasted applied Codex prompts that explicitly required CMake to generate the Visual Studio solution/projects and stated that hand-written `.vcxproj` files must not be the authoritative build. Therefore, all earlier "manual IDE projects as canonical" advice is no longer current.
- Later, the user objected that `source` subdirectories inside top-level source directories felt counterintuitive and asked about future tools and components beyond launcher, setup, and game. This led to the product-first model: top-level directories should represent long-lived products, not layers.

## [Dominium Launcher and Setup Architecture](../../_reader/by_chat/launcher_setup_architecture.md)

- The chat also produced multiple Codex work-order prompts and finally a downloadable report package. Those artifacts are useful, but the substance is the architecture: keep engine deterministic, keep setup/launcher/runtime boundaries explicit, make the launcher optional and modular, use a strong process/instance model, and now implement the launcher over dsys/dgfx rather than ad hoc platform UI stacks.
- The user asked how many prompts would be needed for Codex to implement the system. The assistant recommended four main prompts:
- An optional fifth prompt was suggested for runtime CLI/capabilities. The user then asked for the prompts one by one, and the assistant generated them. These prompts were detailed and implementation-oriented, but they reflected the earlier C++98/shared-library approach.
- This is the most important change of direction in the chat. Earlier prompts remain useful historical material, but the latest launcher implementation direction is dsys/dgfx.
- This came up because the user wanted Codex and future implementation work to avoid hidden coupling and future incompatibilities. The assistant expanded the idea into repo layout, file format patterns, CLI contracts, plugin ABIs, and migration/testing expectations.
- Uncertainty:** Accounts/social/wiki/forum/direct messaging are future-facing and were not converted into the final five-tab implementation plan.
- This was the late major shift. The user provided a detailed new prompt stating that all dsys and dgfx backends exist and that the launcher should use them.
- INFERENCE:** The user wanted a future-proof architecture that Codex could implement in stages without repeatedly re-deciding the system design.

## [Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture](../../_reader/by_chat/modularity_aide_refactorability.md)

- The final user action was uploading a preservation-package prompt. That prompt requested a maximum-fidelity preservation report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, downloadable files, and a final in-chat reader. This package is the result.
- The user objected to the XStack/AuditX/RepoX/TestX framing and wanted AIDE adopted quickly. The resulting plan made AIDE the repo-native control plane for inventory, task queues, policies, move maps, salvage maps, evidence ledgers, validation, and refactor history. Existing tools should be recycled, not discarded. This is central to future refactorability.
- The uploaded prompt converted the conversation into a preservation task. It requires a human-readable report first, then registers, spec sheet, aggregator packet, self-audit, and downloadable files. This final package is intended to be merged later with old-chat reports into a master Project Spec Book.
- The conversation implies a goal of turning Dominium into a long-lived product-line platform rather than a single-game repository. It also implies a desire for auditability: decisions should be grounded, visible, mechanically enforceable, and later aggregatable into a master spec. The user appears to value stable boundaries, explicit compatibility policy, and practical Codex/AIDE tasks.
- The live repo still needs verification. The exact AIDE files, contracts, validators, and migration tasks must be implemented. It remains unresolved which existing roots and tools map to which final homes, which APIs become stable, which code is reusable across products/games/projects, and which prior assistant recommendations should become formal requirements after user review.
- 1. **TASK-09** - Verify live repo baseline: current branch, root inventory, validators, CTest status, generated artifacts.
- 2. **TASK-01** - Implement AIDE-STRUCTURE-00: root constitution, ownership slots, AIDE refactor framework, move/salvage map schemas, inventory tooling.
- 3. **TASK-03** - Inventory old XStack/AuditX/RepoX/TestX-style tools and classify them.

## [Dominium Omega/Xi/Pi Architecture & Future-Proofing Planning](../../_reader/by_chat/omega_xi_pi_architecture_future.md)

- After Xi, the assistant planned Pi-series as a meta-blueprint: architecture diagrams, dependency maps, capability ladders, readiness matrices, prompt inventories, and snapshot mapping templates. The user reported Pi-0/Pi-1/Pi-2 were completed and restarted from Xi-8 ground truth, with fingerprints and prompt counts.
- The final strategic direction before this preservation request was to run a ?-series: snapshot intake, reality extraction, blueprint reconciliation, foundation readiness, and final prompt synthesis. This is needed because plans must now be mapped onto current repo reality rather than executed abstractly. The next chat should pick up there.
- The conclusion was that all products should boot through AppShell, use shared command registries, expose descriptors, validate packs/contracts before session start, and never have ad hoc boot paths. This matters for portability, setup/launcher integration, and future distribution.
- The user later reported Xi completion. The enduring lesson is that prompt instructions are not enough; architecture must be machine-readable and enforced.
- The user wanted agent support to work across vendors. The answer was to define a canonical vendor-neutral layer and generate vendor-specific mirrors. Canonical files include AGENTS.md, `.agentignore`, `data/agents/agent_context.json`, and `docs/agents/AGENT_TASKS.md`; mirrors may include Copilot instructions, Claude agent files, Codex skills/MCP wrappers. XStack, not agent prose, enforces truth.
- 4. Preserve all plans, tasks, constraints, risks, decisions, artifacts, and future directions across chats.
- 7. Support future live operations such as hot-swappable renderers and live mod activation, but only after foundations.
- 3. Make the repo robust to future tool/vendor changes.

## [Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer](../../_reader/by_chat/os_interface_repo_architecture.md)

- The central tradeoff was between short-term visible functionality and long-term architectural leverage. The user repeatedly asked whether the plan could be more modular, future-proof, optimized, robust, reliable, useful, and powerful. The answer consistently favored building shared contracts and proof paths before expanding product surfaces.
- This preservation task specifically required FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels, stable IDs, registers, spec sheets, an aggregator packet, self-audit, and downloadable files if tools are available.
- Future facts involving platforms, software support, toolchains, APIs, laws, schedules, prices, current roles, etc. require verification.
- INFERENCE: The user wants future assistants to preserve reasoning and not collapse tentative ideas into final decisions.
- 1. **Uploaded `Pasted text.txt`.** Contains the preservation/export prompt that generated this package.
- 2. **Repo docs inspected during chat.** Key examples: AppShell constitution, GUI baseline, repo layout target, ownership rules, domain split rules, final convergence audit, post-CONVERGE next steps, versioning/distribution docs, code/data report, modularity proof, product boot proof.
- 4. **Conceptual artifacts produced in chat.** These include proposed architectures, matrices, lane plans, Workbench modules, Interface Operating Layer, boot-to-replay MVP, and structured roadmaps.
- 5. **This preservation package.** Newly generated files and ZIP at the end of this task.

## [Dominium Codex Platform Renderer API Plan](../../_reader/by_chat/platform_renderer_api_plan.md)

- Later, the user expanded the horizon: Dominium should start with simple early graphics and audio, but eventually support AAA-quality graphics, spatial audio, environmental acoustics, proximity chat, AI, navigation, terrain, vehicles, economy, combat, weather, modding, tools, and launcher/setup systems. Those ideas were preserved as a **future roadmap**, not current implementation scope.
- The chat ended by generating a maximum-fidelity transfer packet, then a downloadable report package, then an in-chat reader version. The main thing to remember is this: **the active artifact is the final 9-prompt post-master Codex plan, but it is a plan, not evidence that the code exists. The repo must be inspected before execution.
- The user opened with a precise role assignment: the assistant was to act as a staff software architect, technical program manager, and prompt engineer. The task was to generate **ready-to-run prompts** for Codex CLI running GPT-5.2 so that Codex could implement missing or unfinished platforms, renderers, and APIs in the existing Dominium repository.
- The first procedural rule was that the assistant had to ask a **minimal but complete questionnaire** before generating the prompt pack. The questionnaire had to cover platforms, renderers, APIs, definition of done, and repo/build context. The assistant did that.
- This is not a fatal problem for the prompt pack, because the prompts themselves repeatedly tell Codex to discover files with `rg`, `tree`, `type`, CMake commands, and target listing. But it is a major caveat for any future assistant: do not assume the actual repo matches every file path or API name unless checked.
- After the archive upload, an initial prompt plan was generated for platform and renderer work. It covered CMake platform/backend selection, Win32 and POSIX system backends, X11/Wayland/Cocoa gating, software/DX9/DX11/GL2/Metal/Vulkan renderers, sockets/dynlib, and integration. That plan was useful but did not remain active.
- The user then said they already had a set of pending prompts and pasted a **MASTER CODEX PROMPT PLAN**. This changed the sequence. The assistant was no longer planning from scratch; it had to generate a new plan that assumed this prior master plan had already been implemented.
- The user's master prompt plan was extensive. It covered deterministic simulation and engine-core architecture: invariants, packet ABI, scheduler, fields/events/messages, LOD, pose and anchors, TRANS corridors, STRUCT buildings and enclosures, DECOR signage and surface detail, agents/sensors/minds/actions, graph toolkit, domains/frames/propagators, knowledge/fog/visibility/comms, and determinism hardening.

## [Dominium Platform Support Planning](../../_reader/by_chat/platform_support.md)

- UNCERTAIN / UNVERIFIED: The name "Domino" was never confirmed by the user. Future work should treat "Domino" as an assistant-created placeholder unless the user explicitly accepts it. The useful idea is the distinction between full product support and reduced engine/core support, not necessarily the name.
- FACT: The user explicitly decided that PC is the first primary focus and that Android, iOS, and Web are also primary top-tier support. This means future work should treat these platforms as architectural roots. They are not optional ports.
- This topic connects directly to future work because the next major deliverable should be a **Platform Support Matrix** and then **Platform Contracts** for each major target.
- UNCERTAIN / UNVERIFIED: The chat did not establish minimum Android API level, ABI list, target graphics APIs, Play Store rules, Android TV status, Android Go status, Automotive status, Chromebook status, or vendor ROM support. These need future decisions and current-source verification.
- UNCERTAIN / UNVERIFIED: Current console platform facts were not verified in this chat. Future work must verify official PlayStation, Xbox, and Nintendo developer requirements from current official sources before implementation planning.
- UNCERTAIN / UNVERIFIED: XR was never promoted to top-tier. Its priority remains unresolved. Future work should not let XR quietly expand the scope of the main product unless the user explicitly elevates it.
- The latter part of the chat created a Context Transfer Packet and then a downloadable package containing reports, registers, YAML, an aggregator packet, an audit, a manifest, and a ZIP. The user then asked to read the package in-chat. That package is useful because it preserved IDs and future aggregation material.
- This current report should not be about those files, but they are artifacts of the chat. Their purpose was continuity: to allow another assistant or future aggregation process to reconstruct this chat without re-reading everything.

## [Domino/Dominium Portability, Assurance, and Future-Proof Architecture](../../_reader/by_chat/portability_assurance_future_proof.md)

- Limitations: this package preserves visible current-chat context and the uploaded preservation prompt. It does not prove that hidden transcript segments, other conversations, repository files, or older generated artifacts were accessible. Broader project context is not treated as current-chat fact unless labelled.
- The user then clarified that the real concern was broader: all code should be portable, modular, extensible, reusable, replaceable, and future-proof. This shifted the conversation from standards to the whole structure of the engine/product ecosystem.
- The user then uploaded a maximum-fidelity preservation prompt. The task became preserving this chat into a package suitable for human reading and future aggregation. This response is that package.
- A target tree was proposed: include/, contracts/, source/domino/, source/dominium/, tests/conformance/, tests/migration/, tests/fuzz/, tools/validators/, docs/architecture/, docs/assurance/. This is a candidate, not a repo-verified plan.
- Conformance tests prove replaceability. High-trust paths need valid, invalid, malformed, old-version, future-version, migration, roundtrip, determinism, and negative-permission tests.
- The uploaded prompt required this preservation report, registers, spec sheet, aggregator packet, audit, files, and ZIP.
- The user wanted to know whether standards can be used wisely for Domino/Dominium. The user also explicitly wanted portability, modularity, extensibility, reuse, replaceability, proper-game/OS-grade structure, better directories, better names, better APIs, better schemas, and future-proof/backward-compatible design. The uploaded prompt explicitly requested a maximum-fidelity preservation package.
- The user likely wants these outputs to feed a future master Project Spec Book and prevent long-chat context loss.

## [Dominium README Architecture, Ports, and Determinism](../../_reader/by_chat/readme_ports_determinism.md)

- The user then asked for a prompt they could give to Codex. A detailed patch prompt was produced. It instructed Codex to apply minimal edits to the existing README without changing headings, section order, or tone.
- That prompt asked Codex to:
- The user pasted Codex's output after the port prompt. The output correctly added the unified-source and metadata-only port language, but it also introduced a duplicated top section: two overlapping "This repository includes" blocks. The assistant identified that duplication and produced a cleanup prompt.
- That cleanup prompt instructed Codex to remove the redundant block, remove undefined "embedded" from the future systems list, replace vague "lockstep/rollback" wording with lockstep-first canonical networking language, and update the contributing determinism bullet to refer back to Section 2.1 instead of maintaining a separate formulation.
- After the README work, the user asked for a maximum-fidelity context transfer packet. The assistant produced a long state-transfer document with sections for project inventory, decisions, tasks, constraints, open questions, artifacts, risks, and next actions.
- What remains uncertain is whether the actual repository `README.md` matches the final pasted version. The chat only saw pasted text and generated prompts; it did not inspect a Git repository.
- The project's core promise is deterministic simulation. The README already required fixed-point arithmetic and deterministic tick phases, but the chat refined the boundary of that determinism.
- The chat also strengthened RNG discipline. RNG streams can only advance during deterministic tick phases. Debug overlays, UI, rendering, and other non-simulation layers must not advance engine RNG streams.

## [Dominium + Domino Refactor Architecture](../../_reader/by_chat/refactor_architecture.md)

- This chat was mainly about turning the Dominium + Domino project from a collection of partially overlapping architecture ideas into a coherent, refactorable, future-proof structure that could be implemented by Codex and then preserved for future ChatGPT conversations.
- The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.
- The user opened with a long "new thread" prompt framing this as the **Graphics / UI / UX / Packs Architecture Thread** for Dominium + Domino. The explicit scope was visual and audio presentation: rendering architecture, UI framework, graphics packs, sound packs, music packs, theming, skinning, pack composition, overrides, fallbacks, and how all of that should map onto existing `dsys` and `dgfx`.
- FACT:** This early discussion created the future UI/packs design context.
- The assistant then produced a master Codex refactor prompt that instructed Codex how to move files, add compat/platform headers, add product metadata and `--introspect-json`, unify Game modes, implement DOMINIUM_HOME, actions, setup import/GC, packaging naming, and docs updates.
- The user asked what Codex still did not know. The assistant audited missing topics. Then the user asked for phases from scratch; the assistant produced a phased roadmap. Then the user asked whether all phases could be merged into one big prompt; the assistant generated a larger combined refactoring prompt. Then the user requested a post-refactor consistency prompt; the assistant produced one.
- The user then shifted from architecture implementation to preservation. They asked for prompts that would cause Codex to generate starter prompts for future ChatGPT conversations, including an extended master starter prompt. Finally, they asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat readable version of that package.
- The final phase of the chat was therefore about preserving and explaining the architecture so it could be used later without rereading the entire conversation.

## [AIDE, XStack, and Dominium Refactor Control Plane](../../_reader/by_chat/refactor_control_plane.md)

- The chat opened with the user describing a workflow: paying for Codex Pro, using the Codex VS Code extension on one project at a time, and using ChatGPT project spaces to generate prompts that were manually fed into Codex. The user had also installed the ChatGPT and Codex apps and Visual Studio Community. The initial question was whether there was a better, more professional, more integrated way to develop projects.
- The user then asked about optimizing prompts for GPT-5.3/GPT-5.4 and later supplied advice about harness engineering. That advice argued that teams succeed by engineering the environment around agents: tools, docs, linters, feedback loops, memory, and observability. The conversation accepted the core point: the model is not the whole system; the harness is the multiplier.
- The discussion then mapped these ideas onto Dominium's XStack. We considered adding HarnessX, XPlan, XExec, MergeX, ContextX, SkillX, TaskX, BridgeX, SessionX, PermitX, DoctorX, TraceX, and more. Over time this became too many public concepts. We simplified toward higher-level planes and then eventually concluded that XStack should not be the general product at all.
- The user supplied AIDE advice around dev branches, structured commits, and WorkUnit recovery. The accepted model is `main` as canonical truth, `dev` as governed integration, `task/*` as bounded work, and release/hotfix branches as needed. AIDE should enforce commit trailers, branch roles, safe sync/land/promote/prune, and repo-state-first recovery when prompts are repeated or out of order.
- The user explicitly wanted to improve AI-assisted development, design a better harness, decide XStack's role, create AIDE, align Dominium cleanup with AIDE, use AIDE in Dominium safely, and generate a complete preservation package. These goals mattered because the user is managing long-running complex projects and wants future chats, Codex sessions, and repos to stop losing context or repeating mistakes.
- AIDE changed most. It began as a possible full development environment and became a portable repo operating layer. XStack changed from a candidate universal system to a Dominium strict profile. Repo cleanup changed from moving folders to root recycling under AIDE. AI workflow changed from prompt optimization to harness engineering.
- Several decisions are strategic rather than fully implemented. The version/capability model, Git workflow model, install/repair/upgrade model, and tool absorption model are accepted directions but require schemas and code. Future assistants must not mistake them for already completed implementations.
- The user values direct, source-grounded, audit-ready, detailed answers. The user asked for preservation packages that are human-readable and machine-aggregatable. The user repeatedly prefers not to lose nuance, rejected options, uncertainties, or artifacts. The user wants current facts verified when possible and wants future assistants to avoid re-asking answered questions.

## [Dominium XStack Release Identity and Versioning](../../_reader/by_chat/release_identity_and_versioning.md)

- The chat rebuilt SemVer from first principles and decided that strict SemVer should apply only to components with declared public contracts. Candidate true-SemVer entities include SDKs, engine libraries, tool APIs/CLIs, protocol libraries, plugin hosts, schema libraries, and reusable runtime libraries. It remains unresolved which exact repo modules qualify.
- The user explicitly wanted a versioning/release identity policy that would not need to change halfway through. They wanted to avoid SemVer stagnation, arbitrary major bumps, and product-history confusion. Later, the user wanted the conversation reconstructed into a knowledge base and preservation package for future aggregation.
- These rejected or superseded options matter because future assistants may otherwise reintroduce them. The biggest trap is suggesting "just use SemVer everywhere." That was explicitly narrowed. Another trap is treating `stable` or `hotfix` as prerelease suffixes even after SemVer ordering was explained.
- The immediate future work is to convert this design into formal repo/spec artifacts. Recommended order:
- The user values long-term maintainability over short-term prettiness. They prefer explicit metadata over hidden inference. They want future assistants to preserve tentative status and not silently turn brainstorms into decisions.
- This preservation task creates the first actual downloadable package in this chat. Prior artifacts were primarily in-chat examples, summaries, and proposed spec fragments.
- The highest-risk misunderstanding is collapsing the layered model back into one universal version scheme. Future assistants should classify the entity first, then apply the correct policy.

## [Dominium TestX/RepoX Governance and Handoff Chat](../../_reader/by_chat/testx_repox_governance.md)

- That was the initial design phase. At that point, the build-number idea was still broad and aggressive: a global build number incrementing frequently.
- The user had another chat working on content and systems, and asked for a prompt to inform that chat of everything decided so far. A similar prompt was generated for the applications/platforms/renderers chat. These prompts established authoritative boundaries:
- The next major shift came when the user pasted an authoritative prompt called **TESTX** from "The Game chat." TESTX was a major governance layer: permanent verification, versioning, self-defending tests, deterministic execution, repository survey, test taxonomy, assertion tiers, comment density, blocker tracking, and changelog governance.
- This chat then generated new prompts, `EG-TESTX` and `AP-TESTX`, to send to engine/game/content and application/platform/render teams. Those prompts required response prompts from those teams. The user pasted back their responses. Both accepted TESTX canon and identified tensions.
- This chat endorsed that approach and suggested making control systems capability-gated, disabled by default, and subject to a non-interference invariant. The user then asked for a sequel mega-prompt, and **TESTX2** was generated. TESTX2 formalized:
- This mattered because the user wanted future support for such systems without enabling them by default or compromising core principles.
- Based on the tree, the response concluded that the repo already had many ingredients: UI IR/codegen, setup/launcher tooling, tests, validation scripts, platform layers, packaging, and legacy/orphaned directories. What it lacked was an explicit projection layer and enforcement model. The proposed REPOX prompt introduced:
- The user then supplied a detailed matrix for Windows, Mac, and Linux, including language modes and old/new architecture goals. REPOX was generated as a mega-prompt.

## [Dominium Timekeeping and 2038 Resilience](../../_reader/by_chat/timekeeping_and_2038_resilience.md)

- The preservation task at the end changes the purpose of the chat from discussion to archive. The user uploaded a detailed preservation prompt requiring a human-readable report, structured registers, a context-transfer packet, a YAML-style spec sheet, an aggregator packet, audit sections, and downloadable files. This report is therefore both a reader-friendly reconstruction and a future-spec handoff.
- A future assistant should understand that this chat contributes a time architecture doctrine for Dominium: **ACT is authority; DSYS time is runtime-only; observer clocks are derived; civil/astronomical time is projection-only; wall-clock time must never drive authoritative ordering.
- The user then asked for the "most compatible" combination of timekeeping for cross-platform software architecture, including past and future target machines. The assistant answered with a layered model: absolute instant, duration, monotonic elapsed time, and civil/local time. This was the main conceptual upgrade of the chat. It broadened the issue from integer width to semantic separation.
- The user then uploaded a detailed prompt requiring this preservation package. The task became a maximum-fidelity archive and handoff for the current chat.
- The user should remember that unsigned 32-bit is not a future-proof absolute timestamp format. It only delays the overflow.
- The major future work is not to invent the model from scratch, but to harden boundaries and serialization.
- The final topic is this export task. The user requested a human-readable report first, followed by registers, spec prep, context-transfer packet, aggregator packet, self-audit, and files. This package is designed to let the chat be read later without reopening the full transcript and to support merger into a larger Dominium spec book.
- The user appears to be trying to prevent long-term architecture mistakes in Dominium and related C/C++ software. The user values deterministic simulation, legacy compatibility, future-proof serialization, and avoiding subtle date/time bugs that would require painful migrations later.

## [Dominium UE6, Domino, and Deterministic Universe Feasibility](../../_reader/by_chat/ue6_domino_deterministic_universe.md)

- FACT: This package preserves the currently visible chat about whether Dominium should use UE6, UE5, Domino, Unreal, or a custom engine layer for a highly ambitious deterministic solar-system-scale game. It also preserves the current uploaded prompt as an artifact because it defines this preservation task.
- For a future assistant or human reader, the key thing to understand is that the chat did not reject Unreal. It rejected the idea that Unreal or UE6 could be the complete solution. The direction is hybrid: custom simulation and backend as the real engine, Unreal as the first high-quality client, UE6 as a possible future upgrade, and Domino as a possible later frontend/runtime if the core remains portable.
- The answer then proposed the architecture that became the main deliverable of the chat: `DominiumSim`, `DominiumWorldDB`, `DominiumServer`, `DominiumClient_UE`, and `DominiumClient_Domino`. This architecture makes the core simulation, world storage, and server authority independent from the renderer. Unreal becomes an adapter, not the source of truth. Domino becomes a future adapter if the project requires it.
- The first topic was whether Dominium should be made on UE6 instead of Domino. The answer separated availability from suitability. UE6 was treated as not yet available enough for production planning. UE5 was treated as a practical near-term renderer/tooling base. Domino was treated as a possible future runtime or custom engine path, not something that can be reached by automatically exporting an Unreal project.
- Uncertainty: public UE6 technical capabilities and requirements remain time-sensitive and need verification before any future hard commitment.
- The assistant recommended against starting directly on UE6 because public technical access and production documentation were not treated as available in the visible chat. This was not framed as a permanent rejection of UE6. It was a timing decision: do not wait for a future engine to solve current architecture problems.
- This is the highest-value decision candidate. Core rules, simulation, save format, economy, factory logic, fog-of-war state, and replay/hash systems should be portable. This matters because Domino portability is only plausible if the core does not depend on Unreal object lifecycles and assets.
- The chat recommended making Domino a future adapter target. Portability comes from architecture, not from a future conversion button.

## [Dominium UI Editor and Tool Editor Planning](../../_reader/by_chat/ui_editor_tool_editor_planning.md)

- The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.
- Once the architecture was clear, the user asked for a prompt plan that could implement everything in fewer than a dozen Codex prompts. The assistant created an 11-prompt implementation sequence:
- The user then asked "Next" repeatedly, and the assistant generated each of those prompts in detail. These prompts are important artifacts, but they are not evidence that implementation occurred.
- This led to a second prompt plan: UU1 through UU6. These prompts extended the UI Editor with discovery/import/export, CLI modes, `ops.json` scripted editing, launcher UI generation, setup UI generation, and determinism/CI hardening.
- Before the launcher/setup prompts, the user clarified that "Minecraft style" meant logical layout only, not graphical design. This was crucial. The assistant had to avoid custom styling, skins, or owner-drawn controls. The launcher and setup tests were about structure: header areas, side navigation, main content tabs, news panels, wizard steps, progress pages, footer buttons, and similar interaction flow.
- The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical layout description, and the user accepted it as useful. Future work should inspect the bundles before claiming exact screenshot fidelity.
- The final state of the conversation is therefore not "the tool is built," but "the architecture, constraints, prompt plans, and continuation state have been carefully documented."
- The discussion also identified likely flicker causes. The Win32 backend is mostly child HWND controls and does not use custom painting. Flicker likely comes from resize relayout, redraw calls, list refresh invalidation, and visibility toggles. This later led to a planned prompt for structural Win32 batching and coalesced relayout.

## [Dominium Universe Explorer Planning and Repo Handoff](../../_reader/by_chat/universe_explorer_planning.md)

- This changed the future plan from "eventually implement everything" to "first prove seamless lawful inspection/materialization at universe scale."
- The current preservation task then asked for this full chat package.
- A major theme was that useful local inventions must become portable, standardized, industrialized, and institutionally adopted. The repo now has a Formalization Chain spec and Player Desire Acceptance Map that strongly preserve this. The future work is making this playable: drafting, measuring, testing, blueprinting, certifying, teaching, manufacturing, maintaining, and revising designs.
- The final plan accepted the newer repo status: structure is clean enough to stop giant structure prompts. Remaining cleanup should be targeted: stale full-gate tests, pack layout canon, residual taxonomy, AIDE state classification, public header ABI, provider split. This is a planning recommendation, not yet an explicitly accepted user decision.
- 6. Preserve this chat in a maximal-fidelity package for future aggregation.
- 3. Ensure future assistants do not confuse repo truth with chat memory.
- 3. Whether the Universe Explorer has a formal repo task yet.
- 6. Broad structure refactor prompts: now deprioritised because current structure is clean enough with warnings.

## [Dominium Architecture, Workbench, AIDE, and Product-Spine Planning](../../_reader/by_chat/workbench_aide_product_spine.md)

- The largest uncertainty is not the conceptual architecture; that has converged. The largest uncertainty is live execution state: whether prompts generated near the end of the chat have already been run locally, committed, or pushed. The next chat should first inspect `.aide/queue/current.toml`, recent commits, and relevant audit files.
- In the later chat, the user requested a series of Codex/AIDE prompts. The assistant generated prompts for:
- The user noted that earlier prompts were hard to copy because they were not always contained in one code block, and that prompts should better handle dirty worktrees and concurrent tasks. From then on, generated prompts included detailed dirty worktree handling, allowed/forbidden paths, non-goals, validation, blocker classification, and commit/final-response formats.
- Near the end, the user wanted to run prompts in parallel on a permanent `origin/dev` and `local/dev`, then checkpoint/merge to `main`. The conversation converged on the AIDE OS model: agents should not mutate shared dev directly; each prompt should run in a task branch/worktree; AIDE integrates to dev; checkpoint branches prove waves; main receives only evidence-backed promotions.
- Remaining uncertainty: exact implementation of erosion/ecology/evolution proxies remains future domain work.
- The conversation treated epistemics and diegetics as more than flavor. They determine what must be simulated, loaded, rendered, or refined. If a player has not observed something, it can remain summarized so long as future expansion is consistent with seed, law, and causal history.
- AIDE should evolve from prompt generator into task operating system:
- The user needed copyable prompts in a single code block. Future prompts should include:

## [Dominium World Architecture](../../_reader/by_chat/world_architecture.md)

- The future relevance of this chat is high. It should feed directly into the future project spec book and into a corrected implementation prompt. But it should not be treated as final implementation detail everywhere. Many high-level decisions are settled, but solver formulas, exact file encoding details, build system integration, actual repository layout, and some numerical representations still require verification.
- Near the end, the user asked for a Codex 5.1 implementation prompt. A long prompt was produced, instructing Codex to implement the engine core, fixed-point types, world addressing, chunking, save formats, ECS, engine API, runtime CLI, and docs. Later, the context packet and final report package audited that prompt and found important defects. The prompt is useful, but not safe to use directly.
- The main unresolved issue is implementation detail. The design says Q16.16 and Q4.12, but the earlier prompt used signed types incorrectly. The future implementation must use unsigned local coordinates or a centered signed design.
- A subtle but important correction emerged later: within a Segment of `2^16m`, a Region of `2^8m` means there are 256 Regions per Segment per axis. Therefore Region-in-Segment is 8 bits, not 4 bits. Some earlier generated prompt text got this wrong and must be corrected.
- The exact solvers remain unresolved. The architecture is clear, but formulas and resolutions are still future work.
- The user wanted the same future-proof philosophy applied to the entire project. The resulting pattern was:
- A major artifact was a Codex 5.1 prompt. It was designed to tell Codex to implement the architecture in a repo. It included modules, headers, save formats, engine API, CLI runtime, and docs.
- Later audit found it defective. It should be repaired before use. The known issues are signed fixed-point types, Region bit-width inconsistency, C89-incompatible constructs, and saved rotation ambiguity. The best next practical step is to revise that prompt using the corrected report.

## [Dominium XStack and Lab Galaxy Handoff](../../_reader/by_chat/xstack_lab_galaxy.md)

- That problem drove much of the XStack discussion. The assistant and user discussed how to prevent future agents from treating old or bad prompts as literal stop conditions. This led to principles such as:
- prompts are untrusted input,
- The conversation then focused heavily on XStack. The user wanted RepoX, TestX, AuditX, ControlX, PerformX, CompatX, and SecureX to be robust, modular, extensible, and fast. The assistant helped plan or generate many prompts around this. The important architectural outcome was that XStack should behave like a compiler or incremental build system, not like a CI pipeline that reruns everything after every edit.
- Repeated gate calls from prompts needed to short-circuit or cache.
- Later, the user reported that in a new chat they had run a sequence of 13 prompts. They pasted or uploaded a transcript. That transcript became a major source for the handoff package.
- The 13 prompts reportedly implemented, in order:
- After the transcript appeared, the user asked for a maximum-fidelity Context Transfer Packet. The assistant produced one, with sections such as workstreams, decisions, tasks, constraints, open questions, risks, artifacts, and verification queue. Then the user asked to turn that into a downloadable report package. The assistant created Markdown/YAML files and a ZIP archive.
- The conclusion was that docs should be layered: README for accessibility; architecture docs for technical explanation; canon/glossary/contracts for binding doctrine. The 13-prompt transcript reports that docs/canon and many architecture/contract docs were created, but this must be verified.
