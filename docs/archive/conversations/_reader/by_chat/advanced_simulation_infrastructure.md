Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/advanced_simulation_infrastructure/`
Promotion Status: not_reviewed

# Dominium Advanced Simulation and Infrastructure Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

[FACT] This chat was about designing major architecture for the **Dominium/Domino deterministic engine**, with emphasis on advanced simulation, gameplay mechanics, user-buildable infrastructure, arbitrary placement, buildings, splines/corridors, signage, markings, and how all of that should eventually be implemented or merged into an existing refactor plan.

The conversation began from a technical planning prompt for "Plan Part 6 - Advanced Simulation," where the user asked for an architecture covering heat simulation, power grids, fluids, atmospheres, vehicles, structural loads, destruction, and mod-extensible physics. The engine was constrained from the start: **Domino Engine must be ISO C89**, deterministic, fixed-point where determinism matters, free of OS APIs, free of hardcoded game semantics, and portable across platforms. **Dominium**, the game/UI/tools layer, must stay within a portable **C++98 subset**. The user also emphasized strict layering, modularity, portability, deterministic semantics, and data-driven behavior.

[FACT] The first major output was a high-level advanced simulation stack. It proposed simulation domains such as heat, electrical power, fluid networks, hydrology, atmospheres, vehicles, structural loads, and a mod-extensible physics framework. That architecture was not implemented in code. It was a design plan.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, workbench. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__human_readable_chat_report.txt`.

## What Was Decided

- The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it.
- Finally, the chat shifted into archival mode: it produced a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader version. Those later outputs preserved the discussion for future aggregation.
- [INFERENCE] The conclusion was not a finalized implementation but a working architecture: each simulation domain should be deterministic, fixed-point, content-driven, versioned, replayable, and integrated through clear read/write boundaries.
- [INFERENCE] This was one of the strongest architecture decisions because later topics repeatedly built on it.
- This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system.
- The key principle was that not every system should depend on decor directly. Decorative signs and decals are cheap visual objects. If they affect simulation or gameplay, they must be promoted to devices with proper STRUCT/TRANS state and ports.
- The final phase was preservation. The user asked for a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat report reader. These artifacts were about preserving the chat for future use and aggregation, not about new architecture decisions.
- The chat started as a simulation architecture task. It then became a gameplay layering task. It then became an infrastructure representation task. It then became a construction UX and arbitrary placement task. Finally, it became an implementation/handoff/reporting task.
- [FACT] This was explicitly stated by the user in the opening constraints. It is final unless the user later supersedes it.
- The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features, C++ features, compiler extensions, platform APIs, or undefined behavior.
- This decision might only be revisited if the user deliberately changes the engine language constraint.
- The rationale is similar: portability and compatibility. Dominium can be more expressive than the C engine, but it still must not depend on modern C++ features unless the constraint changes.

## What Was Not Decided

- [UNCERTAIN / UNVERIFIED] No repository files were inspected in this chat. No code was implemented. Proposed paths, module names, command names, file names, VM concepts, and data schemas are design proposals until checked against the actual codebase.
- [UNCERTAIN / UNVERIFIED] Exact solvers, fixed-point formats, module paths, data schemas, and tick ordering remain to be verified and specified.
- [UNCERTAIN / UNVERIFIED] The exact gameplay rules runtime was not specified. The command examples were conceptual.
- [UNCERTAIN / UNVERIFIED] The exact cross-section schema, attachment schema, and packing rules remain unresolved.
- [UNCERTAIN / UNVERIFIED] Microsegment length, VM design, storage layout, budget values, and actual code integration remain open.
- [UNCERTAIN / UNVERIFIED] Actual standards packs, rule schema, semantic key format, localization, and AI interaction remain unresolved.
- Then it produced a prompt for another GPT-5.2 chat that already had a refactor/optimization plan. That prompt told the other chat to amend its existing plan instead of restarting, and to verify coverage of arbitrary placement, unified spatial primitives, co-location, signage, buildings, and determinism/performance.
- [UNCERTAIN / UNVERIFIED] The architecture has not been verified against the actual repository. The exact implementation details remain unresolved: Q formats, orientation math, command schemas, VM instruction set, microsegment length, carrier ownership, junction archetypes, facility modules, and DECOR/device promotion policy.
- [UNCERTAIN / UNVERIFIED] Exact Q formats were not finalized.
- [UNCERTAIN / UNVERIFIED] The exact VM is unresolved.
- The most important practical next step is to inspect the current repository. This chat proposed module names and file paths, but did not verify them.
- [FACT] The user asked later reports to preserve uncertainty labels: FACT, INFERENCE, UNCERTAIN / UNVERIFIED, and PROJECT-CONTEXT.

## Ideas Rejected, Superseded, Or Deprioritised

- This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system.
- The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features, C++ features, compiler extensions, platform APIs, or undefined behavior.
- The rationale is similar: portability and compatibility. Dominium can be more expressive than the C engine, but it still must not depend on modern C++ features unless the constraint changes.
- [UNCERTAIN / UNVERIFIED] Exact Q formats were not finalized.
- Alternatives considered implicitly: direct UI mutation or game-specific engine code. These were rejected because they violate determinism and layering.
- The alternative was stacking independent splines. That was rejected because it would be hard to combine realistically. A corridor with cross-section slots makes co-location explicit. It lets one alignment host rails, lanes, sidewalks, ducts, cables, pipes, lights, catenary, barriers, drainage, and more.
- The alternative is full CAD or hand-placing every object. That was rejected as impractical for gameplay. The chosen direction is parametric corridors, junctions, layers, modules, facilities, and carriers.
- Grids are optional UI aids. They do not define engine placement. This is crucial for realistic infrastructure, arbitrary rotations, slopes, tunnels, bridges, curved roads, angled buildings, and freeform layouts.
- This idea was not developed as a serious final option, but it was the implied naive model behind the user's question. It was superseded by corridors with slots.
- It was rejected because overlapping independent splines would not reliably represent shared rails, shared structures, clearance envelopes, co-located utilities, or deterministic editing. It might remain useful as an import or authoring input, but it should canonicalize into corridors.

## What Future Work Came From It

- The user then asked whether the corridor model could be made more extensible and performant. That prompted a refinement: the editable corridor should not be the same as the runtime representation. Users and tools manipulate high-level splines, attachments, and features. The engine compiles that into microsegments, indices, occupancy bitsets, connectivity edges, structural references, and render/sim extraction data.
- The next step was integration. The user asked what other systems this should link into. The answer identified many: RES, ENV, BUILD, TRANS, STRUCT, SIM, POWER, FLUID/HYDRO, HEAT, ATMO, VEHICLE, JOB, AGENT, logistics, inventory, rendering, save/load, replay, multiplayer checksums, ownership/authority, permissions, construction zones, and localization.
- The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it.
- After the architecture was established, the user asked for a Codex prompt plan to implement any necessary changes. A nine-step plan was produced: coordinate/placement specs, deterministic pose/frame math, TRANS 3D corridors, STRUCT arbitrary orientation and anchors, DECOR host placement, deterministic command schemas, UI snapping refactor, performance hardening, and docs/migration notes.
- Finally, the chat shifted into archival mode: it produced a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader version. Those later outputs preserved the discussion for future aggregation.
- Once the architecture was clear, the user wanted implementation planning. The chat produced a nine-step Codex prompt plan covering specs, fixed-point pose/frame math, TRANS, STRUCT, DECOR, deterministic commands, UI snapping, performance hardening, and docs.
- Then it produced a prompt for another GPT-5.2 chat that already had a refactor/optimization plan. That prompt told the other chat to amend its existing plan instead of restarting, and to verify coverage of arbitrary placement, unified spatial primitives, co-location, signage, buildings, and determinism/performance.
- The final phase was preservation. The user asked for a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat report reader. These artifacts were about preserving the chat for future use and aggregation, not about new architecture decisions.
- [FACT] The user wanted a Codex prompt plan to implement necessary changes.
- [FACT] The user wanted a prompt for an existing GPT-5.2 refactor/optimization chat.
- [INFERENCE] The user wants future chats and Codex work to preserve continuity, not keep restarting or re-deciding the same core architecture.
- [INFERENCE] The user wants these reports to feed a future full Project Spec Book.

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
