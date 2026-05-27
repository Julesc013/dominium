Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Dominium_Architecture_IV/`
Promotion Status: not_reviewed

# Dominium Architecture IV - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about turning **Dominium** from a broad game idea into a deeply planned software ecosystem. The conversation moved across engine architecture, platform abstraction, renderer abstraction, install modes, launcher design, setup packaging, tools and SDKs, game simulation architecture, construction systems, vehicles, spaceflight, planets, economy, actors, and long-term modding. The most important outcome was not a piece of code, but a coherent architectural roadmap and a large set of Codex-ready implementation prompts.

The user's underlying goal was to build **Dominium** as more than a single game executable. The desired result is an extensible ecosystem with a reusable engine, a launcher, setup tools, editors, mod/pack SDKs, game creation tools, and a game that can eventually support realistic surfaces, arbitrary construction, vehicles, atmospheric/hydrological/geological systems, spaceflight, AI actors, life support, markets, and politics. The chat therefore focused heavily on **foundations**: what layers should exist, what APIs should be stable, what abstractions should be shared, and what should be built first so future systems do not need constant rewrites.

A central decision was to separate the project into two conceptual layers. **Domino** is the reusable engine layer: platform abstraction, renderer abstraction, audio, UI, core services, package/instance management, simulation control, events, plugins, and low-level reusable systems. **Dominium** is the game/product layer: setup, launcher, tools, game, rules, content, and Dominium-specific systems. This separation matters because the user explicitly wants the engine to be reusable for other games and projects, not locked to Dominium alone.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, workbench, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__human_readable_chat_report.txt`.

## What Was Decided

- The reusable engine layer was named **Domino**. This became one of the most important naming and architectural decisions in the chat. Domino is the engine/core/platform/sim/mod layer, reusable for other games and projects. Dominium is the game/product layer built on it.
- Blueprints are plans or diffs: place element, remove element, modify terrain, place machine, connect network, etc. When accepted, they generate jobs. Manual player actions and queued work for humans, robots, or other agents should use the same job pipeline. This matters because it keeps replay, AI, and automation consistent.
- The user then asked how to structure Codex prompts. The final high-level roadmap became:
- The assistant generated detailed Phase 1 prompts, platform backend templates, renderer backend templates, setup prompts, launcher prompts, tools prompts, and finally a Phase 7+ roadmap for the game. The game phase itself was not expanded into the same full prompt detail as Phases 1-6. That remains a future task.
- At the end, the user shifted from architecture planning to chat retirement. The chat produced a discovery inventory, a context transfer packet, a final downloadable report package, and then an in-chat reader version. The current request asks for a human-readable narrative explanation rather than more registers or machine-oriented handoff files.
- The conclusion was clear and accepted: **Domino is the reusable engine; Dominium is the game/product layer**. What remains uncertain is the actual repository state. The chat planned the split, but did not verify whether the repo already matches it.
- The conclusion was to define UI modes separately from UI backends. This is one of the central product architecture decisions.
- The package/instance system is central to the whole ecosystem. The user wants installed versions, official base/DLC/mod content, downloaded third-party mods and packs, shared data, instance-specific overrides, and arbitrary combinations without duplicating every possible mix.
- The unresolved issue is the exact manifest/schema format. JSON, TOML, and INI-like examples appeared in prompts, but no final schema choice was made.
- This matters because the launcher is central to user workflow and mod ecosystem. It also demonstrates the broader architecture: common logic, arbitrary presentation.
- This matters because modding and content creation are central to the user's goals. The tools also serve as test cases for the architecture: if the common APIs are good, tools can inspect, edit, build, package, and visualize without bypassing engine internals.
- The user described a 3D sparse grid over a `2^24 m` world, with 16?16?16 chunks, vertically spanning a page of 4096 tiles. There can be multiple grids, intersecting grids, deep caves, waterfalls, volcanoes, factories, labs, skyscrapers, and more. The world must support surface, underground, high atmosphere, and eventually space transitions.

## What Was Not Decided

- The conclusion was clear and accepted: **Domino is the reusable engine; Dominium is the game/product layer**. What remains uncertain is the actual repository state. The chat planned the split, but did not verify whether the repo already matches it.
- The unresolved issue is that the actual repo was not inspected in this chat. The planned structure may not match the current files.
- The unresolved issue is practical feasibility, especially for retro targets and Carbon OS. Their actual toolchains and system calls remain unverified.
- The unresolved issue is the exact IR payload layout and how far limited renderers should go. A CGA or MDA backend cannot realistically support modern 3D in the same way as Vulkan. The agreed approach is explicit capability flags and graceful fallback or no-op behaviour.
- The unresolved issue is the exact manifest/schema format. JSON, TOML, and INI-like examples appeared in prompts, but no final schema choice was made.
- The unresolved issue is that external packaging details require verification. WiX, macOS notarization, Linux packaging, and AppImage tooling are all external-world facts and may be stale.
- The package and this report should help future assistants continue without re-reading the whole chat. However, they must preserve uncertainty: actual repo state is unverified, some transcript sections were skipped, external tooling facts may be stale, and assistant suggestions are not user decisions unless accepted or built upon.
- It is also reasonable to infer that the user wants the future project spec book to preserve rationale, not just lists of decisions. The later handoff requests emphasised visible rationale, rejected options, uncertainty, and changes of direction.
- Before doing it, verify the repo state. The generated prompts assume specific directories and may need adaptation.
- Important items labelled as fact, inference, or uncertainty.
- The **Phase 4 setup prompts** describe setup core and wrappers for Windows, macOS, Linux, and retro targets. They should be used only after verifying current external packaging tool details.
- The chat also created downloadable report files and handoff packages. For understanding the substance of the chat, the important thing is not the files themselves but the information they preserved: roadmap, decisions, tasks, constraints, risks, and unresolved issues.

## Ideas Rejected, Superseded, Or Deprioritised

- It is also reasonable to infer that the user wants the future project spec book to preserve rationale, not just lists of decisions. The later handoff requests emphasised visible rationale, rejected options, uncertainty, and changes of direction.
- This was the earlier plan, but it was superseded. The current roadmap starts with ABIs/APIs because all backends and products need stable interfaces. Reconsider only if the repo already has a solid ABI layer.
- This was rejected because launcher/setup/tools should be able to run natively, in CLI, or in TUI without needing the graphics stack. Renderer use remains optional for canvases/previews.
- This was superseded by a unified `DOM_UI_GUI` mode with backend flags. Reconsider only if the UI model proves too limiting.
- The idea of making many signed/unsigned variants first-class was rejected as redundant. Keep ordinary integers plus `Q4.12`, `Q16.16`, and `Q48.16`.
- Rejected for dense fields because of memory overhead. It remains appropriate for sparse aggregate values.
- Rejected as a general representation because it loses flexibility and still needs metadata. It may be useful for very specific counters.
- Rejected for authoritative state due to angle wrap, trig, singularity, and non-linear resolution problems. Still useful for display and orbit bands.
- Rejected as default because it is too expensive and unnecessary for the intended gameplay. Approximate/scripted effects may appear later.
- Rejected because the user wants arbitrary construction. Prefabs remain useful templates, not the construction primitive.

## What Future Work Came From It

- A number of Codex prompts were generated earlier in the chat for refactoring the repo, implementing runtime/platform/render APIs, setup, launcher, game bootstrap, ECS/SIM, and world/terrain/hydrology. However, the user later clarified that none of the Phase 2.5+ prompts had been implemented yet and wanted to pause before going further. The user wanted the systems to be more extensible and modular before committing.
- The user then asked how to structure Codex prompts. The final high-level roadmap became:
- The assistant generated detailed Phase 1 prompts, platform backend templates, renderer backend templates, setup prompts, launcher prompts, tools prompts, and finally a Phase 7+ roadmap for the game. The game phase itself was not expanded into the same full prompt detail as Phases 1-6. That remains a future task.
- The topic mattered because every Codex prompt depends on paths and module boundaries. If the repo layout is inconsistent, prompts will fail or scatter code into the wrong places.
- A platform backend prompt template was generated, along with parameter sets for Win32, Win16, DOS32, DOS16, CP/M-80, CP/M-86, Carbon, Cocoa, X11, Wayland, POSIX, SDL1, SDL2, and null.
- The unresolved issue is the exact manifest/schema format. JSON, TOML, and INI-like examples appeared in prompts, but no final schema choice was made.
- A full set of Phase 5 prompts was generated for launcher core, CLI, TUI, GUI, and extensions.
- Phase 6 prompts were generated for the tool framework, core dev tools, editing backends, and GUI editor host.
- These systems are planned for later phases. The important decision is that they should not create separate incompatible frameworks; they should use the same fields, networks, jobs, packages, and event systems.
- The package and this report should help future assistants continue without re-reading the whole chat. However, they must preserve uncertainty: actual repo state is unverified, some transcript sections were skipped, external tooling facts may be stale, and assistant suggestions are not user decisions unless accepted or built upon.
- The user explicitly wanted a Codex prompt roadmap, because much of the implementation would be carried out by Codex against an existing repo with fragmented/outdated generated code.
- It is also reasonable to infer that the user wants the future project spec book to preserve rationale, not just lists of decisions. The later handoff requests emphasised visible rationale, rejected options, uncertainty, and changes of direction.

## Important Artifacts

- `manifest`: `1`
- `markdown`: `1`
- `primary_report`: `2`
- `reader_brief`: `1`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `1`

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
