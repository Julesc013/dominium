Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

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

## Coverage ladder (authoritative)
The canonical coverage ladder is defined in:
- `docs/roadmap/SIMULATION_COVERAGE_LADDER.md`

This document intentionally avoids duplicating the ladder to prevent drift.