Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/World_Architecture/`
Promotion Status: not_reviewed

# Dominium World Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about designing the foundational world architecture for **Dominium**, especially its spatial model, coordinate system, save format, terrain representation, environmental simulation model, deterministic core constraints, mod/content architecture, and the path toward implementation through Codex.

At the beginning, the discussion was narrow: the user was choosing fixed-point coordinate precision for a world divided into powers-of-two spatial units. That quickly expanded into a much larger architecture question: how should an enormous procedural world be represented, simulated, saved, streamed, rendered, modified, and extended without becoming inconsistent, bloated, or impossible to maintain?

The core problem was this: the user wanted a world that can be both **large and deterministic**, both **smooth and chunked**, both **procedural and editable**, both **content-driven and mod-friendly**, and both **performance-conscious and future-proof**. The game world is not meant to be a simple voxel block world. The ground, air, water, oil, gases, rocks, caves, rivers, buildings, tanks, pipes, and weather are all meant to be represented through abstract fields, spaces, materials, and networks rather than as naive block-by-block matter. At the same time, the world still needs practical chunking, sparse saves, and efficient runtime loading.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, release, setup_launcher, simulation, timekeeping, tooling, ui, workbench, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/World_Architecture/Dominium_World_Architecture__human_readable_chat_report.txt`.

## What Was Decided

- The future relevance of this chat is high. It should feed directly into the future project spec book and into a corrected implementation prompt. But it should not be treated as final implementation detail everywhere. Many high-level decisions are settled, but solver formulas, exact file encoding details, build system integration, actual repository layout, and some numerical representations still require verification.
- Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular, content-driven, and field-based. Chunks are not the world. Chunks are just how the world is cached, meshed, streamed, and saved.
- This comparison was not a final technical dependency, but it helped clarify the design goal: Dominium should not simply copy any one of these systems. It should combine their useful elements while avoiding their limits.
- The user then introduced and refined a power-of-two naming system. The final scale names are:
- This was a major turning point because it standardized the vocabulary. "Country," "state," and other geographic names were discarded in favor of neutral, technical scale names. The user also refined the universe addressing model over time. Earlier values changed; the final stated limits became `2^8` galaxies per universe, `2^24` systems per galaxy, and `2^16` planets per system.
- A key refinement came when the user decided that working memory should use Q16.16 and save files should store Q4.12. This was important because it separated high-precision transient simulation from compact persistent storage. Runtime moving objects get finer precision. Static or saved objects are represented locally within chunks.
- Another major decision was that untouched chunks should not be saved. Even if a procedural chunk is loaded temporarily for rendering or collision, it should not become persistent unless it contains actual dynamic state or overrides. This led to the distinction between untouched, procedural, and overridden chunks. Procedural chunks are temporary caches. Overridden chunks contain edits, objects, or saved changes.
- Near the end, the user asked for a Codex 5.1 implementation prompt. A long prompt was produced, instructing Codex to implement the engine core, fixed-point types, world addressing, chunking, save formats, ECS, engine API, runtime CLI, and docs. Later, the context packet and final report package audited that prompt and found important defects. The prompt is useful, but not safe to use directly.
- The chat was then retired. A maximum-fidelity Context Transfer Packet was produced, followed by a downloadable report package, and finally an in-chat reader version. The current report is a human-readable briefing of the substance of the whole conversation.
- The first topic was how to represent positions in a very large world. The early idea was Q24.8 or similar global fixed-point coordinates, but the design evolved. The final user-confirmed direction is Segment plus Q16.16 runtime coordinates and Q4.12 chunk-local save coordinates.
- FACT:** The horizontal world is a toroidal `2^24m` SurfaceGrid. **FACT:** Each Segment is `2^16m`, so 8-bit Segment indices cover the full horizontal SurfaceGrid. **FACT:** Runtime precision is Q16.16. **FACT:** Save precision is Q4.12 inside a 16m chunk.
- The main unresolved issue is implementation detail. The design says Q16.16 and Q4.12, but the earlier prompt used signed types incorrectly. The future implementation must use unsigned local coordinates or a centered signed design.

## What Was Not Decided

- The main unresolved issue is implementation detail. The design says Q16.16 and Q4.12, but the earlier prompt used signed types incorrectly. The future implementation must use unsigned local coordinates or a centered signed design.
- The unresolved parts are the exact meshing algorithm, the fixed-point scaling of `?`, and the sample resolution. A 32? sample grid per 16m chunk was recommended but not confirmed as final.
- The exact solvers remain unresolved. The architecture is clear, but formulas and resolutions are still future work.
- The save format remains conceptual in places. Exact binary headers, endian policy, compression, and migration strategy are unresolved.
- The crucial caveat is implementation: unsigned or centered representations are needed. The design intent is final, but the exact typedefs must be fixed. If the implementation uses signed types incorrectly, the whole coordinate system breaks.
- This is not yet an implementation-level final spec because solver formulas are unresolved.
- FACT:** Core target is C89. This is non-negotiable in principle, but exact portability mechanics are unresolved because strict C89 lacks standard fixed-width integer types.
- The user wants direct, detailed, rigorous, critical responses. The user prefers source labels, uncertainty preservation, and avoiding invented facts. The user does not want assistant suggestions silently upgraded to decisions.
- The most important unresolved issue is the fixed-point implementation detail. The user chose Q16.16 runtime and Q4.12 save-local, but the implementation must choose the exact signed/unsigned representation. The prior prompt's signed version is invalid. This must be resolved before code.
- The second major unresolved issue is C89 portability. The user wants C89, but the architecture needs 64-bit IDs, RNG states, and accumulators. Strict ISO C89 does not standardize `stdint.h` or 64-bit integer types. A portability layer or compiler-extension policy is required.
- The third unresolved issue is exact save encoding. TLV, Region files, content locks, and sparse saves were designed conceptually, but endian policy, padding, alignment, compression, and path grammar still need specification.
- The fourth unresolved issue is solver math. FluidSpaces, weather, hydrology, oil pressure, ruptures, hydraulics, thermal systems, and electrical networks were designed architecturally, but formulas and fixed-point scales are not final. These do not block v0 core implementation but must be resolved before those systems are coded.

## Ideas Rejected, Superseded, Or Deprioritised

- This decision is final and central. Any future assistant must not suggest floats inside the deterministic core unless the user explicitly reverses the rule.
- FACT:** The user explicitly rejected ground and air being made of blocks. The conclusion was to represent terrain as a continuous signed field `?` and use material/media fields to determine what matter is present.
- FACT:** A Codex prompt was generated. **FACT:** Later audit found it defective. It must not be used unchanged. This is a decision because it changes the next action: repair the prompt before any implementation attempt.
- This was an early recommendation. It made sense as a simple global coordinate format, but it was superseded by Segment + Q16.16 runtime and Q4.12 save-local. The earlier idea can still be relevant for external APIs or debugging, but it is not the final internal model.
- This was considered only because the user asked about 8, 16, or 32 fractional bits. It was rejected as extreme overprecision. Atomic-scale or near-atomic fractional detail is irrelevant to this game's world, and it would waste memory/storage.
- Assistant suggested some geographic names when the user wanted to rename "country." The user later replaced all of that with the final scale names: Plank, Point, Step, Sixteenth, Block, Chunk, Region, Page, Segment, Sector, Surface. The earlier naming is superseded.
- The user wanted arbitrary surface instances internally for future sharding, but later explicitly said only one canonical surface per planet should be saved for now. Multiple saved surface instances are therefore deferred, not permanently rejected. They should be reconsidered when sharding/dimensions require them.
- The user explicitly rejected this. Ground and air should be abstract materials/media interpreted from fields and systems. Blocks remain useful as logical units, but not as the physical substance of the ground or atmosphere.
- This was rejected because it would explode storage and make material representation awkward. Instead, the design uses one geometry field, material IDs, phase/composition fields, derived density/hardness, and sparse overlays or SpatialVolumes.
- The user wanted liquids and gases, but not necessarily a voxel fluid world. The design uses hydrology graphs, basins, heightfields, FluidSpaces, and connectors. Full global Navier-Stokes is rejected as too expensive and unnecessary.

## What Future Work Came From It

- The future relevance of this chat is high. It should feed directly into the future project spec book and into a corrected implementation prompt. But it should not be treated as final implementation detail everywhere. Many high-level decisions are settled, but solver formulas, exact file encoding details, build system integration, actual repository layout, and some numerical representations still require verification.
- Near the end, the user asked for a Codex 5.1 implementation prompt. A long prompt was produced, instructing Codex to implement the engine core, fixed-point types, world addressing, chunking, save formats, ECS, engine API, runtime CLI, and docs. Later, the context packet and final report package audited that prompt and found important defects. The prompt is useful, but not safe to use directly.
- The main unresolved issue is implementation detail. The design says Q16.16 and Q4.12, but the earlier prompt used signed types incorrectly. The future implementation must use unsigned local coordinates or a centered signed design.
- A subtle but important correction emerged later: within a Segment of `2^16m`, a Region of `2^8m` means there are 256 Regions per Segment per axis. Therefore Region-in-Segment is 8 bits, not 4 bits. Some earlier generated prompt text got this wrong and must be corrected.
- The exact solvers remain unresolved. The architecture is clear, but formulas and resolutions are still future work.
- The user wanted the same future-proof philosophy applied to the entire project. The resulting pattern was:
- A major artifact was a Codex 5.1 prompt. It was designed to tell Codex to implement the architecture in a repo. It included modules, headers, save formats, engine API, CLI runtime, and docs.
- Later audit found it defective. It should be repaired before use. The known issues are signed fixed-point types, Region bit-width inconsistency, C89-incompatible constructs, and saved rotation ambiguity. The best next practical step is to revise that prompt using the corrected report.
- FACT:** The user wanted a Codex implementation prompt and then a context/report package.
- INFERENCE:** The user wanted to avoid painting the project into a corner. The repeated requests for future-proofing, modularity, extensibility, deterministic core, and content-agnostic modding imply a strong preference for long-term maintainability.
- The meaning of "surface" also became more precise over time. It started as a scale name, then became a saved canonical planet surface, while arbitrary surface instances became a future/internal sharding option.
- The chat did not resolve exact solver math, exact repository integration, exact C89 portability strategy, exact binary file encoding details, exact meshing algorithm, or exact content/Lua schemas. These remain future work.

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
