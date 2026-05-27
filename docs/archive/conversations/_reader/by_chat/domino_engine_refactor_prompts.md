Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/domino_engine_refactor_prompts/`
Promotion Status: not_reviewed

# Dominium/Domino Engine Refactor Planning - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was a long-form architecture and planning session for the **Dominium/Domino deterministic engine**. Its central purpose was not to write code, but to define how a very large, deterministic simulation engine should be structured so that it can support complex world simulation, agents, infrastructure, future DLCs, modding, replay, multiplayer lockstep, and large-scale performance without collapsing into hardcoded special cases.

**FACT:** The user began by establishing very strict architectural constraints. The **Domino Engine** must be ISO C89, deterministic, portable, fixed-point where determinism matters, and free of OS, platform, UI, rendering, or gameplay-semantic dependencies. The **Dominium** layer is the C++98 UI/tools layer and must only visualize, debug, or emit deterministic commands. The engine must preserve strict layering across systems such as BUILD, TRANS, STRUCT, DECOR, SIM, RES, ENV, JOB, and AGENT. It must use TLV-versioned content formats, stable IDs, deterministic tick scheduling, replay, and input-driven lockstep multiplayer.

The discussion started with advanced physical simulation systems: heat, power, fluids, atmospheres, vehicles, structural loads, destruction, and a mod-extensible physics framework. The important outcome was not a final implementation for each solver, but a general design rule: every heavy system should be content-driven, deterministic, fixed-point, bounded, and integrated through generic primitives such as graphs, fields, ports, events, messages, actions, deltas, and replay hashes.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/domino_engine_refactor_prompts/dominium_domino_engine_refactor_prompts__human_readable_chat_report.txt`.

## What Was Decided

- FACT:** The Domino engine must be ISO C89. The Dominium UI/tools layer must be portable C++98. Engine code must not use OS APIs. Determinism matters, so floats are disallowed in deterministic paths. The engine must avoid platform-dependent behavior and hardcoded game semantics. Everything should be content-driven.
- This became one of the central architectural ideas of the chat. It makes behavior extensible without giving minds direct write access to the world. A mod can add new sensors, observations, intents, capabilities, or actions, but state mutation still passes through a deterministic pipeline.
- After the architecture and prompts were created, the user asked for a maximum-fidelity context transfer packet. The assistant produced one. The user then asked for a downloadable report package; the assistant generated package files and a ZIP. The user later asked for an in-chat reader version of that package, and finally requested this current human-readable explanatory report.
- The final state of the conversation is therefore not just an architecture. It is an architecture plus an implementation roadmap plus preservation artifacts. The important substance remains the deterministic engine design and the prompt plan, not the packaging files.
- The core idea is that deterministic simulation cannot tolerate platform-dependent behavior, nondeterministic iteration, floating-point inconsistencies, OS dependencies, or UI-driven state mutation. The engine must be portable, reproducible, and replayable. Therefore the architecture repeatedly favored fixed-size integer IDs, fixed-point math, TLV schemas, sorted iteration, deterministic queues, and replay hashes.
- The conclusion was not a final physics implementation. It was a framework direction: each physics family should be a deterministic family plugged into the scheduler, using content-defined TLV prototypes, fixed iteration solvers, stable vtables, and replay hooks.
- The user asked whether the same methods could apply across the whole engine. The answer was yes. This became a central theme.
- Instead of storing final geometry as truth, buildings store footprints, volumes, enclosure definitions, surfaces, sockets, carrier intents, and edit records. Derived compilers produce occupancy, voids, enclosure graphs, surface graphs, support graphs, and carrier artifacts. These are caches, not authority.
- For Wargames, fog and information become observer contexts, belief stores, visibility/occlusion, and communications graphs. Knowledge is simulation state, not UI state. This is essential because fog of war affects what players and AI can know and act on; it must therefore be deterministic and replayable.
- The sister-chat prompt added a major spatial authoring requirement: no grid lock. All placement must support arbitrary position, rotation, inclination, and curved geometry in 3D. Engine logic cannot depend on a global grid. Grids may exist only as optional UI snapping aids.
- Once the architecture stabilized, the user asked for a plan of prompts to give Codex. The assistant first produced an 8-prompt plan, but that was superseded after the sister-chat requirements. The final version became a 14-prompt roadmap.
- This roadmap is important because it translates architecture into implementation phases. It starts with invariants and scaffolding, then builds packet IO, scheduler, fields/messages/events, LOD, placement, TRANS, STRUCT, DECOR, agents, graphs, domains, knowledge/comms, and finally determinism hardening.

## What Was Not Decided

- The answer also introduced a deterministic bytecode VM as the preferred way to support modded behavior. A question was raised about whether native-code plugins should also be allowed, but the user did not answer. That remains unresolved.
- What remains uncertain is the actual repository state. The chat designed architecture and prompts, but did not inspect source code. Therefore the plan needs repo verification before implementation.
- The unresolved work is to generate detailed subsystem implementation prompts for heat, power, fluids, atmospheres, vehicles, and structural loads after the core engine spine is implemented.
- The remaining uncertainty is plugin policy. A deterministic VM was proposed, but whether native-code plugins are allowed remains unresolved.
- What remains uncertain is the exact thresholds and content policies for when things promote or demote.
- The unresolved issue is how much of STRUCT compilation should be implemented first. The prompt plan is broad; a real implementation may need a smaller first milestone.
- ignoring FACT/INFERENCE/UNCERTAIN labels;
- UNCERTAIN / UNVERIFIED:** The package files were generated in the sandbox during the prior step, but repository files were not created or inspected.
- The prompts are detailed, but repository state is unverified. Blindly applying them could create duplicate systems or wrong paths.
- Before merging this into a master spec, preserve uncertainty labels and verify against repository state and later decisions.
- The most important unresolved issues are VM/native plugin policy, exact Q formats, repository structure, existing TLV/scheduler state, and derived cache hash policy.
- 9. "What should I verify in the repository before running Codex Prompt 1?"

## Ideas Rejected, Superseded, Or Deprioritised

- FACT:** The Domino engine must be ISO C89. The Dominium UI/tools layer must be portable C++98. Engine code must not use OS APIs. Determinism matters, so floats are disallowed in deterministic paths. The engine must avoid platform-dependent behavior and hardcoded game semantics. Everything should be content-driven.
- Once the architecture stabilized, the user asked for a plan of prompts to give Codex. The assistant first produced an 8-prompt plan, but that was superseded after the sister-chat requirements. The final version became a 14-prompt roadmap.
- This was rejected because the sister-chat requirements explicitly required arbitrary position, rotation, inclination, and curved 3D geometry. Grids may exist as UI snapping aids or spatial indices, but not as authoritative placement logic.
- This was rejected because it breaks deterministic rebuilds, replay, arbitrary editing, and parametric placement. Baked geometry can exist as a derived cache, but it cannot be the authoritative state.
- This was rejected because the user specifically required corridor overlap and co-location through cross-section slots. Independent splines would fight for space and make upgrades, utilities, electrification, road/rail sharing, and junctions harder.
- This was rejected as the default because it does not scale. The accepted model uses vegetation fields, population aggregates, and deterministic promotion.
- This was rejected as unnecessary and too expensive. Group controllers and local bounded steering are preferred.
- This was rejected in the architecture because it would break deterministic ordering. Minds and controllers emit intents; actions emit deltas; the commit phase mutates state.
- This was rejected because fog of war affects knowledge and action validity. It must be simulation state, not a rendering trick.
- This was rejected because it would violate the no-hardcoded-semantics rule. Interstellar and Wargames should be content/DLC use cases of generic domains, frames, propagators, observers, beliefs, visibility, comms, and actions.

## What Future Work Came From It

- The chat then produced a maximum-fidelity context transfer packet and later a downloadable report package. Those are artifacts of preservation, but the substance of the chat is the architecture itself: a deterministic, modular, data-driven engine plan that can scale from plants and wildlife to cities, power grids, spacecraft, fog of war, and future DLCs without violating strict determinism.
- 4. deltas are applied later in a deterministic commit phase.
- The answer also introduced incremental compilation from edit buffers into derived artifacts: occupancy, ports, connectivity, enclosures, surfaces, supports, nav hints, and boundary lists. This later became a key part of the TRANS/STRUCT/DECOR prompt plan.
- The user introduced future **Interstellar** and **Wargames** DLCs. This could have led to hardcoded space and combat systems, but the answer deliberately generalized the requirements.
- The answer produced a delta plan showing what was already satisfied and what needed to be added. Then the user asked for the full new prompt plan.
- The assistant produced a full prompt plan for Codex. The user then requested each prompt one by one with "Next." Fourteen prompts were generated:
- The user then asked for a documentation validation prompt to ensure the docs remain valid, consistent, and correct. That prompt was generated as well.
- After the architecture and prompts were created, the user asked for a maximum-fidelity context transfer packet. The assistant produced one. The user then asked for a downloadable report package; the assistant generated package files and a ZIP. The user later asked for an in-chat reader version of that package, and finally requested this current human-readable explanatory report.
- The final state of the conversation is therefore not just an architecture. It is an architecture plus an implementation roadmap plus preservation artifacts. The important substance remains the deterministic engine design and the prompt plan, not the packaging files.
- What remains uncertain is the actual repository state. The chat designed architecture and prompts, but did not inspect source code. Therefore the plan needs repo verification before implementation.
- The unresolved work is to generate detailed subsystem implementation prompts for heat, power, fluids, atmospheres, vehicles, and structural loads after the core engine spine is implemented.
- deterministic scheduler phases;

## Important Artifacts

- `manifest`: `1`
- `primary_report`: `2`
- `prompt`: `1`
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
