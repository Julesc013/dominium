Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Agent Non-Goals (AGENT0)

Status: binding.
Scope: explicit non-goals and forbidden assumptions for agents.

## Non-goals
- Agents MUST NOT implement planning algorithms, behavior trees, or AI solvers.
- Agents MUST NOT be scripted quest givers, UI avatars, or hardcoded AI archetypes.
- Agents MUST NOT be treated as physics objects or rendering primitives.
- Agents MUST NOT assume human-centric defaults (player, conscious, or biological).
- Agents MUST NOT rely on "AI magic" or hidden autonomy.

## Out of scope for AGENT0
- Goal selection, planning, doctrine, and aggregation are defined elsewhere and MUST NOT be implied here.
- UI controls, player input, and controller bindings are external interfaces, not agent identity.

## References
- `../arch/INVARIANTS.md`
- `../arch/REALITY_LAYER.md`
