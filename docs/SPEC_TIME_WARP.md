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
# SPEC_TIME_WARP — Time Warp and Batch Scheduler Canon

Status: draft  
Version: 1

## Purpose
Define the deterministic time warp model that controls how ACT advances relative
to wall-clock time without introducing local clocks, causality changes, or
non-deterministic batching.

## Core axioms
- ACT is the only authoritative timebase.
- Warp changes pacing, not physics or event semantics.
- Batch stepping is equivalent to step-by-step.
- Event order is invariant under warp.
- Warp is constrained by lane state, fidelity, and authority rules.
- Multiplayer semantics are identical across SP, lockstep, and server-auth.

## Definitions
### Sim rate
Scalar defining ACT seconds advanced per real second.

Examples:
- 1/86400 (1 ACT second per real day)
- 1       (real time)
- 3.15e10 (~1 ACT millennium per real second)

### Time warp state
Immutable, deterministic parameters:
- sim_rate
- warp_policy
- allowed_max_rate
- interrupt_conditions

### Lane state
Context classification that caps warp:
- LOCAL (micro interaction)
- MESO (facility/city)
- MACRO (strategic)
- ORBITAL / LOGISTICS

Each lane defines a maximum safe sim_rate and any required collapse-to-rails
rules.

### Interrupt condition
Deterministic predicate that reduces or stops warp, e.g.:
- arrival event
- hazard spike
- message delivered
- construction complete
- command delivery

## Time warp model
Warp applies only to ACT advancement. The core model is:

  real_time_delta * sim_rate = ACT_delta
  ACT_target = ACT_now + ACT_delta
  process events in order up to ACT_target

ASCII diagram:

  [ real time ] --(sim_rate)--> [ ACT delta ]
        |                              |
        v                              v
    [ ACT target ] ------> [ batch process events <= target ]

## Batch execution rules
- ACT_delta may be split into safe batches.
- All events execute in deterministic order:
  1) trigger_time
  2) stable secondary key
- Batch execution MUST equal step-by-step execution.
- Micro simulation is capped, collapsed, or disallowed under high warp based on
  lane and fidelity rules.

## Relativistic-like and quantum-like effects under warp
- Effects are functions of ACT and therefore scale naturally under warp.
- No special-case logic is permitted for warp.
- Latent states remain latent until their deterministic trigger events occur.

## Multiplayer governance
### Singleplayer / local MP
- Host controls sim_rate.

### Lockstep
- Warp changes are commands.
- Agreement or host authority required.
- All peers advance identically.

### Server-authoritative MMO
- Server owns sim_rate.
- Clients may request warp but cannot force it.
- Server may batch simulate and stream results.
- Clients may do UI-only planning fast-forward without changing ACT.

## Perceived time (UI)
- Perceived time is a renderer over ACT (see calendar/clock systems).
- Different actors may show different perceived time.
- Perceived time never affects simulation or scheduling.

## Integration points
- Event-driven macro stepping (batch execution).
- Fidelity projection and lane constraints.
- Interest sets (relevance does not cancel events).
- Effect fields (degradation is ACT-based).
- Information/communication/command delivery (interrupt conditions).

## Prohibitions
- Local or per-region clocks.
- Per-region warp rates.
- Skipping or reordering events under warp.
- Non-deterministic batch sizing.
- Client-authoritative warp in MMO.

## Examples
1) Singleplayer fast-forward 10 years  
   sim_rate high; batch events run to ACT_target; results identical to stepping.

2) Local interaction at 1x, strategic view at high warp  
   LOCAL lane caps warp; high warp allowed only after collapse to rails.

3) Interplanetary logistics under high warp  
   Shipment arrival event fires at exact ACT; no skipped events.

4) MMO server batching 1 year overnight  
   Server advances ACT with batch processing; clients receive results later.

5) Warp interrupted by incoming message  
   Interrupt condition triggers; warp rate reduced deterministically.

## Test requirements (spec-only)
- Batch vs step equivalence
- Warp boundary caps per lane
- Interrupt condition correctness
- MMO consistency (server-auth vs lockstep)
- Replay determinism under warp

## References
- `docs/SPEC_TIME_CORE.md`
- `docs/SPEC_EVENT_DRIVEN_STEPPING.md`
- `docs/SPEC_EFFECT_FIELDS.md`
- `docs/SPEC_FIDELITY_PROJECTION.md`
