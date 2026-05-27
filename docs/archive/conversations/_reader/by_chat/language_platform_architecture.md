Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Language_Platform_Architecture/`
Promotion Status: not_reviewed

# Dominium Language, Platform, and Architecture Baseline - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was a design-decision and architecture-baseline discussion for Dominium, focused on language standards, platform floors, binary architecture, portability strategy, and the project's long-term modular structure. The user began by asking whether Dominium would gain performance or features by moving beyond the earlier C89 engine and C++98 game plan. Over the conversation, the topic expanded into a full re-evaluation of what should be written in C versus C++, what standards should define the mainline, which operating systems should still count as full native targets, and how old or exotic systems should be supported without distorting the modern architecture.

The most important evolution was away from the crude split "engine = C, game = C++." The better rule that emerged was semantic: C should own stable law, ABI, fixed-width data, serialization, replay, packets, renderer command IR, and deterministic primitives; C++ should own resource-heavy machinery, runtime services, providers, apps, game orchestration, tools, Workbench, and composition. This is the central idea to preserve. The project does not need pure C, pure C++, or a language ideology. It needs stable contracts at the boundaries and modern implementation power internally.

The user initially considered staged old-to-new plans: versions 0.x/1.x using C89/C++98 and later versions moving to C11/C++17. That plan was superseded as the user accepted a more decisive baseline: C17 and C++17 across the mainline, with 64-bit source-native builds and little-endian assumptions. The old C89/C++98 goal moved from active mainline law into retro/projection/archive thinking. The current repo state discussed in the chat supports this: root and engine CMake were observed as already requiring C17/C++17, while the repository still contains documentation and comments that should be updated to match the new doctrine.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, workbench, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `14` source files. The primary extracted source is `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`.

## What Was Decided

- The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.
- The user then consolidated a broad future plan around Domino, Dominium, Workbench, AIDE, contracts, tests, replay, and evidence. The answer agreed that the plan was strong, but identified missing central pieces: composition resolver, lockfiles, compatibility corpus, trust/permissions, virtual filesystem roots, performance budgets, and stable public-surface promotion rules.
- Finally, the user pasted advice favoring C99 or C++11 due to raylib/SDL and legacy targets. The answer rejected a pivot. Raylib and SDL2 being C APIs only means provider boundaries should be C-callable; it does not force the whole engine or game to C99. The final recommendation remained C17 + C++17, with raylib/SDL2 treated as providers and with external deployment claims placed into the verification queue.
- The chat repeatedly compared C89, C99, C11/C17, C23, C++98, C++11, C++17, and newer C++ standards. The final working direction is C17 + C++17 for the mainline. C99 and C++11 were considered but not adopted as the project-wide baseline. Newer C23/C++20/C++23/C++26 were treated as future provider/tool lanes, not current mainline law.
- The project must retain a C-compatible ABI. The public boundary should remain POD-only, versioned, return-code/refusal based, and free of exceptions, STL containers, classes, templates, allocator ownership, and C++ ABI assumptions. This allows providers, plugins, tools, projections, and future bindings to survive implementation changes.
- The deterministic simulation law remains more important than the language standard. Authoritative simulation must use stable IDs, canonical ordering, fixed-width values, fixed-point math, explicit little-endian encoding, and deterministic scheduler phases. Threads may accelerate derived work, but final authoritative commit must be canonical and not depend on OS timing or thread completion.
- Avoid another cleanup cycle by locking hard-to-change decisions early.
- The goal changed from "should old C/C++ standards be upgraded?" to "what is the full future architecture baseline?" The user initially entertained C89/C++98 staging, then accepted C17/C++17 as mainline. The user also moved from "maybe support old systems directly" to "support old systems through constrained/projection/archive lanes."
- DECISION-01:** The accepted direction is C17 + C++17 mainline. This superseded the old C89/C++98 plan and the later temptations to pivot to pure C99 or pure C++11. It depends on restricted deployment/library policy for legacy floors.
- DECISION-02:** Full source-native builds should be 64-bit. This simplifies the release matrix and avoids old memory constraints, while fixed-width data keeps saves/replays portable.
- DECISION-03:** Little-endian is accepted as a mainline invariant. Explicit little-endian serialization remains necessary so that files are stable and auditable.
- DECISION-04:** The public ABI remains C-compatible. This is the key decision that lets modern C++ implementation coexist with tools, providers, projections, and future bindings.

## What Was Not Decided

- The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.
- Exact tolerance for exceptions/RTTI inside private C++17 code remains unsettled. Exact platform floors and raylib/SDL2 priority remain unresolved.
- Verify the Windows 7 and macOS 10.9 toolchain/library assumptions using official sources.

## Ideas Rejected, Superseded, Or Deprioritised

- Finally, the user pasted advice favoring C99 or C++11 due to raylib/SDL and legacy targets. The answer rejected a pivot. Raylib and SDL2 being C APIs only means provider boundaries should be C-callable; it does not force the whole engine or game to C99. The final recommendation remained C17 + C++17, with raylib/SDL2 treated as providers and with external deployment claims placed into the verification queue.
- Keep future assistants from repeating rejected advice such as pure C99 or pure C++11.
- DECISION-01:** The accepted direction is C17 + C++17 mainline. This superseded the old C89/C++98 plan and the later temptations to pivot to pure C99 or pure C++11. It depends on restricted deployment/library policy for legacy floors.
- DECISION-07:** Universal primitive binaries were rejected; projections or generated subsets are the correct extreme-legacy strategy.
- DECISION-08:** Foundation Lock remains blocked while dependency-direction strict validation is red.
- Which parts of the old C89/C++98 plan are fully superseded and which survive as projection/archive ideas?
- The immediate next action is not more architecture brainstorming. The latest project task/review packets say Foundation Lock is blocked because dependency-direction strict validation reports 358 violations and 38 warnings. The next task is FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01. Only after that should Workbench validation or product-facing module work proceed.

## What Future Work Came From It

- The user then consolidated a broad future plan around Domino, Dominium, Workbench, AIDE, contracts, tests, replay, and evidence. The answer agreed that the plan was strong, but identified missing central pieces: composition resolver, lockfiles, compatibility corpus, trust/permissions, virtual filesystem roots, performance budgets, and stable public-surface promotion rules.
- The chat repeatedly compared C89, C99, C11/C17, C23, C++98, C++11, C++17, and newer C++ standards. The final working direction is C17 + C++17 for the mainline. C99 and C++11 were considered but not adopted as the project-wide baseline. Newer C23/C++20/C++23/C++26 were treated as future provider/tool lanes, not current mainline law.
- The project must retain a C-compatible ABI. The public boundary should remain POD-only, versioned, return-code/refusal based, and free of exceptions, STL containers, classes, templates, allocator ownership, and C++ ABI assumptions. This allows providers, plugins, tools, projections, and future bindings to survive implementation changes.
- The deterministic simulation law remains more important than the language standard. Authoritative simulation must use stable IDs, canonical ordering, fixed-width values, fixed-point math, explicit little-endian encoding, and deterministic scheduler phases. Threads may accelerate derived work, but final authoritative commit must be canonical and not depend on OS timing or thread completion.
- Support Windows 7, macOS Mavericks, Linux, and possibly older/future systems.
- Keep future assistants from repeating rejected advice such as pure C99 or pure C++11.
- Prepare material for a future Project Spec Book.
- The goal changed from "should old C/C++ standards be upgraded?" to "what is the full future architecture baseline?" The user initially entertained C89/C++98 staging, then accepted C17/C++17 as mainline. The user also moved from "maybe support old systems directly" to "support old systems through constrained/projection/archive lanes."
- DECISION-04:** The public ABI remains C-compatible. This is the key decision that lets modern C++ implementation coexist with tools, providers, projections, and future bindings.
- The user wants architectural clarity more than fashionable language choices. The user also wants future assistants to preserve tradeoffs, not collapse everything into an oversimplified final answer.
- The biggest future-chat failure would be to answer the language question as if this were a small raylib project. It is not. Another failure would be to treat the final architecture as permission to build every layer immediately. The current red gate is still dependency direction.
- Draft the task packet for FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `2`
- `markdown`: `2`
- `primary_report`: `1`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `source_input`: `1`
- `spec_sheet`: `1`
- `verification`: `1`
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
