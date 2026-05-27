# READER BRIEF — Dominium UE6, Domino, and Deterministic Universe Feasibility

## What this chat was about

This chat asked whether Dominium should use UE6, UE5/Unreal, Domino, or a custom architecture for a deterministic, planet-scale, sparse, MMO-capable civilization/factory/terraforming game. The answer was that no commercial engine solves the full problem. Unreal can be useful as a frontend; the canonical game must be a custom deterministic simulation/world/server system.

## Top 20 things to know

1. Do not treat UE6 as the current production foundation without verification.
2. UE5/Unreal can be useful for rendering and tooling.
3. Unreal should not own canonical game state.
4. Domino portability requires engine-independent rules and data.
5. Dominium’s real engine is `DominiumSim + DominiumWorldDB + DominiumServer`.
6. Determinism requires fixed-step simulation and controlled math/order.
7. Full-scale solar systems require coordinate hierarchy, not one flat scene.
8. Procedural planets should use seeds plus sparse deltas.
9. Terraforming needs chunked/sparse terrain representation.
10. Factories should be graph simulations.
11. Unseen areas need collapse/refine simulation.
12. Fog of war requires server-side sensory authority.
13. Hidden state must not be sent to clients.
14. Clients can propose work but not commit persistent MMO outcomes.
15. One shared universe is plausible with partitioned authority.
16. Millions of players in one local fully interactive area is not plausible.
17. Player-made machines need operation/gas limits.
18. External UE facts need verification.
19. Domino’s exact role is unresolved.
20. The next task is a deterministic headless prototype spec.

## Decisions

Main decision candidates: custom deterministic core; Unreal as frontend only; server-authoritative MMO state; sparse procedural planets; single universe via partitioning; Domino as future adapter.

## Pending tasks

Define the simulation MVP, prototype deterministic tick/replay/hash, design coordinate hierarchy, prototype terrain chunks, design factory graphs, define collapse/refine invariants, clarify Domino, verify UE facts.

## Open questions

What is Domino exactly? Should Unreal be first frontend? Which language/math stack should DominiumSim use? What terrain model is best? How exact must collapsed simulation be? What first MMO scale target is realistic?

## Artifacts

The package includes a human report, context transfer packet, spec sheet, registers, aggregator packet, reader brief, audit file, future chat bootstrap prompt, in-chat reader, and ZIP.

## Best next step

Write a formal `DominiumSim` deterministic MVP spec.
