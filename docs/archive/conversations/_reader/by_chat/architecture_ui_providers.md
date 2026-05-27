Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/architecture_ui_providers/`
Promotion Status: not_reviewed

# Dominium Architecture, UI, Providers, and Robot OS Strategy - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was a strategic architecture and design convergence session for Dominium/Domino. It began from a transferred knowledge base about rebuilding Dominium's GUI and binary strategy, then evolved into a broad platform-specification discussion covering repository structure, product shells, renderer/platform priorities, native applications, language standards, provider architecture, Workbench, UI authoring, and finally the game's core identity as a robotic seed-civilisation simulator with a diegetic robot operating-system interface.

The user was trying to prevent Dominium from becoming a brittle one-off project. The repeated concern was that the codebase, files, directories, APIs, schemas, renderers, GUIs, and data formats should remain portable, modular, extensible, replaceable, and reusable for other Domino-engine games or even unrelated engine/game projects. The conversation therefore treated the project less like a simple indie game and more like a long-lived platform or OS-like codebase. That framing shaped almost every technical recommendation: stable contracts, replaceable implementations, service boundaries, provider manifests, compatibility matrices, command/action/view/document systems, and validators.

The earliest phase dealt with GUI and binary architecture. The retained direction was that every product should have CLI, every product should have at least TUI or deterministic TUI stubs, and GUI support should be modular. Setup and launcher should use OS-native/OEM+ apps where appropriate; the client should use a rendered UI; server remains headless/CLI/TUI first; tools are case-by-case. The user then pushed on directory structure, wanting fewer top-level folders and a more future-proof organization. The resulting doctrine was ownership-based roots: apps compose, runtime implements, contracts define, content supplies, tools validate, and archive preserves historical material.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, tooling, ui, workbench, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `14` source files. The primary extracted source is `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`.

## What Was Decided

- The language baseline decision matters because it changes what old renderers and toolchains matter. C17/C++17 reduces the need to design around C89/C++98 constraints but does not remove the need for C-compatible ABI boundaries. The system floor decision similarly moves many older renderers and OS targets into research/back-port categories.
- The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.
- The final game direction is robotic seed civilisation, not labour management.
- 2. "Summarize the final renderer plan after the C17/C++17 transition."
- 4. "Which decisions in this chat were explicit user decisions versus assistant synthesis?"
- 5. "Which renderer/platform decisions are final, and which are still provisional?"

## What Was Not Decided

- The exact first playable slice remains unresolved. The first provider wedge is clear, but exact sequence between client/workbench gameplay, Robot OS, and gameplay mechanics still needs a formal milestone. The exact Lua version, Linux baseline, current repo status, and external library/version support need verification. The exact degree of Unreal involvement remains unclear.
- 1. Verify and pin external library/toolchain facts.
- It remains uncertain how much the user wants Unreal in the near-term after raylib-first discussion. It also remains uncertain whether Lua 5.4 or 5.5 is preferred; the user appears to value pinning and stability more than "latest" for script ABI.

## Ideas Rejected, Superseded, Or Deprioritised

- No explicit rejected or superseded ideas were extracted automatically.

## What Future Work Came From It

- The user then said the latest docs and code were live at `julesc013/dominium`. The assistant treated the repo as an implementation baseline and observed that AppShell, UI mode resolution, distribution doctrine, and component matrices already existed. This changed the task from inventing a GUI strategy from scratch to reconciling the transfer brief with existing repository doctrine.
- INFERENCE: The user wants to turn Dominium into a platform-level project whose architecture can survive decades of refactors, ports, new games, new providers, and evolving standards. The user also wants future assistants to stop re-litigating already-settled principles and instead build upon the emerging doctrine.
- The user appears to prefer source layouts and naming that remain meaningful years later. They dislike vendor-shaped, framework-shaped, and status-word architecture. Future assistants should not propose "just use X framework" as the answer. They should instead map libraries to providers, profiles, and contracts.
- The UI should feel like a customizable robot OS whose HUD, menus, TUI, CLI, Workbench, and future VR shell are projections of the same system.
- The most important immediate next task is provider/Robot OS wedge planning with validators and manifests.
- 7. "Turn PROVIDER-WEDGE-01 into a Codex-ready implementation task."

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
- `markdown`: `2`
- `primary_report`: `1`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `source_input`: `1`
- `spec_sheet`: `1`
- `verification`: `2`
- `zip`: `1`

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
