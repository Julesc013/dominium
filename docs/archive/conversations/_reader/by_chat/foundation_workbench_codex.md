Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Foundation_Workbench_Codex/`
Promotion Status: not_reviewed

# Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was a high-intensity strategic, architectural, and operational continuation of the Dominium project: a large simulation/game/engine ecosystem in the `Julesc013/dominium` repository. The user's central concern was that the project had spent a very long time in refactor and restructuring work, and that without a clear, enforceable architecture and faster execution model, the project would either drift back into chaos or stall forever before reaching real Workbench and gameplay/product work.

The conversation began from the aftermath of extensive repo cleanup, AIDE installation, build proof, internal pilot proof, and directory/root restructuring work. Earlier in the project, Dominium had a large number of root-level folders such as `core/`, `control/`, `data/`, `packs/`, `profiles/`, `bundles/`, `lib/`, `libs/`, `validation/`, `meta/`, `governance/`, `net/`, and others. The user was extremely frustrated by how long the cleanup took and repeatedly threatened to manually move folders if the process did not converge. This created the need for a more aggressive but still governed model: deterministic routing of bad-root files, quarantine for unknowns, canonical roots, and later a move away from physical folder cleanup into contract/governance hardening.

The conversation ultimately converged on a stable architectural model: **Domino** is the reusable deterministic/runtime substrate; **Dominium** is the game/product family built on Domino; **Workbench** is the production, validation, editing, inspection, packaging, and evidence environment; **AIDE** is the repo/control-plane harness; **Codex** is a bounded patch executor; **Contracts are law**; and **tests, replay, diagnostics, and evidence are proof**. The most important principles became: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, workbench, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `12` source files. The primary extracted source is `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`.

## What Was Decided

- After the root skeleton improved, the assistant and user recognized that the deeper problem was no longer top-level directories. The problem became semantic duplication and governance: what is public, what is private, what is stable, what is provisional, what is generated, what is a fixture, what must stay compatible, what can be replaced, and what proof is required.
- The key conclusion was that Workbench is not the general module system; it is one consumer of the module/command/service/provider/pack/artifact system. Workbench must not call private tools directly. It must route through registered commands and typed results, diagnostics, refusals, views, and evidence.
- The topic came up because the project needed a model that could support world simulation, modding, tooling, Workbench, release, portability, and future games without repeating endless refactors. The conclusion was that stable contracts and semantic IDs must be separated from replaceable private implementation.
- The repo root cleanup dominated much of the conversation. The old root structure was visibly unacceptable and triggered intense user frustration. The conversation explored cautious moves, gates, root inventories, salvage maps, bulk routing, and deterministic quarantine. The final stance was that the root skeleton is now mostly settled and should not be re-litigated unless validators show a live violation.
- The language policy shifted from historical C89/C++98 to C17/C++17. The mainline native architecture policy shifted toward 64-bit source-native: x86_64 and arm64. Public ABI remains C-compatible. Persisted formats must be fixed-width, explicit little-endian, and pointer-width independent.
- Workbench is a future product surface, not the center of authority. The user wants to get to Workbench and code soon, but Workbench must route through commands/services/views/evidence rather than private direct mutation. The first Workbench slice was narrow validation. The next needed bridge is command-result-view projection.
- Workbench's final shape is a shell hosting modules and workspaces. It eventually includes Project Graph Explorer, Interface Studio, Module/Pack Foundry, App Composer, Release Forge, Agent Work Board, Pack Browser, Renderer/Theme Laboratory, Replay/Trace Viewer, and related tools.
- This became the immediate next frontier. The system must avoid separate CLI, TUI, Workbench, rendered, native, and headless implementations of the same behavior. The next slice should prove a command result can become a semantic view projected across multiple surfaces, preserving the same result schema, refusal codes, diagnostics, and evidence.
- to preserve all old requirements and design decisions,
- The decisions above should be treated as the working canon of this chat. The strongest decisions are the architectural identity split, the contract/proof law, the closed root model, the C17/C++17 + C-compatible ABI baseline, fast strict as the normal gate, and the sequencing rule that Workbench/product work must be narrow and command/service/evidence-backed.
- The most tentative decisions are those depending on current live repo state after the latest pasted transcript: Wave 1 completion, current queue state, and exact readiness for `COMMAND-RESULT-VIEW-SLICE-01`. These should be verified before action.
- final architecture split;

## What Was Not Decided

- What remains uncertain is how quickly this architecture will move from contracts and fixtures into runtime implementations and product slices. The next chat should not assume runtime provider resolvers, package runtime, or Workbench shell exist.
- verify latest live repo state after user-pasted Wave 1 completion;
- 1. Verify live repo state.
- The user wants direct, evidence-grounded, audit-ready answers; timestamps/model labels; explicit uncertainty; no repeated clarification unless necessary; large continuous Codex prompt blocks when generating prompts; targeted tests instead of full suites; and rapid progress toward Workbench/code.
- The user is likely to reject slow, report-only, overcautious process. Future assistants should produce executable next prompts quickly after verifying state.
- It is uncertain how many concurrent Codex workers the user will actually run at once and whether the user wants coordinator prompts or worker prompts next.
- The most important continuation is: verify current `origin/main`, confirm Wave 1 and Workbench validation state, then generate or run `COMMAND-RESULT-VIEW-SLICE-01`.

## Ideas Rejected, Superseded, Or Deprioritised

- The key conclusion was that Workbench is not the general module system; it is one consumer of the module/command/service/provider/pack/artifact system. Workbench must not call private tools directly. It must route through registered commands and typed results, diagnostics, refusals, views, and evidence.
- Foundation Lock was the governance gate that determined whether narrow product work could begin. It initially blocked on dependency-direction strict validation. After repair, it reportedly closed with warnings. This topic matters because it marks the transition from infrastructure cleanup to narrow product slices.
- The user wanted to run many autonomous tasks concurrently. The assistant designed branch/worktree isolation and strict parallel-worker rules. Workers do not push to main, do not update global latest AIDE files, and produce task-local evidence. Coordinator merges serially and runs fast strict.
- ensure assistants do not lose constraints;
- preserve emotional and motivational context so future chats do not repeat slow, cautious patterns;
- Manual drag/drop directory cleanup was rejected as dangerous, even though the user threatened it out of frustration.
- Tiny sequential micro-move waves were superseded by deterministic routing and later by governed parallel task work.
- C89/C++98 as mainline was superseded by C17/C++17.
- 32-bit full-native mainline was rejected/deprioritized in favor of constrained/projection/archive lanes.
- Workbench as authority was rejected.

## What Future Work Came From It

- The topic came up because the project needed a model that could support world simulation, modding, tooling, Workbench, release, portability, and future games without repeating endless refactors. The conclusion was that stable contracts and semantic IDs must be separated from replaceable private implementation.
- Workbench is a future product surface, not the center of authority. The user wants to get to Workbench and code soon, but Workbench must route through commands/services/views/evidence rather than private direct mutation. The first Workbench slice was narrow validation. The next needed bridge is command-result-view projection.
- The user wanted to run many autonomous tasks concurrently. The assistant designed branch/worktree isolation and strict parallel-worker rules. Workers do not push to main, do not update global latest AIDE files, and produce task-local evidence. Coordinator merges serially and runs fast strict.
- This topic matters operationally because the user wants speed. The new chat should be ready to generate more parallel prompts or a coordinator review prompt depending on current repo state.
- This matters for the eventual master Project Spec Book and future domain feature work.
- to make the repository tidy and future-proof,
- minimize future architectural reversals;
- make Codex prompts operational rather than theoretical;
- preserve emotional and motivational context so future chats do not repeat slow, cautious patterns;
- parallelize autonomous contract/product-spine tasks
- preserve this chat for future aggregation.
- Tiny sequential micro-move waves were superseded by deterministic routing and later by governed parallel task work.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
- `markdown`: `3`
- `primary_report`: `1`
- `prompt`: `1`
- `reader_brief`: `2`
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
