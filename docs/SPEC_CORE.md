# Dominium — CORE SPECIFICATION (V4)

This file defines the **minimal deterministic simulation core** and its canonical modules.

It is the contract that `/engine/core` and `/engine/sim` must implement.

No module, platform, renderer, or tool may violate these rules.

---

## 0. SCOPE AND NON-GOALS

This spec covers:

- Deterministic tick model and ordering
- Core integer/fixed-point math rules
- Spatial hierarchy and world layout
- Core simulation subsystems (networks, economy, research, climate, workers)
- Minimal RNG model

It does **not** cover:

- Rendering
- Audio
- OS/platform details
- UI
- Modding API details
- Asset formats

Those live in other docs.

---

## 1. CORE MODULE OVERVIEW

The minimal deterministic core is implemented by the following C89 modules:

### 1.1 Core Utility Layer (`/engine/core`)

- `dom_core_types.[ch]`  
  Canonical integer, fixed-point, and ID types.

- `dom_core_mem.[ch]`  
  Deterministic allocators, arenas, zeroing utilities.

- `dom_core_log.[ch]`  
  Deterministic logging API, fixed categories, no OS dependencies.

- `dom_core_rng.[ch]`  
  Deterministic RNG for simulation and tools; no platform dependence.

- `dom_core_fp.[ch]`  
  Fixed-point helpers (q16_16, q32_32) and safe integer math utilities.

### 1.2 Simulation Kernel (`/engine/sim`)

- `dom_sim_tick.[ch]`  
  Tick scheduler, phase pipeline, multi-rate system scheduling.

- `dom_sim_world.[ch]`  
  World registry, surfaces, planets, systems, galaxies, universe hierarchy.

- `dom_sim_space.[ch]`  
  Orbital/space “on-rails” logic (no N-body integration in core).

- `dom_sim_blueprint.[ch]`  
  Blueprint placement, construction stages, cut/fill hooks (minimal subset).

- `dom_sim_network_power.[ch]`  
  Power networks: DC and AC abstractions.

- `dom_sim_network_data.[ch]`  
  Data networks: tick-based packet routing, deterministic latency.

- `dom_sim_network_fluids.[ch]`  
  Fluids (liquids/gases): pressure/flow solver.

- `dom_sim_thermal.[ch]`  
  Heat transfer, temperature fields, thermal networks (minimal).

- `dom_sim_economy.[ch]`  
  Local/global markets, prices, resource accounts (minimal).

- `dom_sim_research.[ch]`  
  Science production and consumption, infinite trees.

- `dom_sim_climate.[ch]`  
  Coarse climate model, property-level weather drivers.

- `dom_sim_workers.[ch]`  
  Workers/robots, job assignment, deterministic path cost model.

The ECS, messaging, job system, and serialization are defined in other volumes, but these modules **must** be compatible with those specs.

---

## 2. TICK MODEL (STRICT DETERMINISM)

### 2.1 Canonical Tick Identity

- Simulation tick ID: `tick_id : uint64`
- Starts at 0, increments by 1.
- No fractional ticks.

### 2.2 Allowed Canonical UPS Values

Canonical UPS set:

`{1, 2, 5, 10, 20, 30, 45, 60, 90, 120, 180, 240, 500, 1000}`

- The **build-time default** is configured via CMake (`DOM_CANONICAL_UPS`).
- Runtime may select any of the above, but must match build metadata for determinism tests.
- If CPU cannot sustain target UPS, simulation **slows**; UPS is not silently changed.

### 2.3 Phase Pipeline (Fixed Order)

Every tick is decomposed into **seven phases**, in this exact order:

1. **INPUT**  
   - Collect external inputs (player commands, network inputs, scheduled events).
   - Write into input/command buffers only; no direct state changes.

2. **PRE-STATE RESOLUTION**  
   - Process events scheduled for this tick from previous state:
     - timers
     - global events
     - cross-lane messages from tick `N-1`
   - Prepare stable read-only view for simulation phase.

3. **SIMULATION (LANES)**  
   - Entities update lane-local state using previous tick’s global state and inputs.
   - No cross-lane writes; no global writes.

4. **NETWORK UPDATE**  
   - Update power, data, fluids, thermal, and other networks using lane outputs.
   - Compute next-tick network state (signals, flows, fields).

5. **MERGE**  
   - Merge lane-local outputs into global state in deterministic lane order (`lane 0..N-1`).
   - Apply structural changes from command buffers.

6. **POST-PROCESS**  
   - Recompute derived values, caches, chunk-local summaries.
   - Apply non-structural deferred operations, e.g., rebuilding indexes.

7. **FINALIZE**  
   - Swap buffers.
   - Increment `tick_id`.
   - Freeze state for next tick’s read-only views.

No system may observe “partial” states across these boundaries.

---

## 3. RNG (DETERMINISTIC ONLY)

### 3.1 RNG State

Simulation RNG implementation (core):

```c
struct dom_rng {
    uint64_t s[2];
};
3.2 API
c
Copy code
void     dom_rng_seed(struct dom_rng *rng, uint64_t seed_hi, uint64_t seed_lo);
uint32_t dom_rng_u32(struct dom_rng *rng);
uint64_t dom_rng_u64(struct dom_rng *rng);
int32_t  dom_rng_i32_range(struct dom_rng *rng, int32_t lo, int32_t hi); /* inclusive */
All RNG operations are purely integer.

The underlying algorithm must be fixed and versioned (e.g., xoshiro256**, but once chosen it cannot change without a deterministic migration step).

3.3 Prohibition on RNG in Core Sim Logic
RNG may be used for:

worldgen

map layout

initial universe generation

RNG must not be used for:

core machine operation

networks

economics

climate

worker job success/failure

All gameplay-critical behaviour must be deterministic functions of state, not random draws.

Any eventual cosmetic randomness (particles, sound variation) must be done outside /engine/sim.

4. MATH MODEL (INTEGER AND FIXED-POINT)
4.1 Allowed Types
Core sim uses:

int32, uint32

int64, uint64

dom_q16_16 (signed 32-bit fixed-point)

dom_q32_32 (signed 64-bit fixed-point)

4.2 Overflow and Division Rules
Unsigned overflow: two’s complement wrap, as per C89 + explicit implementation.

Signed overflow: never use UB; implement via unsigned wrap and cast.

Division by zero: must be handled deterministically (typically returns 0, with an error flag).

All fixed-point helpers live in dom_core_fp.[ch].

5. SPATIAL HIERARCHY AND WORLD STRUCTURE
5.1 Metric Scales (1D Reference)
Core spatial hierarchy (1D scale):

Subnano = 1 / 65,536 m

Submicro = 1 / 4,096 m

Submini = 1 / 256 m

Subtile = 1 / 16 m

Tile = 1 m

Subchunk = 16 m

Chunk = 256 m

Subregion = 4,096 m

Region = 65,536 m

Subcontinent = 1,048,576 m

Continent = 16,777,216 m

Supercontinent = 268,435,456 m

Surface = 4,294,967,296 m (conceptual wrap length)

These units exist in the logical spatial index; storage is chunked.

5.2 Coordinate System
All coordinates are integer:

c
Copy code
typedef int64_t dom_coord_t;  /* metres */
typedef struct {
    dom_coord_t x;
    dom_coord_t y;
    dom_coord_t z;
} dom_vec3m;
z = 0 is defined as planetary sea level for surfaces.

Orientations/rotations are represented by discrete orientations or fixed-point angles, not floating matrices.

5.3 Surface / Planet / System / Galaxy / Universe
Surface
A game-playable 2.5D world layer (terrain + structures) on a planet.

Planet
A collection of surfaces (initially exactly 1 per planet for MVP).

System (star system)
Contains planets and orbital nodes; initial MVP is Sol.

Galaxy
Contains up to 2^32 systems.

Universe
Contains up to 2^32 galaxies.

The MVP core gameplay is a single surface on Earth in the Sol system in the Milky Way galaxy, but the core must support multiple surfaces/planets/systems logically.

5.4 Chunking
Minimal chunk structure for core sim:

Subchunk: 16 × 16 m tiles

Chunk: 16 × 16 subchunks = 256 × 256 m

Subregion: 16 × 16 chunks = 4,096 × 4,096 m

Region: 16 × 16 subregions = 65,536 × 65,536 m

Each surface consists of a sparse set of chunks; only changed or non-default chunks are allocated.

dom_world_space.[ch] must provide:

Mapping (x, y, z) → chunk/subchunk indices

Deterministic iteration order of chunks, subchunks, tiles

Efficient local queries (for pathing and networks)

6. NETWORKS (CORE SUBSYSTEMS)
6.1 Power Network (dom_sim_network_power)
Core abstraction:

Graph of nodes and edges representing power lines, buses, machines.

Types:

DC

1-phase AC

3-phase AC

Minimal tracked quantities per node/edge:

Nominal voltage level (e.g., 24V, 240V, 400V, 11kV, 22kV, etc.)

Apparent power demand/generation

AC subtype: frequency (e.g., 50/60 Hz), phase group

Power flow for core:

At each tick, for each connected component:

Sum total generation G

Sum requested load L

If G >= L: full supply, all loads satisfied.

If G < L: deterministically downrate loads by factor R = G / L.

Transformers, breakers, etc. are represented as edges with constraints and states.

6.2 Data Network (dom_sim_network_data)
Core model:

Directed or undirected graph of routers/switches/nodes.

Packets move one hop per tick.

Each hop has fixed latency = 1 tick.

Queues are fixed-size, deterministic ring buffers.

No random loss:

Under normal operation, capacity must be sufficient.

On overflow (mod abuse/testing), oldest packet dropped with a deterministic flag.

Addresses:

Each node has a stable address (integer).

Higher-level protocols are built on top of this core.

6.3 Fluids Network (dom_sim_network_fluids)
Core fluids (liquid/gas) model:

Graph of tanks/pipes/pumps/valves.

Tracked per node:

Volume

Pressure (integer or fixed-point)

Temperature (fixed-point)

Fluid type ID

No arbitrary mixing in core:

Each connected component is either:

homogeneous fluid type, or

mixing is disabled by default and requires explicit config.

Flow model per edge:

text
Copy code
desired_flow = conductance * (pressure_a - pressure_b)
actual_flow  = clamp(desired_flow, -capacity, +capacity)
Node updates:

text
Copy code
volume_new   = volume_old + Σ flows_in_out
pressure_new = f(volume_new)  // piecewise integer function
7. ECONOMY (dom_sim_economy)
Core economy is discrete and deterministic:

7.1 Account Model
Every property/company has:

Currency account (integer, no floats).

Inventory of resources (integer counts).

Balance sheet aggregator (core quantities only).

7.2 Markets
Local markets at property or region level.

Global markets at universe or galaxy level.

Prices:

Discrete price index per resource.

Updated deterministically from:

supply/demand windows

exogenous scenario inputs (scripted, not random)

TEUs and logistics exist as units in simulation, but minimal core:

Units of cargo described as integer multiples of base quantities.

Transport cost functions deterministic, based on distances and modes.

No speculative stochastic pricing in core.

8. RESEARCH (dom_sim_research)
8.1 Science Production
Science is produced by machines and labs.

Science units:

Integer counters per “science channel” or discipline.

8.2 Research Trees
Research tree is defined as a directed acyclic graph (DAG).

Each node:

Required science amounts (per discipline).

Unlocks machines, network levels, efficiency multipliers.

Infinite research:

Higher tiers may be defined as:

Levelled repeatable techs (e.g., “+1% efficiency per level, hard-capped to an integer bound”).

Although conceptually infinite, each step is discrete.

All research progress is purely additive, no randomness.

9. CLIMATE AND WEATHER (dom_sim_climate)
Core climate model is coarse but deterministic:

Time resolution:

Climate core: monthly or yearly ticks (multi-rate system).

Weather driver: daily or hourly multiples of sim ticks (derived, not random).

Tracked for each surface/region:

Mean temperature

Precipitation index

Wind index

CO₂-equivalent forcing

Ocean/land heat reservoir variables (integer or fixed-point)

Update rules:

Simple energy balance model (EBM) with discrete parameters.

No pseudo-random “noise” in core; weather variability can be derived deterministically from seeds and indices if needed.

10. WORKERS (dom_sim_workers)
Workers = agents that execute jobs in the world:

10.1 Worker Types
Human workers

Have wage rate (integer).

Have skill categories.

Robot workers

Have capital cost (integer).

Have maintenance cost and upgrade level.

10.2 Job Model (Core View)
Jobs are:

Fixed-size structs:

Job type

Priority

Requester entity

Target entity/position

Estimated ticks

Queues:

Local (per entity)

Lane-level

Global

Workers are assigned jobs deterministically:

Filter:

skills

reachability (path existence)

Sort:

Worker ID

workload

last_assigned_tick

No random assignment.

10.3 Pathing
Pathfinding core:

Per-tile cost integer.

A* or Dijkstra with deterministic tie-breaking:

Direction priority order fixed.

Node ordering deterministic.

Path cost is integer, used to estimate job duration.

11. MINIMAL BLUEPRINT/CONSTRUCTION CORE (dom_sim_blueprint)
Blueprints represent:

Future or in-progress entities/buildings on a grid.

Minimal core:

Stores:

Prefab ID

Position (tile coordinates)

Orientation

Stage index

Emits jobs for:

Material delivery

Construction work

Destruction and collapse are not implemented in the core MVP; they must not break this interface when added later.

12. INVARIANTS AND PROHIBITIONS
No floating point in /engine/core or /engine/sim.

All quantities are integer or fixed-point.

No OS, platform, or renderer headers in core modules.

No dynamic allocation in the hot simulation path.

No nondeterministic iteration (all loops over entities/chunks sorted by ID/coordinate).

No random decisions in core subsystems (networks, economy, climate, research, workers).

All multi-rate systems must schedule on tick multiples with explicit offsets.

All world structures (chunks, networks, accounts, research nodes) must have stable IDs for serialization.

Save/load must reproduce bit-for-bit identical core state given identical inputs.

All extensions (combat, advanced AI, N-body orbits, etc.) must be built on top of this core, not by violating it.

End of SPEC_CORE.md (V4).