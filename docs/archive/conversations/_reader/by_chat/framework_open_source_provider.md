Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Framework_Open_Source_Provider/`
Promotion Status: not_reviewed

# Domino Framework and Open-Source Provider Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was about how to accelerate the Dominium/Domino game-engine project by using existing open-source code without letting outside engines or libraries define the architecture. The user's recurring concern was speed: instead of starting from nothing, could Dominium bootstrap a working engine, game client, Workbench, scripting layer, and provider ecosystem using open-source systems such as raylib, SDL2, Lua, Celestia, SpaceEngine-like references, voxel/RTS/factory games, and other modular libraries? The conversation gradually converged on a clear doctrine: use outside code aggressively, but only as replaceable providers behind first-party Domino/Dominium contracts.

The first major theme was the difference between forking a full engine and assembling a framework from modular components. The chat rejected the idea that Dominium should become a modified copy of a large engine. Instead, it preferred a framework approach: Domino should define stable service contracts, provider ABIs, capability/refusal law, profiles, tests, and deterministic simulation interfaces; a Domino engine implementation should satisfy those contracts; the Dominium game implementation should consume those contracts. This means the game should not directly include `raylib.h`, `SDL.h`, `lua.h`, or any other third-party API in its canonical layers.

The second major theme was the raylib ecosystem. The user liked raylib and asked whether its subprojects could be used: raylib itself, `rlgl`, `rlsw`, `raymath`, `raygui`, `raudio`, texture/model/font systems, and examples. The conclusion was yes, but with clear classification. `raylib` is a broad high-level provider suite. `rlgl` is a raylib-family OpenGL abstraction provider, not the final Dominium OpenGL 3.3 backend. `rlsw` is a raylib software-render provider, not the canonical Dominium reference software renderer. `raygui` is an early Workbench/debug UI provider, not UI law. `raudio` is a first audio provider. `raymath` is safe for presentation/editor math, not deterministic simulation law. Asset-loading helpers are import/preview helpers, not Dominium asset identity.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, tooling, ui, workbench, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `14` source files. The primary extracted source is `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md`.

## What Was Decided

- Finally, the user uploaded a detailed preservation prompt and requested a maximum-fidelity report, registers, spec sheet, aggregator packet, audit, and downloadable files. This package is the response to that request.
- This became the central architectural theme. The conversation refined earlier vendor-shaped paths into service-first paths. The stable pattern is:
- The chat inspected `julesc013/dominium` and found evidence of existing abstractions such as system and graphics layers, stubs, and soft-backed backends. The finding was that raylib could fill concrete provider gaps without replacing the architecture. However, current repo facts are stale/uncertain and must be verified, especially the C17/C++17 vs C90/C++98 baseline contradiction.
- The user's large game vision requires an architecture where the world is infinite by addressability but finite by active simulation. The chat proposed activity states such as cold, warm, scheduled, active, and hot. It also proposed cells/islands/constructs as units of scheduling and authority. Clients can contribute compute, but state changes must be host-verified. This topic should become a formal spec chapter.
- The final topic is this package. The user requested a preservation report that is human-readable first, with registers, spec sheet, aggregator packet, self-audit, and downloadable files. This report preserves the visible chat, not any inaccessible past-chat transcripts.
- The exact first implementation branch, versions, and dependency pins are unresolved. The exact Domino Framework ABI is unresolved. The exact Lua version is unresolved. The current repository baseline must be verified. The formal policy for GPL/LGPL/unclear license material is unresolved. The sparse simulation and CAD systems need formal specs and prototypes.
- The main accepted direction was the framework/provider approach. The user explicitly said they liked the framework approach and asked whether it could be used to make a Domino framework provided by any engine implementation and consumed by any Dominium game implementation. This makes sense because it lets the project use raylib and other libraries quickly without baking them into game law.
- The raylib decision was also directionally accepted. The user repeatedly expressed enthusiasm for raylib and asked about using as much of raylib infrastructure as possible. The caveat is that raylib is a provider suite, not architecture. This affects rendering, audio, input, asset preview, and Workbench bootstrap.
- The service-first layout decision matters because it prevents vendor-shaped directories and product variants. A profile can choose raylib or SDL2 providers without making a separate client architecture.
- The SDL2 and Lua decisions matter because they balance speed with portability and extensibility. SDL2 gives a stable platform/input/audio substrate. Lua gives scripting, but the chat decided raw Lua version should not define mod law.
- The sparse deterministic delegated simulation decisions are design doctrines, not implemented decisions. They are accepted as the recommended direction but still need formal proof and prototypes.
- The central tradeoff was speed versus architectural control. The user wanted fast progress. The answer was to use existing libraries, but only behind first-party service contracts. This keeps the project from getting stuck in a third-party object model or rendering/input/save system.

## What Was Not Decided

- The chat inspected `julesc013/dominium` and found evidence of existing abstractions such as system and graphics layers, stubs, and soft-backed backends. The finding was that raylib could fill concrete provider gaps without replacing the architecture. However, current repo facts are stale/uncertain and must be verified, especially the C17/C++17 vs C90/C++98 baseline contradiction.
- The exact first implementation branch, versions, and dependency pins are unresolved. The exact Domino Framework ABI is unresolved. The exact Lua version is unresolved. The current repository baseline must be verified. The formal policy for GPL/LGPL/unclear license material is unresolved. The sparse simulation and CAD systems need formal specs and prototypes.
- The raylib decision was also directionally accepted. The user repeatedly expressed enthusiasm for raylib and asked about using as much of raylib infrastructure as possible. The caveat is that raylib is a provider suite, not architecture. This affects rendering, audio, input, asset preview, and Workbench bootstrap.
- 1. Verify repo baseline and dependency versions.
- The user requires source-grounded, audit-ready, uncertainty-labelled responses. The preservation prompt explicitly requires FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT labels, no invented facts, no treating brainstorms as decisions, and no over-compression. The prompt also requires a human-readable report first and downloadable files if possible ?filecite?turn29file0?.
- The most blocking unresolved issues are repo baseline verification, exact dependency pins, minimal framework ABI, provider profile order, deterministic simulation spec, and license policy.
- Verify the current `julesc013/dominium` CMake language baseline.

## Ideas Rejected, Superseded, Or Deprioritised

- The most important rejected idea is using a full engine fork as the project's main foundation. It was rejected because it would likely make Dominium inherit the full engine's assumptions. The second important rejected idea is allowing raylib to become the engine architecture. The chat repeatedly preserved the boundary: use raylib heavily, but only behind providers.
- A more subtle superseded idea was app-variant architecture. Early structures such as `apps/client/rendered/raylib` were useful for proof bootstraps, but the stronger model is generic apps plus provider profiles.
- Another rejected idea was using external reference projects directly without license review. This matters because later assistants might see Celestia, PCGUniverse2, pgg, or SpaceEngine and assume code can be copied. The chat did not authorize that.
- The user prefers modular architecture over monolithic engine forks. The user prefers long-term portability, extensibility, and replaceability. The user cares about preserving reasoning and rejected options for future aggregation.
- Third-party types must not enter contracts, game law, content, saves, replays, or public SDK.

## What Future Work Came From It

- Finally, the user uploaded a detailed preservation prompt and requested a maximum-fidelity report, registers, spec sheet, aggregator packet, audit, and downloadable files. This package is the response to that request.
- Future work should convert this into a dependency policy: use permissive/weak-copyleft libraries as providers where appropriate; use GPL/proprietary/unclear projects as research references unless explicitly quarantined; require provider manifests, license manifests, and conformance tests.
- The user appears to want a long-lived, auditable project spec that can survive chat transitions and aggregation. The preservation prompt confirms this.
- The user appears to want architecture that remains portable across older desktop systems and future render/platform providers. This was inferred from the platform floor and repeated concern with portability/modularity/extensibility.
- The user requires source-grounded, audit-ready, uncertainty-labelled responses. The preservation prompt explicitly requires FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT labels, no invented facts, no treating brainstorms as decisions, and no over-compression. The prompt also requires a human-readable report first and downloadable files if possible ?filecite?turn29file0?.
- The user prefers modular architecture over monolithic engine forks. The user prefers long-term portability, extensibility, and replaceability. The user cares about preserving reasoning and rejected options for future aggregation.
- The main uploaded artifact is `Pasted text.txt`, containing the preservation task prompt and output requirements ?filecite?turn29file0?. Before this task, no generated report/ZIP package was visible in this chat. This response creates the requested package.
- A future assistant might incorrectly say "we decided to use raylib as the engine." The correct statement is that raylib is a first visible provider suite. Another common mistake would be to treat every assistant proposal as a user decision. Several items are recommended directions, not implemented decisions.
- A future assistant might also rely on stale external facts or repository inspections. Dependency versions, OS floors, repo CMake state, and licenses must be verified.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
- `primary_report`: `1`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `source_input`: `3`
- `spec_sheet`: `1`
- `tsv`: `1`
- `verification`: `2`

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
