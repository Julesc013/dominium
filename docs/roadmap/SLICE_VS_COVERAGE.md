# Slice vs Coverage (ROADMAP)

Status: planning.
Scope: distinguishes player capability milestones from simulation coverage.

Slices are player-facing capability milestones.
Coverage is simulation representability goals.

Runtime code MUST NEVER branch on coverage or era.
Coverage is enforced by TESTX, not gameplay.

## Slice ladder (planning)
| Slice | Player can do |
| --- | --- |
| Slice-0 | Load, inspect, and replay a world without authoritative action. |
| Slice-1 | Perform limited authoritative actions through law/capability gates. |
| Slice-2 | Sustain a minimal play loop with persistence and institutional actors. |
| Slice-3 | Operate the full MVP loop with toolchain parity and enforcement. |

## Coverage ladder (planning)
Coverage categories are defined and enforced by TESTX. This table is descriptive
only and must align to TESTX invariants.

| Coverage | Engine can represent |
| --- | --- |
| C-A | Existence, time, determinism, and law primitives. |
| C-B | Space, domains, travel, and scheduling constraints. |
| C-C | Fields, structures, resources, and material states. |
| C-D | Agents, institutions, authority, and capability boundaries. |
| C-E | Economy, logistics, and production chains. |
| C-F | Epistemics, knowledge diffusion, and history/replay integrity. |
| C-G | Worldgen refinement across scales with bounded budgets. |
