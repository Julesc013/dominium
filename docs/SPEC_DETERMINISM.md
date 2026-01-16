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
# SPEC_DETERMINISM — Deterministic Core Contract

This spec defines the deterministic contract for the Domino engine refactor.
All deterministic simulation, replay, hashing, and lockstep multiplayer must
obey it.

## Scope
This spec applies to all code and data that can affect:
- authoritative simulation state
- per-tick world hashing
- replay recording/playback streams
- lockstep/rollback synchronization

It is not a UI/tooling spec; tooling may *observe* determinism but must not be
the source of nondeterminism in deterministic paths.

## Terminology (canonical)
- **Authoritative state / source of truth:** the state that affects simulation
  outcomes and must participate in deterministic ordering, replay, and world
  hashing. This includes committed deltas and any quantized authoring models
  that drive simulation.
- **Derived cache:** any data that is fully regenerable from authoritative
  inputs. Derived caches MUST NOT become gameplay truth and MUST NOT be required
  to reproduce outcomes.
- **Compiled artifact:** a derived cache produced deterministically from
  authoritative inputs (e.g. compiled graph adjacency, TRANS microsegments,
  STRUCT occupancy indices, DECOR tiles).
- **World hash:** the per-tick hash of authoritative state computed after the
  tick's delta commit point. It is used for replay verification and lockstep.
- **Determinism build hash:** a build-time identifier derived from determinism-
  relevant code/config/schema/content versions. It is used for compatibility and
  diagnostics, and MUST NOT be treated as (or substituted for) the world hash.

## Determinism guarantee (authoritative)
Given:
- the same initial authoritative state (including version ids and RNG state)
- the same deterministic command stream (intents) grouped by tick

Then:
- every peer MUST produce the same authoritative state and the same world hash
  after each tick
- byte-for-byte, platform-independent (within the supported invariants below)

## Authoritative timebase (tick-first)
Deterministic systems MUST use the canonical timebase:
- `tick_index` (`u64`) and `ups` (`u32`, ticks per second)
- wall-clock time is never authoritative and MUST NOT mutate sim state
- calendar labels (days/months/years) are derived presentation only

Any float/double `dt` may exist only in UI/runtime glue and MUST NOT drive
authoritative simulation.

## Capability split (SIM_CAPS vs PERF_CAPS)
- SIM_CAPS are part of the identity digest and launcher handshake. Changes
  require migration or explicit refusal.
- PERF_CAPS are negotiable and MAY change derived/presentation behavior only.
- See `docs/SPEC_CAPABILITIES.md` for field definitions and hashing rules.

## Supported invariants (enforced in code)
Determinism paths MUST assume and enforce:
- C89/C90 compilation for core deterministic modules
- two's complement integers
- arithmetic right shift for signed integers
- truncating signed division (toward zero)
- fixed-width integer sizes per `domino/core/types.h`

The compile-time enforcement hooks live in `source/domino/core/det_invariants.h`.

## Canonical ordering rules
Deterministic behavior MUST NOT depend on pointer addresses or insertion-order
side effects of unordered containers.

### Stimulus substrate (fields/events/messages)
Determinism paths MUST NOT perform direct cross-subsystem calls to exchange
stimuli or authoritative state. Instead:
- **Events**, **messages**, and **field updates/samples** are the only allowed
  cross-module stimulus channels in SIM.
- Producers buffer events/messages/field-updates; delivery/application happens
  only at deterministic scheduler phase boundaries (see
  `docs/SPEC_FIELDS_EVENTS.md` and `docs/SPEC_SIM_SCHEDULER.md`).
- Delivery/application/sampling work is bounded via deterministic budgets and
  carryover queues; no time-based scheduling is allowed.

### Agent/controller substrate (sensors → observations → minds → intents)
Determinism paths MAY include non-semantic actor behavior as an IO pipeline:
- **Agents are composition-only**: agents are data records with component
  attachments; there is no inheritance-based behavior polymorphism.
- **Sensors** read authoritative state via deterministic queries only and emit
  `dg_pkt_observation` into per-agent bounded buffers.
- **Minds/controllers** consume observation buffers + agent components and emit
  `dg_pkt_intent` only; they MUST NOT mutate authoritative state directly.
- **Group controllers** operate on stable member lists and aggregated
  observations and emit group intents; member agents may incorporate these
  intents during their own mind step.

Deterministic enforcement:
- **Stride decimation** MUST use `dg_stride_should_run()` keyed by stable IDs
  (e.g. `(agent_id, sensor_id)` / `(agent_id, mind_id)`).
- **Budgets** MUST consume integer work units and defer overflow work into
  deterministic queues (`dg_budget`, `dg_work_queue`).
- **PRNG** (if used by minds/VMs) MUST be a deterministic stream keyed by
  `(agent_id, stream_id)` and MUST NOT depend on enumeration order.

### Stable IDs
All deterministic objects that can appear in packets, deltas, hashes, or
serialized artifacts MUST have stable numeric IDs.

Stable IDs MUST be:
- deterministic (created from explicit allocator state, not pointer identity)
- comparable (total order)
- serializable

For typed packet IO:
- `type_id` and `schema_id` are content-defined `u64` (hash of canonical string)
- pack-scoped identifiers that need compact runtime IDs MUST use explicit remap
  tables (TLV idmaps); deterministic paths MUST NOT mint new IDs on the fly

### Domains, frames, propagators
Domains, frames, and propagators are semantics-free deterministic primitives:
- **Domains** are containers for authoritative state; they MUST be stepped and
  hashed in canonical `domain_id` order and obey scheduler phases + budgets.
- **Frames** are generic coordinate transforms; evaluation MUST be fixed-point,
  bounded, and non-recursive, and MUST NOT consult platform state.
- **Propagators** are generic time evolution; they MUST run only in allowed
  scheduler phases and MUST use accumulators for lossless deferral under LOD
  decimation and budget carryover.

### Canonical comparison / sorting
When a stable sort is required, ordering MUST be defined by stable keys:
- primary: family/type id (domain/packet/etc.)
- then: stable numeric id(s)
- then: stable sequence numbers (if required)

Collections that are naturally unordered (hash maps, sets) MUST be reified into
arrays and sorted using canonical comparators before deterministic iteration.

### Canonical graph toolkit ordering
Deterministic graph infrastructure (connectivity, adjacency, stitching, rebuild)
MUST obey `docs/SPEC_GRAPH_TOOLKIT.md`:
- per-node adjacency arrays sorted by `(neighbor_node_id, edge_id)` ascending
- per-partition node lists sorted by `node_id` ascending
- boundary stitching driven by stable endpoint keys and canonical edge creation order
- dirty set iteration in canonical ascending ID order (no insertion-order dependence)
- rebuild work scheduled in **PH_TOPOLOGY** with stable `dg_order_key` keys and
  deterministic budget + carryover semantics (no skipping)

### Canonical registry ordering
Deterministic registries (packet types, field types, event/message types, etc.)
MUST iterate in a canonical, stable order:
- primary: ascending `type_id` (`u64`)
- tie-break: ascending `schema_id` (`u64`), then ascending schema versions

### Canonical TLV ordering
All deterministic TLV containers (used for hashing, replay, or lockstep) MUST:
- use a defined byte encoding for TLV headers
  - ABI-stable TLV uses explicit little-endian headers (`u32_le` tag/len), as implemented by `res/dg_tlv_canon.*` and `dtlv_*`
  - legacy blob formats may store `tag`/`len` as native-endian `u32` via `memcpy` and therefore require little-endian hosts
- ensure record ordering is deterministic (canonical sort or stable writer-defined order)

Canonicalization rules implemented by `res/dg_tlv_canon.*` (when canonical sort is required):
- TLV records are sorted by `(tag, payload_bytes)` ascending
  - `tag` is `u32_le`
  - repeated tags are tie-broken by lexicographic payload bytes, then length
- writers MUST emit explicit lengths and MUST NOT include padding bytes

Unknown TLVs MUST be safely skippable using lengths (forward-compat framing).

### Explicit endianness rule
Supported runtime targets are little-endian. Determinism paths must treat the byte encoding of numeric fields as little-endian for stable replay/hashing.

Prefer explicit little-endian routines (`dg_le_*`, `dtlv_le_*`) for ABI-stable formats. Some legacy blob formats serialize numeric headers via host-endian `memcpy` and are therefore deterministic only on little-endian hosts.

## Fixed-point requirements
Determinism paths MUST use fixed-point math only:
- Q formats only (see `domino/core/fixed.h`)
- conversions and rounding MUST follow the explicit rules/macros in
  `source/domino/core/det_invariants.h`
- deterministic trig/sqrt/div must use `source/domino/core/dom_deterministic_math.h`
  (wrapping `include/domino/core/fixed_math.h`)

Forbidden:
- float/double/long double arithmetic in deterministic paths
- math-library functions (sin/cos/etc.) in deterministic paths

Tooling may use floating point only outside determinism paths and MUST NOT feed
float-derived values into deterministic state without explicit quantization.

## Anchors, poses, and “no grids”
Deterministic simulation MUST treat parametric anchors as authoritative truth:
- placement/edit intents MUST be expressed as `(dg_anchor, local dg_pose offset)`
- both anchor parameters and pose components MUST be quantized before commit
- anchor evaluation is query-time only (no cached world-space poses required)

Global grids are UI-only:
- the engine MUST NOT assume a global placement grid in logic
- any grids/tiles/occupancy maps may exist only as derived caches that are
  regenerable and non-authoritative

World-space baked geometry is never authoritative:
- meshes, collision geometry, and other world-space artifacts are derived caches
  generated from anchors + parameters (and deterministic compilation where used)

## TRANS corridors (alignments / slots)
TRANS corridor state and compilation MUST obey these additional constraints:
- **Source of truth:** authored alignments, cross-sections (slots), attachments,
  and junction topology (quantized fixed-point; canonically ordered by stable IDs)
- **Overlap/co-location:** represented only via cross-section slot occupancy
  (multiple occupants in the same corridor slots), not via stacked splines
- **Derived caches:** microsegments, deterministic local frames, slot occupancy
  maps, and chunk-aligned spatial indices (fully rebuildable)
- **Budgeted compilation:** uses canonical work ordering and deterministic
  carryover; the final compiled output MUST be identical independent of deferral
- **Frames:** forward from alignment tangent; up from a stable reference plus
  roll profile; normalization uses bounded integer math (no epsilons)

## STRUCT buildings/infrastructure (instances / footprints / volumes)
STRUCT authoring state and compilation MUST obey these additional constraints:
- **Source of truth:** authored structure instances with stable `struct_id` and
  placement expressed as `(dg_anchor, local dg_pose)` plus referenced parametric
  templates (footprints, volumes, enclosures, surfaces, sockets, carrier intents).
- **No grids:** footprints/volumes are authored in a local structure frame and
  placed via anchor+pose; no axis alignment or world grid assumptions are allowed.
- **Derived caches (rebuildable):**
  - occupancy + void regions + chunk-aligned spatial indices
  - enclosure graphs (room nodes + aperture edges) + room indices
  - surface graphs (facades/interiors) + sockets + surface indices
  - support/load topology graphs + support indices (no physics solving yet)
  - carrier artifacts (bridge/tunnel/cut/fill) + carrier indices
- **Budgeted compilation:** each stage is scheduled as deterministic work items
  ordered by canonical keys; processing consumes explicit budget units and MUST
  stop when the next item cannot fit (no skipping). Remaining work carries over
  deterministically and the final compiled caches MUST match a full rebuild.
- **No baked geometry:** meshes/polygon soups/render geometry MUST NOT be stored
  as authoritative state; compiled artifacts are derived caches only.

### Carrier intents (STRUCT)
- Carrier intents are parametric requests (bridge/viaduct/tunnel/cut/fill), not
  baked geometry.
- STRUCT compilation emits parametric carrier artifacts; TRANS/ENV may consume
  them later, but STRUCT MUST NOT call TRANS directly in determinism paths.

## DECOR decorations (rulepacks / overrides)
DECOR authoring state and compilation MUST obey these additional constraints:
- **Authoring is truth:** rulepacks + overrides + anchors are authoritative; compiled decor tiles/instances are derived caches only.
- **Host-agnostic binding:** decor binds to hosts via stable authoring IDs (terrain patches, TRANS slot surfaces, STRUCT surfaces, room surfaces, sockets), never via baked geometry.

### Canonical baseline generation
- Hosts are enumerated in canonical order by stable IDs (no insertion-order dependence).
- Rulepacks are applied in ascending `rulepack_id` order.
- Deterministic PRNG (if used) is seeded from `(global_seed, host_id, rulepack_id)` and MUST NOT depend on enumeration order.
- Generated decor item IDs MUST be stable (derived from stable inputs) so output is order-independent.

### Override ordering + precedence
- Overrides are applied in ascending `override_id` order.
- **PIN precedence:** pinned items are always present in final output and MUST NOT be removed by SUPPRESS.
- REPLACE/MOVE apply to the targeted `decor_id` after pinning is resolved; results MUST NOT depend on override insertion order.

### Derived outputs (canonical)
- Decor instances are chunk-aligned neutral records (no renderer calls) and sorted deterministically.
- Decor tiles are chunk-aligned batches derived from instances and MUST be rebuildable under budget with deterministic carryover.

## Deterministic LOD / representation framework
The engine-wide LOD framework (see `docs/SPEC_LOD.md`) is part of deterministic
simulation state evolution and MUST obey these additional constraints.

### Interest volumes are lockstep-only
Interest volumes:
- are derived ONLY from lockstep simulation state (player entities, ownership,
  hazards, activity, and registered critical-infra anchors)
- MUST NOT use UI state (camera, viewport, selection) or OS time
- MUST be quantized fixed-point regions (no floats) and stable across platforms

### Stable ordering for promotion/demotion
When choosing representation transitions, ordering MUST be deterministic and
MUST NOT depend on hash iteration or pointer identity.

Canonical ordering (authoritative):
- desired rep priority: `R0` first, then `R1`, then `R2`, then `R3`
- descending interest score (fixed-point integer compare)
- stable tiebreak key: `(domain_id, chunk_id, entity_id, sub_id)` ascending

### Budgeted transitions + deterministic carryover
Promotion/demotion is budgeted work:
- each transition has an explicit deterministic work-unit cost
- work is processed in stable order until the budget is exhausted
- if the next transition cannot fit, processing MUST stop (no skipping)
- remaining transitions MUST carry over to later ticks without reordering

### Accumulator semantics (no “result changes due to LOD”)
LOD may change cadence and fidelity, but MUST NOT change authoritative outcomes.
Systems MUST use accumulators for deferred integration:
- deltas are accumulated deterministically when work is decimated/deferred
- application consumes from accumulators without loss (total applied equals
  total added), independent of deferral pattern
- stride/decimation scheduling MUST be deterministic:
  `(tick + hash(stable_id)) % stride == 0` with a bit-stable hash

## Replay + hashing guarantees
### What replay records
Replay streams MUST record:
- the deterministic command stream (intents) grouped by tick
- any explicit RNG state needed to reproduce the same deterministic results
- version identifiers required to interpret data (schemas, content ids)

Replay streams MUST NOT record:
- OS/platform state
- wall-clock time
- pointer addresses
- UI state

### World hashing (authoritative)
World hashing MUST:
- use a bit-stable algorithm (64-bit FNV-1a is acceptable)
- hash canonical serialized values only (no padding, no pointers)
- cover authoritative state required to reproduce simulation results
- run after the tick's authoritative delta commit point

Derived caches SHOULD NOT be hashed. If a derived cache is hashed for debugging,
it MUST be explicitly versioned and MUST NOT affect simulation outcomes.

## Explicit prohibitions (non-exhaustive)
Determinism paths MUST explicitly forbid:
- treating a global grid as authoritative placement truth or a required
  representation for all objects (UI snapping/grids are non-authoritative;
  explicit lattices are permitted only when the owning subsystem specifies them)
- world-space baked geometry as authoritative state
- tolerance/epsilon-based solvers and comparisons
- unordered iteration in determinism paths (unordered containers, hash tables)
- UI-driven state mutation (UI/tools emit intents only)
- platform-dependent behavior (endianness, alignment, file order, time)
- wall-clock time or timers as simulation inputs
- calendar labels stored in canonical state
- absolute paths in handshake/save/replay artifacts
- raw libc sin/cos/sqrt/pow in authoritative code (use fixed-point wrappers)

## Source of truth vs derived cache
**Source of truth (authoritative):**
- world/domain state stored in deterministic structures
- intent and delta streams (with TLV versioning)
- deterministic allocator/RNG state

**Derived cache (must be regenerable):**
- LOD representations R1–R3 (see `docs/SPEC_LOD.md`)
- knowledge/visibility/comms state (see `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`)
- compiled/expanded graph adjacency caches (see `docs/SPEC_GRAPH_TOOLKIT.md`)
- TRANS microsegments/frames/slotmaps/spatial indices
- any render/UI geometry or visualization state

## Related specs
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_DETERMINISM_GRADES.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_FIELDS_EVENTS.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_LOD.md`
- `docs/SPEC_VM.md`
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_MIGRATIONS.md`
- `docs/SPEC_FEATURE_EPOCH.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
- `docs/SPEC_POSE_AND_ANCHORS.md`
- `docs/SPEC_TRANS_STRUCT_DECOR.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`
- `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`
- `docs/SPEC_TIERS.md`

## Engine core eligibility

> Any system that cannot be hashed, replayed, budgeted, and ordered canonically
> is not eligible to exist in the engine core.
