Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/app_testx_codehygiene/`
Promotion Status: not_reviewed

# Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was a long, high-density planning and consolidation session for the **Dominium / Domino** project. In plain terms, it was about turning an extremely ambitious simulation-game vision into a disciplined, modular, future-proof engineering program. The project being discussed is not a normal game in the narrow sense. It is intended to be a deterministic universe engine and game platform: something that can support tiny single-room scenarios, singleplayer survival, co-op, MMO-scale shared universes, AI-only autorun civilizations, player-only worlds, spectator-only museums, strict competitive servers, anarchy servers, and god-mode administrative tooling without violating determinism, epistemics, reproducibility, or architecture boundaries.

The conversation began as an extended planning effort around engine/game systems: rendering, simulation scale, procedural and real-world world data, timekeeping, calendars, economy, currencies, deaths, respawning, AI agents, politics, war, modding, tooling, and multi-platform support. Over time, the user repeatedly pushed the design toward a single underlying philosophy: **anything that represents world content, laws, capabilities, standards, or gameplay styles should be data-defined and composable where possible, while the engine/game code should provide stable, deterministic mechanisms and enforcement.** That philosophy became central. It was applied to calendars, currencies, units, rendering backends, UI, laws, capabilities, worlds, populations, economies, agents, authority, tools, tests, versions, changelogs, and source-code hygiene.

A major turning point was the repository architecture refactor. The user provided canonical top-level layout rules: `engine/`, `game/`, `client/`, `server/`, `launcher/`, `setup/`, `tools/`, `libs/`, and `schema/` each have sharply separated responsibilities. The engine is reusable and independent. The game depends only on engine public APIs. Client/server are executables that bind engine + game. Launcher and setup must not leak into engine/game. This became a recurring constraint.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`.

## What Was Decided

- A large set of prompts was then generated to lock down architecture, determinism, performance, schema governance, rendering, epistemic UI, sharding, interest sets, and fidelity projection. This became the Phase 1 hardening layer. Additional audit prompts were introduced to ensure consistency before proceeding into life, civilization, war, content, agents, tools, mods, and final long-term policy.
- Because the chat was huge, the user asked for a maximum-fidelity context transfer packet. Then they asked for downloadable report files. Then they asked for an in-chat reader. Finally, they asked for this human-readable explanatory report. This final report is meant to let a future assistant or human understand the substance without re-reading the whole conversation.
- The central project is a deterministic universe engine/game. The user's ambition is not just a normal game but a world runtime that can represent everything from a single-room scenario to an AI-only universe to an MMO. The project is meant to support real-world defaults, arbitrary modding, procedural and defined content, strong epistemics, and long-term replayability.
- The user provided a canonical repository structure and non-negotiable engine/game dependency direction. The engine is reusable and independent. The game depends on engine public APIs only. Engine internals must not leak into game/tools. Rendering backends belong to the engine, not the client. Launcher/setup logic must not enter engine/game. Client/server are executables that bind engine and game.
- This topic is central to long-term scalability. It allows future CPUs, GPUs, NPUs, heterogeneous cores, cache structures, and distributed servers to be supported by adding backend policies rather than rewriting gameplay.
- Rendering decisions were framed around explicit API first: Vulkan/DX12/Metal inform core contracts; legacy renderers are sinks or downgraded consumers. Rendering never affects authoritative simulation.
- The user also wanted AI-only civilizations that could exist outside bounds of play but become visitable and indistinguishable from real civilizations. The answer was existence states and refinement contracts. A macro civilization can be alive without micro-simulating every citizen, but if it is reachable and visitable, it must refine deterministically into micro detail consistent with its macro history.
- Large prompt families were generated for life/death/continuity, civilization/economy/governance, war/conflict, canonical content, agents, tools, mods, and final long-term maintenance. These are extensive background artifacts. Later, the chat shifted away from implementing those systems here because another bootstrap declared the core design complete and locked.
- Later, the user pasted a newer build/version model from another chat. That model superseded simpler earlier ideas: GBN is only for distributed artifacts, BII exists always, build kind and channel are distinct, product SemVer is manual, and all protocols/schemas/API/ABI versions are orthogonal. This matters because future testing and app prompts must use BUILD-ID-0, not the earlier model.
- This became the final active topic. The user provided an application-layer bootstrap and two setup/launcher plans. Those were judged better than earlier app plans because they added concrete contract headers, launcher reference modules, UI IR, command graph parity, RepoX visibility, failure-mode docs, and read-only tools.
- Because the chat became large and slow, the user asked how to transfer knowledge to new chats. The answer was to materialize knowledge into docs and handoff packages. The chat generated a Context Transfer Packet, then a downloadable report package, then an in-chat reader. This final report is the human-readable version.
- At first the chat was actively designing systems. Later it moved toward consolidating and enforcing architecture. Then it moved into application layer implementation planning. Finally it shifted into handoff/report packaging.

## What Was Not Decided

- The main unresolved goal is practical execution: which prompts have actually been run, which files exist, and what implementation should happen next.
- Setup handles install, verify, repair, rollback, upgrade, downgrade, uninstall, and status. Launcher can invoke Setup, but must not replicate its mutation logic. This prevents two products from disagreeing about installation state.
- First, verify whether `libs/contracts` and `libs/appcore` already exist. Then implement the pure contract headers and appcore skeleton. This should include:
- Before implementing app RepoX integration, verify actual RepoX metadata paths, TestX invocation, VALIDATE-0 commands, and BUILD-ID-0 files. Without that, an implementation prompt would guess.
- Use labels like FACT, INFERENCE, UNCERTAIN, PROJECT-CONTEXT in reports.
- From the user profile and instructions, future assistants should verify time-sensitive/current facts with web where relevant. This chat itself is mostly internal project planning, so external citations are not central.
- EXEC, ECSX, KERN, ADOPT, DIST, HWCAPS, EXIST, DOMAIN, TRAVEL, TIME, OMNI, LIFE, CIV, WAR, AGENT, TOOL, MOD, FINAL prompt families were generated earlier. They are important as historical design artifacts, but actual repo execution is unverified.
- The chat produced downloadable handoff files and later an in-chat reader. Those files are useful for aggregation but are not themselves project source code. The package's main caveat is that it does not verify actual repository state.
- The most important unresolved issue is actual repository state. We do not know which prompts were run, which files exist, or which systems are implemented.
- The latest project-context says `CANON_INDEX.md` is the single source of truth. The package does not verify its existence. This should be checked before using docs as canon.
- The versioning model is stated as canon, but actual implementation is unverified.
- The project is too complex for vague summaries. Future assistants should preserve IDs, artifacts, and caveats.

## Ideas Rejected, Superseded, Or Deprioritised

- The user then added a newer versioning model from another chat: product SemVer is manual; build kind is dev/ci/beta/rc/release/hotfix; global build number is only for distributed beta/rc/release/hotfix; build instance ID always exists for dev/ci; channels are separate; all products in a release share the same GBN. This superseded the earlier simpler "build number increments whenever tests pass" model.
- The user provided a canonical repository structure and non-negotiable engine/game dependency direction. The engine is reusable and independent. The game depends on engine public APIs only. Engine internals must not leak into game/tools. Rendering backends belong to the engine, not the client. Launcher/setup logic must not enter engine/game. Client/server are executables that bind engine and game.
- Later, the user pasted a newer build/version model from another chat. That model superseded simpler earlier ideas: GBN is only for distributed artifacts, BII exists always, build kind and channel are distinct, product SemVer is manual, and all protocols/schemas/API/ABI versions are orthogonal. This matters because future testing and app prompts must use BUILD-ID-0, not the earlier model.
- The decision was driven by parity, automation, testing, and accessibility. CLI can be tested easily and consistently. GUI/TUI must not become separate semantic layers. They render the same command graph.
- Setup handles install, verify, repair, rollback, upgrade, downgrade, uninstall, and status. Launcher can invoke Setup, but must not replicate its mutation logic. This prevents two products from disagreeing about installation state.
- Hardcoded modes like "creative mode," "anarchy mode," or "admin mode" were superseded by data-defined laws and capabilities. This rejection is final under current canon. If a future feature looks like a mode, it should probably be expressed as a capability/law/profile.
- The idea of admin as a hidden bypass was rejected. God mode exists, but as explicit capabilities and law-governed effects with audit trails. This matters because hidden admin shortcuts would corrupt replayability, integrity, and trust.
- Manual changelogs were rejected once RepoX was established as changelog source of truth. This is current and final unless RepoX itself changes.
- Rejected because CLI is canonical. GUI/TUI can exist, but only as views over the same command graph. This prevents divergent behavior and test complexity.
- Rejected earlier in the reality/travel layer. Movement must go through travel graphs, even exotic movement like portals and wormholes.

## What Future Work Came From It

- A large set of prompts was then generated to lock down architecture, determinism, performance, schema governance, rendering, epistemic UI, sharding, interest sets, and fidelity projection. This became the Phase 1 hardening layer. Additional audit prompts were introduced to ensure consistency before proceeding into life, civilization, war, content, agents, tools, mods, and final long-term policy.
- This was one of the most important engineering turns in the conversation. It made future performance work a backend/policy problem rather than a gameplay rewrite problem.
- Because the chat was huge, the user asked for a maximum-fidelity context transfer packet. Then they asked for downloadable report files. Then they asked for an in-chat reader. Finally, they asked for this human-readable explanatory report. This final report is meant to let a future assistant or human understand the substance without re-reading the whole conversation.
- This topic is central to long-term scalability. It allows future CPUs, GPUs, NPUs, heterogeneous cores, cache structures, and distributed servers to be supported by adding backend policies rather than rewriting gameplay.
- Large prompt families were generated for life/death/continuity, civilization/economy/governance, war/conflict, canonical content, agents, tools, mods, and final long-term maintenance. These are extensive background artifacts. Later, the chat shifted away from implementing those systems here because another bootstrap declared the core design complete and locked.
- For future use, those prompt families are historical/planned artifacts. They may be useful in content/spec aggregation, but current work should not redesign them.
- Later, the user pasted a newer build/version model from another chat. That model superseded simpler earlier ideas: GBN is only for distributed artifacts, BII exists always, build kind and channel are distinct, product SemVer is manual, and all protocols/schemas/API/ABI versions are orthogonal. This matters because future testing and app prompts must use BUILD-ID-0, not the earlier model.
- INFERENCE:** The user wanted to prevent future chats or Codex sessions from drifting, forgetting, or simplifying. They care deeply about maintaining continuity across many chats and turning fragmented planning into a stable project corpus.
- The biggest change was from "generate more design prompts" to "architecture is closed; now implement, audit, maintain, and preserve."
- The main unresolved goal is practical execution: which prompts have actually been run, which files exist, and what implementation should happen next.
- This decision affects everything. A future assistant should not propose new ontology, new architecture, or major rule changes unless the user explicitly asks.
- The original TEST0 prompt aimed to generate and run exhaustive tests. The user then added requirements for long-lived modular tests, version integration, changelogs, git discipline, blockers, assertions, comment density, and future automation. TESTX replaced TEST0 to include all of that.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
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
