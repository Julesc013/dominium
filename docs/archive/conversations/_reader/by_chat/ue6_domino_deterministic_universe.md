Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/UE6_Domino_Deterministic_Universe/`
Promotion Status: not_reviewed

# Dominium UE6, Domino, and Deterministic Universe Feasibility - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about whether Dominium could or should be built on Unreal Engine 6, Unreal Engine 5, Domino, or some custom architecture that uses a commercial engine only as a frontend. The user began by pasting a confident external-style answer claiming that UE6 had been unveiled, that UE6 would raise baseline OS requirements, and that high-performance UE6 games would probably require modern Windows, macOS, and Linux targets. The user then asked the key strategic question: could Dominium be made on UE6 instead of Domino, and could it be made portable to Domino later?

The first answer established the central architectural position of this chat: Dominium should not wait for UE6 or treat UE6 as the whole game platform. The recommended path was to build using current Unreal technology where useful, structure the project for a future UE6 transition, and preserve portability to Domino by keeping the durable game logic outside Unreal-specific systems. The important distinction was between the game itself and the engine used to render or host it. The answer framed DominiumCore as the permanent game, Unreal or UE6 as one possible renderer/runtime, and Domino as a later renderer/runtime. That distinction matters because Dominium's broader design is not a conventional Unreal game. It is intended to be a long-lived, portable, deterministic, multi-platform, simulation-heavy project.

The user then escalated the technical scope substantially. They asked whether UE5, UE6, or any other engine could handle a deterministic full-scale real solar system with fully recreated procedural planets, player-built civilizations, terraforming, cut-and-fill terrain, megaprojects, machine/device/factory design, fog of war, sparse simulation, collapsed unobserved regions, single-player multi-universe gameplay, an MMORPG single universe, and client-shared compute where each client simulates its own area or assists other areas when servers cannot keep up. The user also asked whether Unreal could do this without lag, with low latency, at high FPS, and with millions of players in the same universe.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `15` source files. The primary extracted source is `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__01_human_readable_report.md`.

## What Was Decided

- FACT: This package preserves the currently visible chat about whether Dominium should use UE6, UE5, Domino, Unreal, or a custom engine layer for a highly ambitious deterministic solar-system-scale game. It also preserves the current uploaded prompt as an artifact because it defines this preservation task.
- That response also introduced a rule that shaped the rest of the chat: Unreal should render and host Dominium, but Unreal should not define Dominium. That was the first major conceptual decision point. It reframed Dominium not as an engine project in the narrow sense, but as a portable game/simulation system with replaceable frontends.
- Conclusion: machine gameplay must be designed as a scalable graph simulation, not as unrestricted physics.
- The user asked whether every client can share compute load. The answer said this is only safe in limited forms. The core pattern must be client proposes, server verifies, server commits. Full client authority would break the economy, fog of war, and anti-cheat model.
- The chat did not settle whether Unreal should definitely be used as the first client. It recommended Unreal as a plausible first high-quality frontend, but the final choice still depends on prototype results, licensing, team capacity, platform targets, and how much custom simulation work is required.
- The assistant recommended against starting directly on UE6 because public technical access and production documentation were not treated as available in the visible chat. This was not framed as a permanent rejection of UE6. It was a timing decision: do not wait for a future engine to solve current architecture problems.
- This is the highest-value decision candidate. Core rules, simulation, save format, economy, factory logic, fog-of-war state, and replay/hash systems should be portable. This matters because Domino portability is only plausible if the core does not depend on Unreal object lifecycles and assets.
- The chat rejected the idea that clients can authoritatively simulate resource production, hidden state, enemy bases, combat, or persistent terrain changes in an MMO. Clients can assist, but the server must verify and commit.
- The chat accepted a practical definition of a single universe: one persistent identity and shared world, partitioned across regions, servers, databases, and interest sets. It rejected the literal idea that millions of players can all share one local mutually interacting space at low latency and high FPS.
- The central tradeoff is between engine convenience and architectural control. Unreal gives rendering, tooling, animation, UI, asset workflows, and a mature editor. But the more Dominium relies on Unreal for gameplay truth, the harder determinism, portability, and Domino migration become.
- A fourth tradeoff is between single-universe identity and local concurrency. A single persistent universe is plausible. A single local space with millions of fully relevant players is not. Dominium must use spatial partitioning, interest management, time dilation or degradation modes, region caps, and possibly soft instancing for local overload.
- UNCERTAIN: The final intended role of Domino remains unclear in the visible transcript. It may be a custom engine, target runtime, renderer, or broader platform plan, but the current chat does not fully define it.

## What Was Not Decided

- UNCERTAIN / UNVERIFIED: This is not a complete reconstruction of every Dominium conversation ever held. The project context shows that many other chats exist about platforms, renderers, setup, game architecture, ecology, ECS, launcher design, and development planning, but their full transcripts are not visible here. Those items are labelled PROJECT-CONTEXT when referenced.
- Uncertainty: public UE6 technical capabilities and requirements remain time-sensitive and need verification before any future hard commitment.
- The chat rejected the idea that clients can authoritatively simulate resource production, hidden state, enemy bases, combat, or persistent terrain changes in an MMO. Clients can assist, but the server must verify and commit.
- REJECTED-02: Waiting for UE6 before beginning serious work. Deprioritised because UE6 availability and capabilities remain uncertain.
- The user wants direct, source-grounded, audit-ready answers; explicit uncertainty; bounded estimates; and correction when framing is wrong. The preservation prompt explicitly requires human-readable explanation first, structured registers second, uncertainty labels, no invented facts, no hidden chain-of-thought, and downloadable files if tools are available.
- UNCERTAIN: The final intended role of Domino remains unclear in the visible transcript. It may be a custom engine, target runtime, renderer, or broader platform plan, but the current chat does not fully define it.

## Ideas Rejected, Superseded, Or Deprioritised

- For a future assistant or human reader, the key thing to understand is that the chat did not reject Unreal. It rejected the idea that Unreal or UE6 could be the complete solution. The direction is hybrid: custom simulation and backend as the real engine, Unreal as the first high-quality client, UE6 as a possible future upgrade, and Domino as a possible later frontend/runtime if the core remains portable.
- Conclusion: use Unreal/UE5 as a practical client layer if useful, do not wait for UE6, and do not make Unreal-specific systems the canonical game.
- The assistant recommended against starting directly on UE6 because public technical access and production documentation were not treated as available in the visible chat. This was not framed as a permanent rejection of UE6. It was a timing decision: do not wait for a future engine to solve current architecture problems.
- The chat treated Unreal as valuable for rendering, animation, editor workflows, UI, construction preview, and visual streaming. It should not own the canonical simulation. The alternative was an "Unreal is the whole game" approach, which was rejected because it would entangle gameplay with engine-specific non-deterministic systems.
- The chat rejected the idea that clients can authoritatively simulate resource production, hidden state, enemy bases, combat, or persistent terrain changes in an MMO. Clients can assist, but the server must verify and commit.
- The chat accepted a practical definition of a single universe: one persistent identity and shared world, partitioned across regions, servers, databases, and interest sets. It rejected the literal idea that millions of players can all share one local mutually interacting space at low latency and high FPS.
- REJECTED-01: Treating Unreal or UE6 as the whole game engine. Rejected because determinism, persistence, server authority, and portability need custom control.
- REJECTED-02: Waiting for UE6 before beginning serious work. Deprioritised because UE6 availability and capabilities remain uncertain.
- REJECTED-03: Trusting clients with persistent MMO simulation. Rejected for anti-cheat, fog-of-war, and economy-integrity reasons.
- REJECTED-04: Supporting millions of players in one local fully interactive space at low latency. Rejected as a networking and computation impossibility under normal internet/consumer-client assumptions.

## What Future Work Came From It

- FACT: This package preserves the currently visible chat about whether Dominium should use UE6, UE5, Domino, Unreal, or a custom engine layer for a highly ambitious deterministic solar-system-scale game. It also preserves the current uploaded prompt as an artifact because it defines this preservation task.
- For a future assistant or human reader, the key thing to understand is that the chat did not reject Unreal. It rejected the idea that Unreal or UE6 could be the complete solution. The direction is hybrid: custom simulation and backend as the real engine, Unreal as the first high-quality client, UE6 as a possible future upgrade, and Domino as a possible later frontend/runtime if the core remains portable.
- The answer then proposed the architecture that became the main deliverable of the chat: `DominiumSim`, `DominiumWorldDB`, `DominiumServer`, `DominiumClient_UE`, and `DominiumClient_Domino`. This architecture makes the core simulation, world storage, and server authority independent from the renderer. Unreal becomes an adapter, not the source of truth. Domino becomes a future adapter if the project requires it.
- The first topic was whether Dominium should be made on UE6 instead of Domino. The answer separated availability from suitability. UE6 was treated as not yet available enough for production planning. UE5 was treated as a practical near-term renderer/tooling base. Domino was treated as a possible future runtime or custom engine path, not something that can be reached by automatically exporting an Unreal project.
- Uncertainty: public UE6 technical capabilities and requirements remain time-sensitive and need verification before any future hard commitment.
- The assistant recommended against starting directly on UE6 because public technical access and production documentation were not treated as available in the visible chat. This was not framed as a permanent rejection of UE6. It was a timing decision: do not wait for a future engine to solve current architecture problems.
- This is the highest-value decision candidate. Core rules, simulation, save format, economy, factory logic, fog-of-war state, and replay/hash systems should be portable. This matters because Domino portability is only plausible if the core does not depend on Unreal object lifecycles and assets.
- The chat recommended making Domino a future adapter target. Portability comes from architecture, not from a future conversion button.
- The recommended roadmap is staged:
- The user wants direct, source-grounded, audit-ready answers; explicit uncertainty; bounded estimates; and correction when framing is wrong. The preservation prompt explicitly requires human-readable explanation first, structured registers second, uncertainty labels, no invented facts, no hidden chain-of-thought, and downloadable files if tools are available.
- INFERENCE: The user values long-term architectural optionality more than short-term engine convenience. They also prefer explicit handling of failure modes, stale facts, and future aggregation.
- ARTIFACT-05: Uploaded `Pasted text.txt`. Purpose: maximum-fidelity preservation prompt.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
- `markdown`: `2`
- `primary_report`: `2`
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
