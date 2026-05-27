# Reader Brief — Domino/Dominium Engine Baseline, Architecture, and Feasibility

## What this chat was about

This chat examined the Domino engine and Dominium game at three levels: what the project is, what the current engine can actually do, and how to make the long-term vision feasible. It moved from broad architecture into hard current-state sequencing.

## Top 20 things to know

1. Domino should be the reusable deterministic substrate.
2. Dominium should be one game/rules/product layer on top.
3. The engine substrate is real, but not a finished playable engine.
4. The client advertises `support_claim_playable=false`.
5. The current playtest path is a target recipe, not one finished command.
6. Milestone 0 must come before builder/destruction work.
7. Milestone 0 means fixing local playtest blockers and strict validation.
8. Broad gameplay expansion should wait.
9. CAD should be supported but not required for normal play.
10. Ordinary players need templates/assisted authoring/accessibility modes.
11. Advanced users can have CAD-grade tooling.
12. Default gameplay should not rely on recipes, tech trees, or XP.
13. Those systems can exist in mods/game modes.
14. Building/destruction should likely use hybrid geometry, not voxel-first.
15. Full-scale universe simulation requires collapse/sparse fidelity.
16. Full fidelity everywhere is impossible.
17. Unreal may help as renderer/editor shell but not authoritative simulation core.
18. Clients can help compute only with proof/verification and no hidden-truth leaks.
19. Stable contracts matter more than directory aesthetics.
20. Preserve uncertainty: not every assistant recommendation is a user decision.

## Decisions

The key accepted decision is Milestone 0 first. The key architectural direction is contract-driven deterministic substrate with game/product layers on top.

## Pending tasks

Fix server import/CLI path, fix session create/boot, resolve bundle seam, fix time-anchor registry, add canonical playtest command, pass strict local playtest validator.

## Open questions

Exact playtest command, bundle default strategy, missing time-anchor registry, geometry provider choice, DesignArtifact schema, Unreal shell decision.

## Artifacts

The package includes full human report, registers, context transfer packet, spec sheet, aggregator packet, verification/audit file, future chat prompt, and in-chat reader.

## Best next step

Ask: “Write the Milestone 0 implementation prompt/task card for fixing the local playable baseline.”
