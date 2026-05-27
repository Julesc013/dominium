Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Dominium_Architecture_II/`
Promotion Status: not_reviewed

# Dominium Architecture II - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about turning the **Dominium** game/engine from a broad, ambitious design into a coherent, Codex-ready architecture. The user had already explored many individual systems elsewhere or earlier in the same chat: railways, roadways, waterways, airways, spaceways, electrical networks, data networks, building systems, terrain, cut/fill, tunnels, bridges, arbitrary splines, deterministic simulation, cross-platform rendering, and retro-platform support. The purpose of this chat became to **unify those ideas into a small number of durable core systems**, then convert that architecture into documentation, directory contracts, Codex prompts, and finally a handoff package.

The central design problem was complexity. Dominium is not a small game concept. The user wants a deterministic simulation engine that can eventually support everything from dusty bicycle lanes and miniature railways to orbital stations, drop pods, interplanetary logistics, arbitrary buildings, power networks, data networks, roads, rails, waterways, airways, and spaceways. If every domain were implemented separately, the project would collapse under its own complexity. The major architectural solution reached in this chat was to generalise everything into a few reusable primitives: **Frames + Lattices**, **Archetypes + Components**, **Graphs + Fields**, **Blueprints + Diffs**, and **Ticks + Messages + Jobs**. These primitives are intended to explain almost everything in the game: a building, a tunnel, a railway, a power grid, a data network, a worker task, a cargo tug, an orbital station, or a cut-and-fill earthwork.

A second core theme was **determinism**. The user wants the engine to run deterministically across old and new platforms, from Windows 98, DOS, and macOS Classic through modern Windows, Linux, macOS, and future platforms. The simulation core must use integer or fixed-point math, avoid floating-point authoritative state, avoid nondeterministic threading, and run in strict tick phases. Rendering, audio, platform APIs, and UI must be separated from the simulation so they cannot affect game state. This led to an explicit platform/renderer split: platform backends handle windows, input, timers, files, and OS details; renderer backends handle DirectX/OpenGL/Vulkan/software drawing; the simulation knows neither.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`.

## What Was Decided

- The last part of the chat was handoff extraction. The user asked for discovery inventory, structured registers, a context transfer packet, and then a downloadable package. The generated package captured the chat's workstreams, decisions, tasks, constraints, open questions, artifacts, risks, and verification items. This current report is a plain-language explanation of that substance.
- The entire conversation is anchored by the requirement that Dominium must run deterministically. This means the same initial state and same inputs must produce the same state across machines, compilers, operating systems, and eventually retro and modern platforms.
- The chat discussed fixed tick phases, virtual lanes, merge order, command buffers, event queues, and deterministic serialization. The simulation must not depend on render FPS, wall-clock time, OS scheduler behaviour, GPU state, or floating-point quirks. This explains many later decisions: C89 core, integer/fixed-point math, no sim floats, no platform headers in simulation, and renderer as pure observer.
- What remains uncertain is the exact code-level API and component layouts. The chat produced specs and prompts, not final source code.
- The decision to use on-rails orbital mechanics mattered because it avoids the complexity of full n-body simulation. Instead of integrating every orbital body continuously, the game can use deterministic graph-like orbital states and transitions. This fits the rest of the engine: graphs, fields, frames, and state machines.
- Railways began as a major topic but later became part of the larger transport framework. Roads, waterways, airways, and spaceways were all discussed. The final architecture treats transport as graph/corridor/path systems. Rail and road use alignments and nodes. Water can use depth fields plus navigation graphs. Air can use flight corridors, runways, and holding patterns. Space uses orbital graphs.
- The final portion of the chat created a formal package of reports: full chat report, YAML spec sheet, aggregator packet, registers, reader brief, audit file, and manifest. These are not design decisions themselves, but they are important artifacts for later Project aggregation. The current response exists because the user wanted a human-readable explanation of the chat rather than more machine-readable outputs.
- The building-system goal also evolved. The user originally asked vector versus voxel. The final model became hybrid: discrete blocks/cells/faces/edges as sim truth, vector as authoring/generation/visual layer.
- Finalize render command and camera APIs.
- FACT: The user selected the meter-based option. This means one tile is one metre, with smaller subdivisions represented through fixed-point units. This made sense because the game is largely about buildings, infrastructure, vehicles, and terrain, where metre-scale cells are natural. Sub-metre detail remains possible without making the entire world millimetre-indexed.
- FACT: The user selected strict separation. Rendering and platform APIs cannot influence simulation. This decision was made because the user wants deterministic simulation across a wide range of systems, including old platforms. Graphics APIs, OS windows, timing, input polling, and GPU state are all platform-specific and nondeterministic from the simulation's perspective.
- FACT: The user provided the full scale ladder. This was accepted as the spatial basis. Its base-16 structure aligns with fixed-point subdivisions and chunk hierarchy. It affects chunk sizes, region scales, world streaming, serialization, and coordinate conversion.

## What Was Not Decided

- What remains uncertain is the exact code-level API and component layouts. The chat produced specs and prompts, not final source code.
- This is an important implementation detail, but some of it remains unverified. Lua 5.4.4 portability to old compilers needs testing. The exact Lua data schemas still need definition. The docs also still have JSON-oriented format sections, so the Lua-vs-JSON policy needs reconciliation.
- The biggest unresolved goals are practical:
- Verify DX9/Windows 2000, SDL2, Lua/toolchain compatibility.
- FACT: This was answered in response to Codex's clarifying questions. It is a concrete implementation direction, though Lua 5.4.4 portability remains unverified.
- 1. **Verify and apply V4 docs.
- The user repeatedly requested maximum-fidelity reports, registers, handoff packets, and human-readable summaries. The user wants labelled uncertainty and does not want future assistants to invent missing context.
- or forget that Lua-vs-JSON remains unresolved.
- The most important unresolved issue is **actual repo state**. The chat generated many documents, but it is unknown whether they were applied to disk. Before Codex implements anything, the repo must be inspected.
- Another major unresolved issue is **Lua data versus JSON formats**. The user explicitly wants Lua for all MVP data, but generated `DATA_FORMATS.md` and data specs include JSON-style formats. This may be acceptable if JSON is long-term and Lua is MVP, but the docs must say that clearly.
- The exact MVP component set is also unresolved. The chat implies Transform, occupancy, power node, fluid node, data node, worker/agent, building/device, prefab IDs, inventory/job state, and possibly simple vehicle/path components, but exact fields are not final.
- Major unresolved issues are actual repo state, Lua-vs-JSON policy, render command/camera API, external compatibility, MVP component fields, and licence validity.

## Ideas Rejected, Superseded, Or Deprioritised

- This solved both modularity and user control. Tunnel types do not contain special door code; door behaviour lives in door fixtures. Long empty tunnels can remain empty. Long tunnels with repeated utilities can use explicit pattern placement. Stations become compositions of platform corridors, building microgrids, portals, stairs, lifts, and fixtures.
- The chat discussed fixed tick phases, virtual lanes, merge order, command buffers, event queues, and deterministic serialization. The simulation must not depend on render FPS, wall-clock time, OS scheduler behaviour, GPU state, or floating-point quirks. This explains many later decisions: C89 core, integer/fixed-point math, no sim floats, no platform headers in simulation, and renderer as pure observer.
- What remains uncertain is the exact code-level API and component layouts. The chat produced specs and prompts, not final source code.
- A subtle but important user requirement was: do not code doors into every tunnel type, and do not make doors appear where not explicitly placed. The chat solved this with anchors/sockets and fixtures.
- The chat preserved several important "do not repeat this debate" outcomes.
- Pure vector simulation was rejected as the authoritative building/world model. It was considered because the user wanted arbitrary shapes, but it was rejected for runtime truth because continuous vector geometry is too hard to make deterministic, efficient, serializable, and retro-compatible. Vectors remain useful for authoring, visual skins, and generating discrete structures.
- Full n-body orbital mechanics was rejected for the main space model. It could perhaps return as an optional specialized system, but it is not the core and not MVP.
- Synchronous cross-surface simulation was rejected because it would undermine sharding and determinism. Cross-surface interactions should be asynchronous messages, trade, or scheduled transitions.
- Automatic doors in tunnels were rejected very clearly. Doors and devices must be explicitly placed fixtures.
- Runtime arbitrary spline math was rejected for simulation hot loops. Splines must bake into deterministic structures.

## What Future Work Came From It

- The last part of the chat was handoff extraction. The user asked for discovery inventory, structured registers, a context transfer packet, and then a downloadable package. The generated package captured the chat's workstreams, decisions, tasks, constraints, open questions, artifacts, risks, and verification items. This current report is a plain-language explanation of that substance.
- This matters because it prevented future implementation from chasing arbitrary continuous geometry in the deterministic core. The user wanted arbitrary shapes, but also deterministic integer math and old-platform support. The compromise was to allow rich authoring tools while baking runtime state into deterministic structures.
- The chat discussed fixed tick phases, virtual lanes, merge order, command buffers, event queues, and deterministic serialization. The simulation must not depend on render FPS, wall-clock time, OS scheduler behaviour, GPU state, or floating-point quirks. This explains many later decisions: C89 core, integer/fixed-point math, no sim floats, no platform headers in simulation, and renderer as pure observer.
- What remains uncertain is the exact code-level API and component layouts. The chat produced specs and prompts, not final source code.
- This was one of the most important conceptual outputs. It provides the future assistant with a mental model for everything else. Railways are graph/corridor systems. Buildings are microgrid frames plus archetypes and fixtures. Terrain is base fields plus delta fields. Power, data, and fluids are graph/field systems. Construction is blueprints and jobs. Space travel is an orbital graph/domain system.
- The default world is Earth in Sol in the Milky Way. The base game MVP is one surface, but the architecture should support galaxies, systems, planets, and future server/shard arrangements.
- The user also wanted buildings rigid for now but future collapse/destruction support. The conclusion was to include future-proof structural fields but not implement collapse in the MVP.
- This is important for future hydrology, geology, stability, collapse, pathing, and undo/history.
- The chat discussed electrical systems with DC, AC phases, voltages, frequencies, power factor, and traction integration. It also discussed data networks with fibre, copper, wireless, categories, protocols, bandwidth, latency, and telephony-like behaviour.
- The architecture unified these under graph/field networks. Power is a graph with nodes, edges, generation, loads, voltages, phases, transformers, breakers, and deterministic balancing. Data is a graph with packets/signals moving at deterministic hop latency. Fluids use pressure/flow graph models. Thermal and atmosphere can be fields or graph-assisted fields.
- The user provided an actual file tree and said Codex should work only from those files. The chat then updated the main docs and generated Codex prompts. This is a practical implementation layer: the architecture was converted into documents and prompts suitable for a code-generation agent.
- INFERENCE: The user wants a structure that can survive long-term development without collapsing under complexity. This is inferred from repeated requests for unification, directory contracts, modularity, extensibility, and Codex prompts.

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
