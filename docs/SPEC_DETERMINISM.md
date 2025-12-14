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

## Determinism guarantee (authoritative)
Given:
- the same initial authoritative state (including version ids and RNG state)
- the same deterministic command stream (intents) grouped by tick

Then:
- every peer MUST produce the same authoritative state and the same world hash
  after each tick
- byte-for-byte, platform-independent (within the supported invariants below)

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

### Canonical comparison / sorting
When a stable sort is required, ordering MUST be defined by stable keys:
- primary: family/type id (domain/packet/etc.)
- then: stable numeric id(s)
- then: stable sequence numbers (if required)

Collections that are naturally unordered (hash maps, sets) MUST be reified into
arrays and sorted using canonical comparators before deterministic iteration.

### Canonical registry ordering
Deterministic registries (packet types, field types, event/message types, etc.)
MUST iterate in a canonical, stable order:
- primary: ascending `type_id` (`u64`)
- tie-break: ascending `schema_id` (`u64`), then ascending schema versions

### Canonical TLV ordering
All deterministic TLV containers (used for hashing, replay, or lockstep) MUST:
- use explicit little-endian numeric encoding in TLV headers
- be canonicalized before hashing or comparison

Canonicalization rules implemented by `res/dg_tlv_canon.*`:
- TLV records are sorted by `(tag, payload_bytes)` ascending
  - `tag` is `u32_le`
  - repeated tags are tie-broken by lexicographic payload bytes, then length
- writers MUST emit explicit lengths and MUST NOT include padding bytes

Unknown TLVs MUST be safely skippable using lengths (forward-compat framing).

### Explicit endianness rule
Determinism paths MUST NOT parse numeric fields via host-endian `memcpy` into
integers. All deterministic IO numeric decoding/encoding MUST use explicit
little-endian routines.

## Fixed-point requirements
Determinism paths MUST use fixed-point math only:
- Q formats only (see `domino/core/fixed.h`)
- conversions and rounding MUST follow the explicit rules/macros in
  `source/domino/core/det_invariants.h`

Forbidden:
- float/double/long double arithmetic in deterministic paths
- math-library functions (sin/cos/etc.) in deterministic paths

Tooling may use floating point only outside determinism paths and MUST NOT feed
float-derived values into deterministic state without explicit quantization.

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
- global grids as logic dependencies (grids may exist only as derived caches)
- world-space baked geometry as authoritative state
- tolerance/epsilon-based solvers and comparisons
- unordered iteration in determinism paths (unordered containers, hash tables)
- UI-driven state mutation (UI/tools emit intents only)
- platform-dependent behavior (endianness, alignment, file order, time)

## Source of truth vs derived cache
**Source of truth (authoritative):**
- world/domain state stored in deterministic structures
- intent and delta streams (with TLV versioning)
- deterministic allocator/RNG state

**Derived cache (must be regenerable):**
- LOD representations R1–R3 (see `docs/SPEC_LOD.md`)
- knowledge/visibility/comms state (see `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`)
- compiled/expanded graph adjacency caches (see `docs/SPEC_GRAPH_TOOLKIT.md`)
- any render/UI geometry or visualization state

## Related specs
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_FIELDS_EVENTS.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_LOD.md`
- `docs/SPEC_VM.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
- `docs/SPEC_POSE_AND_ANCHORS.md`
- `docs/SPEC_TRANS_STRUCT_DECOR.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`
- `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`
