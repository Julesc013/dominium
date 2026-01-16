--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_SIM — Simulation Orchestrators (DSIM vs SIM Scheduler)

This repository currently contains two simulation orchestration layers:

- **DSIM (`d_sim_*`)**: a legacy deterministic tick loop used to advance a world
  and call subsystem ticks in a fixed order.
- **SIM scheduler (`dg_sched_*`)**: the refactor scheduler specified by
  `docs/SPEC_SIM_SCHEDULER.md` (phase-ordered, delta-commit based).

This spec describes DSIM’s contract and its relationship to the refactor
scheduler.

## DSIM (legacy deterministic tick loop)
Implementation: `source/domino/sim/d_sim.c`

Authoritative contract:
- Simulation advances in integer ticks (`tick_index`); tick count is authoritative.
- `d_sim_step(ctx, ticks)` increments tick counters deterministically and runs:
  1. deterministic net command application for the tick (`d_net_apply_for_tick`)
  2. subsystem ticks via the subsystem registry (`d_subsystem_desc.tick`)
  3. DSIM-local system callbacks registered via `d_sim_register_system`
- Ordering is deterministic:
  - subsystem iteration order is `d_subsystem_get_by_index(i)` (stable registry order)
  - DSIM system callbacks run in DSIM registration order
- DSIM code and all tick callbacks must obey `docs/SPEC_DETERMINISM.md`.

DSIM is a compatibility orchestrator. It does not define the phase-based
stimulus/action/delta/commit semantics; those are specified by the SIM scheduler
spec below.

## SIM scheduler (refactor)
Authoritative phase ordering, delta commit rules, and canonical ordering keys
are specified in `docs/SPEC_SIM_SCHEDULER.md` and implemented under
`source/domino/sim/sched/**`.

Refactor rule:
- Any subsystem/module that participates in the refactor scheduler MUST obey
  the phase boundaries and delta-commit mutation rules from
  `docs/SPEC_SIM_SCHEDULER.md` and `docs/SPEC_ACTIONS.md`.

## Forbidden behaviors (both)
- Using wall-clock time, OS input, or thread timing as a simulation input.
- Unordered iteration (hash-table iteration order, pointer identity) in any
  deterministic tick path.
- Treating derived caches (including compiled artifacts and render geometry) as
  authoritative state.

## Related specs
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_DETERMINISM.md`
