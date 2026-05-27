# In-Chat Reader — Domino/Dominium Engine Baseline, Architecture, and Feasibility

## Package overview

This package preserves a chat about the Domino engine and Dominium game: project identity, engine state, feasibility, modularity, CAD/building, geometry/destruction, full-scale universe architecture, Unreal comparison, and baseline-first roadmap.

## File index

Read `01_human_readable_report.md` first for context. Use `04_registers.md` for structured tasks and decisions. Use `05_aggregator_packet.md` for merging with other old-chat reports. Use `03_spec_sheet.yaml` for machine-assisted aggregation.

## Plain-English explanation

The chat concluded that the project has a real deterministic substrate but not a finished playable game engine. The most important next action is Milestone 0: make one canonical repo-local playable baseline command pass strict validation. Only after that should the project begin a tiny builder/destruction lab.

## Question menu

- What exactly is Milestone 0?
- Which blockers are P0?
- Which ideas are final decisions and which are recommendations?
- What should go into the master spec book?
- What needs verification?
- How should the first build/destroy slice be scoped?

## Top things to preserve

- Baseline-first sequencing.
- Domino/Dominium boundary.
- No default recipes/tech trees/levels.
- CAD-capable but not CAD-required authoring.
- Hybrid geometry recommendation.
- Full scale, not full fidelity.
- User-pasted readiness correction.

## Safest next actions

1. Reproduce current baseline blockers.
2. Fix circular import.
3. Fix session create/boot.
4. Fix time-anchor registry.
5. Implement one canonical strict playtest command.
