Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Interest Set Implementation Guide (SCALE1)

This guide defines the required Interest Set implementation patterns for Dominium.
Interest Sets are the ONLY mechanism that activates simulation, refinement, and processing.

## Canonical data model

**MUST**
- Use stable IDs only (system_id, region_id, entity_id, route_id, org_id).
- Store `interest_reason`, `interest_strength`, and `expiry_tick` per entry.
- Provide deterministic ordering and deduplication.

**MUST NOT**
- Use camera/view state as a proxy for interest.
- Depend on insertion order for membership or ordering.

## Required sources

Interest sources MUST be explicit and enumerable:
- Player control/focus
- Active CommandIntents
- Logistics routes and shipments
- Sensors and comm endpoints
- Hazards/conflicts
- Governance scope

Sources live in `game/` and emit entries via `dom_interest_emit_*`.

## Aggregation rules

**MUST**
- Aggregate deterministically (union of sources).
- Apply stable tie-breaking (by ID, kind, reason).
- Apply hysteresis (enter thresholds > exit thresholds).
- Enforce bounded size and overflow reporting.

**MUST NOT**
- Iterate global registries to find interest.
- Hide missing interest by falling back to “tick all”.

## Correct usage (examples)

### Macro update

```c
dom_interest_set set;
dom_macro_stats stats;

dom_interest_set_init(&set);
dom_interest_set_reserve(&set, 1024u);
/* emit sources */
dom_interest_set_finalize(&set);
dom_macro_step(&set, &stats);
```

### Transition application

```c
dom_interest_policy policy = { 50u, 40u, 80u, 60u, 2 };
dom_interest_state_apply(&set, states, state_count, &policy, now_tick, transitions, &cap);
```

## Anti-patterns (forbidden)

- `update_all_*` or `tick_all_*` loops in authoritative paths.
- Rendering or UI visibility used to activate simulation.
- Implicit interest derived from camera distance.

## Migration guide for legacy “tick all”

1) Identify the global update loop.
2) Define stable IDs for the objects being processed.
3) Emit interest entries from explicit sources only.
4) Pass the InterestSet into the update function.
5) Remove any fallback global scans.
6) Add tests for:
   - latent universe
   - deterministic ordering
   - hysteresis stability

## CI enforcement

CI fails on:
- Missing InterestSet parameters in macro/meso update paths (SCALE-INT-001).
- Camera/view-driven activation in authoritative code (SCALE-INT-002).

See `docs/CI_ENFORCEMENT_MATRIX.md` for details.