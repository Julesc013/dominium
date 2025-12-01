```markdown
// docs/book/Volume02-Simulation.md
# Dominium Design Book v3.0
## Volume 02 — Simulation

### Overview
The simulation kernel is tick-driven, deterministic, and integer-based. It runs fixed phases, uses canonical UPS values, deterministic virtual lanes with ordered merges, and enforces backpressure over loss for all networks and events. Multiplayer operates in lockstep; real-time speed may slow but never alters simulation results.

### Requirements (MUST)
- Use canonical UPS set {1,2,5,10,20,30,45,60,90,120,180,240}; slow deterministically if hardware cannot keep up.
- Execute the seven-phase pipeline every tick: Input → Pre-State Resolution → Simulation (lanes) → Network Update → Merge → Post-Process → Finalize.
- Apply virtual lanes: lane_id = entity_id % NUM_LANES; lanes read prior tick state, write lane-local outputs, and merge in lane order 0..N-1 only.
- Use integer/fixed-point math (e.g., q16_16, q32_32, fixed24.8) with wrap-around overflow rules; no floating-point in simulation.
- Enforce deterministic network propagation: signals 1-tick latency, packets one hop per tick, fluids/heat/power solved with fixed iteration counts and deterministic clamping.
- Provide deterministic event queues and buffers with fixed sizes; overflow drops oldest and flags deterministically.
- Maintain lockstep multiplayer: exchange inputs per tick, run tick only when all inputs present; desync triggers log+halt with checksums.
- Disallow dynamic allocation during ticks; allocate at load/startup/entity creation only.

### Recommendations (SHOULD)
- Stagger heavy systems via multi-rate schedules (e.g., fluids every 2–4 ticks, heat every 6, pollution every 30, environment every 60).
- Use dense arrays keyed by entity IDs and sorted iteration to avoid nondeterministic traversal.
- Use deterministic fixed iteration solvers for power/fluids/thermal; keep consistent traversal orders.
- Clamp/scale loads deterministically (e.g., power downrating by ratio) instead of dropping work.

### Prohibitions (MUST NOT)
- No asynchronous side effects between ticks; no background tasks altering state.
- No floating-point math, platform RNG, or time-dependent behavior in simulation.
- No nondeterministic data structures (hash iteration, unordered maps) in core loops.
- No direct state writes across lanes before merge; no 0-tick network propagation.
- No implicit packet/flow drops; no dynamic allocation or garbage collection in tick phases.

### Detailed Sections
#### 2.1 — Tick Pipeline
- Input phase: order by input_stream_index, player_id, command timestamp, sequence; write to input buffer only.
- Pre-State Resolution: resolve time/threshold triggers, insert queued events/packets, clamp queues deterministically, freeze pre-state.
- Simulation (lanes): execute entities per lane, produce signals/packets/flows/movement deltas/event flags; no cross-lane writes.
- Network Update: process signals, packets, fluids, power, heat, pollution, radiation, light/sound, air pressure, atmosphere with deterministic solvers.
- Merge: lane 0→N-1; sum totals, append packet queues, resolve conflicts (lower entity_id wins if illegal conflict).
- Post-Process: recompute derived stats, apply construction/removal, update chunk caches, validate overlaps.
- Finalize: swap buffers, advance tick_id, commit snapshot for UI/replay.

#### 2.2 — Arithmetic and Types
- Allowed numeric types: int32/uint32, int64/uint64, q16_16, q32_32, fixed24.8 for voltages/currents/frequencies, fixed16.16 for resistances/reactances.
- Overflow uses deterministic wrap; fixed-point multiply/divide follows defined shift rules; no platform-dependent UB.

#### 2.3 — Concurrency Model
- Virtual lanes fixed per entity lifetime; no migration.
- Merge order deterministic for sums/min/max/conflict resolution.
- Pathfinding or async preparation must integrate via deterministic queues and tick boundaries.

#### 2.4 — Events, Buffers, and Backpressure
- Message/event queues are fixed-size ring buffers; overflow drops oldest and flags overflow.
- Backpressure preferred: actual_output = min(requested, capacity); remainder never exists, nothing is silently lost.
- Deterministic clamping: x_new = min(max(x_value, low), high).

#### 2.5 — RNG and Versioning
- RNG API: struct dom_rng{s[2]}; seed with hi/lo, u32 output, float01 helper; only seeded software RNG allowed.
- Deterministic reproducibility requires identical engine/mod/script versions, simulation constants, UPS schedule, world seed/universe hash; savefiles carry versions, mod lists, seeds, tick counter, component hashes.

#### 2.6 — Degradation and Error Handling
- If actual_ups < target, simulation slows by actual/target; rendering FPS decoupled and never drives simulation.
- Error handling: div-by-zero returns 0; overflow wraps; illegal state asserts in debug and clamps in release; NaN impossible.

#### 2.7 — Lockstep Multiplayer
- Only initial full snapshot and periodic checksums allowed; no mid-run state streaming except explicit resync.
- Desync procedure: log tick, save divergent states, halt awaiting host decision.

### Cross-References
- Volume 01 — Vision (engine-first deterministic focus)
- Volume 03 — World (spatial model feeding simulation)
- Volume 04 — Networks (power/data/fluids/transport solvers)
- Volume 05 — Economy (tick-driven markets and costs)
- Volume 06 — Climate (environment updates in multi-rate schedule)
- Volume 07 — UIUX (snapshots consumed by UI)
- Volume 08 — Engine (ECS/messaging backing simulation)
- Volume 09 — Modding (versioning and deterministic data packs)
```
