--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- None. Game consumes engine primitives where applicable.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- Canonical formats and migrations defined here live under `schema/`.

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
# SPEC_PACKETS — Typed Packet ABI + TLV Payloads

This spec defines the deterministic packet families used by SIM, replay, and
lockstep. It does not define platform transports; it defines stable content.

## Scope
Applies to:
- deterministic command streams (intents)
- deterministic state mutation streams (deltas)
- deterministic outputs (events/messages/observations)
- debug probes that MUST NOT affect simulation state

## Packet families (authoritative taxonomy)
Packet family names are semantic; actual encodings are TLV-versioned.

- **Intent**: external command input for tick `N` (from UI/tools/agents).
- **Action**: validated internal command representation (optional encoding).
- **Delta**: authoritative mutation record applied at commit points.
- **Event**: discrete fact about something that occurred this tick (derived).
- **Message**: directed/broadcast communication (derived, deterministic routing).
- **Field**: field update/sample framing (derived; fixed-point only).
- **Observation**: sampled outputs for observers/agents (derived).
- **Probe**: debug/query packet; MUST be read-only (no state mutation).

## ABI: packet framing
All deterministic packets are framed as:
- `dg_pkt_hdr` (fixed fields; no pointers)
- `payload` bytes (external buffer) of length `hdr.payload_len`

### `dg_pkt_hdr` fields
The authoritative in-memory header is defined in `source/domino/sim/pkt/dg_pkt_common.h`.

Fields:
- `type_id` (`u64`): packet type identifier (taxonomy)
- `schema_id` (`u64`): payload schema identifier
- `schema_ver` (`u16`): payload schema version
- `flags` (`u16`)
- `tick` (`u64`): authoritative simulation tick
- `src_entity` (`u64`): optional; `0` means none
- `dst_entity` (`u64`): optional; `0` means none/broadcast
- `domain_id` (`u64`): stable domain id (0 allowed)
- `chunk_id` (`u64`): stable chunk id (0 allowed)
- `seq` (`u32`): strictly for stable ordering within tick/phase
- `payload_len` (`u32`): TLV payload byte length

### Canonical wire encoding (endianness)
Deterministic IO MUST NOT serialize/hash raw C structs.

When serializing or hashing the header:
- Each numeric field is encoded explicitly as little-endian.
- Field order is exactly the list above.
- Total header wire bytes: 68 (`DG_PKT_HDR_WIRE_BYTES`).

## TLV payload format
All packet payloads are TLV containers (tag-length-value):
- `tag` (`u32_le`)
- `len` (`u32_le`)
- `payload` (`len` bytes)

Rules:
- Introducing new packet types requires a deterministic registry update.
- Changing payload shape requires incrementing `schema_ver`.
- Unknown types MUST be skippable by length.
- Unknown versions MUST either be rejected explicitly or upgraded explicitly;
  silent reinterpretation is forbidden.

## Schema validation policy
Implemented plumbing:
- Payloads can be validated as well-formed TLV containers.
- Optional schema conformance validation uses `dg_tlv_schema_desc` field lists.
- No implicit upgrades are performed by default; upgrades (if any) must be
  explicit and versioned.

## Placement/edit intent contract
All placement/edit intents (BUILD / TRANS / STRUCT / DECOR) MUST be expressed as:
- `dg_anchor`: a parametric reference to authoring primitives (stable IDs)
- `dg_pose` offset: a local pose relative to the anchor

Rules:
- All fixed-point values MUST be quantized before becoming authoritative state.
- Raw world-space meshes/vertex lists are forbidden in intents.
- Anchors are authoritative; world-space geometry is derived cache only.

## Stable ID requirements
Packets that reference world objects MUST use stable numeric IDs:
- domain ids, entity ids, frame ids, graph node ids, etc.
- IDs MUST NOT be pointer-derived and MUST have a total order.

Within packet payloads:
- repeated elements MUST be emitted in canonical order (sorted by stable key)
- tie-breaking MUST be stable and explicit (see `docs/specs/SPEC_DETERMINISM.md`)

For packet batches/streams:
- canonical ordering is `(tick, stream_id, family, primary_key..., seq)`

## Determinism guarantees
- Packet parsing and serialization MUST be platform-independent.
- Packets MUST NOT contain floats or platform-dependent representations.
- Packet order MUST be explicit; no implicit reliance on container iteration.

## Forbidden behaviors
- Encoding raw memory blobs that include padding/pointers.
- UI-driven mutation: UI/tools MUST emit intents only; they MUST NOT write
  directly to engine state.
- Platform-dependent fields (paths, timestamps, locale-dependent strings).

## Type IDs and schema IDs
Implemented policy:
- `type_id` and `schema_id` are **content-defined** 64-bit IDs.
- The canonical construction is `FNV-1a 64` of a canonical ASCII string.
  - The string MUST be stable and namespace-qualified (e.g. `pkt:event/foo`,
    `schema:obs/bar@v1`).
- `0` is reserved for "none/unspecified" where allowed.

## Pack ID remap tables
Packs may be referenced by stable IDs in deterministic data. When a compact or
machine-local runtime ID is required, a remap table MUST be provided:
- A deterministic TLV idmap maps `external_pack_id -> runtime_pack_id`.
- Simulation determinism paths MUST NOT allocate new IDs; missing mappings are
  an error.

## Source of truth vs derived cache
**Source of truth:**
- intent streams (player/tool/agent commands)
- delta streams (authoritative state mutations)
- schema/version identifiers for packet interpretation

**Derived cache:**
- events/messages/observations (must be reproducible from state + deltas)
- debug probe outputs

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_FIELDS_EVENTS.md`
- `docs/SPEC_VM.md`
