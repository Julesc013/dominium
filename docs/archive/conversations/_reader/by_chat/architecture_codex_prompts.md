Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/architecture_codex_prompts/`
Promotion Status: not_reviewed

# Dominium/Domino Architecture and Codex Prompt Roadmap - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

FACT: This chat was mainly about turning the user's Dominium/Domino game-engine vision into a coherent, modular, deterministic architecture and then into a long sequence of implementation prompts for Codex or another coding agent. It began with a large project-defining prompt from the user. That prompt established Domino as the low-level deterministic engine and Dominium as the game/product suite built on top of it. Domino is constrained to ISO C89, fixed-point math, strict platform abstraction, stable ABI, deterministic replay/network semantics, and broad portability from retro platforms through modern systems. Dominium is constrained to a portable C++98 subset and must remain a thin product layer rather than reimplementing engine systems.

FACT: The conversation then expanded from one subsystem-resources, items, recipes, entities, and extraction mechanics-into almost the entire engine and product ecosystem. We discussed how resource fields should work, how players should build factories, how conveyors and robotic manipulators should be modeled realistically without high CPU cost, how packaging and containers should reduce item simulation load, how arbitrary buildings and machine placement should work, how interior spaces should interact with rain, wind, gases, heat, pressure, pollution, radiation, and hydrology, how blueprints and reusable designs should be stored and shared, and how all of this should integrate with worldgen, save/load, mods, tools, launcher/setup, and future advanced simulation.

FACT: The central architectural theme that emerged was: **the engine must remain generic and data-driven**. Domino should not know about actual "iron ore," "drills," "belts," "factories," or other game-specific content. Instead, the engine should know generic concepts such as materials, items, containers, processes, deposits, structures, splines, ports, jobs, agents, zones, fields, models, IDs, tags, and TLV blobs. The actual game content belongs in packs, mods, blueprints, and TLV-defined data. This became one of the strongest carry-forward rules in the chat, especially after the user explicitly reminded that "our engine and core know nothing about the actual data definitions."

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, release, setup_launcher, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__human_readable_chat_report.txt`.

## What Was Decided

- The most important thing to remember is this: **this chat is the architectural and implementation-roadmap backbone for Dominium/Domino, but it is not an implementation log**. It should be preserved as a design/specification source and as a prompt library, while actual code and current facts must be verified separately.
- FACT: The user opened by pasting an "Extended Master Starter Prompt - Dominium + Domino." That prompt established the role of the assistant as a senior engine architect and defined the main project philosophy. Domino was described as a deterministic, fixed-point, C89 engine portable across old and modern OS/architecture combinations. Dominium was described as the product suite built on top of Domino.
- FACT: The user asked, succinctly, how a player would build a complete machine workshop. The assistant described a progression: extract raw materials, process them into industrial materials, produce mechanical components, produce electrical components, establish power distribution, establish logistics, assemble machine frames and machines, add measurement/control tooling, then scale horizontally and vertically.
- FACT: The user then said they wanted inserters and belts, but "much more realistic" and with "WAY less processing power." They wanted conveyors/inserters to make sense in real-world use cases, and suggested inserters might be more generic robot arms. They also wanted belts constructed as splines like roads and rails.
- FACT: The user explicitly wanted packaging into crates, bags, pallets, containers, jars, cans, boxes, etc. The stated purpose was to reduce the number of physical items simulated while preserving realistic packing/unpacking mechanics and obeying mass, volume, density, and other physical constraints.
- FACT: The user then asked how hydrology, atmology, lithology, light, rain, wind, temperature, pressure, pollution, magnetic fields, radiation, gases, and similar phenomena should work with buildings and enclosed spaces. They also asked how to support blueprints/templates and how to build realistically on sloped terrain without ugly foundation blocks or forced leveling.
- FACT: The user asked whether the whole system could be made more extensible and modular. The assistant proposed applying the same pattern everywhere: core + registry + models + data. This produced the repeated architecture model used later in prompts: each subsystem has a core API, model family/vtables, data prototypes, runtime instances, registries, TLV schemas, and save/load hooks.
- FACT: The user asked to summarize the entire system and then asked for the hierarchy of data definitions/types and how to implement actual items/functions/features. The assistant produced major architectural summaries: IDs, protos, models, instances, systems; resource/env/build/trans/items/struct/vehicle/blueprints/jobs/worldgen/save.
- FACT: The user asked for a plan for a prompt to Codex to implement all the changes and document them. Then the user asked how to split it into multiple prompts under ten. The assistant split the work into seven major prompts. The user then repeatedly said "Next," and the assistant generated Prompts 1 through 7 in detail.
- FACT: After the first seven prompts, the user said they wanted a minimal GUI and did not want to test only in CLI. They also reminded that the engine and core know nothing about actual data definitions and that those need to stay in base/mods/packs.
- This correction is one of the most important points in the chat: **the project must be GUI-testable and content-driven from the start.
- FACT: The user continued with "Next" and "Proceed," and prompts 13 through 18 were generated.

## What Was Not Decided

- UNCERTAIN / UNVERIFIED: No repository code was inspected or modified in this chat. The prompts and architecture are plans and artifacts, not proof that implementation exists. The actual repository state, build system, existing code quality, GUI backend availability, TLV schemas, and whether any prompts have been applied remain unverified.
- Uncertainty remains about actual repository code and build system, but the layering itself is a strong established principle.
- Unresolved issues include exact TLV schema field tags, exact registry implementation, base pack structure, and whether engine comments/docs may use examples with domain words.
- The main uncertainty is implementation: the prompts define it, but no code was verified.
- Unresolved details include exact process IO schemas, machine runtime state, and the relationship between autonomous machines and agent-operated jobs.
- Unresolved: exact nesting policy, allowed packing modes, and how far to model real packing constraints.
- Uncertainty remains about freeform geometry versus grid shell as the long-term building representation.
- The exact destruction and structural-load models remain unresolved and part of Path D.
- Unverified: actual save file format and current repo serialization code.
- The most important caveat is that actual repo state is unknown.
- Unverified: actual hash design and validators have not been implemented in this chat.
- UNCERTAIN / UNVERIFIED: Actual implementation remains unresolved. The prompts are ready, but no code was verified.

## Ideas Rejected, Superseded, Or Deprioritised

- The assistant responded by proposing that belts should be spline-based continuous transport entities, not grids of tile entities. Belts would move item packets or containers rather than every individual item. Inserters would become generic robotic manipulators: programmable, job-driven, with deterministic kinematics. This rejected a Factorio-style design where every belt tile and inserter constantly ticks.
- Rejected options here include Factorio-style tile/tick belts and per-item bulk simulation.
- 3. Engine/core do not contain actual gameplay data.
- This affects every implementation prompt. Codex must not use C99 mixed declarations, VLAs, C++11, exceptions, RTTI, or platform-specific convenience APIs unless explicitly allowed.
- This was rejected because the user wanted more realistic conveyors and lower processing cost. A per-tile, per-item simulation would produce excessive entity/tick load and push gameplay toward puzzle-like belt mechanics rather than realistic logistics. The replacement is spline-based transport with packets and containers.
- The pasted dres proposal explicitly rejected core knowledge of ore, oil, trees, mining drills, or wells. The chat carried that forward. Resource semantics belong in resource models and content prototypes, not the resource core.
- The starter prompt rejected OS-native drawing. All UI and rendering must go through `dgfx`, DVIEW, and DUI. This is final.
- The user explicitly rejected relying only on CLI. Headless and CLI remain necessary for servers, automation, and tools, but the user wants a minimal GUI smoke test early.
- The assistant deprioritized a full general rigid-body simulation for every object because it would be expensive and difficult to make deterministic across all targets. Instead, dynamic physics is constrained to vehicles, characters, movable props, debris, and other selected entities. Structures are static unless damaged.
- The assistant deprioritized full 3D CFD because it would be too expensive. The selected direction is coarse hydrology cells, environment fields, zones, volumes, and network solvers. This is a practical compromise.

## What Future Work Came From It

- UNCERTAIN / UNVERIFIED: No repository code was inspected or modified in this chat. The prompts and architecture are plans and artifacts, not proof that implementation exists. The actual repository state, build system, existing code quality, GUI backend availability, TLV schemas, and whether any prompts have been applied remain unverified.
- The most important thing to remember is this: **this chat is the architectural and implementation-roadmap backbone for Dominium/Domino, but it is not an implementation log**. It should be preserved as a design/specification source and as a prompt library, while actual code and current facts must be verified separately.
- FACT: The user opened by pasting an "Extended Master Starter Prompt - Dominium + Domino." That prompt established the role of the assistant as a senior engine architect and defined the main project philosophy. Domino was described as a deterministic, fixed-point, C89 engine portable across old and modern OS/architecture combinations. Dominium was described as the product suite built on top of Domino.
- This phase introduced one of the chat's most durable ideas: **engine systems should operate on generic IDs, tags, models, and TLV parameters, not hardcoded content families.
- FACT: The user asked whether the whole system could be made more extensible and modular. The assistant proposed applying the same pattern everywhere: core + registry + models + data. This produced the repeated architecture model used later in prompts: each subsystem has a core API, model family/vtables, data prototypes, runtime instances, registries, TLV schemas, and save/load hooks.
- FACT: The user asked for a plan for a prompt to Codex to implement all the changes and document them. Then the user asked how to split it into multiple prompts under ten. The assistant split the work into seven major prompts. The user then repeatedly said "Next," and the assistant generated Prompts 1 through 7 in detail.
- Those first seven prompts covered:
- FACT: After the first seven prompts, the user said they wanted a minimal GUI and did not want to test only in CLI. They also reminded that the engine and core know nothing about actual data definitions and that those need to stay in base/mods/packs.
- FACT: The user continued with "Next" and "Proceed," and prompts 13 through 18 were generated.
- FACT: The user then said they would branch out into another conversation and focus on "D." The assistant interpreted D as the advanced simulation path and generated a new-chat starter prompt focused on heat, power grids, fluids, atmosphere, vehicles, structural loads, destruction, and mod-extensible physics.
- The final state of the conversation is therefore: the architecture and implementation-roadmap discussion has been preserved, but the actual next work is elsewhere-especially the Path D advanced simulation conversation.
- This matters because resources can include ores, reservoirs, vegetation, aquifers, geothermal fields, or future exotic systems without rewriting the core.

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
