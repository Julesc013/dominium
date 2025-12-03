# Dominium — CORE SPECIFICATION (V5)

This is the binding deterministic core contract. It reconciles the spec layer with the dev addenda under `docs/dev/dominium_new_engine_*.txt`, the platform/render addendum, and the context pack. No module, platform, renderer, tool, or mod may violate these rules.

---

## 0. SCOPE AND NON-GOALS
**Covered:** deterministic tick pipeline, integer/fixed-point math, spatial hierarchy, ECS and lane behaviour, core simulation subsystems (networks, economy, research, climate, workers), RNG rules.  
**Not covered:** rendering, audio, OS/platform specifics, UI skinning, mod API details, asset formats (see other specs).

---

## 1. CORE MODULE SET (DIRECTORY CONTRACT)
- `/engine/core` (C89): types, log, mem, fp, rng, bits.
- `/engine/sim` (C89): tick, lanes, events, jobs, world registry, networks (power/data/fluids/thermal), orbit (on-rails), economy. No OS, renderer, or audio headers.
- `/engine/spatial` (C89): coordinate hierarchy, grid/chunk/subchunk/region registries, voxel storage, spatial index and queries.
- `/engine/path` (C89): grid/navmesh adjacency, deterministic costs, A*, traffic penalties, route/cache.
- `/engine/physics` (C89): kinematic envelopes, AABB/shape tests, collision queries, spline/vehicle helpers; no floating point.
- `/engine/ecs` (C89): entity ids/generations, component registry, dense storage, archetypes, queries, system registration and fixed ordering.
- `/engine/net` (C89): lockstep protocol, channels, packet formats, deterministic input/replay plumbing; no sockets (platform layer only).
- `/engine/render` (C89/C++98): render command buffer and backends; never mutates sim.
- `/engine/audio` (C89/C++98): deterministic audio command buffer and backends; never mutates sim.
- `/engine/ui` (C89/C++98): retained UI tree, layout, widget behaviours, UI command buffer; no sim logic.
- `/engine/platform` (C89/C++98): OS boundary only; only place where OS/graphics/audio headers are allowed.
- `/engine/io`, `/engine/modding`, `/engine/api` (C89/C++98): serialization, pack/mod loading, and public API surfaces; follow the determinism and layering rules above.

---

## 2. TICK MODEL (STRICT DETERMINISM)
### 2.1 Tick identity and UPS
- `tick_id : uint64`, starts at 0, increments by 1.
- Canonical UPS set: {1, 2, 5, 10, 20, 30, 45, 60, 90, 120, 180, 240, 500, 1000}. Build-time default via `DOM_CANONICAL_UPS`.
- If the machine cannot sustain the target UPS, simulation **slows** deterministically; UPS is never auto-changed.

### 2.2 Phases (fixed order, no shortcuts)
1. **INPUT** — Collect external inputs (player/net/automation). Write only to input/command buffers.
2. **PRE-STATE** — Deliver prior tick events (timers, global, cross-lane) into stable read views.
3. **SIMULATION (LANES)** — Lane-local updates using prior global state + current inputs; no cross-lane writes.
4. **NETWORKS** — Power/data/fluids/thermal/orbit updates using lane outputs; compute next-tick network state.
5. **MERGE** — Apply structural changes and lane outputs in deterministic lane order (`0..N-1`); move entities/archetypes.
6. **POST-PROCESS** — Rebuild derived caches/indexes; apply deferred non-structural work.
7. **FINALIZE** — Swap buffers, increment `tick_id`, freeze read-only views.

No system may observe a partial state across these boundaries. Multi-rate tasks use tick modulo scheduling with explicit offsets.

### 2.3 Lanes
- Lane count set at init; mapping is deterministic: `lane = entity_id % num_lanes`.
- Lane execution order is ascending lane id; merge respects the same order.

---

## 3. RNG (DETERMINISTIC ONLY)
### 3.1 State and API
```c
typedef struct dom_rng {
    uint64_t s[2]; /* algorithm is versioned and frozen */
} dom_rng;

void     dom_rng_seed(dom_rng *rng, uint64_t seed_hi, uint64_t seed_lo);
uint32_t dom_rng_u32(dom_rng *rng);
uint64_t dom_rng_u64(dom_rng *rng);
int32_t  dom_rng_i32_range(dom_rng *rng, int32_t lo, int32_t hi); /* inclusive */
```
- Algorithm is fixed and versioned; changes require explicit migration.
- Pure integer; no floats; no platform entropy.

### 3.2 Allowed use
- Allowed: worldgen, map layout, initial universe/surface seeds, cosmetic-only effects outside `/engine/sim`.
- Forbidden: core machine behaviour, networks, economy, climate, worker assignment or success/failure, tick scheduling. Gameplay outcomes must be pure functions of state.

---

## 4. MATH MODEL (INTEGER + FIXED-POINT)
- Core sim types: `int32/uint32`, `int64/uint64`, `dom_q16_16`, `dom_q32_32`.
- Unsigned overflow: two’s complement wrap with documented casts. Signed overflow: never rely on UB; use unsigned intermediates then cast.
- Division by zero handled deterministically (defined return + error flag).
- No floating point in `/engine/core` or `/engine/sim`; renderer/audio may use floats internally but not for sim state.

---

## 5. SPATIAL HIERARCHY AND WORLD STRUCTURE
### 5.1 Units (1D reference)
- Subnano = 1 / 65,536 m  
- Submicro = 1 / 4,096 m  
- Submini = 1 / 256 m  
- Subtile = 1 / 16 m  
- Tile = 1 m  
- Subchunk = 16 m  
- Chunk = 256 m  
- Subregion = 4,096 m  
- Region = 65,536 m  
- Subcontinent = 1,048,576 m  
- Continent = 16,777,216 m  
- Supercontinent = 268,435,456 m  
- Surface = 4,294,967,296 m (conceptual wrap length)

### 5.2 Coordinates
```c
typedef int64_t dom_coord_t; /* metres */
typedef struct { dom_coord_t x, y, z; } dom_vec3m;
```
- `z=0` is planetary sea level for surfaces. Orientations are discrete or fixed-point angles; no float matrices in sim.

### 5.3 World hierarchy
- Surface → Planet → System → Galaxy → Universe. IDs are stable `uint32`.
- MVP: single surface on Earth (Sol/Milky Way), but the core must support multiple surfaces/planets/systems/galaxies logically.

### 5.4 Chunking
- Subchunk: 16×16 m tiles.  
- Chunk: 16×16 subchunks = 256×256 m.  
- Subregion: 16×16 chunks = 4,096×4,096 m.  
- Region: 16×16 subregions = 65,536×65,536 m.
- Chunks are sparse; allocate only when non-default. Iteration order is sorted by (surface, chunk_x, chunk_y, z-layer).
- Spatial mapping provides: (x,y,z) → chunk/subchunk indices, deterministic chunk/subchunk/tile iteration, and efficient queries for pathing/networks.

---

## 6. NETWORK SUBSYSTEMS (CORE)
### 6.1 Power (`dom_sim_network_power`)
- Graph of nodes/edges; types: DC, AC1P, AC3P.
- Tracked per node/edge: nominal voltage level, apparent power demand/gen, frequency (for AC), state flags.
- Per connected component per tick: sum generation `G`, sum load `L`; if `G >= L` supply fully, else scale loads by deterministic factor `R = G/L`. Transformers/breakers are edges with constraints.

### 6.2 Data (`dom_sim_network_data`)
- Graph of routers/switches/nodes. Packets move **one hop per tick**; fixed 1-tick latency per hop.
- Fixed-size deterministic ring buffers; overflow drops oldest with a flag. No random loss.
- Addresses are stable integers; higher protocols build on this core.

### 6.3 Fluids (`dom_sim_network_fluid`)
- Graph of tanks/pipes/pumps/valves.
- Per node: volume, pressure (int/fixed), temperature (fixed), fluid type id.
- Flow per edge: `desired = conductance * (p_a - p_b)`, `actual = clamp(desired, -capacity, +capacity)`. Volume updates sum flows; pressure is deterministic function of volume. Mixing disabled by default unless explicitly configured.

### 6.4 Thermal (`dom_sim_network_thermal`)
- Deterministic grid/graph diffusion with fixed timestep; integer/fixed temperatures.
- Runs on a multi-rate schedule (coarse ticks) but still via the network phase.

---

## 7. ECONOMY
- Integer accounts and inventories per property/company. No floating point.
- Markets: local (property/region) and global (universe/galaxy) price indices; updates are deterministic functions of supply/demand windows and scripted scenario inputs.
- Cargo/logistics units are integer multiples; transport costs are deterministic distance-based functions.

---

## 8. RESEARCH
- Science production is integer per discipline/channel.
- Tech tree is a DAG; each node lists integer costs, prerequisites, unlocks (prefabs/recipes/modifiers).
- Infinite/levelled techs are discrete steps; no random progress. Unlock effects are deterministic.

---

## 9. CLIMATE AND WEATHER
- Coarse climate tick (monthly/yearly) plus derived weather drivers (daily/hourly multiples of sim ticks) scheduled via multi-rate tables.
- Tracked per surface/region: temperature index, precipitation index, wind index, CO₂-equivalent forcing, heat reservoir terms (int/fixed).
- Uses discrete energy-balance style updates; no pseudo-random noise in core.

---

## 10. WORKERS AND JOBS
- Worker types: humans (wage, skills) and robots (capital, maintenance, upgrade level); all integer.
- Jobs are fixed-size structs: type, priority, requester, assignee, target (entity or tile), estimated ticks, payload fields.
- Queues: local (per entity), lane-level, global. Assignment is deterministic: filter by skills/reachability, then sort by worker id, workload, last_assigned_tick, and job priority. No random tie-breaking.
- Pathing uses deterministic cost estimates (see `/engine/path`); job durations are integer.

---

## 11. BLUEPRINT / CONSTRUCTION CORE
- Blueprint instances store: prefab id (or namespaced id), tile position, orientation, stage index, required resources/jobs.
- Emits deterministic jobs for material delivery and construction. Destruction/collapse must not violate this interface when added later.
- Blueprint data is serialized as stable ID + component payloads; order is deterministic.

---

## 12. INVARIANTS AND PROHIBITIONS
- No floating point in `/engine/core` or `/engine/sim`; all authoritative state is integer or fixed-point.
- No OS, renderer, audio, or platform headers in deterministic modules.
- No dynamic allocation in hot tick paths; preallocate or use arenas/pools.
- No nondeterministic iteration; entity/chunk/network traversals are in sorted, documented order.
- Stable IDs for all serializable structures (entities, chunks, networks, accounts, research nodes, blueprints).
- Save/load and replay must reproduce **bit-identical** core state given identical inputs, mod set, and data packs.
- Extensions (combat, advanced AI, physics fidelity, etc.) must layer on top without violating the tick pipeline, math rules, or deterministic scheduling.

End of SPEC_CORE.md (V5).
